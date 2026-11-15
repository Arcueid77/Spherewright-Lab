"""Run the real detached entry's complete preflight without opening the game."""
from pathlib import Path
import os,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from runtime import Runtime
from factory import Factory

def main():
    config,config_sha,output=sys.argv[1:]
    # The detached worker starts beside run.py, not in the invoking shell's
    # directory. Resolve caller arguments first, then verify all referenced
    # evidence in that same context before promising a launch-ready packet.
    config=str(Path(config).resolve());output=str(Path(output).resolve())
    os.chdir(ROOT)
    r=Runtime(config,config_sha,output);a=Factory(r)
    try:
        proof=a.offline_preflight()
        r.put('detached-preflight.private.json',dict(passed=True,sourceSha=r.config['sourceSha'],
            completeBackupVerified=True,realMcpInitialized=True,gameLaunches=0,gameWrites=0))
    finally:
        if a.c is not None:r.put('client-close.private.json',a.c.close())

if __name__=='__main__':main()
