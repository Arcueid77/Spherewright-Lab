"""Query-only Windows job capture; no game memory, assignments or limit changes."""
import datetime,json,os,subprocess
from pathlib import Path

HOST_NAMES={'codex.exe','chatgpt.exe'}

def ancestry(processes,pid):
    byid={p['ProcessId']:p for p in processes};result=[]
    for _ in range(32):
        p=byid.get(pid)
        if p is None or pid in result:break
        result.append(pid);parent=byid.get(p['ParentProcessId'])
        if (parent is None or not p.get('createdFileTime') or not parent.get('createdFileTime')
            or parent['createdFileTime']>p['createdFileTime']):break
        pid=parent['ProcessId']
    return result

def application_scope(processes,caller):
    byid={p['ProcessId']:p for p in processes};chain=ancestry(processes,caller)
    anchors=[pid for pid in chain if byid[pid]['Name'].lower() in HOST_NAMES]
    if not anchors:raise RuntimeError('caller_application_anchor_unknown')
    root=anchors[-1];scope={root}
    for _ in range(32):
        before=len(scope)
        for p in processes:
            parent=byid.get(p['ParentProcessId'])
            if (parent and parent['ProcessId'] in scope and p.get('createdFileTime') and parent.get('createdFileTime')
                and p['createdFileTime']>=parent['createdFileTime']):scope.add(p['ProcessId'])
        if len(scope)==before:break
    else:raise RuntimeError('caller_process_scope_exceeds_bound')
    if caller not in scope:raise RuntimeError('caller_not_in_observed_application_scope')
    return root,scope,chain[:chain.index(root)+1]

