from evidence import need,put,read,sha
from lifetime_contract import qualifies as qualify,terminating_groups
from pathlib import Path
import os,sys,json,subprocess,datetime as dt
D=Path(sys.argv[1]).resolve()
E=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else D
E.mkdir(parents=True,exist_ok=True)
import ctypes
from ctypes import wintypes as w
K=ctypes.WinDLL('kernel32',use_last_error=True);N=ctypes.WinDLL('ntdll')
P=ctypes.c_void_p;U=ctypes.c_size_t
K.GetCurrentProcess.restype=w.HANDLE
K.CreateJobObjectW.argtypes=[P,w.LPCWSTR];K.CreateJobObjectW.restype=w.HANDLE
K.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];K.OpenProcess.restype=w.HANDLE
K.CloseHandle.argtypes=[w.HANDLE];K.CloseHandle.restype=w.BOOL
K.DuplicateHandle.argtypes=[w.HANDLE,w.HANDLE,w.HANDLE,ctypes.POINTER(w.HANDLE),w.DWORD,w.BOOL,w.DWORD];K.DuplicateHandle.restype=w.BOOL
K.IsProcessInJob.argtypes=[w.HANDLE,w.HANDLE,ctypes.POINTER(w.BOOL)];K.IsProcessInJob.restype=w.BOOL
K.QueryInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,P,w.DWORD,ctypes.POINTER(w.DWORD)];K.QueryInformationJobObject.restype=w.BOOL
N.NtQuerySystemInformation.argtypes=[ctypes.c_int,P,w.ULONG,ctypes.POINTER(w.ULONG)];N.NtQuerySystemInformation.restype=ctypes.c_long
class Entry(ctypes.Structure):
    _fields_=[('object',P),('pid',U),('handle',U),('access',w.ULONG),('backtrace',w.USHORT),('type',w.USHORT),('attributes',w.ULONG),('reserved',w.ULONG)]
class Basic(ctypes.Structure):
    _fields_=[('processTime',ctypes.c_longlong),('jobTime',ctypes.c_longlong),('flags',w.DWORD),('minWs',U),('maxWs',U),('activeCount',w.DWORD),('affinity',U),('priority',w.DWORD),('scheduling',w.DWORD)]
class IO(ctypes.Structure):_fields_=[(n,ctypes.c_ulonglong)for n in ('readCount','writeCount','otherCount','readBytes','writeBytes','otherBytes')]
class Extended(ctypes.Structure):_fields_=[('basic',Basic),('io',IO),('processMemory',U),('jobMemory',U),('peakProcess',U),('peakJob',U)]
def in_job(process,job):
    answer=w.BOOL()
    if not K.IsProcessInJob(process,job,ctypes.byref(answer)):return None
    return bool(answer.value)
