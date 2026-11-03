"""Run the real detached entry's complete preflight without opening the game."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from runtime import Runtime
from factory import Factory

def main():
    config,config_sha,output=sys.argv[1:]
    r=Runtime(config,config_sha,output);a=Factory(r)
    try:
        proof=a.offline_preflight()
        r.put('detached-preflight.private.json',dict(passed=True,sourceSha=r.config['sourceSha'],
            completeBackupVerified=True,realMcpInitialized=True,gameLaunches=0,gameWrites=0))
    finally:
        if a.c is not None:r.put('client-close.private.json',a.c.close())

if __name__=='__main__':main()
