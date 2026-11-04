"""Replay the captured host membership transition with synthetic identifiers."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent/'live'))
from lifetime_contract import qualifies


def captured_host(caller_in_outer=False):
    # The real new host had caller=false in outer jobs while its Codex process
    # belonged to them. Game and Steam were observed false in every job.
    rows = []
    for owner, flags, caller, codex in [
        (40, 15360, caller_in_outer, True),
        (30, 8192, caller_in_outer, True),
        (30, 10240, True, False),
    ]:
        rows.append(dict(ownerPid=owner, limitFlags=flags, killOnClose=True,
                         memberships={'game': False, 'steam': False,
                                      'caller': caller, 'codex-30': codex}))
    return dict(callerAncestry=[10, 20, 30, 40, 50], queriedJobs=rows,
                refusedQueries=[dict(ownerPid=99)])


class LifetimeContractTests(unittest.TestCase):
    def test_old_and_new_observed_host_models(self):
        self.assertTrue(qualifies(captured_host(True)))
        self.assertTrue(qualifies(captured_host(False)))

    def test_each_outer_job_still_protects_game_and_steam(self):
        for index in range(3):
            for process in ('game', 'steam'):
                for membership in (True, None):
                    evidence = captured_host()
                    evidence['queriedJobs'][index]['memberships'][process] = membership
                    self.assertFalse(qualifies(evidence))

    def test_missing_group_or_unexamined_caller_owner_refuses(self):
        for index in range(3):
            evidence = captured_host()
            evidence['queriedJobs'].pop(index)
            self.assertFalse(qualifies(evidence))
        for owner in (10, 20, 30, 40):
            evidence = captured_host()
            evidence['refusedQueries'].append(dict(ownerPid=owner))
            self.assertFalse(qualifies(evidence))

    def test_unrelated_system_jobs_do_not_claim_complete_system_coverage(self):
        evidence = captured_host()
        evidence['queriedJobs'].append(dict(ownerPid=99, limitFlags=8192,
            killOnClose=True, memberships={'caller': False, 'codex-30': False,
                                           'game': None, 'steam': None}))
        self.assertTrue(qualifies(evidence))
        evidence['callerAncestry'] = [10, 20, 50]
        self.assertFalse(qualifies(evidence))


if __name__ == '__main__':
    unittest.main()
