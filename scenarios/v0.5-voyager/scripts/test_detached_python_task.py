"""Offline policy checks; optional real Windows job fixture. Never starts a game.
离线策略测试及真实Windows进程回收替身；不启动游戏或MCP。
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

import detached_python_task as task

HERE = Path(__file__).resolve()


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.target = self.root / 'target.py'
        self.target.write_text("raise AssertionError('The real target must not run in policy tests')", encoding='utf-8')
        self.deadline = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=20)).isoformat()
        self.identity = dict(userSidSha256='synthetic-user', sessionId=1, elevated=False, integrityRid=8192)
        identity_patch = mock.patch.object(task, 'current_security_identity', return_value=self.identity)
        identity_patch.start()
        self.addCleanup(identity_patch.stop)

    def control(self):
        path = self.root / 'intent.private.json'
        task.write_once(path, dict(schemaVersion=1, grantsGameAuthority=False,
            script=str(self.target), scriptSha256=task.digest(self.target), arguments=[],
            deadlineUtc=self.deadline, bootstrapSha256=task.digest(Path(task.__file__)),
            pythonExeSha256=task.digest(Path(sys.executable)), securityIdentity=self.identity,
            transport='command_job', expectedInputs=[]))
        return path

    def test_unknown_or_denied_host_policy_cannot_start_a_task(self):
        observations = [{}, {'isProcessInAnyJob': None},
                        {'isProcessInAnyJob': True, 'limitFlags': None},
                        {'isProcessInAnyJob': True, 'limitFlags': 0x2000}]
        with mock.patch.object(task.subprocess, 'Popen') as spawn:
            for observation in observations:
                with self.subTest(observation=observation), \
                     mock.patch.object(task, 'current_job_observation', return_value=observation):
                    with self.assertRaises(RuntimeError):
                        task.launch_once(self.target, task.digest(self.target), [], self.root/'unused', self.deadline)
            spawn.assert_not_called()
        self.assertFalse((self.root/'unused').exists())

    def test_only_an_existing_windows_allowance_is_used(self):
        self.assertEqual(task.CREATE_BREAKAWAY_FROM_JOB,
                         task.permitted_creation_flag({'isProcessInAnyJob': True, 'limitFlags': 0x2800}))
        self.assertEqual(0, task.permitted_creation_flag({'isProcessInAnyJob': True, 'limitFlags': 0x3000}))
        self.assertEqual(0, task.permitted_creation_flag({'isProcessInAnyJob': False, 'limitFlags': None}))

    def test_provider_job_requires_the_explicit_route_and_exact_nonterminating_flags(self):
        task.validate_child_job({'isProcessInAnyJob':True,'limitFlags':0x1800}, 'same_user_wmi')
        for transport, observation in [('command_job',{'isProcessInAnyJob':True,'limitFlags':0x1800}),
            ('same_user_wmi',{'isProcessInAnyJob':True,'limitFlags':0x2000}),
            ('same_user_wmi',{'isProcessInAnyJob':True,'limitFlags':0x2800}),
            ('same_user_wmi',{'isProcessInAnyJob':True,'limitFlags':0x1804}),
            ('same_user_wmi',{'isProcessInAnyJob':True,'limitFlags':None}),
            ('same_user_wmi',{'isProcessInAnyJob':None,'limitFlags':0x1800})]:
            with self.subTest(transport=transport,observation=observation),self.assertRaises(RuntimeError):
                task.validate_child_job(observation, transport)

    def test_changed_task_content_is_rejected_before_process_creation(self):
        pinned = task.digest(self.target)
        self.target.write_text("raise AssertionError('changed')", encoding='utf-8')
        with mock.patch.object(task.subprocess, 'Popen') as spawn:
            with self.assertRaises(ValueError):
                task.launch_once(self.target, pinned, [], self.root/'unused', self.deadline)
            spawn.assert_not_called()

    def test_expired_unknown_zone_or_extended_deadline_cannot_start(self):
        now = dt.datetime.now(dt.timezone.utc)
        values = [(now-dt.timedelta(seconds=1)).isoformat(),
                  (now+dt.timedelta(seconds=1201)).isoformat(),
                  now.replace(tzinfo=None).isoformat()]
        with mock.patch.object(task.subprocess, 'Popen') as spawn:
            for value in values:
                with self.subTest(value=value), self.assertRaises(ValueError):
                    task.launch_once(self.target, task.digest(self.target), [], self.root/'unused', value)
            spawn.assert_not_called()

    def test_repeat_refuses_and_a_creation_receipt_does_not_claim_admission(self):
        out = self.root/'launch'
        with mock.patch.object(task, 'current_job_observation',
                               return_value={'isProcessInAnyJob': True, 'limitFlags': 0x2800}), \
             mock.patch.object(task.subprocess, 'CREATE_NO_WINDOW', 0x08000000, create=True), \
             mock.patch.object(task.subprocess, 'CREATE_NEW_PROCESS_GROUP', 0x200, create=True), \
             mock.patch.object(task.subprocess, 'Popen', return_value=SimpleNamespace(pid=4321)) as spawn:
            result = task.launch_once(self.target, task.digest(self.target), [], out, self.deadline)
            original = (out/'intent.private.json').read_bytes()
            self.assertEqual('unknown', result['executionOutcome'])
            self.assertEqual('not_observed', result['targetAdmission'])
            self.assertEqual(self.deadline, result['deadlineUtc'])
            self.assertFalse(result['grantsGameAuthority'])
            with self.assertRaises(FileExistsError):
                task.launch_once(self.target, task.digest(self.target), [], out, self.deadline)
            self.assertEqual(1, spawn.call_count)
            self.assertEqual(original, (out/'intent.private.json').read_bytes())
            self.assertIs(spawn.call_args.kwargs['close_fds'], True)

    def test_child_still_in_an_outer_job_never_enters_target(self):
        control = self.control()
        with mock.patch.object(task, 'current_job_observation',
                               return_value={'isProcessInAnyJob': True, 'limitFlags': 0x2800}), \
             mock.patch.object(task.runpy, 'run_path') as enter:
            with self.assertRaises(RuntimeError):
                task.run_control(control, task.digest(control))
            enter.assert_not_called()
        failure = json.loads((self.root/'worker-failure.private.json').read_text())
        self.assertFalse(failure['targetEntered'])
        self.assertEqual('before_target', failure['stage'])

    def test_changed_content_after_creation_is_rejected_by_the_child(self):
        control = self.control()
        self.target.write_text("raise AssertionError('changed after launch')", encoding='utf-8')
        with mock.patch.object(task, 'current_job_observation', return_value={'isProcessInAnyJob': False}), \
             mock.patch.object(task.runpy, 'run_path') as enter:
            with self.assertRaisesRegex(ValueError, 'content changed before admission'):
                task.run_control(control, task.digest(control))
            enter.assert_not_called()

    def test_changed_request_cannot_borrow_the_original_request_hash(self):
        control = self.control()
        pinned = task.digest(control)
        value = json.loads(control.read_text())
        value['deadlineUtc'] = (dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=100)).isoformat()
        control.write_text(json.dumps(value), encoding='utf-8')
        with mock.patch.object(task.runpy, 'run_path') as enter:
            with self.assertRaisesRegex(ValueError, 'request content changed'):
                task.run_control(control, pinned)
            enter.assert_not_called()

    def test_alternate_session_user_or_privilege_never_enters_target(self):
        for field, changed in [('sessionId',2),('userSidSha256','different-user'),
                               ('elevated',True),('integrityRid',12288)]:
            with self.subTest(field=field):
                control = self.control()
                with mock.patch.object(task, 'current_job_observation', return_value={'isProcessInAnyJob': False}), \
                     mock.patch.object(task, 'current_security_identity', return_value={**self.identity,field:changed}), \
                     mock.patch.object(task.runpy, 'run_path') as enter:
                    with self.assertRaisesRegex(RuntimeError, 'privilege scope changed'):
                        task.run_control(control, task.digest(control))
                    enter.assert_not_called()
                control.unlink()
                (self.root/'worker-failure.private.json').unlink()

    def test_changed_input_view_refuses_before_task_entry(self):
        control = self.control()
        value = json.loads(control.read_text())
        value['expectedInputs'] = [dict(path=str(self.target), bytes=self.target.stat().st_size,
                                       sha256='0'*64)]
        control.write_text(json.dumps(value), encoding='utf-8')
        with mock.patch.object(task, 'current_job_observation', return_value={'isProcessInAnyJob': False}), \
             mock.patch.object(task.runpy, 'run_path') as enter:
            with self.assertRaisesRegex(ValueError, 'different protected input content'):
                task.run_control(control, task.digest(control))
            enter.assert_not_called()


def process_running(pid):
    from ctypes import wintypes as w
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
    kernel.OpenProcess.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
    handle = kernel.OpenProcess(0x100000, False, pid)
    if not handle:
        if ctypes.get_last_error() == 87:
            return False
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        wait = kernel.WaitForSingleObject(handle, 0)
        if wait not in (0, 258):
            raise RuntimeError('The fixture process exit is unknown.')
        return wait == 258
    finally:
        kernel.CloseHandle(handle)


def fixture_job():
    # This job is newly created by this fixture and contains only its own
    # synthetic parent/child. Never open or change the Codex/Steam/DSP job.
    from ctypes import wintypes as w
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)

    class Basic(ctypes.Structure):
        _fields_ = [('processTime', ctypes.c_longlong), ('jobTime', ctypes.c_longlong), ('flags', w.DWORD),
                    ('minWorkingSet', ctypes.c_size_t), ('maxWorkingSet', ctypes.c_size_t),
                    ('activeCount', w.DWORD), ('affinity', ctypes.c_size_t), ('priority', w.DWORD), ('scheduling', w.DWORD)]

    class IO(ctypes.Structure):
        _fields_ = [(str(i), ctypes.c_ulonglong) for i in range(6)]

    class Extended(ctypes.Structure):
        _fields_ = [('basic', Basic), ('io', IO), ('processMemory', ctypes.c_size_t),
                    ('jobMemory', ctypes.c_size_t), ('peakProcess', ctypes.c_size_t), ('peakJob', ctypes.c_size_t)]

    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
    kernel.CreateJobObjectW.restype = w.HANDLE
    kernel.GetCurrentProcess.restype = w.HANDLE
    kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
    kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
    handles = []
    # Reproduce both observed layers: an outer kill-only job and an inner
    # kill-on-close job allowing breakaway. Only these new fixture jobs change.
    for flags in (0x2000, 0x2800):
        handle = kernel.CreateJobObjectW(None, None)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = Extended()
        limits.basic.flags = flags
        if not kernel.SetInformationJobObject(handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            raise ctypes.WinError(ctypes.get_last_error())
        if not kernel.AssignProcessToJobObject(handle, kernel.GetCurrentProcess()):
            raise ctypes.WinError(ctypes.get_last_error())
        handles.append(handle)
    kernel.CloseHandle.argtypes = [w.HANDLE]
    return lambda: kernel.CloseHandle(handles[0])


def await_file(path, seconds=6):
    limit = time.monotonic()+seconds
    while time.monotonic()<limit:
        if path.is_file():
            return json.loads(path.read_text(encoding='utf-8'))
        time.sleep(0.03)
    raise TimeoutError('The same fixture did not produce its expected original receipt: '+path.name)


def fixture_role(role, root, deadline, old_parent):
    if role == 'parent':
        close_owned_job = fixture_job()
        ordinary = subprocess.Popen([sys.executable, str(HERE), '--fixture-role', 'ordinary',
            '--evidence', str(root), '--deadline', deadline, '--old-parent', str(os.getpid())],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True, creationflags=subprocess.CREATE_NO_WINDOW)
        independent = task.launch_once(HERE, task.digest(HERE), ['--fixture-role', 'independent',
            '--evidence', str(root), '--deadline', deadline, '--old-parent', str(os.getpid())],
            root/'independent-launch', deadline, transport='same_user_wmi')
        task.write_once(root/'parent-ready.private.json', dict(parentPid=os.getpid(), ordinaryPid=ordinary.pid,
            independentPid=independent['processId'], job=task.current_job_observation(), deadlineUtc=deadline))
        limit = time.monotonic()+6
        while not (root/'release-parent.signal').exists() and time.monotonic()<limit:
            time.sleep(0.03)
        close_owned_job()  # Terminates only this fixture's parent and ordinary child.
        raise AssertionError('The fixture parent survived closing its own kill-on-close job.')

    if role == 'leaf':
        print(json.dumps(dict(job=task.current_job_observation(), securityIdentity=task.current_security_identity())))
        return

    task.write_once(root/(role+'-started.private.json'),
                    dict(processId=os.getpid(), oldParent=old_parent, job=task.current_job_observation(), deadlineUtc=deadline))
    limit = time.monotonic()+8
    while time.monotonic()<limit and dt.datetime.now(dt.timezone.utc)<task.utc(deadline):
        if (root/'parent-exit-observed.signal').exists() and not process_running(old_parent):
            leaf = subprocess.run([sys.executable,str(HERE),'--fixture-role','leaf'],
                stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=3,
                close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
            if leaf.returncode != 0:
                raise RuntimeError('The independent task could not read back its normal child lifetime.')
            sample = json.loads(leaf.stdout)
            task.write_once(root/(role+'-leaf.private.json'),sample)
            task.validate_child_job(sample['job'],'same_user_wmi')
            if sample['securityIdentity'] != task.current_security_identity():
                raise RuntimeError('The normal child security identity changed.')
            for number in range(3):
                task.write_once(root/(role+'-tail-'+str(number)+'.private.json'),
                                dict(afterParentExit=True, sequence=number, deadlineUtc=deadline))
                time.sleep(0.04)
            task.write_once(root/(role+'-completed.private.json'),
                            dict(completed=True, parentExitIndependentlyObserved=True,
                                 deadlineUtc=deadline, gameLaunches=0))
            return
        time.sleep(0.03)
    raise TimeoutError('The finite fixture did not observe the original parent exit.')


def windows_integration(root):
    if os.name != 'nt':
        raise OSError('The real lifecycle fixture needs Windows; it is never simulated as a pass.')
    root = root.resolve()
    root.mkdir()
    deadline = (dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=15)).isoformat()
    receipt = task.launch_once(HERE, task.digest(HERE), ['--fixture-role', 'parent', '--evidence', str(root),
        '--deadline', deadline], root/'parent-launch', deadline, transport='same_user_wmi')
    parent = await_file(root/'parent-ready.private.json')
    ordinary = await_file(root/'ordinary-started.private.json')
    independent = await_file(root/'independent-started.private.json')
    assert parent['parentPid'] == receipt['processId']
    assert ordinary['job']['isProcessInAnyJob'] is True
    task.validate_child_job(independent['job'], 'same_user_wmi')
    assert parent['job']['limitFlags'] == 0x2800
    (root/'release-parent.signal').write_text('Close only the owned synthetic job.', encoding='utf-8')
    end = time.monotonic()+5
    while time.monotonic()<end and (process_running(parent['parentPid']) or process_running(parent['ordinaryPid'])):
        time.sleep(0.03)
    assert not process_running(parent['parentPid']) and not process_running(parent['ordinaryPid'])
    (root/'parent-exit-observed.signal').write_text('Original fixture parent and ordinary child exited.', encoding='utf-8')
    done = await_file(root/'independent-completed.private.json')
    assert done['completed'] and done['parentExitIndependentlyObserved'] and done['deadlineUtc'] == deadline
    end = time.monotonic()+3
    while time.monotonic()<end and process_running(parent['independentPid']):
        time.sleep(0.03)
    assert not process_running(parent['independentPid'])
    assert not (root/'ordinary-completed.private.json').exists()
    leaf = json.loads((root/'independent-leaf.private.json').read_text())
    task.validate_child_job(leaf['job'],'same_user_wmi')
    for number in range(3):
        assert json.loads((root/('independent-tail-'+str(number)+'.private.json')).read_text())['afterParentExit']
    result = dict(passed=True, realWindowsJobClosure=True, nestedKillJobsReproduced=True, ordinaryChildTerminated=True,
                  independentChildCompletedAfterParentExit=True, allFixtureProcessesStopped=True,
                  ordinaryGrandchildOutsideTerminatingHostJob=True, sameUserSessionAndPrivilege=True,
                  originalAbsoluteDeadlineUnchanged=True, hostJobModified=False, gameLaunches=0)
    task.write_once(root/'result.private.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--windows-integration', action='store_true')
    parser.add_argument('--fixture-role', choices=('parent','ordinary','independent','leaf'))
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--deadline')
    parser.add_argument('--old-parent', type=int, default=0)
    args = parser.parse_args()
    if args.fixture_role:
        fixture_role(args.fixture_role, args.evidence, args.deadline, args.old_parent)
    else:
        outcome = unittest.main(argv=[sys.argv[0]], exit=False)
        if not outcome.result.wasSuccessful():
            raise SystemExit(1)
        if args.windows_integration:
            if not args.evidence:
                parser.error('--windows-integration requires a new --evidence directory')
            windows_integration(args.evidence)
