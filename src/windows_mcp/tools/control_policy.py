"""One table for desktop ownership, separate from authorization or data safety.

When adding a tool or a mode, classify it here. Registration coverage tests catch
omissions; unclassified extensions conservatively retain the desktop gate.
"""

# Categories describe desktop interference, not whether an operation is destructive.
DIRECT = frozenset({"Click", "Type", "Scroll", "Move", "Shortcut", "MultiSelect", "MultiEdit"})
POSSIBLE = frozenset({"PowerShell", "Notification"})
OTHER = frozenset(
    {
        "FileSystem",
        "Registry",
        "Snapshot",
        "Screenshot",
        "Scrape",
        "Wait",
        "WaitFor",
        "DisplayInventory",
        "ParsePE",
        "MemoryProtectCheck",
        "ProcessMonitor",
        "PreventSleep",
        "ScreenRecord",
        "ServiceControl",
        "EventLogReader",
        "ScheduledTask",
        "WatchFile",
        "NetState",
        "StartupManager",
        "EnvironmentVariables",
        "SystemStatus",
        "ImeStatus",
        "InstalledApps",
        "PowerPlan",
        "WifiManager",
        "UsbDeviceList",
        "SystemInfo",
        "DriverInfo",
        "FileAssociations",
        "HostsFile",
        "UserAccounts",
        "KeyboardLayouts",
        "LocaleInfo",
        "TimezoneInfo",
        "StorageVolumes",
        "PrinterList",
        "ProcessPriority",
        "SoundDevices",
        "NetworkShares",
        "FirewallStatus",
        "CertificateInfo",
        "DisplayBrightness",
        "HardwareInventory",
        "NetworkConfig",
        "PageFileInfo",
        "SessionInfo",
        "NetworkLatency",
        "DnsLookup",
        "ProcessCommandLine",
        "RegistrySearch",
        "DirectorySize",
        "TimeSyncInfo",
        "FirewallRules",
        "InstalledUpdates",
        "ActiveWindowInfo",
        "MousePosition",
        "ProcessDetail",
        "RecycleBinInfo",
        "TopProcesses",
        "ProcessTree",
        "InstalledFonts",
        "NetworkAdapters",
        "WindowList",
        "DriveSmartInfo",
        "ProcessIOStats",
        "WakeSourceInfo",
        "PortProcessMap",
        "FileHashInfo",
        "SystemPerformanceScore",
        "TraceRoute",
        "ProxySettings",
        "USBDeviceHistory",
        "CrashReportList",
        "HardwareDeviceErrors",
        "RecentFiles",
        "BootTiming",
        "MappedDrives",
        "InstalledProgramsBySize",
        "WindowsLicenseInfo",
        "RemoteDesktopStatus",
        "AutoLogonCheck",
        "DomainMembership",
        "BrowserExtensions",
        "DiskIOStats",
        "WindowsDefenderStatus",
        "NetworkThroughput",
        "ProcessAffinity",
        "NetworkConnectionSummary",
        "SessionProcesses",
        "BluetoothDevices",
    }
)
MODES = {
    "App": {
        "launch": "possible",
        "launch_executable": "possible",
        "resize": "direct",
        "switch": "direct",
    },
    "Process": {"list": "other", "kill": "possible"},
    "Clipboard": {"get": "other", "set": "possible"},
    "ElevationControl": {"status": "other", "verify": "other", "elevate": "possible"},
}
CLASSIFIED_TOOLS = DIRECT | POSSIBLE | OTHER | MODES.keys() | {"ControlStatus"}


def requires_control(policy: str, name: str, arguments: dict | None = None) -> bool:
    """Decide before taking the ownership lock; never inspect arbitrary scripts."""
    if name == "ControlStatus":
        return False
    if policy == "strict":
        return True
    if policy not in ("relaxed", "balanced"):
        raise ValueError(f"Unknown control policy: {policy}")
    category = "direct"  # Unknown tools/modes must not silently bypass ownership.
    if name in MODES:
        mode = (arguments or {}).get("mode", "launch" if name == "App" else None)
        if isinstance(mode, str):
            category = MODES[name].get(mode, "direct")
    elif name in POSSIBLE:
        category = "possible"
    elif name in OTHER:
        category = "other"
    return category == "direct" or (policy == "balanced" and category == "possible")
