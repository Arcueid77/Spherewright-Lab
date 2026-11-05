"""Continue one proven unopened original launch inside its unchanged startup clock."""
from pathlib import Path
import sys,datetime as dt,time,subprocess
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent));sys.dont_write_bytecode=True
from evidence import read,sha,need,actual_prior_rpc_count,put
from runtime import Runtime
from factory import Factory
from mcp_client import Client
import startup_to_action as gate

config,config_sha,previous,output=sys.argv[1:5];prior=Path(previous);r=Runtime(config,config_sha,output);a=Factory(r);c=r.config
closed=read(prior/'client-close.private.json');report=read(prior/'startup-report.private.json');launch=read(prior/'launch-intent.private.json')
need(closed['normalEof'] and closed['processExitCode']==0 and not report['passed'] and not report['unresolved_commit']
 and report.get('first_action_id') is None and not list(prior.glob('*accepted.private.json')) and not (prior/'fresh-resume-plan.private.json').exists(),'only_unopened_unaccepted_original_may_continue')
origin=dt.datetime.fromisoformat(launch['startedAtUtc']);elapsed=(dt.datetime.now(dt.timezone.utc)-origin).total_seconds()
need(0<=elapsed<gate.LIMIT_SECONDS,'original_startup_clock_exhausted_no_relaunch');started=time.monotonic()-elapsed;deadline=started+gate.LIMIT_SECONDS
r.cohort();r.verify_revision_stamps();a.dispatch_utc=origin;a.prior_rpc_count=actual_prior_rpc_count(prior,closed)
if len(sys.argv)>6:
 previous_caller=Path(sys.argv[6]);last=read(previous_caller/'client-close.private.json')
 need(last['normalEof'] and not (previous_caller/'fresh-resume-plan.private.json').exists(),'previous_unopened_caller_not_closed')
 a.prior_rpc_count=actual_prior_rpc_count(previous_caller,last)
a.c=Client(Path(c['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'client',maximum=c['maximumRpc']-a.prior_rpc_count,seconds=c['maximumWallSeconds'],
 total_stdout_limit=c.get('maximumStdoutBytes',64*1024*1024),total_stderr_limit=c.get('maximumStderrBytes',1024*1024))
try:
 _,tools,_,_=a.c.initialize();a.schemas={t['name']:t['inputSchema']for t in tools};a.validate_plan(c['initialSteps'])
 p=a.process();need(p is not None and isinstance(p.get('Path'),str) and Path(p['Path']).resolve()==(Path(c['dspRoot'])/'DSPGAME.exe').resolve()
  and dt.datetime.fromisoformat(p['startedUtc'])>=origin-dt.timedelta(seconds=1),'original_process_identity_unproved')
 a.pid=p['Id'];a.process_record=p;r.put('process-observed.private.json',p);r.put('game-job-proof.private.json',dict(processId=a.pid))
 if len(sys.argv)>5:
  source=Path(sys.argv[5]);life=read(source/'game-lifetime-qualification.private.json')
  need(life['passed'] and life['gameProcessId']==a.pid and read(source/'process-observed.private.json')==p,'external_original_lifetime_identity_changed')
  r.put('game-lifetime-qualification.private.json',life);r.put('lifetime-ready.private.json',dict(passed=True,reusedExternalProofPath=str(source/'game-lifetime-qualification.private.json'),sha256=sha(source/'game-lifetime-qualification.private.json')))
 else:
  audit=subprocess.run([sys.executable,str(ROOT/'audit-lifetime.py'),str(r.output)],capture_output=True,text=True,timeout=45)
  r.put('lifetime-audit-process.private.json',dict(exitCode=audit.returncode,stdout=audit.stdout,stderr=audit.stderr));need(audit.returncode==0,'actual_lifetime_unproved')
 ready=a.wait_ready(None,deadline);need(time.monotonic()<deadline,'original_startup_clock_exhausted')
 q=a.prepare_resume(ready,deadline);r.put('unopened-original-continuation.private.json',dict(passed=True,originalLaunchPath=str(prior/'launch-intent.private.json'),
  elapsedBeforeRecovery=time.monotonic()-started,originalStartupFailureRetained=True,noLaunch=True,noStartupClockReset=True))
 result=a.successful_original(a.commit_resume_once(q));loaded=a.verify_loaded(result,deadline);work=a.prepare_first_work(loaded,deadline)
 need(work['action_kind']in gate.ACTUAL_WORK_KINDS and time.monotonic()<deadline,'original_first_work_clock_exhausted')
 result=a.successful_original(a.commit_first_work_once(work));verified=a.verify_progress(work,result);elapsed=time.monotonic()-started
 r.put('corrected-startup-first-work.private.json',dict(verified=verified,elapsedFromOriginalLaunchSeconds=elapsed,withinOriginal300Seconds=elapsed<300,
  original=result,originalStartupFailureRetained=True,noStartupClockReset=True,noLaunch=True))
 need(verified and elapsed<300,'original_launch_did_not_start_real_work_within_unchanged_gate')
 a.continue_prepared_work(result)
finally:
 if a.c is not None:
  value=a.c.close();value['priorRpcCount']=a.prior_rpc_count;r.put('client-close.private.json',value)
