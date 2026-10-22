"""Launch an already-reviewed Python task outside a permitted Windows host job.

This helper grants no game authority and does not extend a task's absolute UTC
deadline. The pinned target must enforce its existing finite work/call bounds.
No Windows job policy, service, scheduler or app setting is changed.
仅启动已审查并锁定内容的脚本；不授游戏权限、不续期、不修改宿主设置。
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
BREAKAWAY_OK = 0x800
SILENT_BREAKAWAY_OK = 0x1000
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
MAXIMUM_START_HORIZON_SECONDS = 1200


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_once(path: Path, value: dict) -> None:
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())


def utc(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise ValueError('An explicit absolute UTC deadline is required.')
    return parsed


def validate_deadline(value: str, now: dt.datetime | None = None) -> None:
    remaining = (utc(value) - (now or dt.datetime.now(dt.timezone.utc))).total_seconds()
    if not 0 < remaining <= MAXIMUM_START_HORIZON_SECONDS:
        raise ValueError('The original absolute deadline is expired or outside the finite start bound.')


def current_job_observation() -> dict:
    if os.name != 'nt':
        raise OSError('The native job observation requires Windows.')
    from ctypes import wintypes as w
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = w.HANDLE
    kernel.IsProcessInJob.argtypes = [w.HANDLE, w.HANDLE, ctypes.POINTER(w.BOOL)]
    kernel.IsProcessInJob.restype = w.BOOL
    inside = w.BOOL()
    if not kernel.IsProcessInJob(kernel.GetCurrentProcess(), None, ctypes.byref(inside)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not inside.value:
        return dict(isProcessInAnyJob=False, limitFlags=None)

    class Basic(ctypes.Structure):
        _fields_ = [('processTime', ctypes.c_longlong), ('jobTime', ctypes.c_longlong),
                    ('flags', w.DWORD), ('minWorkingSet', ctypes.c_size_t),
                    ('maxWorkingSet', ctypes.c_size_t), ('activeCount', w.DWORD),
                    ('affinity', ctypes.c_size_t), ('priority', w.DWORD), ('scheduling', w.DWORD)]

    class IO(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in
                    ('readCount', 'writeCount', 'otherCount', 'readBytes', 'writeBytes', 'otherBytes')]

    class Extended(ctypes.Structure):
        _fields_ = [('basic', Basic), ('io', IO), ('processMemory', ctypes.c_size_t),
                    ('jobMemory', ctypes.c_size_t), ('peakProcess', ctypes.c_size_t),
                    ('peakJob', ctypes.c_size_t)]

    value = Extended()
    length = w.DWORD()
    kernel.QueryInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p,
                                                w.DWORD, ctypes.POINTER(w.DWORD)]
    kernel.QueryInformationJobObject.restype = w.BOOL
    if not kernel.QueryInformationJobObject(None, 9, ctypes.byref(value), ctypes.sizeof(value), ctypes.byref(length)):
        raise ctypes.WinError(ctypes.get_last_error())
    return dict(isProcessInAnyJob=True, limitFlags=int(value.basic.flags))


def permitted_creation_flag(observation: dict) -> int:
    if observation.get('isProcessInAnyJob') is False:
        return 0
    flags = observation.get('limitFlags')
    if observation.get('isProcessInAnyJob') is not True or type(flags) is not int or flags < 0:
        raise RuntimeError('The current job policy is unknown; no process is launched.')
    # Use only an allowance already granted by Windows; never change a job.
    # https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags
    if flags & BREAKAWAY_OK:
        return CREATE_BREAKAWAY_FROM_JOB
    if flags & SILENT_BREAKAWAY_OK:
        return 0
    raise RuntimeError('The host does not allow an independent task; no process is launched.')


def current_security_identity() -> dict:
    """Read only this process's user, session and privilege scope."""
    if os.name != 'nt':
        raise OSError('The security identity observation requires Windows.')
    from ctypes import wintypes as w
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    security = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel.GetCurrentProcess.restype = w.HANDLE
    security.OpenProcessToken.argtypes = [w.HANDLE, w.DWORD, ctypes.POINTER(w.HANDLE)]
    security.GetTokenInformation.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.POINTER(w.DWORD)]
    security.GetLengthSid.argtypes = [ctypes.c_void_p]
    security.GetLengthSid.restype = w.DWORD
    security.GetSidSubAuthorityCount.argtypes = [ctypes.c_void_p]
    security.GetSidSubAuthorityCount.restype = ctypes.POINTER(ctypes.c_ubyte)
    security.GetSidSubAuthority.argtypes = [ctypes.c_void_p, w.DWORD]
    security.GetSidSubAuthority.restype = ctypes.POINTER(w.DWORD)
    token = w.HANDLE()
    if not security.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        def information(kind):
            length = w.DWORD()
            security.GetTokenInformation(token, kind, None, 0, ctypes.byref(length))
            if not 0 < length.value <= 65536:
                raise RuntimeError('The current security identity is unknown.')
            value = ctypes.create_string_buffer(length.value)
            if not security.GetTokenInformation(token, kind, value, length, ctypes.byref(length)):
                raise ctypes.WinError(ctypes.get_last_error())
            return value
        user = information(1)
        sid = ctypes.cast(user, ctypes.POINTER(ctypes.c_void_p))[0]
        size = security.GetLengthSid(sid)
        if not 8 <= size <= 68:
            raise RuntimeError('The current user SID observation is invalid.')
        sid_hash = hashlib.sha256(ctypes.string_at(sid, size)).hexdigest().upper()
        elevation = information(20)
        elevated = ctypes.cast(elevation, ctypes.POINTER(w.DWORD))[0]
        if elevated not in (0, 1):
            raise RuntimeError('The current elevation observation is unknown.')
        integrity = information(25)
        integrity_sid = ctypes.cast(integrity, ctypes.POINTER(ctypes.c_void_p))[0]
        count = security.GetSidSubAuthorityCount(integrity_sid)[0]
        if not 1 <= count <= 15:
            raise RuntimeError('The current integrity observation is unknown.')
        integrity_rid = security.GetSidSubAuthority(integrity_sid, count-1)[0]
        session = w.DWORD()
        kernel.ProcessIdToSessionId.argtypes = [w.DWORD, ctypes.POINTER(w.DWORD)]
        if not kernel.ProcessIdToSessionId(os.getpid(), ctypes.byref(session)) or session.value == 0:
            raise RuntimeError('The task must stay in the original interactive user session.')
        return dict(userSidSha256=sid_hash, sessionId=session.value, elevated=bool(elevated),
                    integrityRid=integrity_rid)
    finally:
        kernel.CloseHandle.argtypes = [w.HANDLE]
        kernel.CloseHandle(token)


