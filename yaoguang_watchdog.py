"""Independent monitor recovery if the GUI exits unexpectedly during standby."""

import ctypes
from ctypes import wintypes
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import shutil


def watchdog_main(parent_pid, directory):
    from yaoguang_native import WindowsDesktop
    from yaoguang_devices import restore_devices
    directory = Path(directory)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    parent = kernel32.OpenProcess(0x00100000, False, int(parent_pid))
    if not parent:
        return 1
    try:
        devices = json.loads((directory / "devices.json").read_text(encoding="utf-8"))
        (directory / "ready").touch()
        while True:
            result = kernel32.WaitForSingleObject(parent, 250)
            if result == 0 or (directory / "restore").exists():
                try:
                    WindowsDesktop().signal(-1)
                finally:
                    restore_devices(devices)
                return 0
            if result != 258:
                return 1
    finally:
        kernel32.CloseHandle(parent)
        shutil.rmtree(directory, ignore_errors=True)


class DisplayWatchdog:
    def __init__(self, device_ids):
        self.temporary = tempfile.TemporaryDirectory(prefix="yaoguang-watchdog-")
        self.directory = Path(self.temporary.name)
        (self.directory / "devices.json").write_text(json.dumps(device_ids), encoding="utf-8")
        if getattr(sys, "frozen", False):
            command = [sys.executable, "--watch-parent"]
        else:
            command = [sys.executable, "-B", str(Path(__file__).resolve()), "--watch-parent"]
        environment = os.environ.copy()
        environment["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        self.process = subprocess.Popen(
            command + [str(os.getpid()), str(self.directory)],
            env=environment, creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + 15
        while not (self.directory / "ready").exists():
            if self.process.poll() is not None or time.monotonic() >= deadline:
                self.close()
                raise RuntimeError("显示器恢复保护未启动，未进入下班模式。")
            time.sleep(0.05)

    def close(self):
        # Restore also on normal exit; it is safe if the GUI already restored.
        try:
            (self.directory / "restore").touch()
        except FileNotFoundError:
            pass  # An exited recovery helper may already have cleaned it up.
        try:
            self.process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            raise RuntimeError("显示器恢复保护未正常结束。")
        finally:
            if self.process.poll() is not None:
                self.temporary.cleanup()


if __name__ == "__main__":
    if sys.argv[1:2] != ["--watch-parent"] or len(sys.argv) != 4:
        raise SystemExit("This helper is started automatically by Yaoguang.")
    sys.exit(watchdog_main(sys.argv[2], sys.argv[3]))
