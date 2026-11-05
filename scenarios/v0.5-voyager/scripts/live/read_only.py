"""Bounded public observations; this entry cannot prepare or commit a game action."""
from pathlib import Path
import sys,time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from runtime import Runtime
from driver import Live
from mcp_client import Client
from evidence import read,sha,need
from contracts import is_read_tool,validate_native_calls

def main():
 config,config_sha,plan_path,plan_sha,output=sys.argv[1:];need(sha(plan_path)==plan_sha.upper(),'immutable_read_plan_changed')
 plan=read(plan_path);queries=plan['queries'];need(0<len(queries)<=16 and all(is_read_tool(q['tool']) for q in queries),'read_only_entry_rejects_prepare_or_commit')
 samples=plan.get('sampleCount',1);interval=plan.get('sampleIntervalSeconds',0)
 need(type(samples)is int and 1<=samples<=64 and type(interval)in(int,float) and 0<=interval<=5,'finite_read_sample_envelope_required')
 walk=plan.get('upstreamBeltWalk');walk_limit=0 if walk is None else walk.get('maximumObjects',0)
 need(walk is None or type(walk_limit)is int and 1<=walk_limit<=64 and type(walk.get('startObjectId'))is int and walk['startObjectId']>0,'finite_native_belt_walk_required')
 pages=plan.get('factoryPaginationMaximumPages',0)
 need(type(pages)is int and 0<=pages<=128,'finite_factory_pagination_required')
 r=Runtime(config,config_sha,output);r.cohort();a=Live(r)
 a.c=Client(Path(r.config['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'client',maximum=samples*len(queries)+walk_limit+pages+8,seconds=max(60,samples*(interval+2*len(queries))+2*(walk_limit+pages)+30))
 try:
  _,ts,_,_=a.c.initialize();a.schemas={t['name']:t['inputSchema'] for t in ts}
  calls=[dict(q,kind='read') for q in queries]
  if pages:calls.append(dict(kind='read',tool='spherewright_list_factory_entities',arguments=dict(limit=100,cursor='')))
  if walk is not None:calls.append(dict(kind='read',tool='spherewright_inspect_factory_entity',arguments=dict(objectId=walk['startObjectId'])))
  validate_native_calls(calls,a.schemas)
  s=a.call('spherewright_get_session_state',{});origin=Path(r.config['liveSessionOrigin']);original=read(origin/'loaded-session.private.json')
  need(s['gameLoaded'] and s['ownedBySpherewright'] and s['sessionId']==original['sessionId']
   and s['localPlanetId']==r.config.get('attachmentPlanetId',r.config['planetId']),'read_only_owned_session_changed')
  ctx=dict(sessionId=s['sessionId'],planetId=s['localPlanetId'] if s['localPlanetId'] is not None else 0)
  for sample in range(samples):
   for q in queries:
    props=a.schemas[q['tool']]['properties'];args={k:v for k,v in ctx.items() if k in props};args.update(q.get('arguments',{}))
    suffix='' if samples==1 else f'-sample-{sample:03d}'
    r.put(q['name']+suffix+'-read.private.json',a.call(q['tool'],args))
   if sample+1<samples:time.sleep(interval)
  if walk is not None:
   current=walk['startObjectId'];seen=set()
   for index in range(walk_limit):
    if current in seen:break
    seen.add(current);e=a.call('spherewright_inspect_factory_entity',dict(ctx,objectId=current));r.put(f'actual-native-upstream-belt-{index:03d}.private.json',e)
    if e['componentKind']!='belt':break
    predecessors=[c['otherObjectId'] for c in e['connections'] if not c['isOutput'] and c['otherObjectId']>0]
    if len(predecessors)!=1:break
    current=predecessors[0]
  if pages:
   cursor='';seen=set();complete=False
   for index in range(pages):
    value=a.call('spherewright_list_factory_entities',dict(ctx,limit=100,cursor=cursor));r.put(f'actual-native-factory-page-{index:03d}.private.json',value)
    cursor=value.get('nextCursor') or ''
    if not cursor:complete=True;break
    need(cursor not in seen,'native_factory_cursor_repeated');seen.add(cursor)
   need(complete,'finite_native_factory_page_bound_reached')
  r.put('read-only-complete.private.json',dict(passed=True,gameCommits=0,prepares=0,saves=0,loads=0,noGameWriterCreated=True))
 except Exception as error:
  r.put('read-only-failure.private.json',dict(error=str(error),gameCommits=0,prepares=0,noGameWriterCreated=True));raise
 finally:
  try:closed=a.c.close()
  except Exception:
   r.put('client-close.private.json',read(r.output/'client/client-evidence.private.json'));raise
  else:r.put('client-close.private.json',closed)

if __name__=='__main__':main()
