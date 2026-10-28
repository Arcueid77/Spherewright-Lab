"""Offline caller admission/reconciliation; no client, Native or live proof."""
import copy
import datetime as dt
import sys
import unittest

sys.dont_write_bytecode = True
import structured_batch_receipts as checks


class Receipts(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime.now(dt.timezone.utc)
        self.site = dict(nativeBlueprintObjectLimit=12, nativeCheckPerformed=True,
                         nativeCheckPassed=True, objects=[dict(itemId=2001) for _ in range(12)])
        self.plan = dict(prepared=True, commitAllowedNow=True, actionKind='build', commitBlockers=[],
                         planToken='synthetic-unused', expectedStateHash='synthetic-state', stateHashVersion=1,
                         expiresAtUtc=(self.now + dt.timedelta(seconds=30)).isoformat(),
                         blueprintBuild=dict(buildId='synthetic-build', site=self.site),
                         itemBudget=[dict(itemId=2001, count=12)])

    def test_product_capacity_does_not_grant_four_extra_materials(self):
        with self.assertRaises(ValueError):
            checks.prepared_batch(self.plan, 2001, self.now)
        with self.assertRaises(ValueError):
            checks.prepared_batch(self.plan, 2001, self.now, approved_maximum_new_objects=8)
        self.assertEqual(12, checks.prepared_batch(
            self.plan, 2001, self.now, approved_maximum_new_objects=12)['count'])

    def test_thirteen_belts_other_item_expansion_and_wrong_debit_are_refused(self):
        cases = []
        p = copy.deepcopy(self.plan); p['blueprintBuild']['site']['objects'].append(dict(itemId=2001)); cases.append((p, 2001))
        p = copy.deepcopy(self.plan)
        for row in p['blueprintBuild']['site']['objects']: row['itemId'] = 2203
        p['itemBudget'][0]['itemId'] = 2203; cases.append((p, 2203))
        p = copy.deepcopy(self.plan); p['itemBudget'][0]['count'] = 8; cases.append((p, 2001))
        for p, item in cases:
            with self.subTest(item=item), self.assertRaises(ValueError):
                checks.prepared_batch(p, item, self.now, approved_maximum_new_objects=12)

    def test_original_twelve_receipts_share_one_debit_and_cannot_recreate(self):
        original = dict(actionId='synthetic-action', idempotencyKey='synthetic-key',
                        sessionId='synthetic-session', planetId=104, actionKind='build', buildId='synthetic-build')
        control = dict(phase='completed_idle', physicalIdleVerified=True, exactBindingVerified=True,
                       wholeBatchDebitSharedByObjectReceipts=True)
        action = dict(original, terminal=True, succeeded=True, state='completed',
                      blueprintBuildId=original['buildId'], constructionControl=control)
        progress = dict(buildId=original['buildId'], phase='completed', freshWorldReconciled=True,
                        persistenceHealthy=True, stateHash='synthetic-progress', site=self.site,
                        objects=[dict(state='completed', entityId=100+i, inventoryBefore=13, inventoryAfter=1)
                                 for i in range(12)])
        result = checks.observe_original(action, original, progress)
        self.assertEqual(12, result['materialDebit']); self.assertFalse(result['mayCreate'])
        for change in ('different-action', 'unpaid', 'no-idle', 'mismatched-site'):
            a = copy.deepcopy(action); p = copy.deepcopy(progress)
            if change == 'different-action': a['actionId'] = 'synthetic-other'
            if change == 'unpaid': p['objects'][0]['inventoryAfter'] = 2
            if change == 'no-idle': a['constructionControl']['physicalIdleVerified'] = False
            if change == 'mismatched-site': p['site']['objects'].pop()
            with self.subTest(change=change), self.assertRaises(ValueError):
                checks.observe_original(a, original, p)
        action.update(state='outcome_unknown', succeeded=False)
        result = checks.observe_original(action, original, progress)
        self.assertEqual('original_reconciliation_only', result['state']); self.assertFalse(result['mayCreate'])


if __name__ == '__main__':
    unittest.main()
