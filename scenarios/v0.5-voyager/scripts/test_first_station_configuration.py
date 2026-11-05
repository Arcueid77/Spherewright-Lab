"""Caller field/enum and accounting regressions; no Native game is simulated."""
from pathlib import Path
import sys,json,copy,tempfile,unittest
sys.path.insert(0,str(Path(__file__).parent/'live'))
from factory import Factory
from evidence import actual_prior_rpc_count

class FirstStationConfigurationTests(unittest.TestCase):
 def test_actual_physical_arrival_shape_passes_through_first_operation_without_recipe_change(self):
  before=json.loads((Path(__file__).parent/'fixtures/captured-station-support-arrived.json').read_text(encoding='utf-8'))
  before['stateHash']='full-entity-hash';before['logisticsStation']['configurationStateHash']='configuration-before'
  after=copy.deepcopy(before);after['logisticsStation']['configurationStateHash']='configuration-after'
  after['logisticsStation']['storageSlots'][1]['remoteLogic']='None'
  work=dict(entityId=101,recipeId=0,mode='logistics-station-storage',stationStorageIndex=1,
    stationItemId=1301,stationMaximumCount=100,stationLocalLogic='none',stationRemoteLogic='none',beforeStationRemoteLogic='demand')
  a=Factory.__new__(Factory);a.ctx=dict(sessionId='synthetic',planetId=901);saved=[];calls=[]
  a.runtime=type('Runtime',(),dict(config={'firstOperation':work},put=lambda _,n,v:saved.append((n,v))))()
  a.entity=lambda _:before
  def call(name,args):
   calls.append((name,args));return dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='synthetic-plan')
  a.call=call
  result=a.prepare_first_work(None,None)
  self.assertEqual('configure-building',result['action_kind'])
  args=calls[0][1];self.assertEqual('full-entity-hash',args['expectedFactoryStateHash'])
  self.assertEqual('configuration-before',args['expectedStationConfigurationStateHash'])
  self.assertEqual('none',args['stationRemoteLogic']);self.assertEqual(100,args['stationMaximumCount'])
  a.entity=lambda _:after
  self.assertTrue(a.verify_progress(result,dict(succeeded=True,actionId='synthetic-action')))
  self.assertEqual(100,after['logisticsStation']['storageSlots'][1]['count'])

 def test_nested_actual_rpc_counts_use_original_attachment_without_rewriting_handoff(self):
  with tempfile.TemporaryDirectory() as folder:
   prior=Path(folder);closed={'priorRpcCount':11,'requestCount':9}
   self.assertEqual(20,actual_prior_rpc_count(prior,closed))
   (prior/'attached-existing-session.private.json').write_text(json.dumps(dict(passed=True,noStartupClockReset=True,priorRpcCount=18)))
   self.assertEqual(27,actual_prior_rpc_count(prior,closed));self.assertEqual(11,closed['priorRpcCount'])
   with self.assertRaisesRegex(RuntimeError,'accounting_unproved'):
    actual_prior_rpc_count(prior,dict(priorRpcCount=19,requestCount=9))

if __name__=='__main__':unittest.main()
