"""Exercise the production OS capture using a harmless external process pair."""
from pathlib import Path
import datetime,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent));sys.dont_write_bytecode=True
from evidence import read,put,sha,need
import detached_python_task as launcher
from job_lifetime_capture import capture
from lifetime_contract import qualifies,cleanup_groups

out=Path(sys.argv[1]).resolve();steam_pid=int(sys.argv[2]);entry=ROOT/'lifetime_probe_task.py'
worker=out.parent/(out.name+'-worker')
launcher.launch_once(entry,sha(entry),[str(out)],worker,
 (datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=180)).isoformat(),
 transport='same_user_wmi',expected_inputs=[dict(path=str(entry),bytes=entry.stat().st_size,sha256=sha(entry))])
end=time.monotonic()+20
while not (out/'process.private.json').exists() and time.monotonic()<end:time.sleep(.1)
need((out/'process.private.json').exists(),'harmless_probe_start_unproved')
try:
    raw=capture(read(out/'process.private.json'),target_kind='probe',expected_image='python.exe',
        expected_parent_image='python.exe',extra_targets={'actual-steam':steam_pid})
    put(out/'complete-job-capture.private.json',raw)
    good=qualifies(raw,expected_target_kind='probe')
    steam_clear=all(j['memberships'].get('actual-steam') is False for j in cleanup_groups(raw))
    put(out/'qualification.private.json',dict(passed=good and steam_clear,gameCalls=0,actualGameOpened=False,
        scopeProcesses=len(raw['scopePids']),observedCleanupGroups=len(cleanup_groups(raw)),
        observedActualSteamOutsideCleanupJobs=steam_clear,productionGameCertificate=False))
    need(good and steam_clear,'actual_harmless_OS_probe_did_not_qualify')
    print('Complete OS ownership/membership capture and actual Steam isolation verified without opening the game.')
finally:(out/'stop.private.flag').write_text('normal probe stop',encoding='utf-8')
