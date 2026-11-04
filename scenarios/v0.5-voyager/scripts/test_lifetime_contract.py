"""Replay variable host groups, shared handles, unknowns and complete ownership."""
from pathlib import Path
import copy,json,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent/'live'))
from lifetime_contract import qualifies
from job_lifetime_capture import application_scope

def observed_host(groups=2):
 # Membership shapes replay the captured two/three-group hosts. Process IDs,
 # inventory and identity fields are synthetic model inputs, not a game proof.
 processes=[dict(ProcessId=40,ParentProcessId=99,Name='ChatGPT.exe',createdFileTime=1),
  dict(ProcessId=30,ParentProcessId=40,Name='codex.exe',createdFileTime=2),
  dict(ProcessId=20,ParentProcessId=30,Name='pwsh.exe',createdFileTime=3),
  dict(ProcessId=10,ParentProcessId=20,Name='python.exe',createdFileTime=4),
  dict(ProcessId=31,ParentProcessId=30,Name='other-worker.exe',createdFileTime=5),
  dict(ProcessId=80,ParentProcessId=99,Name='steam.exe',createdFileTime=2),
  dict(ProcessId=81,ParentProcessId=80,Name='DSPGAME.exe',createdFileTime=6)]
 root,scope,chain=application_scope(processes,10);rows=[]
 captures=json.loads((Path(__file__).parent/'fixtures/captured-host-job-membership-shapes.json').read_text())['cases']
 captured=next(case['rows'] for case in captures if len(case['rows'])==groups)
 for i,row in enumerate(captured):
  flags=row['limitFlags']
  memberships={name:False for name in ['game','steam','caller']+['scope-'+str(pid) for pid in chain]}
  memberships['scope-30']=row['applicationMember'];memberships['caller']=row['callerMember']
  memberships['game']=row['gameMember'];memberships['steam']=row['steamMember']
  rows.append(dict(objectKey=str(i),ownerPids=[40 if i==0 else 30],limitFlags=flags,killOnClose=True,memberships=memberships))
 return dict(schemaVersion=2,targetKind='game',gameIdentityVerified=True,processIdentitiesStable=True,
  gameProcessId=81,steamProcessId=80,callerProcessId=10,processes=processes,scopeRootPid=root,
  scopePids=sorted(scope),callerAncestry=chain,jobMetadataEnumerationComplete=True,
  enumeratedJobs=[dict(objectKey=j['objectKey'],ownerPids=j['ownerPids']) for j in rows],
  queriedJobs=rows,unresolvedJobObjects=[],queryAttempts=[],anyJobMembership=dict(game=False,steam=True),
  queryOnlyJobAccess=4,gameMemoryReads=0,jobAssignments=0,jobLimitChanges=0,processTerminations=0)

class LifetimeContractTests(unittest.TestCase):
 def test_two_and_three_observed_group_shapes_need_no_magic_count(self):
  self.assertTrue(qualifies(observed_host(2)));self.assertTrue(qualifies(observed_host(3)))
 def test_every_relevant_game_and_steam_membership_must_be_false(self):
  for group in range(2):
   for target in ('game','steam'):
    for value in (True,None):
     snapshot=observed_host();snapshot['queriedJobs'][group]['memberships'][target]=value
     self.assertFalse(qualifies(snapshot))
 def test_omitted_or_unqueryable_owned_object_is_not_hidden_by_other_jobs(self):
  for unresolved in (False,True):
   snapshot=observed_host();row=snapshot['queriedJobs'].pop()
   if unresolved:snapshot['unresolvedJobObjects'].append(dict(objectKey=row['objectKey'],ownerPids=row['ownerPids']))
   self.assertFalse(qualifies(snapshot))
 def test_sibling_owned_shared_job_is_covered_even_when_caller_not_a_member(self):
  snapshot=observed_host();job=copy.deepcopy(snapshot['queriedJobs'][0]);job.update(objectKey='shared',ownerPids=[99,31])
  job['memberships']={name:False for name in job['memberships']};job['memberships']['steam']=True
  snapshot['queriedJobs'].append(job);snapshot['enumeratedJobs'].append(dict(objectKey='shared',ownerPids=[99,31]))
  self.assertFalse(qualifies(snapshot))
 def test_resolved_duplicate_query_failure_is_not_an_unresolved_object(self):
  snapshot=observed_host();snapshot['queryAttempts'].append(dict(objectKey='0',ownerPid=40,reason='first_handle_refused'))
  self.assertTrue(qualifies(snapshot))
 def test_unreported_kernel_address_keeps_each_owner_handle_in_inventory(self):
  snapshot=observed_host()
  for j in snapshot['queriedJobs']:j['objectKey']='handle-'+str(j['ownerPids'][0])+'-'+j['objectKey']
  snapshot['enumeratedJobs']=[dict(objectKey=j['objectKey'],ownerPids=j['ownerPids']) for j in snapshot['queriedJobs']]
  self.assertTrue(qualifies(snapshot));snapshot['queriedJobs'].pop();self.assertFalse(qualifies(snapshot))
 def test_unrelated_system_objects_remain_explicitly_unexamined(self):
  snapshot=observed_host();snapshot['enumeratedJobs'].append(dict(objectKey='system',ownerPids=[99]))
  snapshot['unresolvedJobObjects'].append(dict(objectKey='system',ownerPids=[99]));self.assertTrue(qualifies(snapshot))
  snapshot['enumeratedJobs'][-1]['ownerPids'].append(31);snapshot['unresolvedJobObjects'][-1]['ownerPids'].append(31)
  self.assertFalse(qualifies(snapshot))
 def test_process_tree_identity_mutation_and_missing_inventory_refuse(self):
  for fault in ('tree','identity','enumeration','legacy','probe','unknown-any'):
   snapshot=observed_host()
   if fault=='tree':next(p for p in snapshot['processes'] if p['ProcessId']==80)['ParentProcessId']=40
   elif fault=='identity':snapshot['processIdentitiesStable']=False
   elif fault=='enumeration':snapshot['jobMetadataEnumerationComplete']=False
   elif fault=='legacy':snapshot['schemaVersion']=1
   elif fault=='probe':snapshot['targetKind']='probe'
   else:snapshot['anyJobMembership']['steam']=None
   self.assertFalse(qualifies(snapshot),fault)
 def test_reused_parent_pid_does_not_make_an_older_process_a_descendant(self):
  snapshot=observed_host();snapshot['processes'].append(dict(ProcessId=90,ParentProcessId=31,Name='old.exe',createdFileTime=1))
  self.assertNotIn(90,application_scope(snapshot['processes'],10)[1])

if __name__=='__main__':unittest.main()
