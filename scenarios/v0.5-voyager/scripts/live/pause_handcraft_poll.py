"""Pause only a proved owned Python poller while its original forge task runs.

No game/MCP suspension, game writes, new action, counter reset or config edit.
The Native action continues; a separate read-only observer settles its exact ID.
The same caller is always resumed in finally, including observation failures.
"""
import ctypes
from ctypes import wintypes
from pathlib import Path
import json,os,subprocess,sys,time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from evidence import read,sha,need
from runtime import Runtime
from driver import Live
from mcp_client import Client
from contracts import validate_native_calls


class ProcessPause:
 def __init__(self,pid,created_filetime):
  need(os.name=='nt' and type(pid)is int and pid>0 and pid!=os.getpid(),'exact_other_windows_process_required')
  self.kernel=ctypes.WinDLL('kernel32',use_last_error=True);self.native=ctypes.WinDLL('ntdll')
  self.kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];self.kernel.OpenProcess.restype=wintypes.HANDLE
  self.kernel.CloseHandle.argtypes=[wintypes.HANDLE];self.kernel.CloseHandle.restype=wintypes.BOOL
  self.kernel.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4
  self.kernel.GetProcessTimes.restype=wintypes.BOOL
  for name in ('NtSuspendProcess','NtResumeProcess'):
   method=getattr(self.native,name);method.argtypes=[wintypes.HANDLE];method.restype=wintypes.LONG
  self.handle=self.kernel.OpenProcess(0x1800,False,pid);self.suspended=False
  if not self.handle:raise ctypes.WinError(ctypes.get_last_error())
  try:
   times=[wintypes.FILETIME() for _ in range(4)]
   if not self.kernel.GetProcessTimes(self.handle,*[ctypes.byref(t) for t in times]):raise ctypes.WinError(ctypes.get_last_error())
   actual=(times[0].dwHighDateTime<<32)|times[0].dwLowDateTime
   need(actual==created_filetime,'caller_pid_reused_no_suspension')
  except BaseException:self.close();raise
 def suspend(self):
  need(self.handle and not self.suspended,'caller_already_suspended_or_closed')
  status=self.native.NtSuspendProcess(self.handle)
  need(status==0,'owned_caller_suspend_failed:'+str(status));self.suspended=True
 def resume(self):
  if self.suspended:
   status=self.native.NtResumeProcess(self.handle)
   need(status==0,'owned_caller_resume_failed:'+str(status));self.suspended=False
 def close(self):
  try:self.resume()
  finally:
   if self.handle:self.kernel.CloseHandle(self.handle);self.handle=None


def owned_caller(prior):
 control=prior.parent/(prior.name+'-worker')/'intent.private.json'
 intent=read(control);need(Path(intent['script']).name in ('run.py','attach.py')
  and Path(intent['arguments'][-1]).resolve()==prior,'owned_writer_intent_unproved')
 command="""$rows=@();foreach($m in @(Get-CimInstance Win32_Process -Filter \"Name='Spherewright.Mcp.exe'\")){$p=Get-CimInstance Win32_Process -Filter ('ProcessId='+$m.ParentProcessId);if($p.Name -eq 'python.exe'){$q=Get-Process -Id $p.ProcessId;$rows+=@{Id=[int]$p.ProcessId;Name=$p.Name;CommandLine=$p.CommandLine;createdFileTime=$q.StartTime.ToFileTimeUtc();mcpId=[int]$m.ProcessId}}};ConvertTo-Json -InputObject @($rows) -Compress"""
 rows=json.loads(subprocess.check_output(['powershell.exe','-NoProfile','-NonInteractive','-Command',command],text=True,creationflags=0x08000000))
 rows=[p for p in rows if str(control).lower() in p['CommandLine'].lower() and sha(control) in p['CommandLine'].upper()]
 need(len(rows)==1 and rows[0]['Id']!=os.getpid(),'unique_exact_owned_caller_unproved')
 return rows[0]