def capture(expected,*,target_kind='game',expected_image='DSPGAME.exe',expected_parent_image='steam.exe',extra_targets=None):
    import ctypes
    from ctypes import wintypes as w
    from evidence import need
    K=ctypes.WinDLL('kernel32',use_last_error=True);N=ctypes.WinDLL('ntdll')
    P=ctypes.c_void_p;U=ctypes.c_size_t
    K.GetCurrentProcess.restype=w.HANDLE
    K.CreateJobObjectW.argtypes=[P,w.LPCWSTR];K.CreateJobObjectW.restype=w.HANDLE
    K.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];K.OpenProcess.restype=w.HANDLE
    K.CloseHandle.argtypes=[w.HANDLE];K.CloseHandle.restype=w.BOOL
    K.DuplicateHandle.argtypes=[w.HANDLE,w.HANDLE,w.HANDLE,ctypes.POINTER(w.HANDLE),w.DWORD,w.BOOL,w.DWORD];K.DuplicateHandle.restype=w.BOOL
    K.IsProcessInJob.argtypes=[w.HANDLE,w.HANDLE,ctypes.POINTER(w.BOOL)];K.IsProcessInJob.restype=w.BOOL
    K.QueryInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,P,w.DWORD,ctypes.POINTER(w.DWORD)];K.QueryInformationJobObject.restype=w.BOOL
    K.GetProcessTimes.argtypes=[w.HANDLE,*([ctypes.POINTER(w.FILETIME)]*4)];K.GetProcessTimes.restype=w.BOOL
    K.GetExitCodeProcess.argtypes=[w.HANDLE,ctypes.POINTER(w.DWORD)];K.GetExitCodeProcess.restype=w.BOOL
    N.NtQuerySystemInformation.argtypes=[ctypes.c_int,P,w.ULONG,ctypes.POINTER(w.ULONG)];N.NtQuerySystemInformation.restype=ctypes.c_long
    class Entry(ctypes.Structure):
        _fields_=[('object',P),('pid',U),('handle',U),('access',w.ULONG),('backtrace',w.USHORT),('type',w.USHORT),('attributes',w.ULONG),('reserved',w.ULONG)]
    class Basic(ctypes.Structure):
        _fields_=[('processTime',ctypes.c_longlong),('jobTime',ctypes.c_longlong),('flags',w.DWORD),('minWs',U),('maxWs',U),('activeCount',w.DWORD),('affinity',U),('priority',w.DWORD),('scheduling',w.DWORD)]
    class IO(ctypes.Structure):_fields_=[(n,ctypes.c_ulonglong)for n in ('readCount','writeCount','otherCount','readBytes','writeBytes','otherBytes')]
    class Extended(ctypes.Structure):_fields_=[('basic',Basic),('io',IO),('processMemory',U),('jobMemory',U),('peakProcess',U),('peakJob',U)]
    def in_job(process,job):
        answer=w.BOOL()
        return bool(answer.value) if K.IsProcessInJob(process,job,ctypes.byref(answer)) else None
    def created(handle):
        values=[w.FILETIME() for _ in range(4)]
        need(K.GetProcessTimes(handle,*[ctypes.byref(v) for v in values]),'process_identity_query_failed')
        return (values[0].dwHighDateTime<<32)|values[0].dwLowDateTime
    def alive(handle):
        code=w.DWORD();return bool(K.GetExitCodeProcess(handle,ctypes.byref(code))) and code.value==259
    command="Get-CimInstance Win32_Process|Select-Object Name,ProcessId,ParentProcessId,ExecutablePath,@{N='createdFileTime';E={if($_.CreationDate){$_.CreationDate.ToFileTimeUtc()}else{0}}}|ConvertTo-Json -Compress"
    processes=json.loads(subprocess.check_output(['powershell.exe','-NoProfile','-NonInteractive','-Command',command],text=True,timeout=20))
    byid={p['ProcessId']:p for p in processes};gamepid=expected['Id'];game=byid.get(gamepid)
    need(game is not None and game['Name'].lower()==expected_image.lower(),'game_process_identity_changed')
    need(Path(game['ExecutablePath']).resolve()==Path(expected['Path']).resolve(),'game_process_image_changed')
    steam=byid.get(game['ParentProcessId']);need(steam is not None and steam['Name'].lower()==expected_parent_image.lower(),'game_steam_parent_unproved')
    root,scope,chain=application_scope(processes,os.getpid())
    targets={'game':gamepid,'steam':steam['ProcessId'],'caller':os.getpid()}
    targets.update({'scope-'+str(pid):pid for pid in chain})
    if extra_targets:
        need(target_kind=='probe' and not set(extra_targets)&set(targets),'extra_targets_only_for_harmless_probe')
        targets.update(extra_targets)
    handles={name:K.OpenProcess(0x1000,False,pid) for name,pid in targets.items()}
    need(all(handles.values()),'scope_or_target_process_query_unavailable')
    current=K.GetCurrentProcess();probe=K.CreateJobObjectW(None,None);need(probe,'query_type_probe_unavailable')
    try:
        need(created(handles['game'])==expected['createdFileTime'] and alive(handles['game']),'game_pid_reused_or_exited')
        identities={name:created(handle) for name,handle in handles.items()}
        any_jobs={name:in_job(handles[name],None) for name in ('game','steam','caller')}
        length=w.ULONG();size=1024*1024
        for _ in range(8):
            need(size<=32*1024*1024,'bounded_job_metadata_exceeded')
            buffer=ctypes.create_string_buffer(size);status=N.NtQuerySystemInformation(64,buffer,size,ctypes.byref(length))
            if status==0:break
            need(status in (-1073741820,-1073741789),'job_metadata_query_refused');size=max(size*2,int(length.value)+65536)
        else:raise RuntimeError('job_metadata_snapshot_not_stable')
        count=U.from_buffer(buffer,0).value
        need(0<count<=800000 and 2*ctypes.sizeof(U)+count*ctypes.sizeof(Entry)<=size,'job_metadata_malformed')
        entries=(Entry*count).from_buffer(buffer,2*ctypes.sizeof(U))
        types=[int(e.type)for e in entries if int(e.pid)==os.getpid() and int(e.handle)==int(probe)]
        need(len(types)==1,'job_type_not_identified');objects={}
        for e in entries:
            if int(e.type)==types[0]:
                # An unreported kernel address is not an absent job. Keep its
                # exact owner/handle as a separate inventory entry; never merge
                # it with another handle or infer successful coverage from one.
                key=str(int(e.object)) if e.object else 'handle-'+str(int(e.pid))+'-'+str(int(e.handle))
                objects.setdefault(key,[]).append((int(e.pid),int(e.handle)))
        inventory=[];rows=[];unresolved=[];attempts=[]
        for key,refs in objects.items():
            owners=sorted({pid for pid,_ in refs});inventory.append(dict(objectKey=key,ownerPids=owners));resolved=False
            for pid,value in sorted(refs,key=lambda x:x[0] not in scope):
                source=K.OpenProcess(0x0040,False,pid)
                if not source:attempts.append(dict(objectKey=key,ownerPid=pid,reason='duplicate_access_unavailable'));continue
                duplicate=w.HANDLE()
                try:ok=K.DuplicateHandle(source,w.HANDLE(value),current,ctypes.byref(duplicate),0x0004,False,0)
                finally:K.CloseHandle(source)
                if not ok:attempts.append(dict(objectKey=key,ownerPid=pid,reason='query_duplicate_unavailable'));continue
                try:
                    info=Extended();outlen=w.DWORD()
                    if not K.QueryInformationJobObject(duplicate,9,ctypes.byref(info),ctypes.sizeof(info),ctypes.byref(outlen)):
                        attempts.append(dict(objectKey=key,ownerPid=pid,reason='job_limits_unavailable'));continue
                    memberships={name:in_job(handle,duplicate) for name,handle in handles.items()}
                    rows.append(dict(objectKey=key,ownerPids=owners,limitFlags=int(info.basic.flags),
                        killOnClose=bool(info.basic.flags&0x2000),memberships=memberships));resolved=True;break
                finally:K.CloseHandle(duplicate)
            if not resolved:unresolved.append(dict(objectKey=key,ownerPids=owners))
        need(all(created(h)==identities[name] and alive(h) for name,h in handles.items()),'process_identity_changed_during_capture')
        return dict(schemaVersion=2,targetKind=target_kind,capturedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            gameProcessId=gamepid,steamProcessId=steam['ProcessId'],callerProcessId=os.getpid(),
            gameIdentityVerified=True,processIdentitiesStable=True,processes=processes,scopeRootPid=root,
            scopePids=sorted(scope),callerAncestry=chain,jobMetadataEnumerationComplete=True,handleCount=count,
            enumeratedJobs=inventory,queriedJobs=rows,unresolvedJobObjects=unresolved,queryAttempts=attempts,
            anyJobMembership=any_jobs,queryOnlyJobAccess=4,gameMemoryReads=0,jobAssignments=0,
            jobLimitChanges=0,processTerminations=0)
    finally:
        K.CloseHandle(probe)
        for handle in handles.values():
            if handle:K.CloseHandle(handle)
