"""Explicit expired startup preservation, only before any world was loaded."""
from pathlib import Path
import sys,datetime as dt
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from runtime import Runtime
from driver import Live
from mcp_client import Client
from evidence import read,need

def main():
 config,config_sha,original_output,output=sys.argv[1:];origin=Path(original_output)
 closed=read(origin/'client-close.private.json');report=read(origin/'startup-report.private.json');intent=read(origin/'launch-intent.private.json')
 need(closed['normalEof'] and closed['processExitCode']==0 and not report['passed'] and not report['unresolved_commit'],'original_caller_not_closed')
 need(not list(origin.glob('*-accepted.private.json')) and not (origin/'loaded-session.private.json').exists(),'world_or_action_already_accepted')
 start=dt.datetime.fromisoformat(intent['startedAtUtc']);need((dt.datetime.now(dt.timezone.utc)-start).total_seconds()>300,'startup_clock_not_expired')
 r=Runtime(config,config_sha,output);r.cohort();a=Live(r);a.pid=read(origin/'process-observed.private.json')['Id']
 a.c=Client(Path(r.config['pluginDestination'])/'Spherewright.Mcp.exe',r.output/'client',maximum=10,seconds=30)
 try:
  a.c.initialize();s=a.call('spherewright_get_session_state',{});need(s['gameLoaded'] is False,'a_world_is_loaded_no_automatic_exit')
  r.put('empty-menu-verified.private.json',dict(gameLoaded=False,noAcceptedAction=True,expiredStartupPreserved=True,noSave=True,noLoad=True))
 finally:r.put('client-close.private.json',a.c.close());a.c=None
 a.normal_close_current_process()

if __name__=='__main__':main()
