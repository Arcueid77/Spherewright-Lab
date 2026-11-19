"""Single-writer shared public MCP lifecycle. Work plans are immutable private input."""
from pathlib import Path
from collections.abc import Mapping
import datetime as dt,json,math,re,subprocess,time,uuid
import startup_to_action as G
from geometry_request import complete_geometry_arrays
from evidence import need,read,sha,json_value
from mcp_client import Client
from saved_space import exact_last_exit_echo,paused_space_source,exact_ui_supply,saved_identity_token
from contracts import quarantined_navigation_original_accounted,fully_observed_dry_surface,observed_short_crossing_dry_landing
from contracts import native_movement_order_released,remote_paused_saved_after_isolated_home,remote_roundtrip_paused_after_isolation
from contracts import ordinary_owned_resume_echo,resume_admission_echo,validate_steps,validate_native_calls,strict_native_player_idle,native_warper_auto_supply_enabled,quarantined_paid_original_accounted,quarantined_harvest_no_effect_accounted,isolated_paid_belt_build_accounted,quarantined_local_move_saved_source,completed_saved_surface_move,isolated_surface_unknown_after_saved_home,isolated_saved_menu_unknown,remote_saved_after_isolated_home,remote_paid_saved_after_isolated_remote,remote_failed_resume_saved_after_paid,remote_healthy_saved_after_isolation,remote_paused_harvest_saved_after_isolation,remote_failed_same_tick_saved_after_isolation,remote_live_exit_after_isolation

PLAYER_SETTING_MODES=('enable-mecha-construction-drones','disable-mecha-research-auto-supply',
 'enable-mecha-research-auto-supply','enable-mecha-warper-auto-supply')

class AcceptedActionFailure(RuntimeError):
 def __init__(self,message,receipt=None):self.receipt=receipt;super().__init__(message)

class NativePreacceptanceRefusal(G.CommitRejected):
 def __init__(self,tool,error):
  self.tool=tool;self.error=error
  super().__init__('authoritative_preacceptance_refusal:'+str(error.get('code')))

class ToolRefused(RuntimeError):
    def __init__(self, tool, error):
        self.tool=tool; self.error=error or {}; super().__init__(tool+':'+str(self.error.get('code')))

def successful_surface_prepare_arguments(config, token, now):
 target=config.get('surfaceRecoveryTarget');seconds=config.get('recoveryWindowSeconds')
 renamed=config.get('restoreRenamedLastExitIdentity') is True
 content_hash=config.get('expectedRenamedLastExitContentHash','')
 need(config.get('recoveryProfile')=='successful-outbound-surface'
  and config.get('recoveryMode')=='authorize_remote_primary_recovery' and config.get('sourceRole')==('lastExit' if renamed else 'primary')
  and type(config.get('sourceTick')) is int and config['sourceTick']>=0 and isinstance(target,Mapping)
  and set(target)==set('xyz') and all(type(target[k]) in (int,float) and math.isfinite(target[k]) for k in 'xyz')
  and type(seconds) in (int,float) and math.isfinite(seconds) and seconds>0
  and type(config.get('additionalVoyagerGameTicks')) is int and config['additionalVoyagerGameTicks']>=0
  and isinstance(token,str) and bool(token)
  and (isinstance(content_hash,str) and re.fullmatch(r'sha256:[0-9a-f]{64}',content_hash) is not None if renamed else not content_hash),
  'successful_surface_source_shape_invalid')
 args=dict(resumeToken=token,recoveryMode=config['recoveryMode'],
  recoveryDeadlineUtc=(now+dt.timedelta(seconds=seconds)).isoformat(),recoveryScope='continue_original_finite_task',
  maximumChargeGameTicks=18000,maximumChargeWallSeconds=300,additionalVoyagerGameTicks=config['additionalVoyagerGameTicks'],
  surfaceRecoveryExpectedSourceGameTick=config['sourceTick'])
 args.update(dict(zip(('surfaceRecoveryTargetX','surfaceRecoveryTargetY','surfaceRecoveryTargetZ'),(target[k] for k in 'xyz'))))
 if renamed:args.update(restoreRenamedLastExitIdentity=True,expectedRenamedLastExitContentHash=content_hash)
 return args


def ordinary_remote_prepare_arguments(config,token,now):
 seconds=config.get('recoveryWindowSeconds');extra=config.get('additionalVoyagerGameTicks')
 need(config.get('recoveryProfile')=='ordinary-owned-remote'
  and config.get('recoveryMode')=='authorize_remote_primary_recovery'
  and (config.get('sourceRole')=='primary' or config.get('sourceRole')=='lastExit' and bool(
   config.get('remoteFailedResumeSavedIsolation') or config.get('remoteLiveExitIsolation')))
  and config.get('surfaceRecoveryTarget') is None and type(config.get('sourceTick')) is int and config['sourceTick']>=0
  and type(seconds) in (int,float) and math.isfinite(seconds) and 0<seconds<=86400
  and type(extra) is int and 0<=extra<=5184000 and isinstance(token,str) and bool(token),
  'ordinary_remote_source_shape_invalid')
 return dict(resumeToken=token,recoveryMode=config['recoveryMode'],minimumRecoveryGameTick=config['sourceTick'],
  expectedRecoveryGameTick=config['sourceTick'],recoveryDeadlineUtc=(now+dt.timedelta(seconds=seconds)).isoformat(),
  recoveryScope='continue_original_finite_task',maximumChargeGameTicks=18000,maximumChargeWallSeconds=300,
  additionalVoyagerGameTicks=extra)


