"""Windows display control and temporary mouse suppression while the screen is off."""

import ctypes
from ctypes import wintypes
import threading


LRESULT = ctypes.c_ssize_t
WPARAM = ctypes.c_size_t
LPARAM = ctypes.c_ssize_t
HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, WPARAM, LPARAM)


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD), ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class WindowsDesktop:
    def __init__(self):
        self.mouse = None
        self.watchdog = None
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.user32.SendMessageTimeoutW.argtypes = [
            wintypes.HWND, wintypes.UINT, WPARAM, LPARAM,
            wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_size_t),
        ]
        self.user32.SendMessageTimeoutW.restype = LRESULT
        self.user32.GetLastInputInfo.argtypes = [ctypes.POINTER(LASTINPUTINFO)]
        self.user32.GetLastInputInfo.restype = wintypes.BOOL
        self.kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        self.kernel32.CreateMutexW.restype = wintypes.HANDLE
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL
        self.kernel32.SetThreadExecutionState.argtypes = [wintypes.DWORD]
        self.kernel32.SetThreadExecutionState.restype = wintypes.DWORD
        self.user32.CreateWindowExW.argtypes = [
            wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, ctypes.c_void_p,
        ]
        self.user32.CreateWindowExW.restype = wintypes.HWND
        self.user32.DestroyWindow.argtypes = [wintypes.HWND]
        self.user32.DestroyWindow.restype = wintypes.BOOL
        # One private standard window handles SC_MONITORPOWER directly using
        # DefWindowProc, without depending on every other application's
        # window procedure to respond to a global broadcast.
        self._power_window = self.user32.CreateWindowExW(
            0, "STATIC", "Yaoguang display control", 0,
            0, 0, 0, 0, None, None, None, None,
        )
        if not self._power_window:
            raise ctypes.WinError(ctypes.get_last_error())

    def signal(self, level):
        if level == -1:
            # One-time idle reset. Do not create a persistent display-on request.
            if not self.kernel32.SetThreadExecutionState(0x00000002):
                raise ctypes.WinError(ctypes.get_last_error())
        result = ctypes.c_size_t()
        if not self.user32.SendMessageTimeoutW(
            self._power_window, 0x0112, 0xF170, level, 0x0002, 1000, ctypes.byref(result)
        ):
            raise ctypes.WinError(ctypes.get_last_error() or 1460)

    def display(self, level):
        if level == 2:
            from yaoguang_devices import MouseDevices
            from yaoguang_watchdog import DisplayWatchdog
            if self.watchdog is not None:
                self.watchdog.close()
                self.watchdog = None
            self.mouse = MouseDevices()
            # Snapshot and arm independent recovery BEFORE pausing any device.
            self.watchdog = DisplayWatchdog(self.mouse.ids)
            try:
                self.mouse.suspend()
                self.signal(2)
            except Exception:
                self.display(-1)
                raise
        else:
            try:
                if self.mouse is not None:
                    self.mouse.restore()
            finally:
                self.signal(-1)

    def close(self):
        try:
            if self.mouse is not None:
                try:
                    self.display(-1)
                finally:
                    self.mouse = None
        finally:
            try:
                if self.watchdog is not None:
                    self.watchdog.close()
                    self.watchdog = None
            finally:
                if self._power_window:
                    self.user32.DestroyWindow(self._power_window)
                    self._power_window = None

    def last_input(self):
        info = LASTINPUTINFO(ctypes.sizeof(LASTINPUTINFO), 0)
        if not self.user32.GetLastInputInfo(ctypes.byref(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        return info.dwTime

    def acquire_instance(self):
        handle = self.kernel32.CreateMutexW(None, False, "Local\\Yaoguang.KeyboardWake")
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        if ctypes.get_last_error() == 183:
            self.kernel32.CloseHandle(handle)
            return None
        return handle

    def release_instance(self, handle):
        self.kernel32.CloseHandle(handle)


class KeyboardWakeGuard:
    """Pump input hooks on a dedicated thread; consume the first wake key.

    Every mouse event is discarded only while armed. A keyboard key-down
    releases the mouse immediately. No key content is stored or logged.
    """

    def __init__(self):
        self._user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
        self._user32.SetWindowsHookExW.restype = wintypes.HANDLE
        self._user32.CallNextHookEx.argtypes = [wintypes.HANDLE, ctypes.c_int, WPARAM, LPARAM]
        self._user32.CallNextHookEx.restype = LRESULT
        self._user32.UnhookWindowsHookEx.argtypes = [wintypes.HANDLE]
        self._user32.UnhookWindowsHookEx.restype = wintypes.BOOL
        self._user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
        self._user32.GetMessageW.restype = wintypes.BOOL
        self._user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]
        self._user32.PeekMessageW.restype = wintypes.BOOL
        self._user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, WPARAM, LPARAM]
        self._user32.PostThreadMessageW.restype = wintypes.BOOL
        self._kernel32.GetCurrentThreadId.restype = wintypes.DWORD
        self._kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        self._kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        self._thread = None
        self._thread_id = 0
        self._ready = threading.Event()
        self._woken = threading.Event()
        self._armed = False
        self._error = None
        self._wake_key = None
        self._mouse_proc = HOOKPROC(self._mouse_event)
        self._keyboard_proc = HOOKPROC(self._keyboard_event)

    def arm(self):
        self.close()
        self._ready.clear()
        self._woken.clear()
        self._error = None
        self._wake_key = None
        self._armed = True
        self._thread = threading.Thread(target=self._run, name="yaoguang-input", daemon=True)
        self._thread.start()
        if not self._ready.wait(3):
            self.close()
            raise RuntimeError("输入保护启动超时，未进入下班模式。")
        if self._error is not None:
            self.close()
            raise self._error

    def take_wake(self):
        if self._woken.is_set():
            self._woken.clear()
            return True
        return False

    def close(self):
        self._armed = False
        if self._thread is not None and self._thread.is_alive():
            if self._thread_id:
                self._user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)
            self._thread.join(timeout=3)
            if self._thread.is_alive():
                raise RuntimeError("输入保护线程未正常退出，请退出程序后重试。")
        self._thread = None
        self._thread_id = 0

    def _mouse_event(self, code, message, data):
        if code >= 0 and self._armed:
            return 1
        return self._user32.CallNextHookEx(None, code, message, data)

    def _keyboard_event(self, code, message, data):
        if code >= 0:
            key = ctypes.cast(data, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents.vkCode
            if self._armed and message in (0x0100, 0x0104):
                self._wake_key = key
                self._armed = False
                self._woken.set()
                return 1
            if key == self._wake_key:
                if message in (0x0101, 0x0105):
                    self._wake_key = None
                return 1
        return self._user32.CallNextHookEx(None, code, message, data)

    def _run(self):
        hooks = []
        try:
            message = wintypes.MSG()
            self._user32.PeekMessageW(ctypes.byref(message), None, 0, 0, 0)
            self._thread_id = self._kernel32.GetCurrentThreadId()
            module = self._kernel32.GetModuleHandleW(None)
            for kind, callback in ((14, self._mouse_proc), (13, self._keyboard_proc)):
                hook = self._user32.SetWindowsHookExW(kind, callback, module, 0)
                if not hook:
                    raise ctypes.WinError(ctypes.get_last_error())
                hooks.append(hook)
            self._ready.set()
            while True:
                result = self._user32.GetMessageW(ctypes.byref(message), None, 0, 0)
                if result == 0:
                    break
                if result == -1:
                    raise ctypes.WinError(ctypes.get_last_error())
        except Exception as error:
            self._error = error
            self._armed = False
            self._woken.set()
        finally:
            self._armed = False
            for hook in reversed(hooks):
                self._user32.UnhookWindowsHookEx(hook)
            self._ready.set()
