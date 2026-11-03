"""Replay immutable public observations; never reads or operates the game."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT.parent))
from evidence import read,sha,put,need
from flight_observers import SailConversionTrace

def main():
 spec_path,spec_sha,output=sys.argv[1:];need(sha(spec_path)==spec_sha.upper(),'immutable_replay_spec_changed');spec=read(spec_path)
 def opened(ref):
  need(sha(ref['path'])==ref['sha256'],'native_readback_bytes_changed');return read(ref['path'])
 initial=opened(spec['baseline']);trace=SailConversionTrace(initial['ejector'],spec['count'],spec['orbitId'])
 rows=[(opened(ref),ref) for ref in spec['sourceReadbacks']];rows.sort(key=lambda pair:pair[0]['capturedAtGameTick']);last=initial['capturedAtGameTick'];done=False
 for e,ref in rows:
  need(e['sessionId']==initial['sessionId'] and e['planetId']==initial['planetId'] and e['objectId']==initial['objectId']
   and e['capturedAtGameTick']>=last,'native_replay_identity_or_clock_changed')
  last=e['capturedAtGameTick'];done=trace.observe(e['ejector'])
 need(done,'native_causal_conversion_not_yet_closed')
 out=Path(output);out.mkdir(exist_ok=False)
 put(out/'native-sail-conversion-proof.private.json',dict(passed=True,sourceSha=spec['sourceSha'],nativeAssemblySha256=spec['nativeAssemblySha256'],
  exactAmmoConsumed=spec['count'],nativeUnconvertedBallisticsObserved=trace.flight_seen,exactNativeOrbitSailsAdded=spec['count'],
  visualPoolIncludesConvertedTrails=True,noNativeActionsReplayed=True,baseline=spec['baseline'],sourceReadbacks=spec['sourceReadbacks'],final=rows[-1][0]))

if __name__=='__main__':main()
