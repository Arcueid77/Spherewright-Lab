"""Replay real station DTOs through the production arrival observer."""
from pathlib import Path
import json,sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent/'live'))
from contracts import observed_item_count
from factory import Factory
from evidence import sha
from retire_idle_caller import validate_read_wait

class StationArrivalTests(unittest.TestCase):
 def captured(self):
  return json.loads((Path(__file__).parent/'fixtures/captured-station-inflight-stock.json').read_text(encoding='utf-8'))

 def test_stock_count_excludes_research_points_and_power_units(self):
  entity=dict(componentKind='lab',buffers=[
   dict(itemId=6005,count=2,countUnit='items',unitsPerItem=1),
   dict(itemId=6005,count=7200,countUnit='research_matrix_points',unitsPerItem=3600),
   dict(itemId=6005,count=4980,countUnit='joules_per_tick',unitsPerItem=0),
   dict(itemId=6005,count=3600,countUnit='items',unitsPerItem=3600)])
  self.assertEqual(2,observed_item_count(entity,6005))

 def test_legacy_item_buffers_retain_native_contract_defaults(self):
  entity=dict(componentKind='storage',buffers=[
   dict(itemId=6005,count=2),
   dict(itemId=6005,count=3,countUnit='items'),
   dict(itemId=6005,count=4,unitsPerItem=1),
   dict(itemId=6004,count=100)])
  self.assertEqual(9,observed_item_count(entity,6005))

 def test_production_wait_requires_physical_cubes_after_research_points(self):
  points=dict(componentKind='lab',buffers=[
   dict(itemId=6005,count=7200,countUnit='research_matrix_points',unitsPerItem=3600)])
  cubes=dict(componentKind='lab',buffers=[
   dict(itemId=6005,count=2,countUnit='items',unitsPerItem=1)])
  values=iter([points,cubes]);saved=[]
  adapter=Factory.__new__(Factory);adapter.ctx=dict(planetId=7);adapter.refs={}
  adapter.state=lambda:None;adapter.entity=lambda _:next(values)
  adapter.runtime=type('Evidence',(),dict(put=lambda _,name,value:saved.append((name,value))))()
  with patch('factory.time.sleep'):
   result=adapter.step(dict(kind='wait-buffer',role='green',entity=12,itemId=6005,
    minimumCount=2,maximumSeconds=10,pollSeconds=1))
  self.assertIs(cubes,result)
  self.assertEqual([('green-proof.private.json',cubes)],saved)

 def test_real_order_is_not_arrival_and_machine_buffers_are_not_station_stock(self):
  e=self.captured()
  self.assertEqual([],e['buffers'])
  self.assertEqual(100,e['logisticsStation']['storageSlots'][1]['remoteOrder'])
  self.assertEqual(0,observed_item_count(e,1301))
  self.assertEqual(100,observed_item_count(e,1013))
  delivered=json.loads((Path(__file__).parent/'fixtures/captured-station-support-arrived.json').read_text(encoding='utf-8'))
  self.assertEqual(0,observed_item_count(e,1802))
  self.assertEqual(100,observed_item_count(delivered,1301))
  self.assertEqual(100,observed_item_count(delivered,1802))

 def test_production_wait_replays_inflight_to_physical_arrival(self):
  before=self.captured();after=json.loads((Path(__file__).parent/'fixtures/captured-station-board-arrived.json').read_text(encoding='utf-8'))
  values=iter([before,after]);saved=[];health=[]
  a=Factory.__new__(Factory);a.ctx={'planetId':7};a.refs={};a.state=lambda:health.append(True)
  a.entity=lambda _:next(values)
  a.runtime=type('Evidence',(),{'put':lambda _,name,value:saved.append((name,value))})()
  with patch('factory.time.sleep'):
   result=a.step(dict(kind='wait-buffer',role='arrive',entity=101,itemId=1301,minimumCount=100,maximumSeconds=10,pollSeconds=1))
  self.assertIs(after,result);self.assertEqual(3,len(health));self.assertEqual([('arrive-proof.private.json',after)],saved)

 def test_missing_or_wrong_station_binding_rejects_instead_of_inventing_stock(self):
  e=self.captured();e['logisticsStation']['entityId']=102
  with self.assertRaisesRegex(ValueError,'binding_unproved'):observed_item_count(e,1301)
  e=self.captured();e['logisticsStation']['storageSlots']=None
  with self.assertRaisesRegex(ValueError,'unobserved'):observed_item_count(e,1301)

 def test_read_wait_retirement_refuses_future_world_writes(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);plan=root/'plan.json'
   plan.write_text(json.dumps({'steps':[{'kind':'wait-buffer'}]}))
   envelope={'path':str(plan),'sha256':sha(plan)}
   (root/'next-plan-001.private.json').write_text(json.dumps(envelope))
   (root/'initial-complete.private.json').write_text('{}')
   validate_read_wait(root,1)
   (root/'next-plan-002.private.json').write_text('{}')
   with self.assertRaisesRegex(RuntimeError,'future_plan'):validate_read_wait(root,1)
   (root/'next-plan-002.private.json').unlink()
   plan.write_text(json.dumps({'steps':[{'kind':'operation'}]}))
   envelope['sha256']=sha(plan);(root/'next-plan-001.private.json').write_text(json.dumps(envelope))
   with self.assertRaisesRegex(RuntimeError,'only_read_wait'):validate_read_wait(root,1)
   plan.write_text(json.dumps({'steps':[{'kind':'wait-buffer'},{'kind':'dump','queries':[{'tool':'spherewright_commit_save'}]}]}))
   envelope['sha256']=sha(plan);(root/'next-plan-001.private.json').write_text(json.dumps(envelope))
   with self.assertRaisesRegex(RuntimeError,'write_tool'):validate_read_wait(root,1)

if __name__=='__main__':unittest.main()
