"""Replace only a stopped caller; continue the exact healthy live session without Load/Save."""
from pathlib import Path
import sys,datetime as dt,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent));sys.dont_write_bytecode=True
from evidence import read,sha,need
from runtime import Runtime
from factory import Factory
from mcp_client import Client

def main():
    config,config_sha,previous,output=sys.argv[1:];prior=Path(previous)
    r=Runtime(config,config_sha,output);a=Factory(r);c=r.config
    if (prior/'client-close.private.json').exists():
        old=read(prior/'client-close.private.json');need(old['stdoutEofObserved'] and old['stderrEofObserved'],'old_caller_not_closed')
    else:
        old=read(prior/'caller-handoff.private.json');need(old['callerStopped'] and old['noActiveGameAction'] and old['gameProcessRetained'],'old_caller_handoff_unproved')
    origin=Path(c.get('liveSessionOrigin',str(prior)))
    prepared=read(origin/'fresh-resume-plan.private.json');deadline=dt.datetime.fromisoformat(prepared['effectiveRecoveryDeadlineUtc'].replace('Z','+00:00'))
    prior_count=old.get('priorRpcCount',0)+old['requestCount']
    a.prior_rpc_count=prior_count
    seconds=(deadline-dt.datetime.now(dt.timezone.utc)).total_seconds();remaining=c['maximumRpc']-prior_count
    need(seconds>60 and remaining>0,'original_finite_caller_allowance_ended');r.cohort()
    a.c=Client(Path(c['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'client',maximum=remaining,seconds=seconds,
        total_stdout_limit=c.get('maximumStdoutBytes',64*1024*1024),total_stderr_limit=c.get('maximumStderrBytes',1024*1024))
    try:
        _,tools,_,_=a.c.initialize();a.schemas={t['name']:t['inputSchema'] for t in tools}
        original=read(origin/'loaded-session.private.json');s=a.call('spherewright_get_session_state',{})
        need(s['gameLoaded'] and s['ownedBySpherewright'] and s['writesAllowed'] and s['sessionId']==original['sessionId']
            and s['localPlanetId']==original['localPlanetId'],'exact_healthy_live_session_changed')
        a.ctx=dict(sessionId=s['sessionId'],planetId=s['localPlanetId']);a.pid=read(origin/'process-observed.private.json')['Id'];a.loaded=True
        process=a.process();need(process is not None and process['Id']==a.pid,'original_live_process_changed')
        r.put('attached-existing-session.private.json',dict(passed=True,sessionId=s['sessionId'],gameProcessId=a.pid,
            gameTick=s['gameTick'],priorRpcCount=prior_count,remainingRpc=remaining,originalDeadlineUtc=deadline.isoformat(),
            noLoad=True,noSave=True,noLaunch=True,noTickRefund=True,sourceSha=c['sourceSha']))
        try:a.execute_plan(c['initialSteps'],'attached-initial')
        except Exception as error:
            r.put('attached-initial-failure.private.json',dict(error=str(error),activeOriginalAction=a.active))
            if a.active is not None:raise
        a.await_next_plan()
    finally:
        if a.c is not None:
            closed=a.c.close();closed['priorRpcCount']=prior_count;r.put('client-close.private.json',closed)

if __name__=='__main__':main()
