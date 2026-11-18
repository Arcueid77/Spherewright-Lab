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
    def test_normal_refuel_passes_only_after_original_success_and_verified_delta(self):
        f=Fixture();f.work_kind='refuel'
        result=f.run();self.assertTrue(result.passed);self.assertIn('commit_work',f.calls);self.assertIn('continue',f.calls)
        f=Fixture();f.work_kind='refuel';f.delta=False
        result=f.run();self.assertFalse(result.passed);self.assertNotIn('continue',f.calls)
    def test_paid_native_control_starts_work_while_the_same_macro_remains_pending(self):
        f=Fixture();f.work_kind='interplanetary-flight'
        effect=dict(actionId='work',actionKind='interplanetary-flight',terminal=False,succeeded=False,state='waiting_for_game',
         nativeHomeReturnFirstEffect=dict(evidenceScope='synchronous_paid_native_home_return_control',nativeBindingVerified=True,
          paidControlObserved=True,coreBefore=10000000,coreAfter=9990000,nativeThrustDebitJoules=10000,
          positionBeforeX=0,positionBeforeY=0,positionBeforeZ=0,positionAfterX=0,positionAfterY=0,positionAfterZ=0,
          velocityBeforeX=0,velocityBeforeY=0,velocityBeforeZ=7.8,velocityAfterX=1,velocityAfterY=0,velocityAfterZ=7.8))
        def observe_effect(*_):
            f.active='work';return effect
        f.wait_first_effect=observe_effect
        def continue_original(r):
            self.assertFalse(r['terminal']);f.calls.append('wait_same_original_to_terminal')
        f.continue_prepared_work=continue_original
        result=f.run();self.assertTrue(result.passed);self.assertTrue(result.unresolved_commit)
        self.assertIn('wait_same_original_to_terminal',f.calls)
        effect['nativeHomeReturnFirstEffect']['nativeThrustDebitJoules']=0
        self.assertFalse(gate.paid_native_home_effect(effect))

    def test_pending_acceptance_without_native_effect_never_passes_startup(self):
        f=Fixture();f.work_kind='interplanetary-flight'
        f.wait_first_effect=lambda *_:dict(actionId='work',actionKind='interplanetary-flight',terminal=False,state='waiting_for_game')
        result=f.run();self.assertFalse(result.passed);self.assertTrue(result.unresolved_commit)
        self.assertNotIn('continue',f.calls);self.assertNotIn('cleanup',f.calls)

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

    def test_repeated_preload_reads_back_off_without_delaying_first_retry(self):
        clock = Clock(); calls = []; waits = []
        def probe():
            calls.append(clock.now)
            if len(calls) < 4: raise TimeoutError()
            return 'ready'
        def sleep(seconds): waits.append(seconds); clock.now += seconds
        self.assertEqual('ready', gate.retry_read_only(probe, 120, lambda e: isinstance(e, TimeoutError), clock, sleep))
        self.assertEqual([.25, .5, 1.0], waits)
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
    def test_approved_longer_startup_keeps_the_original_clock_and_records_its_limit(self):
        f=Fixture();f.ready_seconds=320;f.proof['startup_limit_seconds']=600
        result=f.run();self.assertTrue(result.passed);self.assertEqual(335,result.startup_seconds)
        self.assertEqual(1,f.calls.count('launch'))
        self.assertTrue(any(e.get('limit_seconds')==600 for e in f.events))
        self.assertEqual(600,gate.retained_startup_limit(dict(limitSeconds=600),dict(startupLimitSeconds=600)))
        with self.assertRaisesRegex(ValueError,'original_startup_limit_changed'):
            gate.retained_startup_limit(dict(limitSeconds=300),dict(startupLimitSeconds=600))
    def test_invalid_startup_limit_never_launches(self):
        for value in (0,-1,float('inf'),float('nan'),True,'600'):
            with self.subTest(value=value):
                f=Fixture();f.proof['startup_limit_seconds']=value
                self.assertEqual('offline_not_ready',f.run().outcome);self.assertEqual([],f.calls)
    def test_missing_offline_proof_never_opens_game(self):
        for key in gate.READINESS_FLAGS:
            f = Fixture(); f.proof[key] = False
            self.assertEqual('offline_not_ready', f.run().outcome); self.assertEqual([], f.calls)
    def test_proved_isolated_unknown_can_start_without_claiming_the_old_action_resolved(self):
        f = Fixture(); f.proof['original_actions_reconciled'] = False; f.proof['original_unknowns_isolated'] = True
        self.assertTrue(f.run().passed)
        self.assertFalse(f.proof['original_actions_reconciled'])
        f = Fixture(); f.proof['original_actions_reconciled'] = False; f.proof['original_unknowns_isolated'] = False
        self.assertEqual('offline_not_ready', f.run().outcome); self.assertEqual([], f.calls)
    def test_proved_new_move_inside_recovery_counts_without_an_artificial_second_order(self):
        f=Fixture();f.verify_recovery_as_first_work=lambda *_:True
        result=f.run()
        self.assertTrue(result.passed);self.assertEqual('resume',result.first_action_id)
        self.assertIn('commit_resume',f.calls);self.assertNotIn('commit_work',f.calls);self.assertIn('continue',f.calls)
        f=Fixture();f.verify_recovery_as_first_work=lambda *_:False
        self.assertTrue(f.run().passed);self.assertIn('commit_work',f.calls)
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
