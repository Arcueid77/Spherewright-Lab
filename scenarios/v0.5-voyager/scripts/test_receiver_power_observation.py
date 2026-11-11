"""Exercise receiver sampling through the production shared-driver entry."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / 'live'))
from contracts import validate_native_calls, validate_steps
from factory import Factory


def sample(tick, generated=100):
    return dict(sessionId='synthetic-session', planetId=7, objectId=12, itemId=2208,
        capturedAtGameTick=tick, rayReceiver=dict(nativeBindingVerified=True,
            planetId=7, starId=1, entityId=12, itemId=2208, generatorComponentId=4,
            networkId=2, capturedAtGameTick=tick, mode='electricity', productItemId=0,
            capacityEnergyPerTick=1000, generatedEnergyPerTick=generated))


def declaration():
    return dict(kind='observe-receiver-power', role='power', entity=12, starId=1,
        networkId=2, gameTicks=6, maximumSampleGapGameTicks=3, pollSeconds=.25,
        maximumSeconds=2)


class ReceiverPowerObservationTests(unittest.TestCase):
    def adapter(self, samples):
        values = iter(samples)
        adapter = Factory.__new__(Factory)
        adapter.ctx = dict(sessionId='synthetic-session', planetId=7)
        adapter.c = type('Client', (), dict(deadline=float('inf')))()
        adapter.refs = {}
        adapter.state = lambda: dict(gameTick=1)
        adapter.entity = lambda _: next(values)
        saved = {}
        adapter.runtime = type('Evidence', (), dict(
            put=lambda _, name, value: saved.update({name: value})))()
        return adapter, saved

    def test_complete_positive_interval_uses_actual_power_and_retains_every_cut(self):
        adapter, saved = self.adapter([sample(100), sample(103, 50), sample(106)])
        with patch('dyson_observers.time.sleep'):
            proof = adapter.step(declaration())
        self.assertEqual(3, proof['sampleCount'])
        self.assertEqual(106, proof['declaredEndGameTick'])
        self.assertEqual(3, proof['largestSampleGapGameTicks'])
        self.assertEqual(3000, proof['minimumSampledPowerWatts'])
        self.assertEqual(0, proof['gameActionsSubmitted'])
        self.assertEqual([100, 103, 106], [cut['capturedAtGameTick']
            for cut in saved['power-samples.private.json']['samples']])
        self.assertTrue(saved['power-proof.private.json']['passed'])

    def test_zero_output_with_positive_capacity_retains_failure_in_the_original_interval(self):
        adapter, saved = self.adapter([sample(100), sample(103, 0), sample(106)])
        with patch('dyson_observers.time.sleep'):
            with self.assertRaisesRegex(RuntimeError, 'sample_not_electricity_output'):
                adapter.step(declaration())
        self.assertFalse(saved['power-samples.private.json']['passed'])
        self.assertEqual(0, saved['power-samples.private.json']['samples'][-1]
            ['rayReceiver']['generatedEnergyPerTick'])
        self.assertNotIn('power-proof.private.json', saved)

    def test_foreign_identity_network_and_photon_mode_are_rejected(self):
        changes = [dict(networkId=3), dict(starId=2), dict(nativeBindingVerified=False),
            dict(entityId=13), dict(mode='photon', productItemId=1208)]
        for change in changes:
            with self.subTest(change=change):
                cut = sample(100)
                cut['rayReceiver'].update(change)
                adapter, saved = self.adapter([cut])
                with self.assertRaises(RuntimeError):
                    adapter.step(declaration())
                self.assertFalse(saved['power-samples.private.json']['passed'])
                self.assertNotIn('power-proof.private.json', saved)

    def test_reused_generator_component_cannot_continue_the_original_receiver_interval(self):
        replaced = sample(103)
        replaced['rayReceiver']['generatorComponentId'] = 5
        adapter, saved = self.adapter([sample(100), replaced])
        with patch('dyson_observers.time.sleep'):
            with self.assertRaisesRegex(RuntimeError, 'receiver_generator_changed'):
                adapter.step(declaration())
        self.assertEqual(2, len(saved['power-samples.private.json']['samples']))

    def test_missing_sample_coverage_or_backwards_ticks_do_not_pass(self):
        for tick in (99, 104):
            with self.subTest(tick=tick):
                adapter, saved = self.adapter([sample(100), sample(tick)])
                with patch('dyson_observers.time.sleep'):
                    with self.assertRaisesRegex(RuntimeError, 'sample_coverage_lost'):
                        adapter.step(declaration())
                self.assertNotIn('power-proof.private.json', saved)

    def test_receiver_and_factory_timestamps_must_share_the_current_native_cut(self):
        cut = sample(100)
        cut['capturedAtGameTick'] = 99
        adapter, saved = self.adapter([cut])
        with self.assertRaisesRegex(RuntimeError, 'current_native_cut_unproved'):
            adapter.step(declaration())
        self.assertFalse(saved['power-samples.private.json']['passed'])

    def test_frozen_game_ticks_expire_without_turning_repeated_frames_into_duration(self):
        adapter, saved = self.adapter([sample(100), sample(100)])
        with patch('dyson_observers.time.monotonic', side_effect=[0, 0, 0, 1, 1, 2]), \
                patch('dyson_observers.time.sleep'):
            with self.assertRaisesRegex(RuntimeError, 'finite_receiver_observation_expired'):
                adapter.step(declaration())
        self.assertFalse(saved['power-samples.private.json']['passed'])
        self.assertNotIn('power-proof.private.json', saved)

    def test_late_read_cannot_pass_the_declared_or_caller_cleanup_deadline(self):
        for caller_deadline, late in ((100, 3), (61, 1.1)):
            with self.subTest(caller_deadline=caller_deadline):
                adapter, saved = self.adapter([sample(100), sample(106)])
                adapter.c.deadline = caller_deadline
                with patch('dyson_observers.time.monotonic', side_effect=[0, 0, 0, .5, late]), \
                        patch('dyson_observers.time.sleep'):
                    with self.assertRaisesRegex(RuntimeError, 'finite_receiver_observation_expired'):
                        adapter.step(declaration())
                self.assertEqual(2, len(saved['power-samples.private.json']['samples']))
                self.assertFalse(saved['power-samples.private.json']['passed'])
                self.assertNotIn('power-proof.private.json', saved)

    def test_plan_requires_finite_positive_duration_gap_and_bound_network(self):
        validate_steps([declaration()])
        for change in (dict(entity=0), dict(entity=''), dict(entity=True),
                dict(networkId=0), dict(gameTicks=0), dict(maximumSampleGapGameTicks=7),
                dict(pollSeconds=0), dict(maximumSeconds=float('inf')),
                dict(maximumSeconds=float('nan'))):
            with self.subTest(change=change):
                step = dict(declaration(), **change)
                with self.assertRaisesRegex(ValueError, 'finite_receiver_observation'):
                    validate_steps([step])

    def test_plan_checks_both_real_sdk_read_shapes(self):
        schemas = dict(spherewright_get_session_state=dict(properties={}, required=[]),
            spherewright_inspect_factory_entity=dict(properties=dict(objectId=dict(type='integer')),
                required=['objectId']))
        validate_native_calls([declaration()], schemas)
        del schemas['spherewright_inspect_factory_entity']
        with self.assertRaisesRegex(ValueError, 'actual_sdk_unknown_tool'):
            validate_native_calls([declaration()], schemas)


if __name__ == '__main__':
    unittest.main()
