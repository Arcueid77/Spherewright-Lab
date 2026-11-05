"""Normal OS quit after an exact known stopped, unwarped failed Voyager leg.

This neither reloads its older checkpoint nor claims grounded/zero-tail idle.
The full current space state must be present in the new normal LastExit.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent));sys.dont_write_bytecode=True
from evidence import read,sha,need
from runtime import Runtime
from driver import Live
from mcp_client import Client

config,config_sha,original_output,action_id,output=sys.argv[1:]
origin=Path(original_output);prior=read(origin/'client-close.private.json')
need(prior['normalEof'] and prior['processExitCode']==0,'original_writer_not_closed')
original=read(origin/f'terminal-{action_id}.private.json')
need(original['actionKind']=='interplanetary-flight' and original['terminal'] and not original['succeeded']
 and original['state']=='recovery_required','exact_known_failed_leg_required')
r=Runtime(config,config_sha,output);r.cohort();a=Live(r)
a.pid=read(origin/'process-observed.private.json')['Id']
a.c=Client(Path(r.config['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'client',maximum=12,seconds=45)
try:
    a.c.initialize();s=a.call('spherewright_get_session_state',{});current=a.call('spherewright_get_action_result',dict(actionId=action_id))
    r.put('actual-current-session.private.json',s);r.put('actual-original-terminal.private.json',current)
    v=current.get('voyagerFlightReadback') or {}
    need(s['gameLoaded'] and s['ownedBySpherewright'] and s['sessionId']==original['sessionId'],
        'same_owned_world_unproved')
    need(current['terminal'] and current['state']=='recovery_required' and not current['succeeded'],
        'current_original_known_failure_unproved')
    if r.config.get('stoppedSpaceHomeReturnRole'):
        role=r.config['stoppedSpaceHomeReturnRole']
        plan=read(origin/(role+'-plan.private.json'));accepted=read(origin/(role+'-accepted.private.json'))
        need(plan.get('plannedStoppedSpaceHomeReturn') is True and accepted['actionId']==action_id,
            'exact_native_home_return_plan_or_original_handle_changed')
        p=a.call('spherewright_get_player_state',dict(sessionId=s['sessionId'],planetId=s['localPlanetId'] or 0))
        later=a.call('spherewright_get_session_state',{})
        paused=(p.get('spaceTransit') or {}).get('nativePaused') is True or \
            'native_paused_not_execution_ready' in (p.get('nativeLocalControlEnergy') or {}).get('blockers',[])
        need(paused and later['sessionId']==s['sessionId'] and later['gameTick']==s['gameTick']
            and later['localPlanetId']==s['localPlanetId'],'same_native_paused_return_failure_cut_unproved')
        r.put('actual-native-paused-player.private.json',p)
    else:
        need(s['localPlanetId'] is None and v.get('bindingVerified') is True and v.get('nativeExitObserved') is True
        and v.get('nativeWarpState')==0 and v.get('nativeWarpCommand') is False
        and v.get('entryAttempted') is False and v.get('nativeWarpersConsumed')==0
        and v.get('actualPlanetId') is None and v.get('actualStarId')==v.get('originStarId'),
        'original_native_stop_and_zero_warp_consumption_unproved')
    floor=s['gameTick'];r.put('normal-current-space-close-intent.private.json',dict(originalActionId=action_id,
        minimumCurrentLastExitTick=floor,noCheckpointReload=True,noReplay=True,noGroundedIdleClaim=True,forceKill=False))
finally:
    r.put('client-close.private.json',a.c.close());a.c=None
a.normal_close_current_process()
manifest=read(r.output/'after-normal-close-complete-backup/manifest.private.json')
need(manifest['latest']['lastExit']['gameTick']>=floor,'normal_current_space_LastExit_not_preserved_no_rollback')
r.put('current-space-preservation-complete.private.json',dict(passed=True,originalActionId=action_id,
    lastExitTick=manifest['latest']['lastExit']['gameTick'],minimumTick=floor,checkpointReloaded=False,
    originalFailureRetained=True,progressRolledBack=False))
print('Current stopped space state normally saved/closed and completely backed up; no older checkpoint loaded.')
