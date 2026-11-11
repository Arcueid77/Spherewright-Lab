from pathlib import Path
from types import SimpleNamespace
import copy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent / 'live'))
from driver import Live


class FirstStorageTransferTests(unittest.TestCase):
    def make_driver(self, direction='storage-to-player'):
        writes = {}
        work = dict(kind='storage-transfer', direction=direction, entityId=17, itemId=1120, count=200)
        runtime = SimpleNamespace(config=dict(firstOperation=work), put=lambda name, value: writes.update({name: value}))
        live = Live(runtime)
        live.ctx = dict(sessionId='synthetic', planetId=104)
        live.player = lambda: dict(stateHash='synthetic-player')
        live.entity = lambda entity: dict(stateHash='synthetic-storage', objectId=entity)
        calls = []
        def call(tool, arguments):
            calls.append((tool, arguments))
            return dict(prepared=True, commitAllowedNow=True, commitBlockers=[], planToken='synthetic-token')
        live.call = call
        return live, writes, calls

    def receipt(self, direction='storage-to-player'):
        sign = 1 if direction == 'storage-to-player' else -1
        return dict(actionId='synthetic-original', actionKind='transfer', terminal=True, succeeded=True,
                    beforeTargetAmount=300, afterTargetAmount=300-sign*200,
                    itemDeltas=[dict(itemId=1120, delta=sign*200)])

    def test_prepares_one_exact_native_storage_transfer_without_committing(self):
        for direction in ['storage-to-player', 'player-to-storage']:
            with self.subTest(direction=direction):
                live, _, calls = self.make_driver(direction)
                prepared = live.prepare_first_work({}, 100)
                self.assertEqual('transfer', prepared['action_kind'])
                self.assertEqual('spherewright_commit_transfer', prepared['tool'])
                self.assertEqual(1, len(calls))
                tool, arguments = calls[0]
                self.assertEqual('spherewright_prepare_transfer', tool)
                self.assertEqual(direction, arguments['direction'])
                self.assertEqual(200, arguments['count'])
                self.assertEqual(17, arguments['storageEntityId'])
                self.assertEqual('synthetic-player', arguments['expectedPlayerStateHash'])
                self.assertEqual('synthetic-storage', arguments['expectedStorageStateHash'])

    def test_progress_requires_the_paired_same_tick_receipt_in_both_directions(self):
        for direction in ['storage-to-player', 'player-to-storage']:
            with self.subTest(direction=direction):
                live, writes, _ = self.make_driver(direction)
                prepared = live.prepare_first_work({}, 100)
                receipt = self.receipt(direction)
                self.assertTrue(live.verify_progress(prepared, receipt))
                self.assertTrue(writes['actual-progress.private.json']['noReplay'])
                self.assertEqual(receipt, writes['actual-progress.private.json']['originalSameTickReceipt'])

    def test_an_incorrect_or_incomplete_receipt_cannot_prove_work(self):
        for fault in ['terminal', 'succeeded', 'kind', 'target_delta', 'player_delta', 'negative', 'missing']:
            with self.subTest(fault=fault):
                live, _, _ = self.make_driver()
                prepared = live.prepare_first_work({}, 100)
                receipt = copy.deepcopy(self.receipt())
                if fault == 'terminal': receipt['terminal'] = False
                if fault == 'succeeded': receipt['succeeded'] = False
                if fault == 'kind': receipt['actionKind'] = 'move'
                if fault == 'target_delta': receipt['afterTargetAmount'] += 1
                if fault == 'player_delta': receipt['itemDeltas'][0]['delta'] = 199
                if fault == 'negative': receipt['afterTargetAmount'] = -1
                if fault == 'missing': del receipt['beforeTargetAmount']
                self.assertFalse(live.verify_progress(prepared, receipt))

    def test_invalid_operation_shapes_fail_before_any_prepare(self):
        for field, value in [('direction', 'generator-fuel'), ('count', 0), ('count', -1), ('itemId', 0)]:
            with self.subTest(field=field, value=value):
                live, _, calls = self.make_driver()
                live.runtime.config['firstOperation'][field] = value
                with self.assertRaises(RuntimeError): live.prepare_first_work({}, 100)
                self.assertEqual([], calls)


if __name__ == '__main__':
    unittest.main()
