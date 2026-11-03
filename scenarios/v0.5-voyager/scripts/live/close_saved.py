"""Normal Native exit after an explicit healthy Save and caller-only handoff."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from evidence import read,need
from runtime import Runtime
from driver import Live

def main():
 config,config_sha,original_output,output=sys.argv[1:];origin=Path(original_output)
 handoff=read(origin/'caller-handoff.private.json');closed=read(origin/'client-close.private.json')
 need(handoff['noActiveGameAction'] and handoff['gameProcessRetained'] and closed['normalEof'],'healthy_caller_handoff_unproved')
 r=Runtime(config,config_sha,output);r.cohort()
 saves=[read(p) for p in origin.glob('terminal-*.private.json')]
 need(any(x.get('actionKind')=='save' and x.get('succeeded') and x.get('terminal')
     and x.get('completedAtGameTick',-1)>=r.config['sourceTick'] for x in saves),'current_normal_save_unproved')
 game_origin=Path(r.config.get('liveSessionOrigin',str(origin)))
 a=Live(r);a.pid=read(game_origin/'process-observed.private.json')['Id'];a.normal_close_current_process()

if __name__=='__main__':main()