current=K.GetCurrentProcess();probe=K.CreateJobObjectW(None,None)
need(bool(probe),'Empty metadata type probe could not be created.')
try:
    length=w.ULONG();size=1024*1024
    for _ in range(8):
        need(size<=32*1024*1024,'OS handle metadata exceeds finite bound.')
        buffer=ctypes.create_string_buffer(size)
        status=N.NtQuerySystemInformation(64,buffer,size,ctypes.byref(length))
        if status==0:break
        need(status in (-1073741820,-1073741789),'OS handle metadata query refused.')
        size=max(size*2,int(length.value)+65536)
    else:raise RuntimeError('OS handle snapshot did not stabilize within bound.')
    count=U.from_buffer(buffer,0).value
    need(0<count<=800000 and 2*ctypes.sizeof(U)+count*ctypes.sizeof(Entry)<=size,'Malformed OS handle metadata.')
    entries=(Entry*count).from_buffer(buffer,2*ctypes.sizeof(U))
    types=[int(e.type)for e in entries if int(e.pid)==os.getpid() and int(e.handle)==int(probe)]
    need(len(types)==1,'Own empty-job object type was not identified.')
    jobtype=types[0]
    raw=subprocess.check_output(['powershell.exe','-NoProfile','-NonInteractive','-Command',
        "Get-CimInstance Win32_Process|Select-Object Name,ProcessId,ParentProcessId|ConvertTo-Json -Compress"],text=True,timeout=20)
    processes=json.loads(raw);byid={int(p['ProcessId']):p for p in processes}
    ancestry=[];walk=os.getpid()
    for _ in range(16):
        if walk not in byid or walk in ancestry:break
        ancestry.append(walk);walk=int(byid[walk]['ParentProcessId'])
    launchjob=read(D/'game-job-proof.private.json');gamepid=launchjob['processId']
    steampid=int(byid[gamepid]['ParentProcessId'])
    targets={'game':gamepid,'steam':steampid,'caller':os.getpid()}
    for p in processes:
        if 'codex' in p['Name'].lower():targets['codex-'+str(p['ProcessId'])]=int(p['ProcessId'])
    handles={n:K.OpenProcess(0x1000,False,pid)for n,pid in targets.items()}
    need(all(handles[n]for n in ('game','steam','caller')),'Game/Steam/caller query handles unavailable.')
    rows=[];refused=[];seen=set()
    try:
        for e in entries:
            if int(e.type)!=jobtype:continue
            key=int(e.object or 0)
            if key and key in seen:continue
            source=K.OpenProcess(0x0040,False,int(e.pid))
            if not source:
                refused.append(dict(ownerPid=int(e.pid),reason='process_duplicate_query_unavailable'));continue
            duplicate=w.HANDLE()
            try:
                if not K.DuplicateHandle(source,w.HANDLE(int(e.handle)),current,ctypes.byref(duplicate),0x0004,False,0):
                    refused.append(dict(ownerPid=int(e.pid),reason='query_only_duplication_unavailable'));continue
            finally:K.CloseHandle(source)
            try:
                info=Extended();outlen=w.DWORD()
                if not K.QueryInformationJobObject(duplicate,9,ctypes.byref(info),ctypes.sizeof(info),ctypes.byref(outlen)):
                    refused.append(dict(ownerPid=int(e.pid),reason='job_limits_query_unavailable'));continue
                memberships={n:in_job(h,duplicate)if h else None for n,h in handles.items()}
                if key:seen.add(key)
                rows.append(dict(ownerPid=int(e.pid),ownerName=byid.get(int(e.pid),{}).get('Name'),limitFlags=int(info.basic.flags),
                    killOnClose=bool(info.basic.flags&0x2000),memberships=memberships))
            finally:K.CloseHandle(duplicate)
    finally:
        for h in handles.values():
            if h:K.CloseHandle(h)
    put(E/'job-memberships.raw.private.json',dict(capturedAtUtc=dt.datetime.now(dt.timezone.utc).isoformat(),
        gameProcessId=gamepid,steamProcessId=steampid,callerProcessId=os.getpid(),callerAncestry=ancestry,
        callerAncestryProcesses=[byid[p]for p in ancestry],handleCount=count,jobTypeIndex=jobtype,queriedJobs=rows,
        refusedQueries=refused,queryOnlyJobAccess=4,gameMemoryReads=0,jobAssignments=0,jobLimitChanges=0,processTerminations=0))
finally:K.CloseHandle(probe)

import copy
raw=read(E/'job-memberships.raw.private.json')
need(qualify(raw),'Actual Game/Steam separation from observed caller cleanup groups is unproved.')
relevant=terminating_groups(raw)
need(len(relevant)>=3 and {8192,10240,15360}.issubset({j['limitFlags']for j in relevant}),
    'All three current caller/application terminating groups must be observed, not just the nearest command group.')
bad=copy.deepcopy(raw)
next(j for j in bad['queriedJobs']if j['killOnClose'] and j['memberships'].get('caller') is True)['memberships']['game']=True
need(not qualify(bad),'A game inside a caller cleanup job must be rejected.')
unknown=copy.deepcopy(raw)
next(j for j in unknown['queriedJobs']if j['killOnClose'] and j['memberships'].get('caller') is True)['memberships']['game']=None
need(not qualify(unknown),'Unknown caller membership must be rejected.')
missing=copy.deepcopy(raw);missing['refusedQueries'].append(dict(ownerPid=raw['callerAncestry'][0],reason='synthetic_unavailable'))
need(not qualify(missing),'An unexamined caller-owned group must be rejected.')
put(D/'game-lifetime-qualification.private.json',dict(passed=True,gameProcessId=raw['gameProcessId'],steamProcessId=raw['steamProcessId'],
    outsideObservedCallerTerminatingJobs=True,completeCallerOwnedJobQueries=True,callerCleanupGroups=len(relevant),
    callerCleanupLimitFlags=sorted(j['limitFlags']for j in relevant),rawSha256=sha(E/'job-memberships.raw.private.json'),rawEvidencePath=str(E/'job-memberships.raw.private.json'),
    systemWideOtherJobQueriesUnknown=len(raw['refusedQueries']),allSystemJobsExamined=False,
    anyJobMembershipAloneIsNotCallerCleanup=True,negativeCallerMembershipRejected=True,negativeUnknownRejected=True,
    negativeUnexaminedCallerJobRejected=True,actualGameRestarted=False,gameCalls=0,
    
    limitation='Exact old game exit cause and unrelated system-owned job behavior remain unknown. No guarantee against OS/Steam termination.',
    nativeReferences=['https://learn.microsoft.com/en-us/windows/win32/api/jobapi/nf-jobapi-isprocessinjob',
                      'https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects']))
print(json.dumps(dict(passed=True,actualGameOutsideThreeCallerCleanupGroups=True,gameCalls=0)))

put(D/'lifetime-ready.private.json',dict(passed=True,proofSha256=sha(D/'game-lifetime-qualification.private.json')))