def main():
 config,digest,prior,role,recipe,output=sys.argv[1:];prior=Path(prior).resolve();recipe=int(recipe)
 need(role and all(c.isalnum() or c in '-_' for c in role) and recipe>0,'exact_original_handcraft_role_required')
 r=Runtime(config,digest,output);r.cohort();a=Live(r);pause=None;observed=False
 end=time.monotonic()+7200
 accepted=prior/(role+'-accepted.private.json')
 while not accepted.exists():
  need(time.monotonic()<end and not(prior/'client-close.private.json').exists(),'original_caller_not_ready')
  if(r.output/'resume-request.private.flag').exists():return
  time.sleep(.5)
 original=read(accepted)['actionId'];owner=owned_caller(prior)
 a.c=Client(Path(r.config['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'observer',maximum=300,seconds=3900)
 try:
  _,tools,_,_=a.c.initialize();schemas={t['name']:t['inputSchema'] for t in tools}
  validate_native_calls([dict(kind='read',tool='spherewright_get_session_state',arguments={}),
   dict(kind='read',tool='spherewright_get_action_result',arguments=dict(actionId=original))],schemas)
  state=a.call('spherewright_get_session_state',{});origin=read(Path(r.config['liveSessionOrigin'])/'loaded-session.private.json')
  need(state['sessionId']==origin['sessionId'] and state['gameLoaded'] and state['ownedBySpherewright'] and state['writesAllowed']
   and state['localPlanetId']==r.config['attachmentPlanetId']
   and state['localPlanetId'] in r.config.get('ordinaryConstructionPlanetIds',[]),'original_healthy_home_world_unproved')
  current=a.call('spherewright_get_action_result',dict(actionId=original))
  need(current['actionId']==original and current['actionKind']=='handcraft','original_forge_action_unproved')
  if current['terminal']:
   r.put('already-terminal-no-suspension.private.json',current);return
  player_args=dict(sessionId=state['sessionId'],planetId=state['localPlanetId'])
  validate_native_calls([dict(kind='read',tool='spherewright_get_player_state',arguments=player_args)],schemas)
  player=a.call('spherewright_get_player_state',player_args)
  need(any(t['recipeId']==recipe for t in player['handcraftQueue']),'original_forge_recipe_not_running')
  r.put('caller-poll-pause-intent.private.json',dict(originalActionId=original,caller=owner,recipeId=recipe,
   gameProcessUntouched=True,mcpProcessUntouched=True,allOriginalLimitsAndCountersPreserved=True,
   nativeActionContinues=True,maximumSuspensionSeconds=3600,pollSeconds=15))
  pause=ProcessPause(owner['Id'],owner['createdFileTime']);pause.suspend()
  r.put('caller-poll-paused.private.json',dict(passed=True,gameNotPaused=True,originalActionId=original))
  deadline=time.monotonic()+3600;sample=0
  while time.monotonic()<deadline:
   result=a.call('spherewright_get_action_result',dict(actionId=original));sample+=1
   need(result['actionId']==original and result['actionKind']=='handcraft','observed_original_action_changed')
   r.put(f'original-action-observation-{sample:03d}.private.json',result)
   if result['terminal']:
    r.put('original-action-terminal-observed.private.json',result);observed=True;break
   until=time.monotonic()+15
   while time.monotonic()<until:
    if(r.output/'resume-request.private.flag').exists():return
    time.sleep(.5)
  need(observed,'finite_original_action_wait_ended_resume_same_caller')
 finally:
  if pause is not None:
   pause.close();r.put('same-caller-resumed.private.json',dict(passed=True,callerId=owner['Id'],originalActionId=original,
    originalTerminalObserved=observed,noNewGameAction=True,noSave=True,noLoad=True,noReplay=True))
  r.put('observer-client-close.private.json',a.c.close())


if __name__=='__main__':main()