def validate_child_job(observation: dict, transport: str) -> None:
    if observation.get('isProcessInAnyJob') is False:
        return
    # The native WMI provider uses its own breakaway-only job. It is not the
    # caller's kill-on-close job. Admit only the observed no-termination limit
    # combination for this explicitly selected provider route; all kill flags,
    # unknown observations and other quota combinations still refuse entry.
    if (transport == 'same_user_wmi' and observation.get('isProcessInAnyJob') is True
            and type(observation.get('limitFlags')) is int
            and observation['limitFlags'] == BREAKAWAY_OK | SILENT_BREAKAWAY_OK):
        return
    raise RuntimeError('The new task remains in an unproved or terminating job; the target is not entered.')


def create_via_wmi(command: list[str], cwd: Path, output: Path) -> int:
    """Explicit same-user Windows provider route, never an automatic fallback.

    WMI has its own job limits: request its documented breakaway flag and then
    independently verify the non-terminating provider job and unchanged
    token/session before target entry.
    https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/create-method-in-class-win32-process
    """
    powershell = shutil.which('powershell.exe')
    if not powershell:
        raise OSError('The native CIM client is unavailable; no alternate route is used.')
    program = r'''
$ErrorActionPreference='Stop'
$r=[Console]::In.ReadToEnd()|ConvertFrom-Json
$startup=New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow=[uint16]0;CreateFlags=[uint32]0x09000200}
$response=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=[string]$r.commandLine;CurrentDirectory=[string]$r.cwd;ProcessStartupInformation=$startup}
@{returnValue=$response.ReturnValue;processId=$response.ProcessId}|ConvertTo-Json -Compress
'''
    request = json.dumps(dict(commandLine=subprocess.list2cmdline(command), cwd=str(cwd)))
    result = subprocess.run([powershell, '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', program],
                            input=request, encoding='utf-8', capture_output=True, timeout=20,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    (output/'cim-response.private.log').write_text(result.stdout, encoding='utf-8')
    (output/'cim-stderr.private.log').write_text(result.stderr, encoding='utf-8')
    if result.returncode != 0:
        raise RuntimeError('The original CIM creation did not return success; reconcile it, never relaunch.')
    response = json.loads(result.stdout)
    if type(response.get('returnValue')) is not int or type(response.get('processId')) is not int:
        raise RuntimeError('The original CIM creation result is unknown; do not relaunch.')
    if response['returnValue'] != 0 or response['processId'] <= 0:
        raise RuntimeError('The original CIM provider refused process creation; no alternate route is used.')
    return response['processId']


def launch_once(script: Path, expected_sha256: str, arguments: list[str],
                evidence_directory: Path, deadline_utc: str, *,
                transport: str = 'command_job', expected_inputs: list[dict] | None = None) -> dict:
    """Caller must already have authority for the exact pinned, bounded target.

    Process creation without a returned receipt is unknown. Never call again
    with a new evidence directory to compensate for a missing observation.
    """
    script = script.resolve(strict=True)
    if script.suffix.lower() != '.py' or digest(script) != expected_sha256.upper():
        raise ValueError('The reviewed Python target content does not match.')
    validate_deadline(deadline_utc)
    parent = current_job_observation()
    if transport not in ('command_job', 'same_user_wmi'):
        raise ValueError('Unrecognized process creation route.')
    flag = permitted_creation_flag(parent) if transport == 'command_job' else None
    identity = current_security_identity()
    evidence_directory = evidence_directory.resolve()
    evidence_directory.mkdir()  # Refuse duplicates before any process creation.
    request = dict(schemaVersion=1, script=str(script), scriptSha256=expected_sha256.upper(),
                   arguments=arguments, deadlineUtc=deadline_utc,
                   bootstrapSha256=digest(Path(__file__).resolve()),
                   pythonExe=str(Path(sys.executable).resolve()),
                   pythonExeSha256=digest(Path(sys.executable).resolve()),
                   parentJob=parent, creationFlag=flag, transport=transport,
                   securityIdentity=identity, expectedInputs=expected_inputs or [], grantsGameAuthority=False)
    control = evidence_directory / 'intent.private.json'
    write_once(control, request)
    command = [sys.executable, str(Path(__file__).resolve()), '--worker-control', str(control),
               '--control-sha256', digest(control)]
    try:
        # No console or inherited host pipe; Python installs an explicit handle
        # list for these three streams. No shell, service, or scheduled job.
        if transport == 'same_user_wmi':
            child_pid = create_via_wmi(command, script.parent, evidence_directory)
        else:
            with (evidence_directory / 'stdout.private.log').open('xb') as stdout, \
                 (evidence_directory / 'stderr.private.log').open('xb') as stderr:
                child = subprocess.Popen(command, cwd=script.parent, stdin=subprocess.DEVNULL,
                                         stdout=stdout, stderr=stderr, close_fds=True,
                                         creationflags=flag | subprocess.CREATE_NO_WINDOW |
                                         subprocess.CREATE_NEW_PROCESS_GROUP)
                child_pid = child.pid
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        write_once(evidence_directory / 'creation-failure.private.json',
                   dict(stage='create_process', errorType=type(error).__name__,
                        winerror=getattr(error, 'winerror', None), creationOutcome='unknown',
                        gameAuthorityGranted=False))
        raise
    receipt = dict(processId=child_pid, deadlineUtc=deadline_utc, parentJob=parent, transport=transport,
                   processCreationReturned=True, targetAdmission='not_observed',
                   executionOutcome='unknown', grantsGameAuthority=False)
    write_once(evidence_directory / 'created.private.json', receipt)
    return receipt


def run_control(control: Path, expected_control_sha256: str) -> None:
    control = control.resolve(strict=True)
    target_started = False
    observation = None
    try:
        if digest(control) != expected_control_sha256.upper():
            raise ValueError('The original launch request content changed.')
        value = json.loads(control.read_text(encoding='utf-8'))
        if value['schemaVersion'] != 1 or value['grantsGameAuthority'] is not False:
            raise ValueError('Unrecognized launch request.')
        if digest(Path(__file__).resolve()) != value['bootstrapSha256']:
            raise ValueError('The launch helper content changed.')
        if digest(Path(sys.executable).resolve()) != value['pythonExeSha256']:
            raise ValueError('The task interpreter content changed.')
        observation = current_job_observation()
        validate_child_job(observation, value['transport'])
        identity = current_security_identity()
        if identity != value['securityIdentity']:
            raise RuntimeError('The task user, session or privilege scope changed; the target is not entered.')
        validate_deadline(value['deadlineUtc'])
        script = Path(value['script']).resolve(strict=True)
        if digest(script) != value['scriptSha256']:
            raise ValueError('The reviewed task content changed before admission.')
        for item in value['expectedInputs']:
            path = Path(item['path']).resolve(strict=True)
            if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
                raise ValueError('The independent task sees different protected input content.')
        write_once(control.parent / 'admitted.private.json',
                   dict(processId=os.getpid(), admittedAtUtc=dt.datetime.now(dt.timezone.utc).isoformat(),
                        deadlineUtc=value['deadlineUtc'], job=observation,
                        scriptSha256=value['scriptSha256'], securityIdentity=identity,
                        inputFilesVerified=len(value['expectedInputs']), gameAuthorityGranted=False))
        # Only this worker's files are replaced; it inherits no host pipes.
        sys.stdout = (control.parent/'stdout.private.log').open('x', encoding='utf-8') if value['transport']=='same_user_wmi' else sys.stdout
        sys.stderr = (control.parent/'stderr.private.log').open('x', encoding='utf-8') if value['transport']=='same_user_wmi' else sys.stderr
        sys.argv = [str(script), *value['arguments']]
        target_started = True
        runpy.run_path(str(script), run_name='__main__')
    except Exception as error:
        write_once(control.parent / 'worker-failure.private.json',
                   dict(stage='target' if target_started else 'before_target',
                        errorType=type(error).__name__, message=str(error),
                        targetEntered=target_started, sameDecisionJobObservation=observation))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker-control', required=True, type=Path)
    parser.add_argument('--control-sha256', required=True)
    args = parser.parse_args()
    run_control(args.worker_control, args.control_sha256)
