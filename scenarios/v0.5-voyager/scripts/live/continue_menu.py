"""Continue one unaccepted menu recovery inside its original launch clock."""
from pathlib import Path
import sys,time,datetime as dt
ROOT=Path(__file__).resolve().parent;sys.path[:0]=[str(ROOT),str(ROOT.parent)]
from runtime import Runtime
from factory import Factory
from mcp_client import Client
from evidence import read,need

def main():
 config,digest,origin,output=sys.argv[1:];origin=Path(origin);r=Runtime(config,digest,output);a=Factory(r);c=r.config
 report=read(origin/'startup-report.private.json');closed=read(origin/'client-close.private.json')
 need(not report['passed'] and not report['unresolved_commit'] and report['first_action_id'] is None
      and not (origin/'resume-accepted.private.json').exists() and closed['normalEof'],'only unaccepted original menu may continue')
 launch=read(origin/'launch-intent.private.json');start=dt.datetime.fromisoformat(launch['startedAtUtc']);elapsed=(dt.datetime.now(dt.timezone.utc)-start).total_seconds()
 need(0<=elapsed<240,'original startup has insufficient remaining time')
 a.prior_rpc_count=closed.get('priorRpcCount',c['priorRpcCount'])+closed['requestCount'];a.pid=read(origin/'process-observed.private.json')['Id']
 r.cohort();a.c=Client(Path(c['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'client',maximum=c['maximumRpc']-a.prior_rpc_count,seconds=c['maximumWallSeconds']-elapsed)
 try:
  _,tools,_,_=a.c.initialize();a.schemas={t['name']:t['inputSchema']for t in tools};s=a.call('spherewright_get_session_state',{})
  need(not s['gameLoaded'] and a.process()['Id']==a.pid,'original idle-menu process changed')
  deadline=time.monotonic()+300-elapsed;q=a.prepare_resume(dict(session=s),deadline);result=a.successful_original(a.commit_resume_once(q));s=a.verify_loaded(result,deadline)
  work=a.prepare_first_work(s,deadline);result=a.successful_original(a.commit_first_work_once(work));verified=a.verify_progress(work,result)
  total=(dt.datetime.now(dt.timezone.utc)-start).total_seconds();r.put('original-menu-startup-work.private.json',dict(verified=verified,original=result,elapsedFromOriginalLaunchSeconds=total,withinOriginal300Seconds=total<300,noStartupClockReset=True))
  need(verified and total<300,'original startup did not reach proven work in time');a.continue_prepared_work(result)
 finally:
  if a.c is not None:
   closed=a.c.close();closed['priorRpcCount']=a.prior_rpc_count;r.put('client-close.private.json',closed)

if __name__=='__main__':main()
