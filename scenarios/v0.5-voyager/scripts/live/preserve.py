"""Explicit failed-action preservation; never called for a caller/prepare error."""
from pathlib import Path
import sys,time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from runtime import Runtime
from driver import Live
from mcp_client import Client
from evidence import read,need
from contracts import paused_failed_cut

def main():
 config,config_sha,original_output,action_id,output=sys.argv[1:]
 origin=Path(original_output);prior=read(origin/'client-close.private.json')
 need(prior['normalEof'] and prior['processExitCode']==0,'original_caller_not_closed')
 terminal=read(origin/f'terminal-{action_id}.private.json')
 need(terminal['terminal'] and terminal['state'] in ('action_failed','outcome_unknown') and not terminal['succeeded'],'not_a_failed_accepted_action')
 runtime=Runtime(config,config_sha,output);runtime.cohort();a=Live(runtime);a.pid=read(origin/'process-observed.private.json')['Id']
 a.c=Client(Path(runtime.config['pluginDestination'])/'Spherewright.Mcp.exe',runtime.output/'client',maximum=30,seconds=120)
 a.c.initialize();sessions=[];players=[]
 try:
  for i in range(2):
   s=a.call('spherewright_get_session_state',{});need(s['localPlanetId']==runtime.config['planetId'],'planet_changed')
   a.ctx=dict(sessionId=s['sessionId'],planetId=s['localPlanetId']);p=a.player()
   runtime.put(f'session-{i}.private.json',s);runtime.put(f'player-{i}.private.json',p);sessions.append(s);players.append(p);time.sleep(.5)
 finally:
  runtime.put('client-close.private.json',a.c.close());a.c=None
 need(paused_failed_cut(*sessions,*players,action_id),'failed_paused_cut_unproved')
 runtime.put('paused-cut-verified.private.json',dict(passed=True,originalActionId=action_id,gameTick=sessions[1]['gameTick'],physicalIdleNotAssumed=True,noReplay=True))
 a.normal_close_current_process()

if __name__=='__main__':main()
