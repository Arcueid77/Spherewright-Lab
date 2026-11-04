"""Detach one writer, prove OS lifetime separation, then return its progress path."""
from pathlib import Path
import sys,datetime as dt,time,subprocess
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
import detached_python_task as launcher
from evidence import sha,read,need,put
from mcp_client import validate_limits,MAX_STDOUT_BYTES,MAX_STDERR_BYTES

def main():
    attaching=sys.argv[1]=='--attach'
    if attaching:previous,config,config_sha,output=sys.argv[2:]
    else:config,config_sha,output=sys.argv[1:]
    # The detached worker deliberately starts beside its entry point. Freeze
    # caller paths before crossing that working-directory boundary.
    config=str(Path(config).resolve());output=str(Path(output).resolve())
    if attaching:previous=str(Path(previous).resolve())
    c=read(config);out=Path(output)
    validate_limits(c['maximumRpc'],c['maximumWallSeconds'],c.get('maximumStdoutBytes',MAX_STDOUT_BYTES),c.get('maximumStderrBytes',MAX_STDERR_BYTES))
    need(sha(config)==config_sha.upper() and not out.exists(),'config_changed_or_prior_run_exists')
    worker=out.parent/(out.name+'-worker')
    inputs=[Path(config),*ROOT.glob('*.py'),ROOT.parent/'startup_to_action.py',ROOT.parent/'geometry_request.py']
    deadline=dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=c['maximumWallSeconds']+60)
    entry=ROOT/('attach.py' if attaching else 'run.py')
    arguments=[config,config_sha,previous,output] if attaching else [config,config_sha,output]
    if attaching:inputs.extend(Path(previous)/name for name in ('caller-handoff.private.json','client-close.private.json') if (Path(previous)/name).exists())
    result=launcher.launch_once(entry,sha(entry),arguments,worker,deadline.isoformat(),
        transport='same_user_wmi',expected_inputs=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in inputs])
    end=time.monotonic()+300
    while time.monotonic()<end:
        if attaching and (out/'attached-existing-session.private.json').exists():
            print('One replacement caller attached to the original healthy game; no Load/Save/relaunch.',flush=True);return
        if (out/'process-observed.private.json').exists():
            audit=subprocess.run([sys.executable,str(ROOT/'audit-lifetime.py'),str(out)],capture_output=True,text=True,timeout=45)
            put(out/'lifetime-audit-process.private.json',dict(exitCode=audit.returncode,
                stdout=audit.stdout[:65536],stderr=audit.stderr[:65536],
                outputTruncated=len(audit.stdout)>65536 or len(audit.stderr)>65536))
            need(audit.returncode==0,'actual_lifetime_audit_failed_no_relaunch')
            print('One writer launched; actual game lifetime separation verified.',flush=True);return
        if (worker/'worker-failure.private.json').exists():raise RuntimeError('original_writer_failed_before_game_process_no_replay')
        time.sleep(.25)
    raise RuntimeError('original_launch_pending_no_relaunch')

if __name__=='__main__':main()
