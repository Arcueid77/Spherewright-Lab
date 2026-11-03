"""Exactly one detached writer. Inputs are immutable files, never Python packets."""
from pathlib import Path
import sys,json,datetime as dt
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import startup_to_action as gate
from runtime import Runtime
from factory import Factory
from evidence import put

def main():
    config,config_sha,output=sys.argv[1:]
    runtime=Runtime(config,config_sha,output);adapter=Factory(runtime)
    def emit(value):
        with (runtime.output/'timings.private.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(dict(atUtc=dt.datetime.now(dt.timezone.utc).isoformat(),**value))+'\n');f.flush()
    try:
        report=gate.run(adapter,emit)
        runtime.put('startup-report.private.json',gate.asdict(report))
    finally:
        if adapter.c is not None:
            runtime.put('client-close.private.json',adapter.c.close())

if __name__=='__main__':main()
