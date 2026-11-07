import ctypes,json,datetime,pathlib
from ctypes import wintypes
R=pathlib.Path(__file__).resolve().parent;k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE;k.CloseHandle.argtypes=[wintypes.HANDLE];k.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4;k.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)];k.TerminateProcess.argtypes=[wintypes.HANDLE,wintypes.UINT];out={'pid':8948};h=k.OpenProcess(0x1001,False,8948)
if not h:out.update(status='NOT OPENABLE',windows_error=ctypes.get_last_error())
else:
 b=ctypes.create_unicode_buffer(32768);n=wintypes.DWORD(len(b));assert k.QueryFullProcessImageNameW(h,0,b,ctypes.byref(n));times=[wintypes.FILETIME() for _ in range(4)];assert k.GetProcessTimes(h,*[ctypes.byref(t) for t in times]);t=(times[0].dwHighDateTime<<32)|times[0].dwLowDateTime;created=datetime.datetime.fromtimestamp((t-116444736000000000)/10000000,datetime.timezone.utc);freeze=datetime.datetime.fromisoformat(json.loads((R/'PRE-CONTROLS-SEAL.json').read_text())['utc'].replace('Z','+00:00'));out.update(image=b.value,created=created.isoformat(),freeze=freeze.isoformat());delta=(created-freeze).total_seconds()
 if b.value.lower().replace('\\','/').endswith('/codex-primary-runtime/dependencies/python/python.exe') and -1<=delta<=30:out.update(status='TERMINATED ORIGINAL STALLED WORKER' if k.TerminateProcess(h,1) else 'TERMINATE FAILED',windows_error=ctypes.get_last_error())
 else:out.update(status='IDENTITY/TIME DID NOT MATCH; NO TERMINATION')
 k.CloseHandle(h)
(R/'history/original-worker-stop.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
