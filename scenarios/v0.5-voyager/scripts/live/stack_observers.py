"""Finite Native piler input, observed aggregation and exact stock recovery."""
import time
from evidence import need


def observe_piler_aggregation(adapter, step):
    role=step['role'];item=step['itemId'];limit=step['maximumItems']
    piler=adapter.object_id(step['piler']);source=adapter.object_id(step['input']);output=adapter.object_id(step['output'])
    end=time.monotonic()+step['maximumSeconds'];fed=0;pickups=0;aggregate=None;originals=[]

    def stock(player):
        rows=[row for row in player['inventory'] if row['itemId']==item]
        need(all(row['inc']==0 for row in rows),'piler_source_requires_zero_inc_stock')
        return sum(row['count']for row in rows)

    def path(cut,entity):
        paths=[row for row in cut.get('cargoPaths',[])if entity in row.get('beltObjectIds',[])]
        need(cut.get('state')=='observed' and len(paths)==1,'piler_complete_path_unavailable')
        result=paths[0];rows=result.get('items') or []
        need(not result['pathClosed'] and result['outputPathId']==0 and not any(result['inputPathIds'])
             and 0<result['pathLengthCells']<=4096 and 0<len(result['beltObjectIds'])<=64
             and all(row['itemId']==item and row['inc']==0 for row in rows),'piler_path_stock_or_scope_changed')
        need(sum(row['count']for row in rows)==result['itemCount'],'piler_path_count_ambiguous')
        return result

    def observe():
        adapter.state()
        # Both paths and the piler cache come from one Native main-thread cut.
        # Independent observations could double-count a moving packet.
        entity=adapter.call('spherewright_inspect_factory_entity',dict(adapter.ctx,objectId=piler,
            materialInventoryObjectIds=[source,output]))
        cut=entity.get('materialInventoryCut') or {};incoming=path(cut,source);outgoing=path(cut,output)
        need(incoming['pathId']!=outgoing['pathId'],'piler_input_output_path_alias')
        stack=entity.get('stack') or {};layers=[row for row in stack.get('layers',[])if row['objectId']==piler]
        need(stack.get('complete') is True and len(layers)==1,'piler_complete_layer_unavailable')
        state=layers[0].get('deviceState') or {};cargo=state.get('cachedCargo')
        need(state.get('pilerMode')==1 and isinstance(cargo,list)
             and all(row['count']==0 or row['itemId']==item and row['inc']==0 for row in cargo),'piler_mode_or_cached_stock_changed')
        held=sum(row['count']for row in cargo);player=adapter.player()
        need(stock(player)+incoming['itemCount']+outgoing['itemCount']+held==baseline,'piler_total_stock_conservation_failed')
        return dict(input=incoming,output=outgoing,piler=entity,cache=cargo,held=held,player=player)

    def transfer(suffix,entity,direction,count):
        receipt=adapter.native_operation(dict(kind='operation',role=role+'-'+suffix,
            prepareTool='spherewright_prepare_transfer',freshStaleMaximumSeconds=15,
            reads=[dict(name='e',tool='spherewright_inspect_factory_entity',arguments=dict(objectId=entity)),
                   dict(name='p',tool='spherewright_get_player_state')],
            arguments=dict(direction=direction,storageEntityId=entity,itemId=item if count else 0,count=count,
                expectedPlayerStateHash=dict(ref='p.stateHash'),expectedStorageStateHash=dict(ref='e.stateHash'))))
        originals.append(receipt['actionId'])

    baseline=stock(adapter.player());need(baseline>=limit,'piler_finite_source_stock_insufficient')
    first=observe();need(first['input']['itemCount']==first['output']['itemCount']==first['held']==0,'piler_case_requires_empty_paths_and_cache')
    while time.monotonic()<end:
        value=observe();outgoing=value['output']
        if outgoing['itemCount']>outgoing['cargoStackCount']:
            aggregate=value;break
        cached=[row['count']for row in value['cache']]
        if len(cached)>=2 and cached[0]>0 and cached[1]>0 and outgoing['itemCount']>0:
            # Free the real blocked output through the normal complete pickup.
            # The next Native ticks combine the two cached singleton packets.
            pickups+=1;transfer(f'free-{pickups:02d}',output,'belt-cargo-to-player',0)
        elif value['input']['itemCount']==0 and fed<limit:
            fed+=1;transfer(f'put-{fed:02d}',source,'player-to-belt-cargo',1)
        else:time.sleep(.5)
    need(aggregate is not None,'finite_piler_aggregation_not_observed')
    adapter.runtime.put(role+'-aggregation-proof.private.json',dict(passed=True,itemId=item,
        singletonPlacements=fed,observed=aggregate,originalActionIds=list(originals),noNewConstruction=True))
    while time.monotonic()<end:
        value=observe()
        if value['input']['itemCount']==value['output']['itemCount']==value['held']==0:
            need(stock(value['player'])==baseline,'piler_complete_package_not_restored')
            adapter.runtime.put(role+'-conservation-proof.private.json',dict(passed=True,itemId=item,
                beforePackageCount=baseline,afterPackageCount=baseline,inc=0,singletonPlacements=fed,
                originalActionIds=originals,allPathsAndPilerCacheEmpty=True));return
        if value['output']['itemCount']>0:
            pickups+=1;transfer(f'return-{pickups:02d}',output,'belt-cargo-to-player',0)
        else:time.sleep(.5)
    raise RuntimeError('finite_piler_stock_recovery_incomplete')
