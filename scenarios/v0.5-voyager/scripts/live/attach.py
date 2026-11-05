"""Replace only a stopped caller; continue the exact healthy live session without Load/Save."""
from pathlib import Path
import json
import sys,datetime as dt,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent));sys.dont_write_bytecode=True
from evidence import read,sha,need,actual_prior_rpc_count
from runtime import Runtime
from factory import Factory
from mcp_client import Client
from contracts import strict_native_player_idle,validate_steps,validate_native_calls
import startup_to_action as gate

def main():
    config,config_sha,previous,output=sys.argv[1:];prior=Path(previous)
    r=Runtime(config,config_sha,output);a=Factory(r);c=r.config
    if (prior/'client-close.private.json').exists():
        old=read(prior/'client-close.private.json');need(old['normalEof'] and old['processExitCode']==0 and old['readerThreadsStopped'],'old_caller_not_closed')
    else:
        old=read(prior/'caller-handoff.private.json');need(old['callerStopped'] and old['noActiveGameAction'] and old['gameProcessRetained'],'old_caller_handoff_unproved')
    origin=Path(c.get('liveSessionOrigin',str(prior)))
    prepared=read(origin/'fresh-resume-plan.private.json')
    if c.get('recoveryProfile')=='ordinary-owned-home':
        need(prepared['recoveryMode']==c['recoveryMode'] and prepared.get('effectiveRecoveryDeadlineUtc') is None,'ordinary_home_native_deadline_not_applicable')
        events=[json.loads(line) for line in (origin/'timings.private.jsonl').read_text(encoding='utf-8').splitlines()]
        dispatched=[e for e in events if e.get('event')=='launch_dispatched'];need(len(dispatched)==1,'original_launch_clock_unproved')
        deadline=dt.datetime.fromisoformat(dispatched[0]['atUtc'].replace('Z','+00:00'))+dt.timedelta(seconds=c['maximumWallSeconds'])
    else:deadline=dt.datetime.fromisoformat(prepared['effectiveRecoveryDeadlineUtc'].replace('Z','+00:00'))
    prior_count=actual_prior_rpc_count(prior,old)
    if prior_count!=old.get('priorRpcCount',0)+old['requestCount']:
        r.put('inherited-rpc-accounting-correction.private.json',dict(originalHandoffRetained=True,
            correctedActualPriorRpcCount=prior_count,sourceAttachment=str(prior/'attached-existing-session.private.json'),
            noRefund=True,noNativeJournalEdit=True))
    a.prior_rpc_count=prior_count
    seconds=(deadline-dt.datetime.now(dt.timezone.utc)).total_seconds();remaining=c['maximumRpc']-prior_count
    need(seconds>60 and remaining>0,'original_finite_caller_allowance_ended');r.cohort()
    a.c=Client(Path(c['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'client',maximum=remaining,seconds=seconds,
        total_stdout_limit=c.get('maximumStdoutBytes',64*1024*1024),total_stderr_limit=c.get('maximumStderrBytes',1024*1024))
    try:
        _,tools,_,_=a.c.initialize();a.schemas={t['name']:t['inputSchema'] for t in tools}
        validate_steps(c['initialSteps']);validate_native_calls(c['initialSteps'],a.schemas)
        original=read(origin/'loaded-session.private.json');s=a.call('spherewright_get_session_state',{})
        expected_planet=c.get('attachmentPlanetId',original['localPlanetId'])
        if expected_planet!=original['localPlanetId']:
            proof=c['completedPlanetTransition'];need(sha(proof['path'])==proof['sha256'],'original_arrival_receipt_changed')
            arrival=read(proof['path']);native=arrival.get('voyagerFlightReadback') or {}
            need(arrival['terminal'] and arrival['succeeded'] and arrival['sessionId']==original['sessionId']
                and native.get('actualPlanetId')==expected_planet and native.get('nativeExitObserved') is True
                and expected_planet in c['authorizedPlanetIds'],'completed_native_planet_transition_unproved')
        need(s['gameLoaded'] and s['ownedBySpherewright'] and s['writesAllowed'] and s['sessionId']==original['sessionId']
            and s['localPlanetId']==expected_planet,'exact_healthy_live_session_changed')
        a.ctx=dict(sessionId=s['sessionId'],planetId=s['localPlanetId']);a.pid=read(origin/'process-observed.private.json')['Id'];a.loaded=True
        need(strict_native_player_idle(a.player()),'current_native_idle_or_rts_observation_unproved')
        process=a.process();need(process is not None and process['Id']==a.pid,'original_live_process_changed')
        r.put('attached-existing-session.private.json',dict(passed=True,sessionId=s['sessionId'],gameProcessId=a.pid,
            gameTick=s['gameTick'],priorRpcCount=prior_count,remainingRpc=remaining,originalDeadlineUtc=deadline.isoformat(),
            noLoad=True,noSave=True,noLaunch=True,noTickRefund=True,noStartupClockReset=True,sourceSha=c['sourceSha']))
        if c.get('continueRefusedStartup') is True:
            report=read(origin/'startup-report.private.json')
            need(prior==origin and not report['passed'] and not report['unresolved_commit']
                and report.get('first_action_id') is None and not (origin/'first-work-accepted.private.json').exists(),
                'only_unaccepted_first_work_may_continue_original_startup')
            launch=read(origin/'launch-intent.private.json')
            elapsed=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(launch['startedAtUtc'])).total_seconds()
            need(0<=elapsed<gate.LIMIT_SECONDS,'original_startup_expired_preservation_only')
            started=time.monotonic()-elapsed;work=a.prepare_first_work(s,started+gate.LIMIT_SECONDS)
            need(work.get('action_kind') in gate.ACTUAL_WORK_KINDS and time.monotonic()<started+gate.LIMIT_SECONDS,
                'original_startup_first_work_no_longer_admitted')
            result=a.successful_original(a.commit_first_work_once(work));verified=a.verify_progress(work,result)
            elapsed=time.monotonic()-started
            r.put('corrected-startup-first-work.private.json',dict(verified=verified,original=result,elapsedFromOriginalLaunchSeconds=elapsed,
                withinOriginal300Seconds=elapsed<gate.LIMIT_SECONDS,originalStartupFailureRetained=True,noStartupClockReset=True))
            if not verified or elapsed>=gate.LIMIT_SECONDS:
                a.cleanup_known_state();raise RuntimeError('corrected_original_first_work_not_within_startup_gate')
            a.continue_prepared_work(result);return
        try:a.execute_plan(c['initialSteps'],'attached-initial')
        except Exception as error:
            a.record_plan_failure('attached-initial-failure.private.json',error)
            if a.active is not None:raise
        a.await_next_plan()
    finally:
        if a.c is not None:
            closed=a.c.close();closed['priorRpcCount']=prior_count;r.put('client-close.private.json',closed)

if __name__=='__main__':main()
