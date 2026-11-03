"""Bounded, evidence-preserving MCP stdio client. Importing starts no process."""
import datetime
import hashlib
import json
import math
import os
import pathlib
import queue
import subprocess
import threading
import time

URI = 'spherewright://agent/playbooks/opening-movement-v1'
MAX_STDOUT_BYTES = 64 * 1024 * 1024
MAX_LINE_BYTES = 1024 * 1024
MAX_STDERR_BYTES = 1024 * 1024


class McpClientError(RuntimeError):
    def __init__(self, fault_type, message):
        self.fault_type = fault_type
        super().__init__('%s: %s' % (fault_type, message))


class Client:
    def __init__(self, executable, directory, maximum=8, seconds=120,
                 total_stdout_limit=MAX_STDOUT_BYTES):
        if isinstance(maximum, bool) or not isinstance(maximum, int) or maximum < 1:
            raise ValueError('maximum must be a finite positive request count')
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds <= 0:
            raise ValueError('seconds must be finite and positive')
        if (isinstance(total_stdout_limit, bool) or not isinstance(total_stdout_limit, int)
                or not 1 <= total_stdout_limit <= MAX_STDOUT_BYTES):
            raise ValueError('total_stdout_limit must be an integer from 1 through 64 MiB')
        self.directory = pathlib.Path(directory)
        self.directory.mkdir(exist_ok=True)
        self.maximum, self.count = maximum, 0
        self.deadline = time.monotonic() + seconds
        self.total_stdout_limit = total_stdout_limit
        self.lines, self.faults = queue.Queue(), []
        self.stderr = bytearray()
        self.lock = threading.RLock()
        self.stdout_received_bytes = self.stdout_accepted_bytes = self.stdout_frames = 0
        self.stderr_received_bytes = 0
        self.stdout_eof_observed = self.stderr_eof_observed = False
        self.stdin_closed_by_client = self.closed = False
        self.process, self.threads, self.evidence = None, [], None
        self.log = (self.directory / 'rpc.jsonl').open('x', encoding='utf-8')
        self.raw = (self.directory / 'stdout.raw.private.bin').open('xb')
        self.frames = (self.directory / 'stdout-frames.private.jsonl').open('x', encoding='utf-8')
        self.events = (self.directory / 'client-events.private.jsonl').open('x', encoding='utf-8')
        self.error_raw = (self.directory / 'stderr.log').open('xb')
        env = os.environ.copy()
        env.pop('SPHEREWRIGHT_BRIDGE_DESCRIPTOR', None)
        try:
            self.process = subprocess.Popen([str(executable)], cwd=str(pathlib.Path(executable).parent),
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        except Exception as error:
            self._fault('process_start_failed', str(error))
            self._finish_files()
            raise
        self.threads = [threading.Thread(target=self.read_out, daemon=True),
                        threading.Thread(target=self.read_err, daemon=True)]
        for thread in self.threads:
            thread.start()

    @staticmethod
    def _flush(stream):
        stream.flush()
        os.fsync(stream.fileno())

    def _event(self, kind, **details):
        with self.lock:
            event = dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), kind=kind,
                         requestCount=self.count, stdoutReceivedBytes=self.stdout_received_bytes,
                         stdoutAcceptedBytes=self.stdout_accepted_bytes, stdoutFrames=self.stdout_frames,
                         stderrReceivedBytes=self.stderr_received_bytes, **details)
            self.events.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + '\n')
            self._flush(self.events)
            return event

    def _fault(self, fault_type, message):
        with self.lock:
            event = self._event('fault', faultType=fault_type, message=message)
            self.faults.append(event)

    def _fail(self, fault_type, message):
        self._fault(fault_type, message)
        raise McpClientError(fault_type, message)

    def _raise_recorded_fault(self):
        fault = self.faults[0]
        raise McpClientError(fault['faultType'], 'Inspect the original persisted client evidence; never replay a write.')

    def read_out(self):
        try:
            while True:
                line = self.process.stdout.readline(MAX_LINE_BYTES + 1)
                if not line:
                    self.stdout_eof_observed = True
                    self._event('stdout_eof')
                    self.lines.put(None)
                    return
                with self.lock:
                    offset = self.stdout_received_bytes
                    self.stdout_received_bytes += len(line)
                    self.stdout_frames += 1
                    reason = ('stdout_line_limit' if len(line) > MAX_LINE_BYTES else
                              'stdout_total_limit' if self.stdout_received_bytes > self.total_stdout_limit else None)
                    self.raw.write(line)
                    self._flush(self.raw)
                    frame = dict(frame=self.stdout_frames, offset=offset, byteCount=len(line),
                                 cumulativeBytes=self.stdout_received_bytes,
                                 sha256=hashlib.sha256(line).hexdigest().upper(),
                                 endsWithNewline=line.endswith(b'\n'),
                                 limitedLinePrefix=(len(line) == MAX_LINE_BYTES + 1 and not line.endswith(b'\n')),
                                 accepted=reason is None, faultType=reason)
                    self.frames.write(json.dumps(frame, allow_nan=False) + '\n')
                    self._flush(self.frames)
                    if reason is None:
                        self.stdout_accepted_bytes += len(line)
                if reason:
                    self._fault(reason, 'Received bounded stdout frame was persisted before rejection.')
                    self.lines.put(None)
                    return
                self.lines.put(line)
        except Exception as error:
            self._fault('stdout_read_error', '%s: %s' % (type(error).__name__, error))
            self.lines.put(None)

    def read_err(self):
        try:
            while True:
                data = self.process.stderr.read(4096)
                if not data:
                    self.stderr_eof_observed = True
                    self._event('stderr_eof')
                    return
                with self.lock:
                    self.stderr.extend(data)
                    self.stderr_received_bytes += len(data)
                    self.error_raw.write(data)
                    self._flush(self.error_raw)
                if self.stderr_received_bytes > MAX_STDERR_BYTES:
                    self._fault('stderr_total_limit', 'Bounded stderr capture limit exceeded.')
                    return
        except Exception as error:
            self._fault('stderr_read_error', '%s: %s' % (type(error).__name__, error))

    def request(self, method, params):
        if self.faults:
            self._raise_recorded_fault()
        if self.closed:
            raise McpClientError('client_closed', 'The original client is closed.')
        if self.count >= self.maximum:
            self._fail('request_limit', 'The original finite request allowance ended.')
        if time.monotonic() >= self.deadline:
            self._fail('absolute_deadline', 'The original absolute deadline ended.')
        self.count += 1
        request = dict(jsonrpc='2.0', id=self.count, method=method, params=params)
        self._event('request_dispatch', requestId=self.count, method=method)
        try:
            self.process.stdin.write((json.dumps(request, ensure_ascii=False) + '\n').encode('utf-8'))
            self.process.stdin.flush()
        except Exception as error:
            self._fail('stdin_write_failed', '%s: %s' % (type(error).__name__, error))
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            self._fail('absolute_deadline', 'Deadline ended after original dispatch; do not replay.')
        try:
            line = self.lines.get(timeout=min(20, remaining))
        except queue.Empty:
            self._fail('response_wait_timeout', 'No original response within the remaining bounded wait.')
        if line is None:
            if self.faults:
                self._raise_recorded_fault()
            self._fail('stdout_eof_before_response', 'EOF preceded this original response; do not replay.')
        try:
            response = json.loads(line)
        except Exception as error:
            self._fail('response_json_invalid', '%s: %s' % (type(error).__name__, error))
        self.log.write(json.dumps(dict(atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                      request=request, response=response), ensure_ascii=False) + '\n')
        self._flush(self.log)
        if (not isinstance(response, dict) or response.get('id') != self.count
                or response.get('jsonrpc') != '2.0' or 'error' in response or 'result' not in response):
            self._fail('mcp_protocol_error', 'Inspect the persisted original response.')
        return response['result']

    def call(self, name, arguments):
        result = self.request('tools/call', dict(name=name, arguments=arguments))
        return result.get('structuredContent', {}), result.get('isError', False)

    def initialize(self):
        initialized = self.request('initialize', dict(protocolVersion='2025-06-18', capabilities={},
                clientInfo=dict(name='Spherewright.LocalPackageCallability', version='1.0.0')))
        self.process.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        self.process.stdin.flush()
        tools = self.request('tools/list', {})['tools']
        resources = self.request('resources/list', {})['resources']
        resource = self.request('resources/read', dict(uri=URI))
        return initialized, tools, resources, resource

    def _finish_files(self):
        for stream in (self.log, self.raw, self.frames, self.events, self.error_raw):
            if not stream.closed:
                stream.close()

    def close(self):
        if self.closed:
            if self.faults:
                self._raise_recorded_fault()
            return self.evidence
        try:
            self.process.stdin.close()
            self.stdin_closed_by_client = True
        except Exception as error:
            self._fault('stdin_close_failed', '%s: %s' % (type(error).__name__, error))
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self._fault('mcp_child_termination_needed', 'Only this owned MCP child is terminated; never DSP or Steam.')
            try:
                self.process.kill()
            except Exception as error:
                self._fault('mcp_child_kill_failed', '%s: %s' % (type(error).__name__, error))
            else:
                try:
                    self.process.wait(timeout=5)
                except Exception as error:
                    self._fault('mcp_child_wait_failed', '%s: %s' % (type(error).__name__, error))
        except Exception as error:
            self._fault('mcp_child_wait_failed', '%s: %s' % (type(error).__name__, error))
        for thread in self.threads:
            thread.join(timeout=2)
        readers_stopped = all(not thread.is_alive() for thread in self.threads)
        if not readers_stopped:
            self._fault('reader_thread_not_stopped', 'A bounded reader did not stop after closing its own MCP child.')
        exit_code = self.process.poll()
        if exit_code is None:
            self._fault('mcp_exit_not_observed', 'Owned MCP exit remains unknown; never claim normal EOF.')
        elif exit_code != 0:
            self._fault('mcp_exit_nonzero', 'Owned MCP exit code: %s' % exit_code)
        self.evidence = dict(schemaVersion=1, requestCount=self.count, maximumRequests=self.maximum,
                totalStdoutLimitBytes=self.total_stdout_limit, lineLimitBytes=MAX_LINE_BYTES,
                stdoutReceivedBytes=self.stdout_received_bytes, stdoutAcceptedBytes=self.stdout_accepted_bytes,
                stdoutFrames=self.stdout_frames, stderrReceivedBytes=self.stderr_received_bytes,
                stdoutEofObserved=self.stdout_eof_observed, stderrEofObserved=self.stderr_eof_observed,
                stdinClosedByClient=self.stdin_closed_by_client, readerThreadsStopped=readers_stopped,
                ownedMcpChildPid=self.process.pid, processExitCode=exit_code,
                normalEof=bool(self.stdin_closed_by_client and self.stdout_eof_observed and self.stderr_eof_observed
                               and readers_stopped and exit_code == 0 and not self.faults),
                faults=list(self.faults), phaseClosed=True)
        with (self.directory / 'client-evidence.private.json').open('x', encoding='utf-8') as stream:
            json.dump(self.evidence, stream, ensure_ascii=False, indent=2, allow_nan=False)
            self._flush(stream)
        self.closed = True
        if readers_stopped:
            self._finish_files()
        if self.faults:
            self._raise_recorded_fault()
        return self.evidence
