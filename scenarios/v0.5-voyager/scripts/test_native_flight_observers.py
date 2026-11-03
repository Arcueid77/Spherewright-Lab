import copy,sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'live'))
from flight_observers import SailConversionTrace,RocketArrivalTrace


def sail(ammo,flying,alive):
 return dict(nativeBindingVerified=True,swarmAvailable=True,orbitCoverageComplete=True,starEjectorCoverageComplete=True,
  starEjectorCount=1,starId=1,sailCount=ammo,inFlightSailCount=flying,activeSailCount=alive,
  orbitId=1,runtimeOrbitId=1,automaticOrbitSelection=False,firedAnimationActive=False,orbits=[dict(orbitId=1,enabled=True,sailCount=alive)])


def rocket(ammo=0,progress=None,points=0):
 return dict(nativeBindingVerified=True,sphereAvailable=True,rocketCoverageComplete=True,nodeCoverageComplete=True,
  starSiloCoverageComplete=True,starSiloCount=1,starId=1,rocketCount=ammo,inFlightRocketCount=int(progress is not None),
  rockets=[] if progress is None else [dict(rocketId=1,sourcePlanetId=1,targetLayerId=1,targetNodeId=1,nativeFlightProgress=progress)],
  nodes=[dict(layerId=1,nodeId=1,structurePoints=points,maximumStructurePoints=30,orderedStructurePoints=int(progress is not None))])


class NativeFlightTraceTests(unittest.TestCase):
 def test_sails_require_exact_ammo_loss_native_ballistics_and_orbit_conversion(self):
  t=SailConversionTrace(sail(4,0,0),4,1)
  self.assertFalse(t.observe(sail(3,1,0)));self.assertFalse(t.observe(sail(0,3,1)))
  self.assertTrue(t.observe(sail(0,0,4)))
 def test_native_arrived_sail_can_overlap_its_unrecycled_visual_trail_without_creating_an_extra_item(self):
  t=SailConversionTrace(sail(4,0,0),4,1)
  self.assertFalse(t.observe(sail(1,3,0)));self.assertFalse(t.observe(sail(1,3,1)))
  self.assertFalse(t.observe(sail(0,1,4)));self.assertTrue(t.observe(sail(0,0,4)))
 def test_actual_captured_launch_conversion_and_visual_recycle_sequence_closes_without_replaying_native_actions(self):
  f=json.loads((Path(__file__).parent/'fixtures/captured-native-sail-conversion-lifecycle.json').read_text())
  self.assertTrue(any(s['sailCount']+s['inFlightSailCount']+s['activeSailCount']>4 for s in f['samples']))
  t=SailConversionTrace(f['initial'],4,1);done=False
  for s in f['samples']:done=t.observe(s)
  self.assertTrue(done)
 def test_configuration_animation_or_final_count_without_observed_flight_is_not_a_launch(self):
  t=SailConversionTrace(sail(4,0,0),4,1);final=sail(0,0,4);final['firedAnimationActive']=True
  self.assertFalse(t.observe(final))
 def test_sail_pool_loss_foreign_ejector_and_wrong_orbit_fail_closed(self):
  for bad in [sail(3,0,0),dict(sail(3,1,0),starEjectorCount=2),dict(sail(3,1,0),orbitId=2),dict(sail(3,1,0),orbitCoverageComplete=False)]:
   with self.assertRaises(RuntimeError):SailConversionTrace(sail(4,0,0),4,1).observe(bad)
 def test_rocket_requires_one_actual_bound_flight_and_one_native_arrival_point(self):
  t=RocketArrivalTrace(rocket(),1,1,1);self.assertFalse(t.observe(rocket(ammo=1)))
  self.assertFalse(t.observe(rocket(progress=.1)));self.assertFalse(t.observe(rocket(progress=.8)))
  self.assertTrue(t.observe(rocket(points=1)))
 def test_unobserved_flight_or_already_delivered_node_cannot_count_as_new_arrival(self):
  t=RocketArrivalTrace(rocket(),1,1,1);self.assertFalse(t.observe(rocket(points=1)))
  with self.assertRaises(RuntimeError):RocketArrivalTrace(rocket(points=1),1,1,1)
 def test_wrong_source_second_rocket_and_regressed_native_progress_do_not_pass(self):
  t=RocketArrivalTrace(rocket(),1,1,1);t.observe(rocket(progress=.7))
  for bad in [rocket(progress=.6),dict(rocket(progress=.8),starSiloCount=2)]:
   with self.assertRaises(RuntimeError):t.observe(bad)
  bad=rocket(progress=.8);bad['rockets'][0]['sourcePlanetId']=2
  with self.assertRaises(RuntimeError):t.observe(bad)


if __name__=='__main__':unittest.main()
