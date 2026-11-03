"""Caller regressions: actual DTO shape, unaccepted refusals and original-action ownership."""
from pathlib import Path
import sys,unittest,tempfile,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent/'live'))
from contracts import powered_consumers_share_network
from driver import Live,ToolRefused,AcceptedActionFailure
from factory import Factory
from runtime import freeze

class LiveDriverTests(unittest.TestCase):
 def test_known_failed_move_keeps_healthy_idle_writer_but_unknown_cannot_do_so(self):
  a=Factory.__new__(Factory);a.active=None;a.ctx=dict(sessionId='same')
  a.call=lambda *_:dict(gameLoaded=True,ownedBySpherewright=True,writesAllowed=True,sessionId='same')
  a.player=lambda:dict(movementState='Walk',speed=0,nativePhysics=dict(groundContact=dict(checkSphereHit=True),velocity=dict(x=0,y=0,z=0)),handcraftQueue=[],constructionDrones=dict(working=0))
  result=dict(actionId='original',actionKind='move',state='action_failed',terminal=True)
  self.assertTrue(a.can_await_after_known_move(AcceptedActionFailure('known',result)))
  result['state']='outcome_unknown';self.assertFalse(a.can_await_after_known_move(AcceptedActionFailure('unknown',result)))
  result['state']='action_failed';a.player=lambda:dict(movementState='Drift',speed=1)
  self.assertFalse(a.can_await_after_known_move(AcceptedActionFailure('moving',result)))
 def test_actual_detached_runpy_entry_resolves_shared_modules_outside_its_directory(self):
  script=Path(__file__).resolve().parent/'live/run.py'
  with tempfile.TemporaryDirectory() as folder:
   probe=subprocess.run([sys.executable,'-c','import runpy,sys;runpy.run_path(sys.argv[1],run_name="import_only_probe")',str(script)],
     cwd=folder,capture_output=True,text=True,timeout=10)
   self.assertEqual(0,probe.returncode,probe.stderr)
 def test_real_pole_shape_null_is_not_a_disconnected_consumer(self):
  # Exact public DTO branch captured from a real paid pole; identifiers and
  # position omitted. Membership itself still needs the public power graph.
  pole=dict(componentKind='power-node',powerNetworkId=None,recipeId=0)
  miner=dict(componentKind='miner',powerNetworkId=2)
  self.assertTrue(powered_consumers_share_network([pole,miner],2))
  self.assertFalse(powered_consumers_share_network([pole],2))
  self.assertFalse(powered_consumers_share_network([pole,dict(componentKind='miner',powerNetworkId=None)],2))
 def test_private_config_cannot_mutate_a_running_stage(self):
  x=freeze(dict(stages=[dict(item=1)]))
  with self.assertRaises(TypeError):x['stages'][0]['item']=2
 def test_unaccepted_prepare_and_local_postcheck_do_not_trigger_preservation(self):
  a=Live(None)
  self.assertFalse(a.failure_requires_preservation(ToolRefused('spherewright_prepare_build',dict(code='BUILD_LOCATION_INVALID'))))
  self.assertFalse(a.failure_requires_preservation(ValueError('local DTO mismatch')))
 def test_unknown_result_retains_original_action_and_never_submits_cleanup(self):
  a=Live(None);a.active='original';a.c=type('Client',(),dict(deadline=float('inf')))()
  a.runtime=type('Evidence',(),dict(put=lambda *_:None))()
  a.call=lambda *args:dict(terminal=True,state='outcome_unknown',succeeded=False)
  a.wait_original('original');self.assertEqual('original',a.active)

if __name__=='__main__':unittest.main()
