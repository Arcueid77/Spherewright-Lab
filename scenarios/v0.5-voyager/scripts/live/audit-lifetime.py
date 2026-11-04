"""Observe all application job owners; never assign or modify a job."""
from evidence import need,put,read,sha
from lifetime_contract import qualifies,cleanup_groups,terminating_groups
from job_lifetime_capture import capture
from pathlib import Path
import copy,json,sys

D=Path(sys.argv[1]).resolve();E=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else D
E.mkdir(parents=True,exist_ok=True)
raw=capture(read(D/'process-observed.private.json'))
put(E/'job-memberships.raw.private.json',raw)
need(qualifies(raw),'Complete application-owned job separation is unproved; no recovery or relaunch.')
groups=cleanup_groups(raw)
for target in ('game','steam'):
 for value in (True,None):
  bad=copy.deepcopy(raw);key=groups[0]['objectKey']
  next(j for j in bad['queriedJobs'] if j['objectKey']==key)['memberships'][target]=value
  need(not qualifies(bad),'Unsafe or unknown target membership must refuse admission.')
owned=next(j for j in raw['enumeratedJobs'] if set(j['ownerPids'])&set(raw['scopePids']))
missing=copy.deepcopy(raw);missing['queriedJobs']=[j for j in missing['queriedJobs'] if j['objectKey']!=owned['objectKey']]
missing['unresolvedJobObjects'].append(owned)
need(not qualifies(missing),'An unresolved application-owned job must refuse admission.')
put(D/'game-lifetime-qualification.private.json',dict(passed=True,gameProcessId=raw['gameProcessId'],
 steamProcessId=raw['steamProcessId'],basis='complete_application_owned_job_inventory_and_membership',
 outsideObservedCallerTerminatingJobs=True,completeCallerOwnedJobQueries=True,callerCleanupGroups=len(groups),
 callerCleanupLimitFlags=sorted(j['limitFlags'] for j in terminating_groups(raw)),
 rawSha256=sha(E/'job-memberships.raw.private.json'),rawEvidencePath=str(E/'job-memberships.raw.private.json'),
 scopeRootPid=raw['scopeRootPid'],scopeProcessCount=len(raw['scopePids']),fixedGroupCountRequired=False,
 unrelatedSystemJobObjectsUnresolved=len(raw['unresolvedJobObjects']),allSystemJobsExamined=False,
 gameMemoryReads=0,jobAssignments=0,jobLimitChanges=0,actualGameRestarted=False,gameCalls=0,
 limitation='Unrelated system-owned jobs and OS/Steam termination remain outside this certificate.',
 nativeReferences=['https://learn.microsoft.com/en-us/windows/win32/api/jobapi/nf-jobapi-isprocessinjob']))
put(D/'lifetime-ready.private.json',dict(passed=True,proofSha256=sha(D/'game-lifetime-qualification.private.json')))
print(json.dumps(dict(passed=True,completeObservedApplicationJobCoverage=True,gameCalls=0)))
