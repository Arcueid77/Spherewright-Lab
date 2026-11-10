"""The shared piler entry keeps every original placement and recovers all stock."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent/'live'))
from stack_observers import observe_piler_aggregation
from contracts import validate_steps


class Adapter:
    def __init__(self):
        self.ctx={};self.package=100;self.output=0;self.cache=[0,0];self.packed=False;self.pending=False;self.calls=[];self.proofs={}
        self.runtime=type('Runtime',(),dict(put=lambda _,name,value:self.proofs.__setitem__(name,value)))()

    def object_id(self,value):return value
    def state(self):pass
    def player(self):return dict(inventory=[dict(itemId=1108,count=self.package,inc=0)])

    def entity(self,value):
        return dict(stack=dict(complete=True,layers=[dict(objectId=7,deviceState=dict(pilerMode=1,
            cachedCargo=[dict(itemId=1108,count=n,inc=0)for n in self.cache]))]))

    def call(self,tool,args):
        if self.pending:
            self.pending=False;self.output=sum(self.cache);self.cache=[0,0];self.packed=True
        paths=[]
        for entity in args['materialInventoryObjectIds']:
            count=self.output if entity==9 else 0
            paths.append(dict(pathId=entity,pathClosed=False,outputPathId=0,inputPathIds=[],pathLengthCells=30,beltObjectIds=[entity],
                itemCount=count,cargoStackCount=(1 if self.packed and count else count),
                items=[dict(itemId=1108,count=count,inc=0)]if count else []))
        value=self.entity(args['objectId']);value['materialInventoryCut']=dict(state='observed',cargoPaths=paths);return value

    def native_operation(self,step):
        args=step['arguments'];self.calls.append(args)
        if args['direction']=='player-to-belt-cargo':
            self.package-=1
            if self.output<2:self.output+=1
            elif not self.cache[0]:self.cache[0]=1
            else:self.cache[1]=1
        else:
            self.package+=self.output;self.output=0
            if all(self.cache):self.pending=True
        return dict(actionId='synthetic-'+str(len(self.calls)))


class StackObserverTests(unittest.TestCase):
    def test_explicit_moving_cargo_refusal_waits_then_prepares_a_new_pickup(self):
        from unittest.mock import patch
        from driver import NativePreacceptanceRefusal
        adapter=Adapter();adapter.active=None;original=adapter.native_operation;refused=[]
        def transfer(step):
            if 'return-'in step['role']and not refused:
                refused.append(step['role'])
                raise NativePreacceptanceRefusal('spherewright_commit_transfer',dict(code='STALE_STATE'))
            return original(step)
        adapter.native_operation=transfer
        step=dict(kind='observe-piler-aggregation',role='pile',piler=7,input=8,output=9,itemId=1108,maximumItems=8,maximumSeconds=5)
        with patch('stack_observers.time.sleep'):observe_piler_aggregation(adapter,step)
        self.assertEqual(len(refused),1)
        self.assertEqual(adapter.package,100)
        self.assertEqual(len(adapter.calls),6)

    def test_blocked_output_is_normally_collected_then_native_merge_is_observed_and_recovered(self):
        adapter=Adapter();step=dict(kind='observe-piler-aggregation',role='pile',piler=7,input=8,output=9,itemId=1108,maximumItems=8,maximumSeconds=5)
        validate_steps([step]);observe_piler_aggregation(adapter,step)
        self.assertEqual(adapter.package,100)
        self.assertTrue(adapter.proofs['pile-aggregation-proof.private.json']['passed'])
        self.assertEqual(adapter.proofs['pile-conservation-proof.private.json']['singletonPlacements'],4)
        self.assertEqual(sum(row['count']for row in adapter.calls),4)
        self.assertEqual(len(adapter.calls),6)

    def test_unbounded_item_or_time_allowances_are_rejected(self):
        step=dict(kind='observe-piler-aggregation',role='pile',piler=7,input=8,output=9,itemId=1108,maximumItems=8,maximumSeconds=5)
        for change in [dict(maximumItems=65),dict(maximumItems=True),dict(maximumSeconds=float('nan'))]:
            with self.assertRaises(ValueError):validate_steps([dict(step,**change)])


if __name__=='__main__':unittest.main()
