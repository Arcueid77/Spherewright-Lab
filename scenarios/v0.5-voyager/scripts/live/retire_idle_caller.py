"""Retire an exhausted idle caller only; never terminate the game or an action."""
from pathlib import Path
import json,sys,subprocess,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime import Runtime
from evidence import read,sha,need,actual_prior_rpc_count
from mcp_client import Client
from contracts import strict_native_player_idle,is_read_tool

def validate_read_wait(prior,sequence):
 need(sequence>0,'read_wait_sequence_required')
 envelope=read(prior/f'next-plan-{sequence:03d}.private.json')
 need(sha(envelope['path'])==envelope['sha256'],'read_wait_plan_changed')
 steps=read(envelope['path'])['steps']
 need(steps and all(s['kind'] in ('read','dump','wait-buffer','wait-player-still') for s in steps)
      and any(s['kind']=='wait-buffer' for s in steps),'only_read_wait_plan_may_be_retired')
 need(all(is_read_tool(s['tool']) if s['kind']=='read' else
          all(is_read_tool(q['tool']) for q in s['queries']) if s['kind']=='dump' else True
          for s in steps),'write_tool_prevents_read_wait_retirement')
 need(not any(int(p.name.split('-')[2].split('.')[0])>sequence for p in prior.glob('next-plan-*.private.json')),
      'future_plan_prevents_read_wait_retirement')
 need((prior/'initial-complete.private.json').exists(),'initial_operations_not_complete')

def main():
 config,digest,prior,mcp_pid,output=sys.argv[1:6];prior=Path(prior).resolve();mcp_pid=int(mcp_pid)
 r=Runtime(config,digest,output);r.cohort();c=r.config
 need(not (prior/'caller-handoff.private.json').exists() and not (prior/'client-close.private.json').exists(),'prior_already_closed')
 preservation=len(sys.argv)>6 and sys.argv[6]=='--quarantined-for-preservation'
 if preservation:
  need(bool(c.get('expectedPreservationQuarantineActionId')),'exact_preservation_quarantine_required')
 elif len(sys.argv)>6:
  validate_read_wait(prior,int(sys.argv[6]))
 else:need(not (prior/'next-plan-017.private.json').exists(),'pending_plan_prevents_retirement')
 for p in prior.glob('*-accepted.private.json'):
  accepted=read(p);action=accepted.get('actionId')
  if action:
   terminal=read(prior/('terminal-'+action+'.private.json'))
   need(terminal['terminal'] and terminal['state']!='outcome_unknown','accepted_action_unsettled')
 observer=Client(Path(c['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'observer',maximum=12,seconds=60)
 try:
  observer.initialize();response,bad=observer.call('spherewright_get_session_state',{});s=response['result']
  original=read(Path(c['liveSessionOrigin'])/'loaded-session.private.json')
  need(not bad and s['gameLoaded'] and s['ownedBySpherewright'] and s['sessionId']==original['sessionId'],'original_world_unproved')
  if preservation:
   need(not s['writesAllowed'] and s.get('writeQuarantineActionId')==c['expectedPreservationQuarantineActionId'],
        'exact_native_quarantine_unproved')
  else:need(s['writesAllowed'],'healthy_original_world_unproved')
  response,bad=observer.call('spherewright_get_player_state',dict(sessionId=s['sessionId'],planetId=s['localPlanetId']));p=response['result']
  if preservation:
   need(not bad and 'native_paused_not_execution_ready' in (p.get('nativeLocalControlEnergy') or {}).get('blockers',[]),
        'native_pause_for_preservation_unproved')
   time.sleep(.5);second,bad=observer.call('spherewright_get_session_state',{})
   need(not bad and second['result']['sessionId']==s['sessionId'] and second['result']['gameTick']==s['gameTick']
        and second['result'].get('writeQuarantineActionId')==s['writeQuarantineActionId'],
        'same_paused_quarantined_cut_unproved')
  else:need(not bad and strict_native_player_idle(p) and not p['handcraftQueue'] and p['constructionDrones']['working']==0,'idle_unproved')
  need(c['spentGameTicks']+s['gameTick']-c['sourceTick']+c['returnReserveGameTicks']<c['maximumCumulativeGameTicks'],'new_finite_budget_insufficient')
  r.put('native-idle-before-retirement.private.json',dict(session=s,player=p,preservationOnly=preservation,
       physicalIdleNotAssumed=preservation,noResume=True))
 finally:observer.close()
 command=f"$m=Get-CimInstance Win32_Process -Filter 'ProcessId={mcp_pid}';if($m.Name -ne 'Spherewright.Mcp.exe'){{throw 'MCP identity'}};$p=Get-CimInstance Win32_Process -Filter ('ProcessId='+$m.ParentProcessId);$p|Select-Object Name,ProcessId,CommandLine|ConvertTo-Json -Compress"
 owner=json.loads(subprocess.check_output(['powershell.exe','-NoProfile','-Command',command],text=True))
 control=prior.parent/(prior.name+'-worker')/'intent.private.json';intent=read(control)
 need(owner['Name'].lower()=='python.exe' and str(control).lower() in owner['CommandLine'].lower()
      and sha(control) in owner['CommandLine'].upper() and Path(intent['script']).name in ('run.py','attach.py')
      and Path(intent['arguments'][-1]).resolve()==prior,'exact_owned_caller_identity_unproved')
 r.put('caller-only-retirement-intent.private.json',dict(caller=owner,mcpProcessId=mcp_pid,gameTermination=False))
 subprocess.run(['powershell.exe','-NoProfile','-Command',f"Stop-Process -Id {owner['ProcessId']} -ErrorAction Stop"],check=True)
 # Closing the sole pipe owner lets the MCP exit on EOF; do not kill its child.
 for _ in range(30):
  result=subprocess.run(['powershell.exe','-NoProfile','-Command',f"if(Get-Process -Id {mcp_pid} -ErrorAction SilentlyContinue){{exit 1}}"],capture_output=True)
  if result.returncode==0:break
  time.sleep(.5)
 else:raise RuntimeError('old_mcp_exit_unproved_no_replacement')
 logs=[json.loads(line) for line in (prior/'client/rpc.jsonl').read_text(encoding='utf-8').splitlines()]
 from evidence import put
 request_count=max(x['request']['id'] for x in logs)
 total=actual_prior_rpc_count(prior,dict(priorRpcCount=c.get('priorRpcCount',0),requestCount=request_count))
 put(prior/'caller-handoff.private.json',dict(callerStopped=True,noActiveGameAction=True,gameProcessRetained=True,requestCount=request_count,priorRpcCount=total-request_count,noSave=True,noLoad=True,noLaunch=True,externalIdleCallerRetirement=True,preservationOnlyQuarantined=preservation,nativeIdleEvidence=str(r.output/'native-idle-before-retirement.private.json')))
 r.put('caller-only-retirement-complete.private.json',dict(passed=True,gameTerminated=False,originalActionsNotReplayed=True,oldMcpExitedAfterPipeOwnerStopped=True))

if __name__=='__main__':main()
