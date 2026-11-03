"""Bounded public observations; this entry cannot prepare or commit a game action."""
from pathlib import Path
import sys
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
 r=Runtime(config,config_sha,output);r.cohort();a=Live(r)
 a.c=Client(Path(r.config['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'client',maximum=24,seconds=60)
 try:
  _,ts,_,_=a.c.initialize();a.schemas={t['name']:t['inputSchema'] for t in ts}
  validate_native_calls([dict(q,kind='read') for q in queries],a.schemas)
  s=a.call('spherewright_get_session_state',{});origin=Path(r.config['liveSessionOrigin']);original=read(origin/'loaded-session.private.json')
  need(s['gameLoaded'] and s['ownedBySpherewright'] and s['sessionId']==original['sessionId']
   and s['localPlanetId']==r.config.get('attachmentPlanetId',r.config['planetId']),'read_only_owned_session_changed')
  ctx=dict(sessionId=s['sessionId'],planetId=s['localPlanetId'])
  for q in queries:
   props=a.schemas[q['tool']]['properties'];args={k:v for k,v in ctx.items() if k in props};args.update(q.get('arguments',{}))
   r.put(q['name']+'-read.private.json',a.call(q['tool'],args))
  r.put('read-only-complete.private.json',dict(passed=True,gameCommits=0,prepares=0,saves=0,loads=0,noGameWriterCreated=True))
 finally:r.put('client-close.private.json',a.c.close())

if __name__=='__main__':main()
