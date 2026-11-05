"""Caller-only startup gate: 120-second target, 300-second hard limit.

Adapters must use public MCP, retain original actions, and prepare all expensive
offline work before launch. An accepted action is reconciled even after expiry.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import time, math
from typing import Callable, Protocol

TARGET_SECONDS = 120.0
LIMIT_SECONDS = 300.0
READINESS_FLAGS = (
    'game_stopped', 'source_qualified', 'installed_match', 'backup_complete',
    'original_actions_reconciled', 'budgets_preserved', 'first_operation_ready',
)
ACTUAL_WORK_KINDS = frozenset(('move', 'transfer', 'handcraft', 'build', 'configure-building', 'harvest', 'select-research', 'supply_mecha_warpers', 'interplanetary-flight'))


def paid_native_home_effect(result):
    p=result.get('nativeHomeReturnFirstEffect') or {}
    fields=('coreBefore','coreAfter','nativeThrustDebitJoules','velocityBeforeX','velocityBeforeY','velocityBeforeZ',
            'velocityAfterX','velocityAfterY','velocityAfterZ','positionBeforeX','positionBeforeY','positionBeforeZ',
            'positionAfterX','positionAfterY','positionAfterZ')
    return (result.get('actionKind')=='interplanetary-flight' and result.get('state') in ('waiting_for_game','executing','completed')
        and p.get('evidenceScope') in ('synchronous_paid_native_home_return_control','paid_native_home_return_player_tick')
        and p.get('nativeBindingVerified') is True and p.get('paidControlObserved') is True
        and all(type(p.get(k)) in (int,float) and math.isfinite(p[k]) for k in fields)
        and p['coreBefore']>=0 and p['coreAfter']>=0 and p['nativeThrustDebitJoules']>0
        and (any(p['velocityBefore'+k]!=p['velocityAfter'+k] for k in 'XYZ')
            or any(p['positionBefore'+k]!=p['positionAfter'+k] for k in 'XYZ')))


class DeadlineExceeded(RuntimeError):
    pass

class StartupReadinessFailure(RuntimeError):
    """An observed pre-recovery failure; preserve and close the unopened world."""


class CommitRejected(RuntimeError):
    """Only an authoritative pre-acceptance Native refusal may use this type."""


def retry_read_only(probe, deadline, is_transient, clock=time.monotonic, sleep=time.sleep):
    """Retry only a caller-designated READ, within the original startup clock.

    A read timeout is not a terminal game result. Never wrap a commit in this
    helper; accepted actions keep their original handle and are not resubmitted.
    """
    while clock() < deadline:
        try:
            return probe()
        except Exception as error:
            if not is_transient(error):
                raise
        remaining = deadline - clock()
        if remaining > 0:
            sleep(min(.25, remaining))
    raise DeadlineExceeded('Read-only readiness observation exceeded the original startup budget')


class Adapter(Protocol):
    def offline_preflight(self) -> dict: ...
    def launch_once(self, deadline: float): ...
    def wait_ready(self, process, deadline: float): ...
    def prepare_resume(self, ready, deadline: float): ...
    def commit_resume_once(self, prepared): ...
    def wait_original(self, handle): ...
    def verify_loaded(self, result, deadline: float): ...
    def prepare_first_work(self, loaded, deadline: float): ...
    def commit_first_work_once(self, prepared): ...
    def verify_progress(self, prepared, result) -> bool: ...
    def continue_prepared_work(self, result): ...
    def cleanup_known_state(self): ...


@dataclass
class StartupReport:
    passed: bool = False
    outcome: str = 'not_started'
    startup_seconds: float | None = None
    phase_seconds: dict = field(default_factory=dict)
    first_action_id: str | None = None
    failure: str | None = None
    unresolved_commit: bool = False
    cleanup_failure: str | None = None
    continuation_failure: str | None = None


def run(adapter: Adapter, emit: Callable[[dict], None], clock=time.monotonic) -> StartupReport:
    """Exactly one launch/resume/work submission; never retries a write.

    The timer starts BEFORE dispatching the normal launch request, including
    Steam delay. Offline checks run before the timer and before any game start.
    Only actual successful game progress qualifies. Reads, Load and Save do not.
    """
    report = StartupReport()
    proof = adapter.offline_preflight()
    if any(proof.get(name) is not True for name in READINESS_FLAGS):
        report.outcome = 'offline_not_ready'
        report.failure = 'Complete offline readiness and first-operation preparation before opening the game.'
        emit(asdict(report))
        return report
    started = clock()
    deadline = started + LIMIT_SECONDS
    launched = False

    def checkpoint(name):
        elapsed = clock() - started
        report.phase_seconds[name] = elapsed
        emit(dict(event=name, elapsed_seconds=elapsed, target_seconds=TARGET_SECONDS, limit_seconds=LIMIT_SECONDS))
        if elapsed >= LIMIT_SECONDS:
            raise DeadlineExceeded(f'{name}: startup-to-action exceeded {LIMIT_SECONDS:g} seconds')

    def submit(method, prepared, first_effect=False):
        report.unresolved_commit = True
        try:
            handle = method(prepared)
        except CommitRejected:
            report.unresolved_commit = False
            raise
        result = adapter.wait_first_effect(handle, prepared, deadline) if first_effect and hasattr(adapter,'wait_first_effect') else adapter.wait_original(handle)
        if first_effect and prepared.get('action_kind')=='interplanetary-flight' and result.get('terminal') is not True:
            if result.get('actionId')!=handle or not paid_native_home_effect(result):
                raise RuntimeError('No paid original Native home-return effect; keep the pending handle for reconciliation.')
            # Actual paid motion has begun; completion remains owned by the same
            # writer. Startup success is never relabelled terminal landing.
            return result
        if result.get('terminal') is not True or result.get('state') == 'outcome_unknown':
            raise RuntimeError('Original accepted action needs reconciliation; no replay or competing cleanup.')
        report.unresolved_commit = False
        if result.get('succeeded') is not True:
            raise RuntimeError('Original action terminally failed; preserve its exact receipt.')
        return result

    try:
        # A launch exception can still mean a process was created: cleanup must
        # observe and reconcile it, never issue a second launch.
        launched = True
        process = adapter.launch_once(deadline)
        checkpoint('launch_dispatched')
        ready = adapter.wait_ready(process, deadline)
        checkpoint('menu_modules_ready')
        prepared = adapter.prepare_resume(ready, deadline)
        checkpoint('resume_prepared')
        result = submit(adapter.commit_resume_once, prepared)
        checkpoint('resume_completed')
        loaded = adapter.verify_loaded(result, deadline)
        checkpoint('owned_world_verified')
        work = adapter.prepare_first_work(loaded, deadline)
        if work.get('action_kind') not in ACTUAL_WORK_KINDS:
            raise RuntimeError('First work must be a prepared real operation, not a read, Load, Save or heartbeat.')
        checkpoint('first_work_prepared')
        result = submit(adapter.commit_first_work_once, work, first_effect=True)
        if not adapter.verify_progress(work, result):
            raise RuntimeError('No actual progress proven by the original action and fresh state delta.')
        checkpoint('first_actual_work_completed')
        report.passed = True
        report.outcome = 'started_actual_work'
        report.first_action_id = result.get('actionId')
        report.startup_seconds = clock() - started
        emit(asdict(report))
        # No return to planning at the menu: continue the already prepared
        # executor immediately. A validation-only adapter preserves and closes.
        adapter.continue_prepared_work(result)
        report.unresolved_commit = bool(getattr(adapter,'active',None))
        return report
    except Exception as error:
        if report.passed:
            report.continuation_failure = str(error)
            report.unresolved_commit = bool(getattr(adapter, 'active', None))
            report.outcome = 'continuation_reconciliation_required' if report.unresolved_commit else 'continuation_failed'
        else:
            report.outcome = 'reconciliation_required' if report.unresolved_commit else 'startup_failed'
            report.failure = str(error)
        if report.startup_seconds is None:
            report.startup_seconds = clock() - started
        emit(asdict(report))
        preserve = getattr(adapter, 'failure_requires_preservation', lambda _error: True)(error)
        if launched and not report.unresolved_commit and preserve:
            try:
                adapter.cleanup_known_state()
            except Exception as cleanup_error:
                report.cleanup_failure = str(cleanup_error)
                report.outcome = 'cleanup_required'
                emit(asdict(report))
        return report
