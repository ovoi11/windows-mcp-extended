import comtypes.client
from comtypes import GUID, IUnknown, COMMETHOD
from ctypes import POINTER
from ctypes.wintypes import HWND, BOOL
import logging
import threading
import sys
import ctypes
from ctypes import HRESULT, c_void_p, byref
from ctypes.wintypes import UINT
from comtypes import STDMETHOD

logger = logging.getLogger(__name__)

_thread_local = threading.local()


def _get_manager():
    if not hasattr(_thread_local, "manager"):
        _thread_local.manager = VirtualDesktopManager()
    return _thread_local.manager


def is_window_on_current_desktop(hwnd: int) -> bool:
    return _get_manager().is_window_on_current_desktop(hwnd)


def get_window_desktop_id(hwnd: int) -> str:
    return _get_manager().get_window_desktop_id(hwnd)


def move_window_to_desktop(hwnd: int, desktop_id: str):
    _get_manager().move_window_to_desktop(hwnd, desktop_id)


CLSID_VirtualDesktopManager = GUID("{aa509086-5ca9-4c25-8f95-589d3c07b48a}")


class IVirtualDesktopManager(IUnknown):
    _iid_ = GUID("{a5cd92ff-29be-454c-8d04-d82879fb3f1b}")
    _methods_ = [
        COMMETHOD(
            [],
            HRESULT,
            "IsWindowOnCurrentVirtualDesktop",
            (["in"], HWND, "topLevelWindow"),
            (["out", "retval"], POINTER(BOOL), "onCurrentDesktop"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetWindowDesktopId",
            (["in"], HWND, "topLevelWindow"),
            (["out", "retval"], POINTER(GUID), "desktopId"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "MoveWindowToDesktop",
            (["in"], HWND, "topLevelWindow"),
            (["in"], POINTER(GUID), "desktopId"),
        ),
    ]


CLSID_ImmersiveShell = GUID("{C2F03A33-21F5-47FA-B4BB-156362A2F239}")
CLSID_VirtualDesktopManagerInternal = GUID("{C5E0CDCA-7B6E-41B2-9FC4-D93975CC467B}")
IID_IServiceProvider = GUID("{6D5140C1-7436-11CE-8034-00AA006009FA}")


class IServiceProvider(IUnknown):
    _iid_ = IID_IServiceProvider
    _methods_ = [
        COMMETHOD(
            [],
            HRESULT,
            "QueryService",
            (["in"], POINTER(GUID), "guidService"),
            (["in"], POINTER(GUID), "riid"),
            (["out"], POINTER(POINTER(IUnknown)), "ppvObject"),
        ),
    ]


class IObjectArray(IUnknown):
    _iid_ = GUID("{92CA9DCD-5622-4BBA-A805-5E9F541BD8CC}")
    _methods_ = [
        COMMETHOD([], HRESULT, "GetCount", (["out"], POINTER(UINT), "pcObjects")),
        COMMETHOD(
            [],
            HRESULT,
            "GetAt",
            (["in"], UINT, "uiIndex"),
            (["in"], POINTER(GUID), "riid"),
            (["out"], POINTER(POINTER(IUnknown)), "ppv"),
        ),
    ]


class HSTRING(c_void_p):
    pass


try:
    _combase = ctypes.windll.combase
    _WindowsCreateString = _combase.WindowsCreateString
    _WindowsCreateString.argtypes = [ctypes.c_wchar_p, UINT, POINTER(HSTRING)]
    _WindowsCreateString.restype = HRESULT
    _WindowsDeleteString = _combase.WindowsDeleteString
    _WindowsDeleteString.argtypes = [HSTRING]
    _WindowsDeleteString.restype = HRESULT
except Exception:
    _WindowsCreateString = None
    _WindowsDeleteString = None


def create_hstring(text):
    if not _WindowsCreateString:
        return HSTRING(0)
    hs = HSTRING()
    hr = _WindowsCreateString(text, len(text), byref(hs))
    if hr != 0:
        raise OSError(f"WindowsCreateString failed: {hr}")
    return hs


def delete_hstring(hs):
    if _WindowsDeleteString and hs:
        _WindowsDeleteString(hs)


BUILD = sys.getwindowsversion().build

if BUILD >= 26100:
    IID_IVirtualDesktopManagerInternal = GUID("{53F5CA0B-158F-4124-900C-057158060B27}")
    IID_IVirtualDesktop = GUID("{3F07F4BE-B107-441A-AF0F-39D82529072C}")
elif BUILD >= 22621:
    IID_IVirtualDesktopManagerInternal = GUID("{A3175F2D-239C-4BD2-8AA0-EEBA8B0B138E}")
    IID_IVirtualDesktop = GUID("{3F07F4BE-B107-441A-AF0F-39D82529072C}")
else:
    IID_IVirtualDesktopManagerInternal = GUID("{F31574D6-B682-4CDC-BD56-1827860ABEC6}")
    IID_IVirtualDesktop = GUID("{FF72FFDD-BE7E-43FC-9C03-AD81681E88E4}")


class IVirtualDesktop(IUnknown):
    _iid_ = IID_IVirtualDesktop
    _methods_ = [
        STDMETHOD(HRESULT, "IsViewVisible", (POINTER(IUnknown), POINTER(UINT))),
        COMMETHOD([], HRESULT, "GetID", (["out"], POINTER(GUID), "pGuid")),
        COMMETHOD([], HRESULT, "GetName", (["out"], POINTER(HSTRING), "pName")),
        COMMETHOD([], HRESULT, "GetWallpaperPath", (["out"], POINTER(HSTRING), "pPath")),
        COMMETHOD([], HRESULT, "IsRemote", (["out"], POINTER(HWND), "pW")),
    ]


class IApplicationView(IUnknown):
    _iid_ = GUID("{372E1D3B-38D3-42E4-A15B-8AB2B178F513}")


class IVirtualDesktopManagerInternal(IUnknown):
    _iid_ = IID_IVirtualDesktopManagerInternal
    if BUILD >= 26100:
        _methods_ = [
            COMMETHOD([], HRESULT, "GetCount", (["out"], POINTER(UINT), "pCount")),
            STDMETHOD(HRESULT, "MoveViewToDesktop", (POINTER(IApplicationView), POINTER(IVirtualDesktop))),
            STDMETHOD(HRESULT, "CanViewMoveDesktops", (POINTER(IApplicationView), POINTER(UINT))),
            COMMETHOD([], HRESULT, "GetCurrentDesktop", (["out"], POINTER(POINTER(IVirtualDesktop)), "pDesktop")),
            COMMETHOD([], HRESULT, "GetDesktops", (["out"], POINTER(POINTER(IObjectArray)), "array")),
            STDMETHOD(HRESULT, "GetAdjacentDesktop", (POINTER(IVirtualDesktop), UINT, POINTER(POINTER(IVirtualDesktop)))),
            STDMETHOD(HRESULT, "SwitchDesktop", (POINTER(IVirtualDesktop),)),
            STDMETHOD(HRESULT, "SwitchDesktopAndMoveForegroundView", (POINTER(IVirtualDesktop),)),
            COMMETHOD([], HRESULT, "CreateDesktopW", (["out"], POINTER(POINTER(IVirtualDesktop)), "pDesktop")),
            STDMETHOD(HRESULT, "MoveDesktop", (POINTER(IVirtualDesktop), UINT)),
            COMMETHOD([], HRESULT, "RemoveDesktop", (["in"], POINTER(IVirtualDesktop), "destroyDesktop"), (["in"], POINTER(IVirtualDesktop), "fallbackDesktop")),
            COMMETHOD([], HRESULT, "FindDesktop", (["in"], POINTER(GUID), "pGuid"), (["out"], POINTER(POINTER(IVirtualDesktop)), "pDesktop")),
            STDMETHOD(HRESULT, "GetDesktopSwitchIncludeExcludeViews", (POINTER(IVirtualDesktop), POINTER(POINTER(IObjectArray)), POINTER(POINTER(IObjectArray)))),
            COMMETHOD([], HRESULT, "SetName", (["in"], POINTER(IVirtualDesktop), "pDesktop"), (["in"], HSTRING, "name")),
        ]
    elif BUILD >= 22621:
        _methods_ = [
            COMMETHOD([], HRESULT, "GetCount", (["out"], POINTER(UINT), "pCount")),
            STDMETHOD(HRESULT, "MoveViewToDesktop", (POINTER(IApplicationView), POINTER(IVirtualDesktop))),
            STDMETHOD(HRESULT, "CanViewMoveDesktops", (POINTER(IApplicationView), POINTER(UINT))),
            COMMETHOD([], HRESULT, "GetCurrentDesktop", (["out"], POINTER(POINTER(IVirtualDesktop)), "pDesktop")),
            COMMETHOD([], HRESULT, "GetDesktops", (["out"], POINTER(POINTER(IObjectArray)), "array")),
            STDMETHOD(HRESULT, "GetAdjacentDesktop", (POINTER(IVirtualDesktop), UINT, POINTER(POINTER(IVirtualDesktop)))),
            STDMETHOD(HRESULT, "SwitchDesktop", (POINTER(IVirtualDesktop),)),
            COMMETHOD([], HRESULT, "CreateDesktopW", (["out"], POINTER(POINTER(IVirtualDesktop)), "pDesktop")),
            STDMETHOD(HRESULT, "MoveDesktop", (POINTER(IVirtualDesktop), UINT)),
            COMMETHOD([], HRESULT, "RemoveDesktop", (["in"], POINTER(IVirtualDesktop), "destroyDesktop"), (["in"], POINTER(IVirtualDesktop), "fallbackDesktop")),
            COMMETHOD([], HRESULT, "FindDesktop", (["in"], POINTER(GUID), "pGuid"), (["out"], POINTER(POINTER(IVirtualDesktop)), "pDesktop")),
            STDMETHOD(HRESULT, "GetDesktopSwitchIncludeExcludeViews", (POINTER(IVirtualDesktop), POINTER(POINTER(IObjectArray)), POINTER(POINTER(IObjectArray)))),
            COMMETHOD([], HRESULT, "SetName", (["in"], POINTER(IVirtualDesktop), "pDesktop"), (["in"], HSTRING, "name")),
        ]
    else:
        _methods_ = [
            COMMETHOD([], HRESULT, "GetCount", (["out"], POINTER(UINT), "pCount")),
            STDMETHOD(HRESULT, "MoveViewToDesktop", (POINTER(IApplicationView), POINTER(IVirtualDesktop))),
            STDMETHOD(HRESULT, "CanViewMoveDesktops", (POINTER(IApplicationView), POINTER(UINT))),
            COMMETHOD([], HRESULT, "GetCurrentDesktop", (["out"], POINTER(POINTER(IVirtualDesktop)), "pDesktop")),
            COMMETHOD([], HRESULT, "GetDesktops", (["out"], POINTER(POINTER(IObjectArray)), "array")),
            STDMETHOD(HRESULT, "GetAdjacentDesktop", (POINTER(IVirtualDesktop), UINT, POINTER(POINTER(IVirtualDesktop)))),
            STDMETHOD(HRESULT, "SwitchDesktop", (POINTER(IVirtualDesktop),)),
            COMMETHOD([], HRESULT, "CreateDesktopW", (["out"], POINTER(POINTER(IVirtualDesktop)), "pDesktop")),
            COMMETHOD([], HRESULT, "RemoveDesktop", (["in"], POINTER(IVirtualDesktop), "destroyDesktop"), (["in"], POINTER(IVirtualDesktop), "fallbackDesktop")),
            COMMETHOD([], HRESULT, "FindDesktop", (["in"], POINTER(GUID), "pGuid"), (["out"], POINTER(POINTER(IVirtualDesktop)), "pDesktop")),
        ]


class VirtualDesktopManager:
    """
    Wrapper around the Windows IVirtualDesktopManager interface.
    Allows checking if a window is on the current virtual desktop, getting its Desktop ID,
    and moving windows between desktops.
    """

    def __init__(self):
        self._manager = None
        try:
            import ctypes

            try:
                ctypes.windll.ole32.CoInitialize(None)
            except Exception:
                pass

            self._manager = comtypes.client.CreateObject(
                CLSID_VirtualDesktopManager, interface=IVirtualDesktopManager
            )

            try:
                service_provider = comtypes.client.CreateObject(
                    CLSID_ImmersiveShell, interface=IServiceProvider
                )
                unk = service_provider.QueryService(
                    byref(CLSID_VirtualDesktopManagerInternal),
                    byref(IVirtualDesktopManagerInternal._iid_),
                )
                self._internal_manager = unk.QueryInterface(IVirtualDesktopManagerInternal)
            except Exception as e:
                logger.warning(f"Failed to initialize VirtualDesktopManagerInternal: {e}")
                self._internal_manager = None

        except Exception as e:
            logger.error(f"Failed to initialize VirtualDesktopManager: {e}")

    def is_window_on_current_desktop(self, hwnd: int) -> bool:
        if not self._manager:
            return True
        try:
            return self._manager.IsWindowOnCurrentVirtualDesktop(hwnd)
        except Exception:
            return True

    def get_window_desktop_id(self, hwnd: int) -> str:
        if not self._manager:
            return ""
        try:
            guid = self._manager.GetWindowDesktopId(hwnd)
            return str(guid)
        except Exception:
            return ""

    def _get_name_from_registry(self, guid_str: str) -> str:
        try:
            import winreg

            path = f"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VirtualDesktops\\Desktops\\{guid_str}"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
                name, _ = winreg.QueryValueEx(key, "Name")
                return name
        except Exception:
            return None

    def _resolve_to_guid(self, name: str) -> str:
        desktops_map = {}

        try:
            desktops_array = self._internal_manager.GetDesktops()
            count = desktops_array.GetCount()

            for i in range(count):
                unk = desktops_array.GetAt(i, byref(IVirtualDesktop._iid_))
                desktop = unk.QueryInterface(IVirtualDesktop)
                guid = getattr(desktop, "GetID", lambda: None)()
                if not guid:
                    continue
                guid_str = str(guid)

                reg_name = self._get_name_from_registry(guid_str)
                display_name = reg_name if reg_name else f"Desktop {i + 1}"

                desktops_map[display_name.lower()] = guid_str
                if name.lower() == guid_str.lower():
                    return guid_str

        except Exception as e:
            logger.error(f"Error scanning desktops for resolution: {e}")
            return None

        if name.lower() in desktops_map:
            return desktops_map[name.lower()]

        return None

    def move_window_to_desktop(self, hwnd: int, desktop_name: str):
        if not self._manager:
            return
        try:
            target_guid_str = self._resolve_to_guid(desktop_name)
            if not target_guid_str:
                logger.error(f"Desktop '{desktop_name}' not found.")
                return
            guid = GUID(target_guid_str)
            self._manager.MoveWindowToDesktop(hwnd, byref(guid))
        except Exception as e:
            logger.error(f"Failed to move window to desktop: {e}")

    def create_desktop(self, name: str = None) -> str:
        if not self._internal_manager:
            raise RuntimeError("Internal VDM not initialized")

        desktop = self._internal_manager.CreateDesktopW()
        guid = desktop.GetID()
        guid_str = str(guid)

        if name:
            self.rename_desktop_by_guid(guid_str, name)
            return name
        else:
            desktops = self.get_all_desktops()
            return desktops[-1]["name"]

    def remove_desktop(self, desktop_name: str):
        if not self._internal_manager:
            raise RuntimeError("Internal VDM not initialized")

        target_guid_str = self._resolve_to_guid(desktop_name)
        if not target_guid_str:
            logger.error(f"Desktop '{desktop_name}' not found.")
            return

        target_guid = GUID(target_guid_str)

        try:
            target_desktop = self._internal_manager.FindDesktop(target_guid)
        except Exception:
            logger.error(f"Could not find desktop with GUID {target_guid_str}")
            return

        desktops_array = self._internal_manager.GetDesktops()
        count = desktops_array.GetCount()
        fallback_desktop = None

        for i in range(count):
            unk = desktops_array.GetAt(i, byref(IVirtualDesktop._iid_))
            candidate = unk.QueryInterface(IVirtualDesktop)
            candidate_id = candidate.GetID()
            if str(candidate_id) != str(target_guid):
                fallback_desktop = candidate
                break

        if not fallback_desktop:
            logger.error("No fallback desktop found (cannot delete the only desktop)")
            return

        self._internal_manager.RemoveDesktop(target_desktop, fallback_desktop)

    def rename_desktop(self, desktop_name: str, new_name: str):
        target_guid_str = self._resolve_to_guid(desktop_name)
        if not target_guid_str:
            logger.error(f"Desktop '{desktop_name}' not found.")
            return

        self.rename_desktop_by_guid(target_guid_str, new_name)

    def rename_desktop_by_guid(self, guid_str: str, new_name: str):
        if not self._internal_manager:
            return

        target_guid = GUID(guid_str)
        try:
            target_desktop = self._internal_manager.FindDesktop(target_guid)
        except Exception:
            return

        hs_name = create_hstring(new_name)
        try:
            if hasattr(self._internal_manager, "SetName"):
                self._internal_manager.SetName(target_desktop, hs_name)
            else:
                logger.warning("Rename desktop is not supported on this Windows build.")
        except Exception as e:
            logger.error(f"Failed to rename desktop: {e}")
        finally:
            delete_hstring(hs_name)

    def switch_desktop(self, desktop_name: str):
        if not self._internal_manager:
            raise RuntimeError("Internal VDM not initialized")

        target_guid_str = self._resolve_to_guid(desktop_name)
        if not target_guid_str:
            logger.error(f"Desktop '{desktop_name}' not found")
            return

        target_guid = GUID(target_guid_str)
        try:
            target_desktop = self._internal_manager.FindDesktop(target_guid)
            self._internal_manager.SwitchDesktop(target_desktop)
        except Exception as e:
            logger.error(f"Failed to switch desktop: {e}")

    def get_all_desktops(self) -> list[dict]:
        if not self._internal_manager:
            return [
                {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "name": "Default Desktop",
                }
            ]

        desktops_array = self._internal_manager.GetDesktops()
        count = desktops_array.GetCount()

        result = []
        for i in range(count):
            try:
                unk = desktops_array.GetAt(i, byref(IVirtualDesktop._iid_))
                desktop = unk.QueryInterface(IVirtualDesktop)
                guid = getattr(desktop, "GetID", lambda: None)()
                if not guid:
                    continue

                guid_str = str(guid)
                reg_name = self._get_name_from_registry(guid_str)
                if reg_name:
                    name = reg_name
                else:
                    name = f"Desktop {i + 1}"

                result.append({"id": guid_str, "name": name})
            except Exception as e:
                logger.error(f"Error retrieving desktop at index {i}: {e}")
                continue

        return result

    def get_current_desktop(self) -> dict:
        if not self._internal_manager:
            return {
                "id": "00000000-0000-0000-0000-000000000000",
                "name": "Default Desktop",
            }

        current_desktop = self._internal_manager.GetCurrentDesktop()
        guid = current_desktop.GetID()
        guid_str = str(guid)

        all_desktops = self.get_all_desktops()
        for d in all_desktops:
            if d["id"] == guid_str:
                return d

        return {"id": guid_str, "name": "Unknown"}


def create_desktop(name: str = None) -> str:
    return _get_manager().create_desktop(name)


def remove_desktop(desktop_name: str):
    _get_manager().remove_desktop(desktop_name)


def rename_desktop(desktop_name: str, new_name: str):
    _get_manager().rename_desktop(desktop_name, new_name)


def switch_desktop(desktop_name: str):
    _get_manager().switch_desktop(desktop_name)


def get_all_desktops() -> list[dict]:
    return _get_manager().get_all_desktops()


def get_current_desktop() -> dict:
    return _get_manager().get_current_desktop()
