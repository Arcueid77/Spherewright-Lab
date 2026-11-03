"""Single-writer shared public MCP lifecycle. Work plans are immutable private input."""
from pathlib import Path
import datetime as dt,json,math,re,subprocess,time,uuid
import startup_to_action as G
from geometry_request import complete_geometry_arrays
from evidence import need,read,sha,json_value
from mcp_client import Client

class AcceptedActionFailure(RuntimeError):
 def __init__(self,message,receipt=None):self.receipt=receipt;super().__init__(message)

class ToolRefused(RuntimeError):
    def __init__(self, tool, error):
        self.tool=tool; self.error=error or {}; super().__init__(tool+':'+str(self.error.get('code')))

class Live:
 def __init__(self,runtime):
  self.runtime=runtime;self.c=None;self.seq=0;self.ctx=None;self.pid=None;self.loaded=False;self.cleanup_entered=False;self.active=None
 def call(self,name,args):
  args=json_value(args)
  if name=='spherewright_inspect_factory_entity' and args.get('geometry') is not None: args=dict(args,geometry=complete_geometry_arrays(args['geometry']))
  self.seq+=1;self.runtime.put(f'request-{self.seq:05d}.private.json',dict(tool=name,arguments=args))
  r,bad=self.c.call(name,args);self.runtime.put(f'response-{self.seq:05d}.private.json',dict(response=r,toolError=bad))
  if bad or not r.get('success'): raise ToolRefused(name,r.get('error'))
  return r.get('result',r.get('status'))
 def offline_preflight(self):
  s=self.runtime;c=s.config;s.stopped();s.cohort();m=s.verify_backup()
  for ref in c['qualifiedInputs']:
   need(sha(ref['path'])==ref['sha256'],'qualified_input_changed')
  q=read(c['qualificationPath']);sdk=read(c['sdkQualificationPath'])
  need(q['passed'] and q['sourceSha']==c['sourceSha'] and sdk['passed'],'source_or_sdk_unqualified')
  for original in c['terminalOriginalActions']:
   receipt=read(original['path'])
   need(sha(original['path'])==original['sha256'] and receipt['terminal'] and receipt['state']!='outcome_unknown',
     'current_original_action_not_reconciled')
  need(c['firstOperationReady'] and c['originalActionsReconciled'],'offline_not_ready')
  self.c=Client(Path(c['pluginDestination'])/'Spherewright.Mcp.exe',s.output/'client',maximum=c['maximumRpc'],seconds=c['maximumWallSeconds'],
    total_stdout_limit=c.get('maximumStdoutBytes',64*1024*1024),total_stderr_limit=c.get('maximumStderrBytes',1024*1024))
  _,tools,_,_=self.c.initialize();self.schemas={t['name']:t['inputSchema'] for t in tools}
  self.steam=subprocess.check_output(['powershell.exe','-NoProfile','-NonInteractive','-Command',"(Get-ItemProperty -LiteralPath 'HKCU:/Software/Valve/Steam' -Name SteamExe).SteamExe"],text=True,timeout=10).strip()
  need(Path(self.steam).is_file(),'steam_missing')
  proof={key:True for key in G.READINESS_FLAGS};proof.update(sourceSha=c['sourceSha'],completeBackupFiles=len(m['rows']),knownFloor=c['sourceTick'])
  s.put('offline-ready.private.json',proof);return proof
 def launch_once(self,deadline):
  self.deadline=deadline;self.dispatch_utc=dt.datetime.now(dt.timezone.utc)
  self.runtime.put('launch-intent.private.json',dict(sourceSha=self.runtime.config['sourceSha'],startedAtUtc=self.dispatch_utc.isoformat(),maximumLaunches=1,limitSeconds=300))
  si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
  p=subprocess.Popen([self.steam,'-applaunch','1366540'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,startupinfo=si,creationflags=0x200,close_fds=True)
  self.runtime.put('steam-proxy.private.json',dict(processId=p.pid));return p.pid
 def process(self):
  raw=subprocess.check_output(['powershell.exe','-NoProfile','-NonInteractive','-Command',"@(Get-Process DSPGAME -ErrorAction SilentlyContinue)|Select-Object Id,Path,Responding,@{N='startedUtc';E={$_.StartTime.ToUniversalTime().ToString('O')}}|ConvertTo-Json -Compress"],text=True,timeout=10).strip()
  rows=json.loads(raw)if raw else []
  if isinstance(rows,dict):rows=[rows]
  need(len(rows)<=1,'multiple_game_processes')
  return rows[0]if rows else None
 def wait_ready(self,process,deadline):
  while time.monotonic()<deadline:
   p=self.process()
   if p:
    need(Path(p['Path']).resolve()==(Path(self.runtime.config['dspRoot'])/'DSPGAME.exe').resolve(),'game_path_changed')
    need(dt.datetime.fromisoformat(p['startedUtc'])>=self.dispatch_utc-dt.timedelta(seconds=1),'prior_game_process')
    if self.pid is None:
     self.pid=p['Id'];self.process_record=p;self.runtime.put('game-job-proof.private.json',dict(processId=self.pid));self.runtime.put('process-observed.private.json',p)
    need(self.pid==p['Id'],'original_process_changed')
    if (self.runtime.output/'lifetime-ready.private.json').exists():
     life=read(self.runtime.output/'game-lifetime-qualification.private.json');need(life['passed']and life['gameProcessId']==self.pid,'lifetime_mismatch')
     log=Path(self.runtime.config['dspRoot'])/'BepInEx/LogOutput.log'
     if log.exists()and log.stat().st_mtime>=dt.datetime.fromisoformat(p['startedUtc']).timestamp():
      raw=log.read_bytes();need(len(raw)<8*1024*1024,'log_bound');observed={}
      for name,mvid,info,av,error in re.findall(r'Spherewright loaded module: name=(\S+) mvid=(\S+) informationalVersion=(\S+) assemblyVersion=(\S+) captureError=(\S+)',raw.decode('utf-8-sig')):
       need(name not in observed,'repeated_startup');observed[name]=dict(moduleVersionId=mvid,informationalVersion=info,error=error)
      stamps=read(Path(self.runtime.config['revisionStamps']));expected={x['assemblyName']:x for x in stamps['modules']};expected['Assembly-CSharp']=stamps['native']
      if set(observed)==set(expected):
       for name,x in observed.items():
        need(x['error']=='none'and x['moduleVersionId'].lower()==expected[name]['moduleVersionId'].lower(),'loaded_module_mismatch')
        if name!='Assembly-CSharp':need(x['informationalVersion']=='0.5.0+'+self.runtime.config['sourceSha'],'loaded_source_mismatch')
       if not(self.runtime.output/'loaded-modules.private.json').exists():self.runtime.put('loaded-modules.private.json',dict(passed=True,sourceSha=self.runtime.config['sourceSha'],processId=self.pid,modules=observed))
       try:
        s=G.retry_read_only(lambda:self.call('spherewright_get_session_state',{}),deadline,lambda e:any(k in str(e)for k in ('REQUEST_TIMEOUT','BRIDGE_NOT_READY','BRIDGE_UNAVAILABLE')))
        if not s['gameLoaded']and s.get('restartResumeAvailable'):
         return dict(session=s)
       except RuntimeError as e:
        if not any(k in str(e)for k in ('REQUEST_TIMEOUT','BRIDGE_NOT_READY','BRIDGE_UNAVAILABLE')):raise
   time.sleep(.25)
  raise G.DeadlineExceeded('Native menu/module/lifetime readiness exceeded startup budget')

 def commit(self,role,tool,args):
  self.runtime.put(role+'-intent.private.json',args);self.active='unresolved_submission:'+role
  try: accepted=self.call(tool,args)
  except ToolRefused as e:
   if e.error.get('code') in ('STALE_STATE','INVALID_REQUEST','USER_CONFIRMATION_REQUIRED','WRITES_DISABLED'):
    self.active=None;raise G.CommitRejected('authoritative_preacceptance_refusal:'+str(e.error.get('code')))
   raise
  self.runtime.put(role+'-accepted.private.json',accepted)
  need(bool(accepted.get('actionId')),'accepted_action_handle_missing')
  self.active=accepted['actionId'];return self.active

 def wait_original(self,handle):
  while time.monotonic()<self.c.deadline:
   r=self.call('spherewright_get_action_result',dict(actionId=handle))
   if r['terminal']:
    self.runtime.put('terminal-'+handle+'.private.json',r)
    if r['state']!='outcome_unknown':self.active=None
    return r
   time.sleep(.5)
  raise RuntimeError('original_action_pending_no_replay')

 def prepare_resume(self,ready,deadline):
  c=self.runtime.config;now=dt.datetime.now(dt.timezone.utc)
  args=dict(resumeToken=ready['session']['restartResumeToken'],recoveryMode='authorize_remote_primary_recovery',
   minimumRecoveryGameTick=c['sourceTick'],expectedRecoveryGameTick=c['sourceTick'],
   recoveryDeadlineUtc=(now+dt.timedelta(seconds=c['recoveryWindowSeconds'])).isoformat(),
   recoveryScope='continue_original_finite_task',maximumChargeGameTicks=18000,maximumChargeWallSeconds=300,
   additionalVoyagerGameTicks=c['additionalVoyagerGameTicks'])
  target=c.get('surfaceRecoveryTarget')
  if target is not None:
   args.update(dict(zip(('surfaceRecoveryTargetX','surfaceRecoveryTargetY','surfaceRecoveryTargetZ'),(target[k] for k in 'xyz'))))
  p=G.retry_read_only(lambda:self.call('spherewright_prepare_resume_owned_game',args),deadline,
    lambda e:any(k in str(e) for k in ('BRIDGE_NOT_READY','BRIDGE_UNAVAILABLE','REQUEST_TIMEOUT')))
  need(p['prepared'] and p['userConfirmationRequired'] and not p['commitAllowedNow']
    and [b['code'] for b in p['commitBlockers']]==['USER_CONFIRMATION_REQUIRED'],'unexpected_resume_blockers')
  need(p['remotePrimaryRecoveryAuthorizationUsed'] and p['completedSavedLandingAdmissionUsed']
    and p['expectedPlanetId']==c['planetId'] and p['candidateGameTick']==p['minimumGameTick']==c['sourceTick']
    and p['discardedUnstoredProgressGameTicks']==0 and p['additionalVoyagerGameTicks']==c['additionalVoyagerGameTicks']
    and p['originalJourneyMaximumGameTicks']==c['originalJourneyMaximumGameTicks']
    and p['effectiveJourneyMaximumGameTicks']==c['originalJourneyMaximumGameTicks']+c['additionalVoyagerGameTicks'],
    'exact_no_loss_source_or_budget_echo_changed')
  if target is not None:
   need(p['surfaceRecoveryMaximumWorkGameTicks']==600 and p['surfaceRecoveryMaximumWallSeconds']==20
     and all(abs(p['surfaceRecoveryTarget'][k]-target[k])<.0001 for k in 'xyz'),'surface_target_disclosure_changed')
  self.runtime.put('fresh-resume-plan.private.json',p);return p

 def commit_resume_once(self,p):
  return self.commit('resume','spherewright_commit_resume_owned_game',dict(planToken=p['planToken'],
    idempotencyKey=str(uuid.uuid4()),userConfirmedInConversation=True,confirmationDigest=p['confirmationDigest']))

 def verify_loaded(self,result,deadline):
  c=self.runtime.config;s=self.call('spherewright_get_session_state',{})
  need(result['succeeded'] and s['gameLoaded'] and s['ownedBySpherewright'] and s['writesAllowed']
    and s['localPlanetId']==c['planetId'] and s['gameTick']>=c['sourceTick'],'owned_admission_unproved')
  self.loaded=True;self.ctx=dict(sessionId=s['sessionId'],planetId=c['planetId']);self.runtime.put('loaded-session.private.json',s)
  return s

 def cleanup_known_state(self):
  need(not self.cleanup_entered and self.active is None,'original_cleanup_or_action_unsettled')
  self.cleanup_entered=True;s=self.call('spherewright_get_session_state',{})
  if s['gameLoaded']:
   need(s['ownedBySpherewright'] and s['writesAllowed'],'unsafe_cleanup_world')
   self.ctx=dict(sessionId=s['sessionId'],planetId=s['localPlanetId'])
   q=self.call('spherewright_prepare_return_to_main_menu',dict(self.ctx,expectedRevision=s['revision']))
   h=self.commit('normal-save-menu','spherewright_commit_return_to_main_menu',dict(self.ctx,planToken=q['planToken'],idempotencyKey=str(uuid.uuid4())))
   need(self.wait_original(h)['succeeded'],'original_save_menu_failed')
   s=self.call('spherewright_get_session_state',{})
  need(not s['gameLoaded'],'native_menu_unproved');self.c.close();self.c=None
  self.normal_close_current_process()

 def normal_close_current_process(self):
  need(self.c is None,'mcp_must_close_before_native_exit')
  p=self.process();need(p is not None and p['Id']==self.pid,'original_process_changed')
  need(Path(p['Path']).resolve()==(Path(self.runtime.config['dspRoot'])/'DSPGAME.exe').resolve(),'original_process_path_changed')
  self.runtime.put('normal-close-intent.private.json',dict(processId=self.pid,forceKill=False,maximumRequests=1))
  r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',
    f"$p=Get-Process -Id {self.pid} -ErrorAction Stop;if(-not $p.CloseMainWindow()){{throw 'Normal close refused'}}"],capture_output=True,timeout=10)
  need(r.returncode==0,'normal_close_refused')
  end=time.monotonic()+30
  while time.monotonic()<end:
   if self.process() is None:
    self.runtime.put('normal-close-result.private.json',dict(passed=True,gameStopped=True))
    self.runtime.backup_after_normal_close();return
   time.sleep(.25)
  raise RuntimeError('normal_close_unknown_no_force_kill')

 def failure_requires_preservation(self,error):
  # Local validation and unaccepted prepare errors do not imply world damage.
  # The still-resident writer may inspect and fresh-prepare a corrected plan.
  return isinstance(error,(AcceptedActionFailure,G.DeadlineExceeded))

 def successful_original(self,handle):
  r=self.wait_original(handle)
  if not r.get('succeeded'):raise AcceptedActionFailure('original_action_failed_no_replay:'+handle,r)
  return r

 def player(self):return self.call('spherewright_get_player_state',self.ctx)
 def entity(self,i):return self.call('spherewright_inspect_factory_entity',dict(self.ctx,objectId=i))
 def state(self):
  c=self.runtime.config;s=self.call('spherewright_get_session_state',{})
  need(s['gameLoaded'] and s['ownedBySpherewright'] and s['writesAllowed']
    and s['localPlanetId']==self.ctx['planetId'] and s['localPlanetId'] in c.get('authorizedPlanetIds',[c['planetId']]),'owned_world_health_changed')
  spent=c['spentGameTicks']+s['gameTick']-c['sourceTick']
  need(spent+c['returnReserveGameTicks']+c['cleanupReserveGameTicks']<c['maximumCumulativeGameTicks'],'finite_stage_work_reserve_reached')
  return s
 def configure(self,role,entity_id,recipe_id,mode='production',filter_item=0):
  e=self.entity(entity_id)
  args=dict(self.ctx,entityId=entity_id,recipeId=recipe_id,mode=mode,
    expectedFactoryStateHash=e['configurationStateHash'] if mode=='sorter-filter' else e['stateHash'])
  if mode=='sorter-filter':args['filterItemId']=filter_item
  q=self.call('spherewright_prepare_configure_building',args)
  need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'configuration_not_prepared')
  self.successful_original(self.commit(role,'spherewright_commit_configure_building',dict(self.ctx,planToken=q['planToken'],idempotencyKey=str(uuid.uuid4()))))
  return self.entity(entity_id)

 def prepare_first_work(self,loaded,deadline):
  work=self.runtime.config['firstOperation'];mode=work.get('mode','production')
  if work.get('kind')=='move':
   p=self.player();self.first_before=p;target=work['target']
   args=dict(self.ctx,targetX=target['x'],targetY=target['y'],targetZ=target['z'],arrivalTolerance=1.5,expectedPlayerStateHash=p['stateHash'])
   q=self.call('spherewright_prepare_move',args);need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'first_move_not_prepared')
   return dict(action_kind='move',tool='spherewright_commit_move',prepared=q)
  e=self.player() if mode=='enable-mecha-construction-drones' else self.entity(work['entityId']);self.first_before=e
  if mode=='production':need(e['recipeId']!=work['recipeId'],'first_recipe_already_applied_no_delta')
  args=dict(self.ctx,entityId=work['entityId'],recipeId=work.get('recipeId',0),mode=mode,expectedFactoryStateHash=e['stateHash'])
  if mode=='storage-capacity':args.update(storageOperation=work['storageOperation'],filterItemId=work.get('filterItemId',0))
  q=self.call('spherewright_prepare_configure_building',args)
  need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'first_operation_not_prepared')
  return dict(action_kind='configure-building',tool='spherewright_commit_configure_building',prepared=q)
 def commit_first_work_once(self,w):return self.commit('first-work',w['tool'],dict(self.ctx,planToken=w['prepared']['planToken'],idempotencyKey=str(uuid.uuid4())))
 def verify_progress(self,w,r):
  c=self.runtime.config['firstOperation'];mode=c.get('mode','production')
  if c.get('kind')=='move':
   e=self.player();ground=(e.get('nativePhysics') or {}).get('groundContact') or {};velocity=(e.get('nativePhysics') or {}).get('velocity') or {}
   moved=math.dist([self.first_before['position'][k] for k in 'xyz'],[e['position'][k] for k in 'xyz'])
   ok=r['succeeded'] and moved>1 and e['movementState']=='Walk' and e['speed']<=.1 and ground.get('checkSphereHit') is True and all(velocity.get(k)==0 for k in 'xyz')
   self.runtime.put('actual-progress.private.json',dict(verified=ok,actionId=r['actionId'],before=self.first_before,after=e));return ok
  e=self.player() if mode=='enable-mecha-construction-drones' else self.entity(c['entityId'])
  if mode=='enable-mecha-construction-drones':
   ok=r['succeeded'] and self.first_before['constructionDrones']['enabled'] is False and e['constructionDrones']['enabled'] is True
  elif mode=='storage-capacity':
   before=self.first_before.get('storageConfiguration') or {};after=e.get('storageConfiguration') or {}
   filters=after.get('gridFilterItemIds') or []
   ok=r['succeeded'] and bool(r.get('storageConfigurationReadback')) and bool(filters)
   ok=ok and all(x==c['filterItemId'] for x in filters) and before!=after
  else:ok=r['succeeded'] and e['recipeId']==c['recipeId'] and self.first_before['recipeId']!=e['recipeId']
  self.runtime.put('actual-progress.private.json',dict(verified=ok,actionId=r['actionId'],before=self.first_before,after=e))
  return ok
