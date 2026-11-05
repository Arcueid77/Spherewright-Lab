"""Read-only preflight in the external writer's filesystem/process context."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime import Runtime

config,config_sha,output=sys.argv[1:]
r=Runtime(config,config_sha,output)
try:
    r.stopped();r.cohort();r.verify_revision_stamps();m=r.verify_backup()
    r.put('qualification.private.json',dict(passed=True,sourceSha=r.config['sourceSha'],
        completeBackupFiles=len(m['rows']),gameCalls=0,gameOpened=False))
except Exception as error:
    r.put('failure.private.json',dict(error=str(error),gameCalls=0,gameOpened=False))
    raise
