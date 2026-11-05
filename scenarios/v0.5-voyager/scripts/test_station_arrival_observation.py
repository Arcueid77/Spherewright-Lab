"""Replay real station DTOs through the production arrival observer."""
from pathlib import Path
import copy,json,sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent/'live'))
from contracts import observed_item_count
from factory import Factory
from evidence import sha
from retire_idle_caller import validate_read_wait

class StationArrivalTests(unittest.TestCase):
 def captured(self):
  return json.loads((Path(__file__).parent/'fixtures/captured-station-inflight-stock.json').read_text(encoding='utf-8'))

 def test_real_order_is_not_arrival_and_machine_buffers_are_not_station_stock(self):
  e=self.captured()
  self.assertEqual([],e['buffers'])
  self.assertEqual(100,e['logisticsStation']['storageSlots'][1]['remoteOrder'])
  self.assertEqual(0,observed_item_count(e,1301))
  self.assertEqual(100,observed_item_count(e,1013))

 def test_production_wait_replays_inflight_to_physical_arrival(self):
  before=self.captured();after=copy.deepcopy(before)
  # Explicit modeled delivery transition, based on the captured in-flight DTO.
  slot=after['logisticsStation']['storageSlots'][1];slot.update(count=100,remoteOrder=0)
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
