"""Caller regressions: actual DTO shape, unaccepted refusals and original-action ownership."""
from pathlib import Path
import sys,unittest,tempfile,json
sys.path.insert(0,str(Path(__file__).resolve().parent/'live'))
from contracts import powered_consumers_share_network
from driver import Live,ToolRefused
from runtime import freeze

class LiveDriverTests(unittest.TestCase):
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
