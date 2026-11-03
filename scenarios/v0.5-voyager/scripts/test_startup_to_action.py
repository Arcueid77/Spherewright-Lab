"""Offline timing and original-action fault checks, not runtime acceptance."""
import unittest

import startup_to_action as gate


class Clock:
    now = 0.0
    def __call__(self): return self.now


class Fixture:
    def __init__(self):
        self.clock = Clock(); self.events = []; self.calls = []
        self.proof = {k: True for k in gate.READINESS_FLAGS}
        self.ready_seconds = 70; self.resume_seconds = 8; self.work_seconds = 2
        self.work_kind = 'transfer'; self.unknown = False; self.delta = True
    def offline_preflight(self): self.clock.now += 300; return self.proof
    def launch_once(self, deadline): self.calls.append('launch'); self.clock.now += 5; return 'process'
    def wait_ready(self, process, deadline): self.clock.now += self.ready_seconds; return 'ready'
    def prepare_resume(self, ready, deadline): self.calls.append('prepare_resume'); return 'fresh-plan'
    def commit_resume_once(self, prepared): self.calls.append('commit_resume'); return 'resume'
    def wait_original(self, handle):
        self.clock.now += self.resume_seconds if handle == 'resume' else self.work_seconds
        return dict(actionId=handle, terminal=True, succeeded=not self.unknown,
                    state='outcome_unknown' if self.unknown else 'completed')
    def verify_loaded(self, result, deadline): return 'owned-world'
    def prepare_first_work(self, loaded, deadline): return dict(action_kind=self.work_kind)
    def commit_first_work_once(self, prepared): self.calls.append('commit_work'); return 'work'
    def verify_progress(self, prepared, result): return self.delta
    def continue_prepared_work(self, result): self.calls.append('continue')
    def cleanup_known_state(self): self.calls.append('cleanup')
    def run(self): return gate.run(self, self.events.append, self.clock)


class StartupGateTests(unittest.TestCase):
    def test_later_unknown_preserves_successful_startup_and_blocks_competing_cleanup(self):
        f = Fixture()
        def later_unknown(result):
            f.active = 'original-later-action'
            raise RuntimeError('retained unknown build')
        f.continue_prepared_work = later_unknown
        r=f.run()
        self.assertTrue(r.passed)
        self.assertEqual('continuation_reconciliation_required',r.outcome)
        self.assertEqual('retained unknown build',r.continuation_failure)
        self.assertNotIn('cleanup',f.calls)
    def test_retryable_read_timeout_is_observed_again_without_restarting(self):
        clock = Clock(); calls = []
        def probe():
            calls.append('read')
            if len(calls) == 1: raise TimeoutError('read-only timeout')
            return 'fresh-state'
        def sleep(seconds): clock.now += seconds
        self.assertEqual('fresh-state', gate.retry_read_only(probe, 120, lambda e: isinstance(e, TimeoutError), clock, sleep))
        self.assertEqual(['read', 'read'], calls)
    def test_read_observation_does_not_renew_the_deadline(self):
        clock = Clock(); clock.now = 119.9
        def probe(): raise TimeoutError()
        def sleep(seconds): clock.now += seconds
        with self.assertRaises(gate.DeadlineExceeded):
            gate.retry_read_only(probe, 120, lambda e: isinstance(e, TimeoutError), clock, sleep)
        self.assertEqual(120, clock.now)
    def test_cleanup_failure_keeps_original_failure_and_report(self):
        f = Fixture(); f.ready_seconds = gate.LIMIT_SECONDS - 4
        def fail_cleanup(): raise RuntimeError('menu read pending')
        f.cleanup_known_state = fail_cleanup; r = f.run()
        self.assertEqual('cleanup_required', r.outcome)
        self.assertIn(f'{gate.LIMIT_SECONDS:g} seconds', r.failure)
        self.assertEqual('menu read pending', r.cleanup_failure)
        self.assertNotIn('commit_resume', f.calls)
    def test_slow_offline_work_precedes_launch_and_real_progress_finishes_in_budget(self):
        f = Fixture(); r = f.run()
        self.assertTrue(r.passed); self.assertEqual(85, r.startup_seconds)
        self.assertEqual(['launch', 'prepare_resume', 'commit_resume', 'commit_work', 'continue'], f.calls)
    def test_missing_offline_proof_never_opens_game(self):
        for key in gate.READINESS_FLAGS:
            f = Fixture(); f.proof[key] = False
            self.assertEqual('offline_not_ready', f.run().outcome); self.assertEqual([], f.calls)
    def test_late_menu_does_not_load_or_restart(self):
        f = Fixture(); f.ready_seconds = gate.LIMIT_SECONDS - 4
        self.assertFalse(f.run().passed); self.assertEqual(['launch', 'cleanup'], f.calls)
    def test_accepted_load_finishes_original_after_deadline_then_cleans_up(self):
        f = Fixture(); f.resume_seconds = gate.LIMIT_SECONDS - 74
        self.assertFalse(f.run().passed)
        self.assertEqual(1, f.calls.count('commit_resume')); self.assertNotIn('commit_work', f.calls)
        self.assertIn('cleanup', f.calls)
    def test_unknown_action_is_not_replayed_or_given_competing_cleanup(self):
        f = Fixture(); f.unknown = True; r = f.run()
        self.assertTrue(r.unresolved_commit); self.assertEqual('reconciliation_required', r.outcome)
        self.assertEqual(1, f.calls.count('commit_resume')); self.assertNotIn('cleanup', f.calls)
    def test_metadata_cannot_count_as_first_actual_work(self):
        for kind in ('read', 'save', 'resume-owned-game'):
            f = Fixture(); f.work_kind = kind
            self.assertFalse(f.run().passed); self.assertNotIn('commit_work', f.calls)
    def test_successful_action_without_observed_delta_is_not_progress(self):
        f = Fixture(); f.delta = False
        self.assertFalse(f.run().passed); self.assertIn('cleanup', f.calls)
    def test_boundary_is_strict_even_when_work_terminally_succeeds(self):
        f = Fixture(); f.work_seconds = gate.LIMIT_SECONDS - 83
        self.assertFalse(f.run().passed); self.assertNotIn('continue', f.calls)
        self.assertEqual(1, f.calls.count('commit_work')); self.assertIn('cleanup', f.calls)


if __name__ == '__main__': unittest.main()
