"""Harmless bounded OS lifetime probe. Never opens or calls the game."""
import ctypes,os,sys,time,subprocess
from pathlib import Path
from ctypes import wintypes as w
sys.path.insert(0,str(Path(__file__).resolve().parent))
from evidence import put
sys.dont_write_bytecode=True
if len(sys.argv)==2:
    child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--child',sys.argv[1]],
        stdin=subprocess.DEVNULL,creationflags=0x08000000)
    raise SystemExit(child.wait(timeout=125))
if len(sys.argv)!=3 or sys.argv[1]!='--child':raise RuntimeError('invalid_probe_arguments')
out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=w.HANDLE
k.GetProcessTimes.argtypes=[w.HANDLE,*([ctypes.POINTER(w.FILETIME)]*4)];k.GetProcessTimes.restype=w.BOOL
values=[w.FILETIME() for _ in range(4)]
if not k.GetProcessTimes(k.GetCurrentProcess(),*[ctypes.byref(v) for v in values]):raise RuntimeError('probe_identity_unavailable')
put(out/'process.private.json',dict(Id=os.getpid(),Path=sys.executable,
 createdFileTime=(values[0].dwHighDateTime<<32)|values[0].dwLowDateTime,gameCalls=0))
end=time.monotonic()+120
while time.monotonic()<end and not (out/'stop.private.flag').exists():time.sleep(.1)
put(out/'completed.private.json',dict(gameCalls=0,normalStopRequested=(out/'stop.private.flag').exists()))
