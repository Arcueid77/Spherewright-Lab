"""Normally save a fresh exact Native-paused quarantine; never resume it."""
from pathlib import Path
import sys,uuid
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from runtime import Runtime
from driver import Live
from mcp_client import Client
from evidence import read,need,actual_prior_rpc_count

def main():
 config,digest,origin,output=sys.argv[1:];origin=Path(origin)
 handoff=read(origin/'caller-handoff.private.json')
 need(handoff['callerStopped'] and handoff['noActiveGameAction'] and handoff.get('preservationOnlyQuarantined'),
      'only_exact_quarantined_preservation_handoff_allowed')
 r=Runtime(config,digest,output);r.cohort();a=Live(r);c=r.config
 a.prior_rpc_count=actual_prior_rpc_count(origin,handoff)
 game_origin=Path(c['liveSessionOrigin']);a.pid=read(game_origin/'process-observed.private.json')['Id']
 a.c=Client(Path(c['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'client',maximum=50,seconds=180)
 try:
  a.c.initialize();s=a.call('spherewright_get_session_state',{});original=read(game_origin/'loaded-session.private.json')
  need(s['gameLoaded'] and s['ownedBySpherewright'] and not s['writesAllowed']
       and s['sessionId']==original['sessionId'] and s['localPlanetId']==c['planetId']
       and s.get('writeQuarantineActionId')==c['expectedPreservationQuarantineActionId'],'exact_native_quarantine_changed')
  a.ctx=dict(sessionId=s['sessionId'],planetId=s['localPlanetId']);p=a.player();later=a.call('spherewright_get_session_state',{})
  need('native_paused_not_execution_ready' in (p.get('nativeLocalControlEnergy') or {}).get('blockers',[])
       and later['gameTick']==s['gameTick'],'paused_preservation_cut_unproved')
  r.put('actual-native-paused-quarantine.private.json',dict(session=s,player=p,noPhysicalIdleClaim=True,noResume=True))
  q=a.call('spherewright_prepare_save',dict(a.ctx,expectedRevision=later['revision'],preserveQuarantinedProgress=True))
  need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'] and q.get('preservesQuarantine') is True
       and q.get('preservationGameTick')==s['gameTick'],'exact_preservation_save_not_prepared')
  r.put('fresh-quarantine-preservation-plan.private.json',q)
  handle=a.commit('quarantine-preserve','spherewright_commit_save',dict(a.ctx,planToken=q['planToken'],idempotencyKey=str(uuid.uuid4())))
  result=a.wait_original(handle);need(result['terminal'] and result['succeeded'],'original_preservation_save_not_proved')
  floor=s['gameTick'];r.put('current-quarantine-save-proof.private.json',dict(passed=True,minimumCurrentTick=floor,
      originalQuarantineRetained=True,noResume=True,noReplay=True,noOlderSourceLoaded=True))
 finally:
  closed=a.c.close();closed['priorRpcCount']=a.prior_rpc_count;r.put('client-close.private.json',closed);a.c=None
 a.normal_close_current_process()
 m=read(r.output/'after-normal-close-complete-backup/manifest.private.json')
 need(m['latest']['primary']['gameTick']>=floor and m['latest']['lastExit']['gameTick']>=floor,
      'normal_current_quarantine_progress_not_completely_preserved')
 r.put('quarantined-preservation-complete.private.json',dict(passed=True,minimumCurrentTick=floor,
     primaryTick=m['latest']['primary']['gameTick'],lastExitTick=m['latest']['lastExit']['gameTick'],
     originalQuarantineRetained=True,noResume=True,noReplay=True))

if __name__=='__main__':main()