class Live:
 def __init__(self,runtime):
  self.runtime=runtime;self.c=None;self.seq=0;self.ctx=None;self.pid=None;self.loaded=False;self.cleanup_entered=False;self.active=None
  self.prior_rpc_count=getattr(runtime,'config',{}).get('priorRpcCount',0)
 def call(self,name,args):
  args=json_value(args)
  if name=='spherewright_inspect_factory_entity' and args.get('geometry') is not None: args=dict(args,geometry=complete_geometry_arrays(args['geometry']))
  self.seq+=1;self.runtime.put(f'request-{self.seq:05d}.private.json',dict(tool=name,arguments=args))
  r,bad=self.c.call(name,args);self.runtime.put(f'response-{self.seq:05d}.private.json',dict(response=r,toolError=bad))
  if bad or not r.get('success'): raise ToolRefused(name,r.get('error'))
  return r.get('result',r.get('status'))

 def assert_home_unknowns_isolated(self,c,backup):
  isolation=c.get('homeSavedUnknownIsolation')
  need(isolation and c.get('recoveryProfile')=='ordinary-owned-home'
    and c.get('originalActionsReconciled') is False,'home_isolation_requires_truthful_home_profile')
  def frozen(key):
   need(sha(isolation[key+'Path'])==isolation[key+'Sha256'],'frozen_home_isolation_evidence_changed')
   return read(isolation[key+'Path'])
  old=frozen('surfaceConfig');originals=old.get('quarantinedLocalMoveOriginals') or []
  need(len(originals)==1 and sha(old['backupManifest'])==old['backupManifestSha256'],
   'original_surface_source_or_backup_changed')
  original=originals[0]
  for key in ('receipt','session','preservation'):
   need(sha(original[key+'Path'])==original[key+'Sha256'],'frozen_local_move_evidence_changed')
  old_backup=read(old['backupManifest']);old_source=old_backup['latest'][old['sourceRole']]
  rows=[row for row in old_backup['rows'] if Path(row['originalPath']).resolve()==Path(old['savePaths'][old['sourceRole']]).resolve()]
  need(old_backup.get('complete') is True and old_backup.get('verified') is True and len(rows)==1
   and rows[0]['sha256']==old_source['sha256'] and sha(rows[0]['backupPath'])==old_source['sha256'],
   'original_surface_backup_copy_changed')
  need(isolated_surface_unknown_after_saved_home(c,old,original,read(original['receiptPath']),read(original['sessionPath']),
   read(original['preservationPath']),old_source,frozen('surfaceProgress'),frozen('loadedSession'),
   frozen('homeFlight'),frozen('homeSave'),backup),'historic_surface_unknown_not_isolated')
  need(isolated_saved_menu_unknown(c,frozen('menuReceipt'),frozen('menuObservedAction'),frozen('menuObservation'),
   frozen('closeIntent'),frozen('closeResult'),backup),'saved_menu_unknown_not_isolated')

 def assert_remote_unknowns_isolated(self,c,backup):
  isolation=c.get('remoteSavedUnknownIsolation')
  need(isolation and not c.get('homeSavedUnknownIsolation'),'remote_isolation_evidence_missing')
  def frozen(key):
   need(sha(isolation[key+'Path'])==isolation[key+'Sha256'],'frozen_remote_isolation_evidence_changed')
   return read(isolation[key+'Path'])
  home=frozen('homeConfig')
  need(sha(home['backupManifest'])==home['backupManifestSha256'],'home_backup_manifest_changed')
  previous=read(home['backupManifest'])
  need(previous.get('complete') is True and previous.get('verified') is True,'home_backup_unproved')
  for role in ('primary','lastExit'):
   home_path=Path(home['savePaths'][role]).resolve()
   need(home_path==Path(c['savePaths'][role]).resolve(),'remote_save_identity_changed')
   rows=[row for row in previous['rows'] if Path(row['originalPath']).resolve()==home_path]
   proof=previous['latest'][role]
   need(len(rows)==1 and rows[0]['sha256']==proof['sha256'] and sha(rows[0]['backupPath'])==proof['sha256'],
    'historical_home_backup_copy_changed')
  self.assert_home_unknowns_isolated(home,previous)
  loaded=frozen('homeLoadedSession')
  need(loaded.get('saveName')==Path(home['savePaths']['primary']).stem,'loaded_home_identity_changed')
  if isolation.get('remotePausedSavePath'):
   need(remote_paused_saved_after_isolated_home(c,home,loaded,frozen('outbound'),
    frozen('remotePausedCut'),frozen('remotePausedSavePlan'),frozen('remotePausedSave'),
    frozen('remoteNormalClose'),frozen('remotePreservation'),backup),
    'remote_paused_outbound_saved_isolation_unproved')
  else:
   need(remote_saved_after_isolated_home(c,home,loaded,frozen('outbound'),
    frozen('remoteMenuSave'),backup),'remote_saved_outbound_isolation_unproved')

 def assert_remote_roundtrip_paused_isolated(self,c,backup,depth=0):
  need(type(depth)is int and 0<=depth<16,'roundtrip_isolation_chain_outside_bound')
  isolation=c.get('remoteRoundtripPausedIsolation')
  need(isolation and not any(c.get(k) for k in ('homeSavedUnknownIsolation','remoteSavedUnknownIsolation',
   'remotePaidSavedUnknownIsolation','remoteFailedResumeSavedIsolation','remoteHealthySavedIsolation',
   'remoteLiveExitIsolation','remotePausedHarvestSavedIsolation','remoteFailedSameTickSavedIsolation')),
   'roundtrip_isolation_evidence_missing')
  def frozen(key):
   need(sha(isolation[key+'Path'])==isolation[key+'Sha256'],'frozen_roundtrip_evidence_changed')
   return read(isolation[key+'Path'])
  previous=frozen('previousConfig')
  need(sha(previous['backupManifest'])==previous['backupManifestSha256'],'previous_remote_backup_manifest_changed')
  older=read(previous['backupManifest'])
  need(older.get('complete') is True and older.get('verified') is True,'previous_remote_backup_unproved')
  for role in ('primary','lastExit'):
   path=Path(previous['savePaths'][role]).resolve()
   need(path==Path(c['savePaths'][role]).resolve(),'roundtrip_save_identity_changed')
   rows=[row for row in older['rows'] if Path(row['originalPath']).resolve()==path];proof=older['latest'][role]
   need(len(rows)==1 and rows[0]['sha256']==proof['sha256'] and sha(rows[0]['backupPath'])==proof['sha256'],
    'previous_remote_backup_copy_changed')
  if previous.get('remoteSavedUnknownIsolation'):
   self.assert_remote_unknowns_isolated(previous,older)
  elif previous.get('remoteHealthySavedIsolation'):
   self.assert_remote_healthy_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteLiveExitIsolation'):
   self.assert_remote_live_exit_isolated(previous,older,depth+1)
  elif previous.get('remotePausedHarvestSavedIsolation'):
   self.assert_remote_paused_harvest_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteFailedSameTickSavedIsolation'):
   self.assert_remote_failed_same_tick_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteFailedResumeSavedIsolation'):
   self.assert_remote_failed_resume_saved_isolated(previous,older,depth+1)
  else:
   need(bool(previous.get('remoteRoundtripPausedIsolation')),'previous_remote_isolation_missing')
   self.assert_remote_roundtrip_paused_isolated(previous,older,depth+1)
  need(remote_roundtrip_paused_after_isolation(c,previous,frozen('loadedSession'),frozen('homeReturn'),
   frozen('homeSave'),frozen('outbound'),frozen('pausedCut'),frozen('pausedSavePlan'),frozen('pausedSave'),
   frozen('normalClose'),frozen('preservation'),backup),'roundtrip_paused_saved_isolation_unproved')

 def assert_remote_paid_unknowns_isolated(self,c,backup):
  isolation=c.get('remotePaidSavedUnknownIsolation')
  need(isolation and not c.get('homeSavedUnknownIsolation') and not c.get('remoteSavedUnknownIsolation'),
   'remote_paid_isolation_evidence_missing')
  def frozen(key):
   need(sha(isolation[key+'Path'])==isolation[key+'Sha256'],'frozen_remote_paid_evidence_changed')
   return read(isolation[key+'Path'])
  previous=frozen('previousConfig')
  need(sha(previous['backupManifest'])==previous['backupManifestSha256'],'previous_remote_backup_manifest_changed')
  older=read(previous['backupManifest'])
  need(older.get('complete') is True and older.get('verified') is True,'previous_remote_backup_unproved')
  for role in ('primary','lastExit'):
   path=Path(previous['savePaths'][role]).resolve()
   need(path==Path(c['savePaths'][role]).resolve(),'remote_paid_save_identity_changed')
   rows=[row for row in older['rows'] if Path(row['originalPath']).resolve()==path]
   proof=older['latest'][role]
   need(len(rows)==1 and rows[0]['sha256']==proof['sha256'] and sha(rows[0]['backupPath'])==proof['sha256'],
    'previous_remote_backup_copy_changed')
  self.assert_remote_unknowns_isolated(previous,older)
  need(remote_paid_saved_after_isolated_remote(c,previous,frozen('loadedSession'),frozen('originalAction'),
   frozen('observedBuild'),frozen('quarantinedSession'),frozen('pausedPlayer'),frozen('observedStation'),
   frozen('pausedSave'),frozen('normalClose'),backup),'remote_paid_saved_isolation_unproved')

 def assert_remote_failed_resume_saved_isolated(self,c,backup,depth=0):
  need(type(depth)is int and 0<=depth<16,'failed_resume_isolation_chain_outside_bound')
  isolation=c.get('remoteFailedResumeSavedIsolation')
  need(isolation and not c.get('homeSavedUnknownIsolation') and not c.get('remoteSavedUnknownIsolation')
   and not c.get('remotePaidSavedUnknownIsolation'),'remote_failed_resume_isolation_evidence_missing')
  def frozen(key):
   need(sha(isolation[key+'Path'])==isolation[key+'Sha256'],'frozen_failed_resume_evidence_changed')
   return read(isolation[key+'Path'])
  previous=frozen('previousConfig')
  need(sha(previous['backupManifest'])==previous['backupManifestSha256'],'previous_paid_backup_manifest_changed')
  older=read(previous['backupManifest'])
  need(older.get('complete') is True and older.get('verified') is True,'previous_paid_backup_unproved')
  for role in ('primary','lastExit'):
   path=Path(previous['savePaths'][role]).resolve()
   need(path==Path(c['savePaths'][role]).resolve(),'failed_resume_save_identity_changed')
   rows=[row for row in older['rows'] if Path(row['originalPath']).resolve()==path]
   proof=older['latest'][role]
   need(len(rows)==1 and rows[0]['sha256']==proof['sha256'] and sha(rows[0]['backupPath'])==proof['sha256'],
    'previous_paid_backup_copy_changed')
  if previous.get('remotePaidSavedUnknownIsolation'):
   self.assert_remote_paid_unknowns_isolated(previous,older)
  else:
   need(bool(previous.get('remoteFailedResumeSavedIsolation')),'previous_paid_or_failed_resume_isolation_missing')
   self.assert_remote_failed_resume_saved_isolated(previous,older,depth+1)
  paused_save=frozen('pausedSave') if isolation.get('pausedSavePath') else None
  need(remote_failed_resume_saved_after_paid(c,previous,frozen('failedResume'),frozen('pausedCut'),
   frozen('normalClose'),backup,paused_save),'failed_resume_saved_isolation_unproved')

 def assert_remote_healthy_saved_isolated(self,c,backup,depth=0):
  need(type(depth)is int and 0<=depth<16,'healthy_remote_isolation_chain_outside_bound')
  isolation=c.get('remoteHealthySavedIsolation')
  need(isolation and not any(c.get(k) for k in ('homeSavedUnknownIsolation','remoteSavedUnknownIsolation',
   'remotePaidSavedUnknownIsolation','remoteFailedResumeSavedIsolation','remoteLiveExitIsolation',
   'remotePausedHarvestSavedIsolation','remoteFailedSameTickSavedIsolation')),'healthy_remote_isolation_evidence_missing')
  def frozen(key):
   need(sha(isolation[key+'Path'])==isolation[key+'Sha256'],'frozen_healthy_remote_evidence_changed')
   return read(isolation[key+'Path'])
  previous=frozen('previousConfig')
  need(sha(previous['backupManifest'])==previous['backupManifestSha256'],'previous_remote_backup_manifest_changed')
  older=read(previous['backupManifest'])
  need(older.get('complete') is True and older.get('verified') is True,'previous_remote_backup_unproved')
  for role in ('primary','lastExit'):
   path=Path(previous['savePaths'][role]).resolve()
   need(path==Path(c['savePaths'][role]).resolve(),'healthy_remote_save_identity_changed')
   rows=[row for row in older['rows'] if Path(row['originalPath']).resolve()==path];proof=older['latest'][role]
   need(len(rows)==1 and rows[0]['sha256']==proof['sha256'] and sha(rows[0]['backupPath'])==proof['sha256'],
    'previous_remote_backup_copy_changed')
  if previous.get('remoteFailedResumeSavedIsolation'):
   self.assert_remote_failed_resume_saved_isolated(previous,older)
  elif previous.get('remoteSavedUnknownIsolation'):
   self.assert_remote_unknowns_isolated(previous,older)
  elif previous.get('remoteRoundtripPausedIsolation'):
   self.assert_remote_roundtrip_paused_isolated(previous,older,depth+1)
  elif previous.get('remoteLiveExitIsolation'):
   self.assert_remote_live_exit_isolated(previous,older,depth+1)
  elif previous.get('remotePausedHarvestSavedIsolation'):
   self.assert_remote_paused_harvest_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteFailedSameTickSavedIsolation'):
   self.assert_remote_failed_same_tick_saved_isolated(previous,older,depth+1)
  else:
   need(bool(previous.get('remoteHealthySavedIsolation')),'previous_remote_isolation_missing')
   self.assert_remote_healthy_saved_isolated(previous,older,depth+1)
  need(remote_healthy_saved_after_isolation(c,previous,frozen('loadedSession'),frozen('successfulResume'),
   frozen('menuSave'),backup),'healthy_remote_saved_isolation_unproved')

 def assert_remote_live_exit_isolated(self,c,backup,depth=0):
  need(type(depth)is int and 0<=depth<16,'remote_live_exit_isolation_chain_outside_bound')
  isolation=c.get('remoteLiveExitIsolation')
  need(isolation and not any(c.get(k) for k in ('homeSavedUnknownIsolation','remoteSavedUnknownIsolation',
   'remotePaidSavedUnknownIsolation','remoteFailedResumeSavedIsolation','remoteHealthySavedIsolation',
   'remotePausedHarvestSavedIsolation','remoteFailedSameTickSavedIsolation')),
   'remote_live_exit_isolation_evidence_missing')
  def frozen(key):
   need(sha(isolation[key+'Path'])==isolation[key+'Sha256'],'frozen_remote_live_exit_evidence_changed')
   return read(isolation[key+'Path'])
  previous=frozen('previousConfig')
  need(sha(previous['backupManifest'])==previous['backupManifestSha256'],'previous_remote_backup_manifest_changed')
  older=read(previous['backupManifest'])
  need(older.get('complete') is True and older.get('verified') is True,'previous_remote_backup_unproved')
  for role in ('primary','lastExit'):
   path=Path(previous['savePaths'][role]).resolve()
   need(path==Path(c['savePaths'][role]).resolve(),'remote_live_exit_save_identity_changed')
   rows=[row for row in older['rows'] if Path(row['originalPath']).resolve()==path];proof=older['latest'][role]
   need(len(rows)==1 and rows[0]['sha256']==proof['sha256'] and sha(rows[0]['backupPath'])==proof['sha256'],
    'previous_remote_backup_copy_changed')
  if previous.get('remoteFailedResumeSavedIsolation'):
   self.assert_remote_failed_resume_saved_isolated(previous,older)
  elif previous.get('remoteSavedUnknownIsolation'):
   self.assert_remote_unknowns_isolated(previous,older)
  elif previous.get('remoteRoundtripPausedIsolation'):
   self.assert_remote_roundtrip_paused_isolated(previous,older,depth+1)
  elif previous.get('remoteHealthySavedIsolation'):
   self.assert_remote_healthy_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteLiveExitIsolation'):
   self.assert_remote_live_exit_isolated(previous,older,depth+1)
  elif previous.get('remotePausedHarvestSavedIsolation'):
   self.assert_remote_paused_harvest_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteFailedSameTickSavedIsolation'):
   self.assert_remote_failed_same_tick_saved_isolated(previous,older,depth+1)
  else:raise RuntimeError('previous_remote_isolation_missing')
  actions=[]
  for ref in isolation['terminalActions']:
   need(sha(ref['path'])==ref['sha256'],'frozen_remote_live_action_changed')
   actions.append(read(ref['path']))
  origin=Path(isolation['clientClosePath']).parent
  accepted=set()
  for request in origin.glob('request-*.private.json'):
   call=read(request)
   if '_commit_' not in call.get('tool',''):continue
   response=read(origin/request.name.replace('request-','response-',1)).get('response') or {}
   if response.get('success') is False:continue
   result=response.get('result') or {};action=result.get('actionId')
   need(result.get('accepted') is True and isinstance(action,str) and action not in accepted,
    'remote_live_original_commit_unreconciled')
   accepted.add(action)
  need(accepted=={a.get('actionId') for a in actions},'remote_live_original_commit_set_changed')
  response=frozen('lastSession')
  last=(response.get('response') or {}).get('result') or {}
  need(remote_live_exit_after_isolation(c,previous,frozen('loadedSession'),frozen('successfulResume'),
   last,frozen('clientClose'),actions,backup),'remote_live_exit_saved_isolation_unproved')

 def assert_remote_paused_harvest_saved_isolated(self,c,backup,depth=0):
  need(type(depth)is int and 0<=depth<16,'paused_harvest_isolation_chain_outside_bound')
  isolation=c.get('remotePausedHarvestSavedIsolation')
  need(isolation and not any(c.get(k) for k in ('homeSavedUnknownIsolation','remoteSavedUnknownIsolation',
   'remotePaidSavedUnknownIsolation','remoteFailedResumeSavedIsolation','remoteHealthySavedIsolation',
   'remoteLiveExitIsolation','remoteFailedSameTickSavedIsolation')),'paused_harvest_isolation_evidence_missing')
  def frozen(key):
   need(sha(isolation[key+'Path'])==isolation[key+'Sha256'],'frozen_paused_harvest_evidence_changed')
   return read(isolation[key+'Path'])
  previous=frozen('previousConfig')
  need(sha(previous['backupManifest'])==previous['backupManifestSha256'],'previous_remote_backup_manifest_changed')
  older=read(previous['backupManifest'])
  need(older.get('complete') is True and older.get('verified') is True,'previous_remote_backup_unproved')
  for role in ('primary','lastExit'):
   path=Path(previous['savePaths'][role]).resolve()
   need(path==Path(c['savePaths'][role]).resolve(),'paused_harvest_save_identity_changed')
   rows=[row for row in older['rows'] if Path(row['originalPath']).resolve()==path];proof=older['latest'][role]
   need(len(rows)==1 and rows[0]['sha256']==proof['sha256'] and sha(rows[0]['backupPath'])==proof['sha256'],
    'previous_remote_backup_copy_changed')
  if previous.get('remoteHealthySavedIsolation'):
   self.assert_remote_healthy_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteSavedUnknownIsolation'):
   self.assert_remote_unknowns_isolated(previous,older)
  elif previous.get('remoteRoundtripPausedIsolation'):
   self.assert_remote_roundtrip_paused_isolated(previous,older,depth+1)
  elif previous.get('remoteLiveExitIsolation'):
   self.assert_remote_live_exit_isolated(previous,older,depth+1)
  elif previous.get('remotePausedHarvestSavedIsolation'):
   self.assert_remote_paused_harvest_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteFailedSameTickSavedIsolation'):
   self.assert_remote_failed_same_tick_saved_isolated(previous,older,depth+1)
  else:raise RuntimeError('previous_remote_isolation_missing')
  reference=frozen('harvestReference')
  need(remote_paused_harvest_saved_after_isolation(c,previous,frozen('loadedSession'),frozen('successfulResume'),
   reference,frozen('harvest'),frozen('harvestCut'),frozen('quarantinedSession'),frozen('pausedSavePlan'),
   frozen('pausedSave'),frozen('normalClose'),frozen('preservation'),backup),'paused_harvest_saved_isolation_unproved')

 def assert_remote_failed_same_tick_saved_isolated(self,c,backup,depth=0):
  need(type(depth)is int and 0<=depth<16,'same_tick_failed_resume_chain_outside_bound')
  isolation=c.get('remoteFailedSameTickSavedIsolation')
  need(isolation and not any(c.get(k) for k in ('homeSavedUnknownIsolation','remoteSavedUnknownIsolation',
   'remotePaidSavedUnknownIsolation','remoteFailedResumeSavedIsolation','remoteHealthySavedIsolation',
   'remoteLiveExitIsolation','remotePausedHarvestSavedIsolation')),'same_tick_failed_resume_evidence_missing')
  def frozen(key):
   need(sha(isolation[key+'Path'])==isolation[key+'Sha256'],'frozen_same_tick_resume_evidence_changed')
   return read(isolation[key+'Path'])
  previous=frozen('previousConfig')
  need(sha(previous['backupManifest'])==previous['backupManifestSha256'],'previous_remote_backup_manifest_changed')
  older=read(previous['backupManifest'])
  need(older.get('complete') is True and older.get('verified') is True,'previous_remote_backup_unproved')
  for role in ('primary','lastExit'):
   path=Path(previous['savePaths'][role]).resolve()
   need(path==Path(c['savePaths'][role]).resolve(),'same_tick_resume_save_identity_changed')
   rows=[row for row in older['rows'] if Path(row['originalPath']).resolve()==path];proof=older['latest'][role]
   need(len(rows)==1 and rows[0]['sha256']==proof['sha256'] and sha(rows[0]['backupPath'])==proof['sha256'],
    'previous_remote_backup_copy_changed')
  if previous.get('remotePausedHarvestSavedIsolation'):
   self.assert_remote_paused_harvest_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteSavedUnknownIsolation'):
   self.assert_remote_unknowns_isolated(previous,older)
  elif previous.get('remoteRoundtripPausedIsolation'):
   self.assert_remote_roundtrip_paused_isolated(previous,older,depth+1)
  elif previous.get('remoteHealthySavedIsolation'):
   self.assert_remote_healthy_saved_isolated(previous,older,depth+1)
  elif previous.get('remoteFailedSameTickSavedIsolation'):
   self.assert_remote_failed_same_tick_saved_isolated(previous,older,depth+1)
  else:raise RuntimeError('previous_remote_isolation_missing')
  need(remote_failed_same_tick_saved_after_isolation(c,previous,frozen('failedResume'),frozen('quarantinedSession'),
   frozen('pausedSavePlan'),frozen('pausedSave'),frozen('normalClose'),backup),'same_tick_failed_resume_isolation_unproved')

 def offline_preflight(self):
  s=self.runtime;c=s.config;s.stopped();s.cohort();s.verify_revision_stamps();m=s.verify_backup()
  for ref in c['qualifiedInputs']:
   need(sha(ref['path'])==ref['sha256'],'qualified_input_changed')
  q=read(c['qualificationPath']);sdk=read(c['sdkQualificationPath'])
  need(q['passed'] and q['sourceSha']==c['sourceSha'] and sdk['passed'],'source_or_sdk_unqualified')
  for original in c['terminalOriginalActions']:
   receipt=read(original['path'])
   need(sha(original['path'])==original['sha256'] and receipt['terminal'] and receipt['state']!='outcome_unknown',
     'current_original_action_not_reconciled')
  for original in c.get('quarantinedOriginalActions',[]):
   need(sha(original['path'])==original['sha256'] and sha(original['preservationPath'])==original['preservationSha256']
    and quarantined_paid_original_accounted(c,original,read(original['path']),read(original['preservationPath'])),
    'unknown_original_must_remain_isolated_with_known_paid_create_and_complete_saved_source')
  for original in c.get('quarantinedNavigationOriginals', []):
   for key in ('receipt', 'session', 'preservation'):
    need(sha(original[key+'Path']) == original[key+'Sha256'], 'frozen_navigation_original_changed')
   need(quarantined_navigation_original_accounted(c, original, read(original['receiptPath']),
       read(original['sessionPath']), read(original['preservationPath'])),
       'unknown_navigation_requires_original_task_release_and_complete_no_loss_saved_source')
  for original in c.get('quarantinedLocalHarvestOriginals',[]):
   for path_key,hash_key in [('path','sha256'),('cutPath','cutSha256'),('sessionPath','sessionSha256'),('preservationPath','preservationSha256')]:
    need(sha(original[path_key])==original[hash_key],'frozen_harvest_original_evidence_changed')
   need(quarantined_harvest_no_effect_accounted(c,original,read(original['path']),read(original['cutPath']),read(original['sessionPath']),read(original['preservationPath'])),
    'unknown_harvest_requires_exact_zero_mutation_cut_and_latest_complete_preservation_no_replay')
  local_moves=c.get('quarantinedLocalMoveOriginals',())
  if c.get('recoveryProfile')=='successful-outbound-surface':
   need(isinstance(local_moves,(list,tuple)) and len(local_moves)==1,'original_local_move_evidence_required')
   for original in local_moves:
    for key in ('receipt','session','preservation'):
     need(sha(original[key+'Path'])==original[key+'Sha256'],'frozen_local_move_evidence_changed')
    need(quarantined_local_move_saved_source(c,original,read(original['receiptPath']),read(original['sessionPath']),
       read(original['preservationPath']),m['latest'][c['sourceRole']]),
       'original_local_move_or_covering_saved_source_unproved')
  else:
   need(not local_moves,'local_move_evidence_requires_surface_profile')
  home_isolated=False
  if c.get('homeSavedUnknownIsolation'):
   self.assert_home_unknowns_isolated(c,m);home_isolated=True
  if c.get('remoteSavedUnknownIsolation'):
   self.assert_remote_unknowns_isolated(c,m);home_isolated=True
  if c.get('remoteRoundtripPausedIsolation'):
   self.assert_remote_roundtrip_paused_isolated(c,m);home_isolated=True
  if c.get('remotePaidSavedUnknownIsolation'):
   self.assert_remote_paid_unknowns_isolated(c,m);home_isolated=True
  if c.get('remoteFailedResumeSavedIsolation'):
   self.assert_remote_failed_resume_saved_isolated(c,m);home_isolated=True
  if c.get('remoteHealthySavedIsolation'):
   self.assert_remote_healthy_saved_isolated(c,m);home_isolated=True
  if c.get('remoteLiveExitIsolation'):
   self.assert_remote_live_exit_isolated(c,m);home_isolated=True
  if c.get('remotePausedHarvestSavedIsolation'):
   self.assert_remote_paused_harvest_saved_isolated(c,m);home_isolated=True
  if c.get('remoteFailedSameTickSavedIsolation'):
   self.assert_remote_failed_same_tick_saved_isolated(c,m);home_isolated=True
  need(c['firstOperationReady'] and (c.get('originalActionsReconciled') is True
    or c.get('recoveryProfile')=='successful-outbound-surface' and bool(local_moves) or home_isolated),'offline_not_ready')
  for original in c.get('isolatedPaidBeltBuilds',[]):
   for key in ('receipt','plan','observation','preservation'):
    need(sha(original[key+'Path'])==original[key+'Sha256'],'frozen_belt_original_evidence_changed')
   need(isolated_paid_belt_build_accounted(c,*[read(original[k+'Path'])for k in ('receipt','plan','observation','preservation')]),
    'unknown_belt_original_requires_exact_paid_creation_and_complete_saved_progress')
  if c.get('recoveryMode')=='authorize_failed_landing_last_exit':
   need(c['additionalVoyagerGameTicks']==0 and c.get('surfaceRecoveryTarget') is None
     and bool(c.get('failedLandingActionId')),'failed_landing_config_shape_invalid')
  need(type(self.prior_rpc_count)is int and 0<=self.prior_rpc_count<c['maximumRpc'],'actual_prior_rpc_allowance_ended')
  self.c=Client(s.mcp_executable(),s.output/'client',maximum=c['maximumRpc']-self.prior_rpc_count,seconds=c['maximumWallSeconds'],
    total_stdout_limit=c.get('maximumStdoutBytes',64*1024*1024),total_stderr_limit=c.get('maximumStderrBytes',1024*1024))
  _,tools,_,_=self.c.initialize();self.schemas={t['name']:t['inputSchema'] for t in tools}
  validate_steps(c['initialSteps']);validate_native_calls(c['initialSteps'],self.schemas)
  if c.get('recoveryProfile')=='successful-outbound-surface':
   shape=successful_surface_prepare_arguments(c,'synthetic-offline-identity',dt.datetime.now(dt.timezone.utc))
   validate_native_calls([dict(kind='prepare-only',prepareTool='spherewright_prepare_resume_owned_game',arguments=shape)],self.schemas)
  if c.get('recoveryProfile')=='ordinary-owned-remote':
   shape=ordinary_remote_prepare_arguments(c,'synthetic-offline-identity',dt.datetime.now(dt.timezone.utc))
   validate_native_calls([dict(kind='prepare-only',prepareTool='spherewright_prepare_resume_owned_game',arguments=shape)],self.schemas)
  work=c.get('firstOperation') or {}
  if work.get('kind')=='storage-transfer':
   need(work.get('direction') in ('storage-to-player','player-to-storage')
    and all(type(work.get(k)) is int and work[k]>0 for k in ('entityId','itemId','count')),
    'first_storage_transfer_shape_invalid')
   shape=dict(direction=work['direction'],storageEntityId=work['entityId'],itemId=work['itemId'],count=work['count'],
    expectedPlayerStateHash='schema-placeholder',expectedStorageStateHash='schema-placeholder')
   validate_native_calls([dict(kind='prepare-only',prepareTool='spherewright_prepare_transfer',arguments=shape),
    dict(kind='prepare-only',prepareTool='spherewright_commit_transfer',
         arguments=dict(planToken='schema-placeholder',idempotencyKey='00000000-0000-4000-8000-000000000001'))],self.schemas)
  self.steam=subprocess.check_output(['powershell.exe','-NoProfile','-NonInteractive','-Command',"(Get-ItemProperty -LiteralPath 'HKCU:/Software/Valve/Steam' -Name SteamExe).SteamExe"],text=True,timeout=10).strip()
  need(Path(self.steam).is_file(),'steam_missing')
  proof={key:True for key in G.READINESS_FLAGS}
  if c.get('recoveryProfile')=='successful-outbound-surface' or home_isolated:
   proof['original_actions_reconciled']=False
   proof['original_unknowns_isolated']=True
  limit=G.startup_limit(c.get('startupLimitSeconds'))
  need(limit<=c['maximumWallSeconds'],'startup_limit_exceeds_caller_window')
  proof.update(sourceSha=c['sourceSha'],completeBackupFiles=len(m['rows']),knownFloor=c['sourceTick'],startup_limit_seconds=limit)
  s.put('offline-ready.private.json',proof);return proof
 def launch_once(self,deadline):
  self.deadline=deadline;self.dispatch_utc=dt.datetime.now(dt.timezone.utc)
  self.runtime.put('launch-intent.private.json',dict(sourceSha=self.runtime.config['sourceSha'],startedAtUtc=self.dispatch_utc.isoformat(),maximumLaunches=1,
   limitSeconds=G.startup_limit(self.runtime.config.get('startupLimitSeconds'))))
  si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
  p=subprocess.Popen([self.steam,'-applaunch','1366540'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,startupinfo=si,creationflags=0x200,close_fds=True)
  self.runtime.put('steam-proxy.private.json',dict(processId=p.pid));return p.pid
 def process(self):
  raw=subprocess.check_output(['powershell.exe','-NoProfile','-NonInteractive','-Command',"@(Get-Process DSPGAME -ErrorAction SilentlyContinue)|Select-Object Id,Path,Responding,@{N='startedUtc';E={$_.StartTime.ToUniversalTime().ToString('O')}},@{N='createdFileTime';E={$_.StartTime.ToFileTimeUtc()}}|ConvertTo-Json -Compress"],text=True,timeout=10).strip()
  rows=json.loads(raw)if raw else []
  if isinstance(rows,dict):rows=[rows]
  need(len(rows)<=1,'multiple_game_processes')
  return rows[0]if rows else None
 def wait_ready(self,process,deadline):
  try:return self.wait_ready_proved(process,deadline)
  except (G.DeadlineExceeded,G.StartupReadinessFailure):raise
  except Exception as error:
   raise G.StartupReadinessFailure('Pre-recovery readiness failed: '+str(error)) from error

 def wait_ready_proved(self,process,deadline):
  while time.monotonic()<deadline:
   if (self.runtime.output/'startup-readiness-abort.private.json').exists():
    raise G.StartupReadinessFailure('Observed startup readiness audit failed before recovery; preserve the original capture.')
   p=self.process()
   if p and not isinstance(p.get('Path'),str):
    # Steam can publish the original process before Windows exposes its path.
    # This is not identity proof or an absent process; await metadata inside
    # the same original deadline, without another launch or any Native write.
    time.sleep(.25);continue
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
        if name!='Assembly-CSharp':need(x['informationalVersion']==self.runtime.config.get('productVersion','0.5.0')+'+'+self.runtime.config['sourceSha'],'loaded_source_mismatch')
       if not(self.runtime.output/'loaded-modules.private.json').exists():self.runtime.put('loaded-modules.private.json',dict(passed=True,sourceSha=self.runtime.config['sourceSha'],processId=self.pid,modules=observed))
       try:
        s=G.retry_read_only(lambda:self.call('spherewright_get_session_state',{}),deadline,lambda e:any(k in str(e)for k in ('REQUEST_TIMEOUT','BRIDGE_NOT_READY','BRIDGE_UNAVAILABLE')))
        if not s['gameLoaded']and saved_identity_token(self.runtime.config,s):
         return dict(session=s)
       except RuntimeError as e:
        if not any(k in str(e)for k in ('REQUEST_TIMEOUT','BRIDGE_NOT_READY','BRIDGE_UNAVAILABLE')):raise
   time.sleep(.25)
  raise G.DeadlineExceeded('Native menu/module/lifetime readiness exceeded startup budget')

 def commit(self,role,tool,args):
  self.runtime.put(role+'-intent.private.json',args);self.active='unresolved_submission:'+role
  try: accepted=self.call(tool,args)
  except ToolRefused as e:
   # Native navigation revalidates this exact inspection before registering
   # either an action or its idempotency key.
   navigation_inspection_refused=(tool=='spherewright_commit_move'
    and e.error.get('code')=='ACTION_REJECTED' and e.error.get('retryable') is True
    and e.error.get('message')=='native_navigation_recent_low_speed_inspection_required')
   if e.error.get('code') in ('STALE_STATE','INVALID_REQUEST','USER_CONFIRMATION_REQUIRED','WRITES_DISABLED') or navigation_inspection_refused:
    self.active=None;raise NativePreacceptanceRefusal(tool,e.error)
   raise
  self.runtime.put(role+'-accepted.private.json',accepted)
  need(bool(accepted.get('actionId')),'accepted_action_handle_missing')
  self.active=accepted['actionId'];return self.active

 def wait_original(self,handle):
  interval=getattr(self.runtime,'config',{}).get('actionPollSeconds',.5)
  need(type(interval) in(int,float) and math.isfinite(interval) and .25<=interval<=30,
   'bounded_original_action_poll_interval_required')
  while time.monotonic()<self.c.deadline:
   r=self.call('spherewright_get_action_result',dict(actionId=handle))
   if r['terminal']:
    self.runtime.put('terminal-'+handle+'.private.json',r)
    if r['state']!='outcome_unknown':self.active=None
    return r
   time.sleep(interval)
  raise RuntimeError('original_action_pending_no_replay')

 def prepare_resume(self,ready,deadline):
  c=self.runtime.config;now=dt.datetime.now(dt.timezone.utc)
  if c.get('recoveryProfile')=='exact-paused-space':
   args=dict(resumeToken=saved_identity_token(c,ready['session']),recoveryMode='open_saved_last_exit',
    minimumRecoveryGameTick=c['sourceTick'],expectedRecoveryGameTick=c['sourceTick'])
   p=G.retry_read_only(lambda:self.call('spherewright_prepare_resume_owned_game',args),deadline,
    lambda e:any(k in str(e) for k in ('BRIDGE_NOT_READY','BRIDGE_UNAVAILABLE','REQUEST_TIMEOUT')))
   need(exact_last_exit_echo(c,p),'exact_paused_space_source_echo_changed')
   identity=self.call('spherewright_get_session_state',{})
   need(not identity['gameLoaded'] and identity.get('restartResumeAvailable') is True
    and bool(identity.get('restartResumeToken')),'prepared_saved_data_identity_hint_unproved')
   self.runtime.put('fresh-saved-data-identity.private.json',identity)
   self.runtime.put('fresh-resume-plan.private.json',p);return p
  if c.get('recoveryProfile')=='ordinary-owned-home':
   args=dict(resumeToken=ready['session']['restartResumeToken'],recoveryMode=c['recoveryMode'])
   if c['recoveryMode']=='verified_newer_lastexit':args.update(minimumRecoveryGameTick=c['sourceTick'],expectedRecoveryGameTick=c['sourceTick'],userConfirmedInConversation=c.get('newerLastExitConfirmed') is True)
   p=G.retry_read_only(lambda:self.call('spherewright_prepare_resume_owned_game',args),deadline,
     lambda e:any(k in str(e) for k in ('BRIDGE_NOT_READY','BRIDGE_UNAVAILABLE','REQUEST_TIMEOUT')))
   need(p.get('prepared') and ordinary_owned_resume_echo(c,p),'ordinary_home_source_or_nullable_echo_changed')
   self.runtime.put('fresh-resume-plan.private.json',p);return p
  surface_source=c.get('recoveryProfile')=='successful-outbound-surface'
  target=c.get('surfaceRecoveryTarget')
  if surface_source:
   args=successful_surface_prepare_arguments(c,saved_identity_token(c,ready['session']),now)
  elif c.get('recoveryProfile')=='ordinary-owned-remote':
   args=ordinary_remote_prepare_arguments(c,saved_identity_token(c,ready['session']),now)
  else:
   args=dict(resumeToken=saved_identity_token(c,ready['session']),recoveryMode=c.get('recoveryMode','authorize_remote_primary_recovery'),
    minimumRecoveryGameTick=c['sourceTick'],expectedRecoveryGameTick=c['sourceTick'],
    recoveryDeadlineUtc=(now+dt.timedelta(seconds=c['recoveryWindowSeconds'])).isoformat(),
    recoveryScope='continue_original_finite_task',maximumChargeGameTicks=18000,maximumChargeWallSeconds=300,
    additionalVoyagerGameTicks=c['additionalVoyagerGameTicks'])
  if args['recoveryMode']=='authorize_failed_landing_last_exit':args['priorActionKnownTerminalFailed']=True
  if target is not None and not surface_source:
   args.update(dict(zip(('surfaceRecoveryTargetX','surfaceRecoveryTargetY','surfaceRecoveryTargetZ'),(target[k] for k in 'xyz'))))
  p=G.retry_read_only(lambda:self.call('spherewright_prepare_resume_owned_game',args),deadline,
    lambda e:any(k in str(e) for k in ('BRIDGE_NOT_READY','BRIDGE_UNAVAILABLE','REQUEST_TIMEOUT')))
  need(p['prepared'] is True and p['userConfirmationRequired'] is True and p['commitAllowedNow'] is False
    and isinstance(p.get('planToken'),str) and bool(p['planToken'])
    and isinstance(p.get('confirmationDigest'),str) and bool(p['confirmationDigest'])
    and [b['code'] for b in p['commitBlockers']]==['USER_CONFIRMATION_REQUIRED'],'unexpected_resume_blockers')
  need(resume_admission_echo(c,p)
    and p['expectedPlanetId']==c['planetId'] and p['candidateGameTick']==p['minimumGameTick']==c['sourceTick']
    and p['additionalVoyagerGameTicks']==c['additionalVoyagerGameTicks']
    and p['originalJourneyMaximumGameTicks']==c['originalJourneyMaximumGameTicks']
    and p['effectiveJourneyMaximumGameTicks']==c['originalJourneyMaximumGameTicks']+c['additionalVoyagerGameTicks'],
    'exact_no_loss_source_or_budget_echo_changed')
  if target is not None:
   need(p['surfaceRecoveryMaximumWorkGameTicks']==600 and p['surfaceRecoveryMaximumWallSeconds']==20
     and all(abs(p['surfaceRecoveryTarget'][k]-target[k])<.0001 for k in 'xyz'),'surface_target_disclosure_changed')
  self.runtime.put('fresh-resume-plan.private.json',p);return p

 def commit_resume_once(self,p):
  return self.commit('resume','spherewright_commit_resume_owned_game',dict(planToken=p['planToken'],
    idempotencyKey=str(uuid.uuid4()),userConfirmedInConversation=p['userConfirmationRequired'],confirmationDigest=p['confirmationDigest']))

 def verify_loaded(self,result,deadline):
  c=self.runtime.config;s=self.call('spherewright_get_session_state',{})
  if c.get('recoveryProfile')=='exact-paused-space':
   need(result['succeeded'],'exact_space_open_original_failed')
   self.ctx=dict(sessionId=s['sessionId'],planetId=c['planetId'])
   p=self.player()
   need(paused_space_source(c,s,p,result['actionId']),'exact_paused_space_source_unproved')
   self.space_open_action=result['actionId']
   self.loaded=True;self.runtime.put('loaded-session.private.json',s)
   self.runtime.put('loaded-space-player.private.json',p);return s
  need(result['succeeded'] and s['gameLoaded'] and s['ownedBySpherewright'] and s['writesAllowed']
    and s['localPlanetId']==c['planetId'] and s['gameTick']>=c['sourceTick'],'owned_admission_unproved')
  self.loaded=True;self.ctx=dict(sessionId=s['sessionId'],planetId=c['planetId']);self.runtime.put('loaded-session.private.json',s)
  return s

 def verify_recovery_as_first_work(self,prepared,result,loaded,deadline):
  c=self.runtime.config
  if c.get('firstOperation',{}).get('kind')!='surface-recovery-move':return False
  need(c.get('recoveryProfile')=='successful-outbound-surface','surface_first_work_requires_its_saved_source')
  p=self.player()
  move=(p.get('nativePhysics') or {}).get('resumeSurfaceRecoveryMove') or {}
  while (move.get('state')=='completed_idle' and move.get('resumeActionId')==result.get('actionId')
    and not strict_native_player_idle(p) and time.monotonic()<deadline):
   time.sleep(min(.25,max(0,deadline-time.monotonic())))
   p=self.player()
   move=(p.get('nativePhysics') or {}).get('resumeSurfaceRecoveryMove') or {}
  ok=completed_saved_surface_move(c,result,loaded,p)
  self.runtime.put('actual-progress.private.json',dict(verified=ok,actionId=result['actionId'],
   originalResumeReceipt=result,player=p,nativeSurfaceMove=(p.get('nativePhysics') or {}).get('resumeSurfaceRecoveryMove'),
   workKind='new-surface-recovery-move',oldUnknownReconciled=False,noReplay=True))
  need(ok,'completed_saved_surface_move_unproved_no_replay')
  return True

 def cleanup_known_state(self):
  need(not self.cleanup_entered and self.active is None,'original_cleanup_or_action_unsettled')
  self.cleanup_entered=True;s=self.call('spherewright_get_session_state',{})
  if getattr(self,'preserve_unloaded_startup_only',False):
   need(not s['gameLoaded'],'pre_recovery_failure_cannot_save_or_exit_an_already_loaded_world')
  if s['gameLoaded']:
   need(s['ownedBySpherewright'] and s['writesAllowed'],'unsafe_cleanup_world')
   self.ctx=dict(sessionId=s['sessionId'],planetId=s['localPlanetId'])
   q=self.call('spherewright_prepare_return_to_main_menu',dict(self.ctx,expectedRevision=s['revision']))
   h=self.commit('normal-save-menu','spherewright_commit_return_to_main_menu',dict(self.ctx,planToken=q['planToken'],idempotencyKey=str(uuid.uuid4())))
   need(self.wait_original(h)['succeeded'],'original_save_menu_failed')
   s=self.call('spherewright_get_session_state',{})
  need(not s['gameLoaded'],'native_menu_unproved')
  closed=self.c.close();closed['priorRpcCount']=getattr(self,'prior_rpc_count',0)
  self.runtime.put('client-close.private.json',closed);self.c=None
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
  if isinstance(error,G.StartupReadinessFailure):
   self.preserve_unloaded_startup_only=True
   return not self.loaded
  return isinstance(error,(AcceptedActionFailure,G.DeadlineExceeded))

 def successful_original(self,handle):
  r=self.wait_original(handle)
  if not r.get('succeeded'):raise AcceptedActionFailure('original_action_failed_no_replay:'+handle,r)
  return r

 def player(self):return self.call('spherewright_get_player_state',self.ctx)
 def entity(self,i):return self.call('spherewright_inspect_factory_entity',dict(self.ctx,objectId=i))
 def state(self):
  c=self.runtime.config;s=self.call('spherewright_get_session_state',{})
  if c.get('recoveryProfile')=='exact-paused-space' and self.ctx['planetId']==0:
   need(s['sessionId']==self.ctx['sessionId'] and paused_space_source(c,s,self.player(),self.space_open_action),
    'exact_paused_source_changed_no_generic_write_admission')
  else:
   need(s['gameLoaded'] and s['ownedBySpherewright'] and s['writesAllowed']
    and s['localPlanetId']==self.ctx['planetId'] and s['localPlanetId'] in c.get('authorizedPlanetIds',[c['planetId']]),'owned_world_health_changed')
  spent=c['spentGameTicks']+s['gameTick']-c['sourceTick']
  need(spent+c['returnReserveGameTicks']+c['cleanupReserveGameTicks']<c['maximumCumulativeGameTicks'],'finite_stage_work_reserve_reached')
  return s
 def configure(self,role,entity_id,recipe_id,mode='production',filter_item=0):
  if mode=='sorter-filter':
   q=self.prepare_sorter_filter_when_ready(role,entity_id,filter_item)
   self.successful_original(self.commit(role,'spherewright_commit_configure_building',dict(self.ctx,planToken=q['planToken'],idempotencyKey=str(uuid.uuid4()))))
   return self.entity(entity_id)
  e=self.player() if mode in PLAYER_SETTING_MODES else self.entity(entity_id)
  args=dict(self.ctx,entityId=entity_id,recipeId=recipe_id,mode=mode,
    expectedFactoryStateHash=e['configurationStateHash'] if mode=='sorter-filter' else e['stateHash'])
  if mode=='research':
   t=self.call('spherewright_get_progression_state',self.ctx)
   need(recipe_id==0 and t['currentTechId']>0,'research_requires_current_matrix_technology')
   args['techId']=t['currentTechId'];self.runtime.put(role+'-current-tech-before.private.json',t)
  if mode=='sorter-filter':args['filterItemId']=filter_item
  q=self.call('spherewright_prepare_configure_building',args)
  need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'configuration_not_prepared')
  if mode=='enable-mecha-warper-auto-supply':need(q.get('plannedMechaWarperAutoSupplyEnabled') is True,'warper_setting_cohort_echo_missing_no_commit')
  result=self.successful_original(self.commit(role,'spherewright_commit_configure_building',dict(self.ctx,planToken=q['planToken'],idempotencyKey=str(uuid.uuid4()))))
  if mode=='enable-mecha-warper-auto-supply':need(native_warper_auto_supply_enabled(result),'original_warper_setting_readback_unproved_no_replay')
  return self.player() if mode in PLAYER_SETTING_MODES else self.entity(entity_id)

 def prepare_sorter_filter_when_ready(self,role,entity_id,filter_item):
  end=time.monotonic()+self.runtime.config.get('maximumConfigurationReadinessSeconds',60);attempt=0
  while time.monotonic()<end:
   self.state();e=self.entity(entity_id);attempt+=1
   need(e['itemId'] in(2011,2012) and e.get('pickTargetObjectId',0)>0 and e.get('insertTargetObjectId',0)>0,
    'sorter_readiness_requires_exact_connected_ordinary_sorter')
   need((e.get('filterItemId') or 0)!=filter_item,'sorter_filter_already_applied_no_new_action')
   held=any(b.get('count',0)>0 for b in e.get('buffers',[]))
   self.runtime.put(role+f'-readiness-{attempt:04d}.private.json',e)
   if not held or e.get('inserterStage')=='Inserting':
    try:
     q=self.call('spherewright_prepare_configure_building',dict(self.ctx,entityId=entity_id,recipeId=0,
      mode='sorter-filter',filterItemId=filter_item,expectedFactoryStateHash=e['configurationStateHash']))
    except ToolRefused as error:
     if getattr(self,'active',None) is not None or error.error.get('code') not in('ACTION_REJECTED','STALE_STATE'):raise
    else:
     need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'sorter_configuration_not_native_prepared')
     return q
   # Readiness only schedules a fresh Native prepare; it never substitutes
   # a local stage judgment for admission or clears/redelivers held cargo.
   time.sleep(.07+.03*(attempt%5))
  raise RuntimeError('finite_sorter_phase_readiness_ended_no_action_or_cargo_replay')

 def prepare_first_work(self,loaded,deadline):
  self.first_work_deadline=deadline
  work=self.runtime.config['firstOperation'];mode=work.get('mode','production')
  if work.get('kind')=='storage-transfer':
   need(work.get('direction') in ('storage-to-player','player-to-storage') and type(work.get('count'))is int
    and work['count']>0 and type(work.get('itemId'))is int and work['itemId']>0,'first_storage_transfer_shape_invalid')
   for attempt in range(16):
    need(time.monotonic()<deadline,'original_first_transfer_deadline_exhausted')
    e=self.entity(work['entityId']);p=self.player();self.first_before=dict(player=p,storage=e)
    try:
     q=self.call('spherewright_prepare_transfer',dict(self.ctx,direction=work['direction'],storageEntityId=work['entityId'],
      itemId=work['itemId'],count=work['count'],expectedPlayerStateHash=p['stateHash'],expectedStorageStateHash=e['stateHash']))
     break
    except ToolRefused as error:
     if error.error.get('code')!='STALE_STATE' or self.active is not None or attempt==15:raise
     self.runtime.put(f'first-transfer-unaccepted-stale-{attempt:02d}.private.json',dict(error=error.error,actionAccepted=False))
     time.sleep(.1)
   need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'first_storage_transfer_not_prepared')
   return dict(action_kind='transfer',tool='spherewright_commit_transfer',prepared=q,actualCount=work['count'])
  if work.get('kind')=='resume-research':
   tech=work.get('techId');need(type(tech)is int and tech>0,'first_research_technology_invalid')
   before=self.call('spherewright_get_progression_state',self.ctx);queue=before.get('techQueue') or []
   need(before.get('currentTechId')==0 and bool(queue) and queue[0]==tech
    and bool(before.get('selectionStateHash')),'first_research_paused_queue_changed')
   self.first_before=before
   q=self.call('spherewright_prepare_select_research',dict(self.ctx,techId=tech,
    expectedSelectionStateHash=before['selectionStateHash'],researchPaused=False))
   need(q.get('prepared') is True and q.get('commitAllowedNow') is True and not q.get('commitBlockers')
    and q.get('researchQueueReadbackVersion')==1 and q.get('plannedResearchPaused') is False,
    'first_research_resume_native_echo_unproved')
   self.runtime.put('first-research-resume-plan.private.json',q)
   return dict(action_kind='select-research',tool='spherewright_commit_select_research',prepared=q)
  if work.get('kind')=='generator-fuel':
   p=self.player();e=self.entity(work['entityId']);self.first_before=dict(player=p,generator=e)
   q=self.call('spherewright_prepare_transfer',dict(self.ctx,direction='player-to-generator-fuel',storageEntityId=work['entityId'],
    itemId=work['itemId'],count=work['count'],expectedPlayerStateHash=p['stateHash'],expectedStorageStateHash=e['stateHash']))
   native=q.get('generatorColdStartFuel') or {}
   need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'] and native.get('evidenceVersion')==1
    and native.get('entityId')==work['entityId'] and native.get('itemId')==work['itemId'] and native.get('count')==work['count']
    and native.get('emptyUnlitGenerator') is True and native.get('nativeOperation')=='PlanetFactory.InsertInto',
    'first_generator_fuel_native_identity_or_count_echo_unproved')
   return dict(action_kind='transfer',tool='spherewright_commit_transfer',prepared=q,actualCount=work['count'])
  if work.get('kind')=='refuel':
   amount=work['count']
   for attempt in range(3):
    if attempt:need(time.monotonic()<deadline,'first_refuel_discovery_exceeded_original_startup_deadline')
    p=self.player();self.first_before=p
    try:q=self.call('spherewright_prepare_refuel',dict(self.ctx,itemId=work['itemId'],count=amount,expectedPlayerStateHash=p['stateHash']))
    except ToolRefused as error:
     # This documented Native refusal is an exact capacity disclosure, not
     # an accepted action. Never infer a quantity from unrelated failures.
     match=re.fullmatch(r"DSP's native one-stack fuel transfer will move exactly ([1-9][0-9]*) item\(s\) into grid ([0-9]+); the requested count was ([1-9][0-9]*)\.",error.error.get('message',''))
     if not(work.get('useNativeExactCount') is True and self.active is None and error.error.get('code')=='INVALID_REQUEST'
       and error.error.get('retryable') is True and match and int(match[3])==amount
       and 1<=int(match[1])<=work['count'] and int(match[1])!=amount):raise
     self.runtime.put(f'first-refuel-unaccepted-count-{attempt}.private.json',dict(error=error.error,actionAccepted=False,
       maximumCount=work['count'],nextFreshCount=int(match[1]),noReplay=True))
     amount=int(match[1]);continue
    need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'first_refuel_not_prepared')
    self.first_refuel_count=amount
    return dict(action_kind='refuel',tool='spherewright_commit_refuel',prepared=q,actualCount=amount)
   raise RuntimeError('first_refuel_exact_count_discovery_ended_without_acceptance')
  if work.get('kind')=='saved-home-return':
   p=self.player();self.first_before=p;t=p['spaceTransit']
   q=self.call('spherewright_prepare_interplanetary_flight',dict(self.ctx,destinationPlanetId=t['originalHomePlanetId'],
    expectedPlayerStateHash=p['stateHash'],expectedStarSystemStateHash=t['returnHomeStateHash'],minimumCoreEnergyRatio=.8,
    stoppedSpaceReturnMaximumGameTicks=work['maximumGameTicks'],stoppedSpaceReturnMaximumWallSeconds=work['maximumWallSeconds'],
    savedHomeReturnPredecessorActionId=work['predecessorActionId'],priorHomeReturnKnownTerminalFailed=True))
   need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers']
    and q.get('plannedStoppedSpaceHomeReturn') is True
    and q.get('plannedSavedHomeReturnPredecessorActionId')==work['predecessorActionId'],'saved_home_return_scope_echo_unproved')
   self.runtime.put('first-work-plan.private.json',q)
   return dict(action_kind='interplanetary-flight',tool='spherewright_commit_interplanetary_flight',prepared=q)
  if work.get('kind')=='supply-mecha-warpers':
   need(self.runtime.config.get('recoveryProfile')=='exact-paused-space' and self.ctx['planetId']==0,
    'first_space_supply_requires_exact_paused_source')
   self.first_before=self.player()
   q=self.call('spherewright_prepare_supply_mecha_warpers',dict(self.ctx,count=work['count'],uiTopUp=True,
    expectedPlayerStateHash=self.first_before['stateHash']))
   need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers']
    and q.get('plannedMechaWarperUiTopUp') is True,'first_native_ui_supply_unproved')
   return dict(action_kind='supply_mecha_warpers',tool='spherewright_commit_supply_mecha_warpers',prepared=q)
  if work.get('kind')=='move':
   tolerance=work.get('arrivalTolerance',1.5)
   targets=work.get('candidateTargets') or [work['target']]
   need(isinstance(targets,(list,tuple)) and 1<=len(targets)<=16,'first_move_candidates_unbounded')
   for index,target in enumerate(targets):
    need(time.monotonic()<deadline,'original_first_move_deadline_exhausted')
    p=self.player();self.first_before=p
    args=dict(self.ctx,targetX=target['x'],targetY=target['y'],targetZ=target['z'],arrivalTolerance=tolerance,expectedPlayerStateHash=p['stateHash'])
    if work.get('allowPassiveDrift') is True and p.get('movementState')=='Drift':args['allowPassiveDrift']=True
    if work.get('useNativeNavigation') is True:
     need(3<=tolerance<=5,'first_native_navigation_tolerance_invalid');args['useNativeNavigation']=True
    q=self.call('spherewright_prepare_move',args)
    need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'first_move_not_prepared')
    if work.get('selectObservedDryLanding') is True:
     observed=fully_observed_dry_surface(q) or observed_short_crossing_dry_landing(q,args,p)
     self.runtime.put(f'first-move-candidate-{index:02d}.private.json',dict(arguments=args,prepared=q,dryLandingObserved=observed))
     if not observed:continue
    return dict(action_kind='move',tool='spherewright_commit_move',prepared=q)
   raise RuntimeError('first_move_has_no_observed_dry_landing_candidate')
  e=self.player() if mode in PLAYER_SETTING_MODES else self.entity(work['entityId']);self.first_before=e
  if mode=='production':need(e['recipeId']!=work['recipeId'],'first_recipe_already_applied_no_delta')
  args=dict(self.ctx,entityId=work['entityId'],recipeId=work.get('recipeId',0),mode=mode,expectedFactoryStateHash=e['stateHash'])
  if mode=='research':
   t=self.call('spherewright_get_progression_state',self.ctx)
   need(args['recipeId']==0 and t['currentTechId']>0,'first_research_requires_current_matrix_technology')
   args['techId']=t['currentTechId']
  if mode=='storage-capacity':args.update(storageOperation=work['storageOperation'],filterItemId=work.get('filterItemId',0))
  if mode=='logistics-station-storage':
   station=e.get('logisticsStation') or {};slots=station.get('storageSlots') or []
   wanted=next((row for row in slots if row['index']==work['stationStorageIndex']),None)
   need(wanted is not None and wanted['itemId']==work['stationItemId']
        and wanted['localLogic'].lower()==work.get('beforeStationLocalLogic','none')
        and wanted['remoteLogic'].lower()==work['beforeStationRemoteLogic'],
        'first_station_configuration_baseline_changed_no_replay')
   args.update({key:work[key] for key in ('stationStorageIndex','stationItemId','stationMaximumCount',
       'stationLocalLogic','stationRemoteLogic')})
   args['expectedStationConfigurationStateHash']=station['configurationStateHash']
  q=self.call('spherewright_prepare_configure_building',args)
  need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'first_operation_not_prepared')
  if mode=='enable-mecha-warper-auto-supply':need(q.get('plannedMechaWarperAutoSupplyEnabled') is True,'first_warper_setting_cohort_echo_missing_no_commit')
  return dict(action_kind='configure-building',tool='spherewright_commit_configure_building',prepared=q)
 def commit_first_work_once(self,w):return self.commit('first-work',w['tool'],dict(self.ctx,planToken=w['prepared']['planToken'],idempotencyKey=str(uuid.uuid4())))
 def wait_first_effect(self,handle,work,deadline):
  if work['action_kind']!='interplanetary-flight':return self.wait_original(handle)
  while time.monotonic()<min(deadline,self.c.deadline):
   r=self.call('spherewright_get_action_result',dict(actionId=handle))
   if r['terminal'] or G.paid_native_home_effect(r):
    self.runtime.put('first-native-effect.private.json',r)
    if r['terminal'] and r['state']!='outcome_unknown':self.active=None
    return r
   time.sleep(.1)
  raise G.DeadlineExceeded('No original paid Native control effect before startup deadline; reconcile original without replay')
 def verify_progress(self,w,r):
  c=self.runtime.config['firstOperation'];mode=c.get('mode','production')
  if c.get('kind')=='resume-research':
   native=r.get('researchQueueReadback') or {};queue=self.first_before.get('techQueue') or []
   ok=(r.get('terminal') is True and r.get('succeeded') is True and r.get('actionKind')=='select-research'
    and native.get('beforeQueue')==queue and native.get('afterQueue')==queue and bool(queue) and queue[0]==c['techId']
    and native.get('previousCurrentTechId')==0 and native.get('currentTechId')==c['techId']
    and native.get('researchProgressPreserved') is True and native.get('inventoryPreserved') is True
    and type(native.get('capturedAtGameTick'))is int and native['capturedAtGameTick']==r.get('completedAtGameTick'))
   self.runtime.put('actual-progress.private.json',dict(verified=ok,actionId=r['actionId'],before=self.first_before,
    originalSameTickReceipt=r,noReplay=True));return ok
  if c.get('kind')=='storage-transfer':
   amount=w.get('actualCount');sign=1 if c['direction']=='storage-to-player' else -1
   before=r.get('beforeTargetAmount');after=r.get('afterTargetAmount')
   ok=(type(amount)is int and amount==c['count'] and r.get('terminal')is True and r.get('succeeded')is True
    and r.get('actionKind')=='transfer' and type(before)is int and type(after)is int and min(before,after)>=0
    and after-before==-sign*amount
    and sum(d['delta']for d in r.get('itemDeltas',[])if d['itemId']==c['itemId'])==sign*amount)
   self.runtime.put('actual-progress.private.json',dict(verified=ok,actionId=r['actionId'],exactNativeTransferCount=amount,
    direction=c['direction'],before=self.first_before,after=self.player(),originalSameTickReceipt=r,noReplay=True))
   return ok
  if c.get('kind') in ('refuel','generator-fuel'):
   amount=w.get('actualCount',c['count']);before=r.get('beforeTargetAmount');after=r.get('afterTargetAmount')
   ok=(type(amount)is int and 1<=amount<=c['count'] and r.get('terminal') is True and r.get('succeeded') is True
    and r.get('actionKind')==('refuel' if c['kind']=='refuel' else 'transfer') and type(before)is int and type(after)is int and before>=0 and after-before==amount
    and sum(d['delta'] for d in r.get('itemDeltas',[]) if d['itemId']==c['itemId'])==-amount)
   proof=dict(verified=ok,actionId=r['actionId'],exactNativeTransferCount=amount,
    before=self.first_before,after=self.player(),originalSameTickReceipt=r,noReplay=True)
   if c['kind']=='generator-fuel':proof['generatorAfter']=self.entity(c['entityId'])
   self.runtime.put('actual-progress.private.json',proof);return ok
  if c.get('kind')=='saved-home-return':
   ok=G.paid_native_home_effect(r)
   self.runtime.put('actual-progress.private.json',dict(verified=ok,actionId=r['actionId'],nativeFirstEffect=r.get('nativeHomeReturnFirstEffect'),
    terminalLandingProved=r.get('terminal') is True and r.get('succeeded') is True));return ok
  if c.get('kind')=='supply-mecha-warpers':
   e=self.player();s=self.call('spherewright_get_session_state',{})
   source=read(self.runtime.output/'loaded-session.private.json')
   ok=exact_ui_supply(r,c['count']) and paused_space_source(self.runtime.config,s,e,source['writeQuarantineActionId'])
   self.runtime.put('actual-progress.private.json',dict(verified=ok,actionId=r['actionId'],before=self.first_before,after=e,
    nativeSupply=r.get('mechaWarperSupplyReadback')));return ok
  if c.get('kind')=='move':
   e=self.player();ground=(e.get('nativePhysics') or {}).get('groundContact') or {};velocity=(e.get('nativePhysics') or {}).get('velocity') or {}
   deadline=getattr(self,'first_work_deadline',None)
   # Native can complete a real move while the mecha is still drifting or
   # descending. The next operation receives its own fresh Native admission;
   # requiring ground contact here would block ordinary water-to-land recovery.
   native_navigation=c.get('useNativeNavigation') is True
   completed_move=(r.get('terminal') is True and r.get('state')=='completed'
    and r.get('succeeded') is True and r.get('actionKind')=='move'
    and r.get('sessionId')==self.first_before.get('sessionId')
    and r.get('planetId')==self.first_before.get('planetId'))
   while not native_navigation and completed_move and deadline is not None and not native_movement_order_released(e,self.first_before) and time.monotonic()<deadline:
    time.sleep(min(.25,max(0,deadline-time.monotonic())))
    e=self.player()
   moved=math.dist([self.first_before['position'][k] for k in 'xyz'],[e['position'][k] for k in 'xyz'])
   within=deadline is None or time.monotonic()<=deadline
   ok=r['succeeded'] and moved>1 and within
   if native_navigation:
    native=r.get('nativeSurfaceNavigationReadback') or {}
    ok=ok and native.get('evidenceVersion')==1 and all(native.get(k)is True for k in
     ('nativeNavigationStarted','nativeFlyObserved','nativeArrivalObserved','nativeNavigationReleased'))
    ok=ok and bool(native.get('planBindingHash')) and native.get('planBindingHash')==w['prepared']['expectedStateHash']
    ok=ok and native.get('movementState') in ('Walk','Drift','Fly')
    ok=ok and type(native.get('finalSurfaceDistanceMetres'))in(int,float) and 0<=native['finalSurfaceDistanceMetres']<=c['arrivalTolerance']
   else:ok=ok and completed_move and native_movement_order_released(e,self.first_before)
   self.runtime.put('actual-progress.private.json',dict(verified=ok,actionId=r['actionId'],before=self.first_before,after=e,
    movedMetres=moved,originalStartupDeadlineRespected=within));return ok
  e=self.player() if mode in PLAYER_SETTING_MODES else self.entity(c['entityId'])
  if mode=='enable-mecha-construction-drones':
   ok=r['succeeded'] and self.first_before['constructionDrones']['enabled'] is False and e['constructionDrones']['enabled'] is True
  elif mode=='enable-mecha-warper-auto-supply':ok=native_warper_auto_supply_enabled(r)
  elif mode in ('disable-mecha-research-auto-supply','enable-mecha-research-auto-supply'):
   desired=mode=='enable-mecha-research-auto-supply'
   # Native proves the empty buffer in the same-tick setting receipt. A later
   # observation may already contain points from the newly enabled research.
   ok=r['succeeded'] and self.first_before['autoManageResearchItems'] is not desired and e['autoManageResearchItems'] is desired
  elif mode=='storage-capacity':
   before=self.first_before.get('storageConfiguration') or {};after=e.get('storageConfiguration') or {}
   filters=after.get('gridFilterItemIds') or []
   ok=r['succeeded'] and bool(r.get('storageConfigurationReadback')) and bool(filters)
   ok=ok and all(x==c['filterItemId'] for x in filters) and before!=after
  elif mode=='logistics-station-storage':
   before=self.first_before.get('logisticsStation') or {};after=e.get('logisticsStation') or {}
   old=next((x for x in before.get('storageSlots',[]) if x['index']==c['stationStorageIndex']),{})
   new=next((x for x in after.get('storageSlots',[]) if x['index']==c['stationStorageIndex']),{})
   ok=r['succeeded'] and before.get('configurationStateHash')!=after.get('configurationStateHash')
   ok=ok and new.get('itemId')==c['stationItemId'] and new.get('maximumCount')==c['stationMaximumCount']
   ok=ok and new.get('localLogic','').lower()==c['stationLocalLogic'] and new.get('remoteLogic','').lower()==c['stationRemoteLogic']
   ok=ok and old.get('itemId')==new.get('itemId') and old.get('count')==new.get('count') and old.get('inc')==new.get('inc')
  else:ok=r['succeeded'] and e['recipeId']==c['recipeId'] and self.first_before['recipeId']!=e['recipeId']
  self.runtime.put('actual-progress.private.json',dict(verified=ok,actionId=r['actionId'],before=self.first_before,after=e))
  return ok
