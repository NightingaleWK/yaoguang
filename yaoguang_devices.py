"""Temporarily pause Mouse-class devices; never touch Keyboard-class or USB parents."""

import ctypes
from ctypes import wintypes
import uuid
import time


class GUID(ctypes.Structure):
    _fields_ = [("data", wintypes.BYTE * 16)]


class SP_DEVINFO_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD), ("classGuid", GUID),
        ("devInst", wintypes.DWORD), ("reserved", ctypes.c_size_t),
    ]


class WindowsMouseApi:
    def __init__(self):
        self.setup = ctypes.WinDLL("setupapi", use_last_error=True)
        self.cm = ctypes.WinDLL("cfgmgr32", use_last_error=True)
        self.setup.SetupDiGetClassDevsW.argtypes = [ctypes.POINTER(GUID), wintypes.LPCWSTR, wintypes.HWND, wintypes.DWORD]
        self.setup.SetupDiGetClassDevsW.restype = wintypes.HANDLE
        self.setup.SetupDiEnumDeviceInfo.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(SP_DEVINFO_DATA)]
        self.setup.SetupDiEnumDeviceInfo.restype = wintypes.BOOL
        self.setup.SetupDiGetDeviceInstanceIdW.argtypes = [wintypes.HANDLE, ctypes.POINTER(SP_DEVINFO_DATA), wintypes.LPWSTR, wintypes.DWORD, ctypes.c_void_p]
        self.setup.SetupDiGetDeviceInstanceIdW.restype = wintypes.BOOL
        self.setup.SetupDiDestroyDeviceInfoList.argtypes = [wintypes.HANDLE]
        self.cm.CM_Get_DevNode_Status.argtypes = [ctypes.POINTER(wintypes.ULONG), ctypes.POINTER(wintypes.ULONG), wintypes.DWORD, wintypes.ULONG]
        self.cm.CM_Get_DevNode_Status.restype = wintypes.ULONG
        self.cm.CM_Disable_DevNode.argtypes = [wintypes.DWORD, wintypes.ULONG]
        self.cm.CM_Disable_DevNode.restype = wintypes.ULONG
        self.cm.CM_Enable_DevNode.argtypes = [wintypes.DWORD, wintypes.ULONG]
        self.cm.CM_Enable_DevNode.restype = wintypes.ULONG

    def enumerate(self):
        mouse_class = GUID.from_buffer_copy(uuid.UUID("4d36e96f-e325-11ce-bfc1-08002be10318").bytes_le)
        handle = self.setup.SetupDiGetClassDevsW(ctypes.byref(mouse_class), None, None, 2)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        result = []
        try:
            index = 0
            while True:
                item = SP_DEVINFO_DATA()
                item.cbSize = ctypes.sizeof(item)
                if not self.setup.SetupDiEnumDeviceInfo(handle, index, ctypes.byref(item)):
                    if ctypes.get_last_error() != 259:
                        raise ctypes.WinError(ctypes.get_last_error())
                    break
                name = ctypes.create_unicode_buffer(1024)
                if not self.setup.SetupDiGetDeviceInstanceIdW(handle, ctypes.byref(item), name, len(name), None):
                    raise ctypes.WinError(ctypes.get_last_error())
                status, problem = wintypes.ULONG(), wintypes.ULONG()
                code = self.cm.CM_Get_DevNode_Status(ctypes.byref(status), ctypes.byref(problem), item.devInst, 0)
                if code != 0:
                    raise RuntimeError(f"读取鼠标状态失败：CONFIGRET={code:#x}")
                result.append({"id": name.value, "devinst": item.devInst, "started": bool(status.value & 8), "problem": problem.value})
                index += 1
        finally:
            self.setup.SetupDiDestroyDeviceInfoList(handle)
        return result

    def disable(self, device):
        # UI_NOT_OK only. Deliberately omit CM_DISABLE_PERSIST: reboot reenables.
        code = self.cm.CM_Disable_DevNode(device["devinst"], 1)
        if code != 0:
            raise RuntimeError(f"临时暂停鼠标失败：CONFIGRET={code:#x}。请以管理员身份运行。")

    def enable(self, device):
        code = self.cm.CM_Enable_DevNode(device["devinst"], 0)
        if code != 0:
            raise RuntimeError(f"恢复鼠标失败：CONFIGRET={code:#x}")


class MouseDevices:
    def __init__(self):
        self.api = WindowsMouseApi()
        self.devices = [device for device in self.api.enumerate() if device["started"] and device["problem"] == 0]
        self.pending = []

    @property
    def ids(self):
        return [device["id"] for device in self.devices]

    def suspend(self):
        if not self.devices:
            raise RuntimeError("未找到可临时暂停的鼠标设备，未进入下班模式。")
        try:
            for device in self.devices:
                # Include the attempted device in rollback even on API failure.
                self.pending.append(device["id"])
                self.api.disable(device)
            current = {item["id"]: item for item in self.api.enumerate()}
            if any(current.get(name, {}).get("problem") != 22 for name in self.ids):
                raise RuntimeError("鼠标设备未全部进入暂停状态，未进入下班模式。")
        except Exception:
            self.restore()
            raise

    def restore(self):
        restore_devices(self.pending, self.api)
        self.pending.clear()


def restore_devices(names, api=None):
    api = api if api is not None else WindowsMouseApi()
    # Re-enumerate by the Mouse class; arbitrary IDs and Keyboard devices cannot
    # be enabled through the recovery channel. Preserve initially disabled mice.
    current = {item["id"]: item for item in api.enumerate()}
    errors = []
    for name in names:
        device = current.get(name)
        if device is not None and device["problem"] == 22:
            try:
                api.enable(device)
            except Exception as error:
                errors.append(error)
    if errors:
        raise errors[0]
    for attempt in range(30):
        states = {item["id"]: item for item in api.enumerate()}
        if all(name not in states or states[name]["problem"] != 22 for name in names):
            return
        time.sleep(0.1)
    raise RuntimeError("鼠标恢复尚未完成，请重试恢复或退出程序。")
