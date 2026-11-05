"""Retire only an idle caller blocked before an unaccepted buffer-dependent suffix.

The old immutable plan remains history. Freeze only its proved Python owner,
then prove quiescent read I/O, every accepted terminal and a fresh blocked Native
buffer before ending that caller. Never stop the game or replay the suffix.
"""
from pathlib import Path
import json,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from runtime import Runtime
from driver import Live
from evidence import read,sha,need,actual_prior_rpc_count
from contracts import is_read_tool,strict_native_player_idle,observed_item_count
from mcp_client import Client
from pause_handcraft_poll import owned_caller,ProcessPause


def blocked_suffix(steps,wait_role,prefix_role):
 matches=[i for i,s in enumerate(steps) if s['role']==wait_role]
 need(len(matches)==1,'unique_buffer_wait_required');index=matches[0];wait=steps[index]
 need(wait['kind']=='wait-buffer' and type(wait['entity'])is int and wait['entity']>0
  and type(wait['itemId'])is int and wait['itemId']>0 and type(wait['minimumCount'])is int
  and wait['minimumCount']>0,'explicit_positive_native_buffer_wait_required')
 writes=[s for s in steps[:index] if s['kind'] not in ('read','dump','wait-buffer','wait-player-still','prepare-only','prove-network')]
 need(writes and writes[-1]['role']==prefix_role and writes[-1]['kind']=='operation','exact_last_settled_prefix_required')
 return wait,[s['role'] for s in steps[index+1:]]


def main():
 config,digest,prior,sequence,wait_role,prefix_role,output=sys.argv[1:];prior=Path(prior).resolve();sequence=int(sequence)
 r=Runtime(config,digest,output);r.cohort();a=Live(r);pause=None;retired=False
 envelope=read(prior/f'next-plan-{sequence:03d}.private.json');need(sha(envelope['path'])==envelope['sha256'],'original_plan_changed')
 wait,suffix=blocked_suffix(read(envelope['path'])['steps'],wait_role,prefix_role)
 need(not(prior/f'continuation-{sequence:03d}-complete.private.json').exists(),'original_plan_already_complete')
 accepted=prior/(prefix_role+'-accepted.private.json');end=time.monotonic()+7200
 while True:
  need(time.monotonic()<end and not(prior/'client-close.private.json').exists(),'finite_prefix_wait_ended')
  if accepted.exists():
   original=read(accepted)['actionId'];terminal=prior/('terminal-'+original+'.private.json')
   if terminal.exists():
    try:read(terminal);break
    except json.JSONDecodeError:pass
  if(r.output/'cancel-request.private.flag').exists():return
  time.sleep(.5)
 need(read(terminal)['terminal'] and read(terminal)['succeeded'],'prefix_not_successfully_settled')
 # Enter the existing read-only wait's completed-I/O gap, not a forge callback.
 ready=time.monotonic()+120
 while True:
  need(time.monotonic()<ready,'completed_buffer_read_gap_not_observed')
  requests=sorted(prior.glob('request-*.private.json'));last=requests[-1]
  response=prior/last.name.replace('request-','response-')
  try:
   request=read(last)
   if (last.stat().st_mtime_ns>=terminal.stat().st_mtime_ns and request['tool']=='spherewright_inspect_factory_entity'
       and request['arguments'].get('objectId')==wait['entity'] and response.exists()
       and read(response)['response']['success'] is True):break
  except json.JSONDecodeError:pass
  time.sleep(.1)
 owner=owned_caller(prior);pause=ProcessPause(owner['Id'],owner['createdFileTime'])
 try:
  pause.suspend()
  # A paused sole writer cannot dispatch a future world step during admission.
  requests=sorted(prior.glob('request-*.private.json'));need(bool(requests),'original_request_ledger_missing')
  last=requests[-1];need((prior/last.name.replace('request-','response-')).exists(),'caller_io_not_quiescent')
  response=read(prior/last.name.replace('request-','response-'));need(response['response']['success'] is True,'last_read_not_complete')
  for request in requests:
   if request.stat().st_mtime_ns>=terminal.stat().st_mtime_ns:
    need(is_read_tool(read(request)['tool']),'post_prefix_world_dispatch_prevents_handoff')
  for role in suffix:need(not(prior/(role+'-accepted.private.json')).exists(),'suffix_already_accepted')
  for path in prior.glob('*-accepted.private.json'):
   receipt=read(path);action=receipt.get('actionId')
   if action:
    result=read(prior/('terminal-'+action+'.private.json'))
    need(result['terminal'] and result['state']!='outcome_unknown','unsettled_original_prevents_handoff')
  a.c=Client(Path(r.config['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'observer',maximum=20,seconds=60)
  a.c.initialize();state=a.call('spherewright_get_session_state',{});origin=read(Path(r.config['liveSessionOrigin'])/'loaded-session.private.json')
  need(state['sessionId']==origin['sessionId'] and state['gameLoaded'] and state['ownedBySpherewright'] and state['writesAllowed']
   and state['localPlanetId']==r.config['attachmentPlanetId'],'same_healthy_world_unproved')
  a.ctx=dict(sessionId=state['sessionId'],planetId=state['localPlanetId']);player=a.player()
  need(strict_native_player_idle(player) and not player['handcraftQueue'] and player['constructionDrones']['working']==0,'fresh_native_idle_unproved')
  native=a.call('spherewright_get_action_result',dict(actionId=original))
  need(native['actionId']==original and native['terminal'] and native['succeeded'],'native_prefix_terminal_changed')
  entity=a.entity(wait['entity']);amount=observed_item_count(entity,wait['itemId'])
  need(amount<wait['minimumCount'],'buffer_is_ready_do_not_retire')
  c=r.config;need(c['spentGameTicks']+state['gameTick']-c['sourceTick']+c['returnReserveGameTicks']+c['cleanupReserveGameTicks']<c['maximumCumulativeGameTicks'],'finite_budget_insufficient')
  evidence=dict(session=state,player=player,buffer=entity,observedCount=amount,requiredCount=wait['minimumCount'],
   originalPrefix=native,abandonedUnacceptedSuffixRoles=suffix,originalPlanEnvelope=envelope,caller=owner,
   gameProcessUntouched=True,allAcceptedActionsSettled=True,soleWriterPausedDuringAdmission=True)
  r.put('fresh-blocked-native-idle-before-handoff.private.json',evidence)
  subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',f"Stop-Process -Id {owner['Id']} -ErrorAction Stop"],check=True,creationflags=0x08000000)
  retired=True;pause.suspended=False;pause.close();pause=None
  for _ in range(60):
   result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',f"if(Get-Process -Id {owner['mcpId']} -ErrorAction SilentlyContinue){{exit 1}}"],capture_output=True,creationflags=0x08000000)
   if result.returncode==0:break
   time.sleep(.5)
  else:raise RuntimeError('old_mcp_eof_exit_unproved_no_replacement')
  r.put('observer-client-close.private.json',a.c.close());a.c=None
  events=[json.loads(line) for line in(prior/'client/client-events.private.jsonl').read_text().splitlines()]
  request_count=max(e['requestCount'] for e in events if e['kind']=='request_dispatch')
  total=actual_prior_rpc_count(prior,dict(priorRpcCount=c.get('priorRpcCount',0),requestCount=request_count))
  covered={Path(p).resolve() for p in c.get('alreadyCountedRpcEventPaths',[])}
  covered.add((prior/'client/client-events.private.jsonl').resolve());supplemental=[];seen=set()
  for root in c.get('supplementalRpcRoots',[]):
   for path in Path(root).rglob('client-events.private.jsonl'):
    path=path.resolve()
    if path in covered or path in seen:continue
    seen.add(path);rows=[json.loads(line) for line in path.read_text().splitlines()]
    ids=[row['requestCount'] for row in rows if row['kind']=='request_dispatch']
    need(sorted(ids)==list(range(1,len(ids)+1)),'supplemental_rpc_dispatch_ledger_incomplete')
    supplemental.append(dict(path=str(path),sha256=sha(path),requestCount=len(ids)))
  total+=sum(row['requestCount'] for row in supplemental)
  r.put('supplemental-rpc-accounting.private.json',dict(originalCounterRetained=True,additionalSources=supplemental,
   additionalRequestCount=sum(row['requestCount'] for row in supplemental),alreadyCountedSources=list(map(str,covered))))
  accounts=list(prior.glob('*-native-success-material-account.private.json'))
  material=read(max(accounts,key=lambda p:p.stat().st_mtime_ns)) if accounts else {}
  from evidence import put
  handoff=dict(callerStopped=True,noActiveGameAction=True,gameProcessRetained=True,requestCount=request_count,
   priorRpcCount=total-request_count,externalIdleCallerRetirement=True,blockedBufferCheckpoint=True,
   abandonedPlanSequence=sequence,abandonedUnacceptedSuffixRoles=suffix,sourceSha=c['sourceSha'],
   noSave=True,noLoad=True,noLaunch=True,noReplay=True,materialUsed=material.get('materialUsed'),
   materialReservations=material.get('materialReservations'),nativeIdleEvidence=str(r.output/'fresh-blocked-native-idle-before-handoff.private.json'))
  handoff['supplementalRpcAccounting']=str(r.output/'supplemental-rpc-accounting.private.json')
  handoff['coveredRpcEventPaths']=list(map(str,covered))+[row['path'] for row in supplemental]
  put(prior/'caller-handoff.private.json',handoff);r.put('blocked-buffer-handoff-complete.private.json',handoff)
 finally:
  if pause is not None:
   pause.close();r.put('same-caller-resumed-no-retirement.private.json',dict(passed=True,callerRetired=False))
  if a.c is not None:r.put('observer-client-close.private.json',a.c.close())
  if retired:r.put('game-not-terminated.private.json',dict(passed=True,gameTermination=False))


if __name__=='__main__':main()
