"""System control services — sleep, elevation, services, env, startup and more."""

from windows_mcp.system.accounts import list_accounts
from windows_mcp.system.apps import list_apps
from windows_mcp.system.auto_logon import auto_logon_check
from windows_mcp.system.bluetooth import bluetooth_devices
from windows_mcp.system.boot_timing import boot_timing
from windows_mcp.system.brightness import brightness_status
from windows_mcp.system.browser_exts import browser_extensions
from windows_mcp.system.certificates import list_certificates
from windows_mcp.system.crash_reports import crash_report_list
from windows_mcp.system.defender import defender_status
from windows_mcp.system.devices import list_devices
from windows_mcp.system.device_errors import device_errors
from windows_mcp.system.dirsize import directory_size
from windows_mcp.system.disk_io import disk_io_stats
from windows_mcp.system.dns import dns_lookup
from windows_mcp.system.domain_info import domain_membership
from windows_mcp.system.drive_health import drive_health
from windows_mcp.system.drivers import list_drivers
from windows_mcp.system.elevation import (
    check_elevation_status,
    elevate_process,
    verify_process_elevation,
)
from windows_mcp.system.environment import (
    delete_environment,
    list_environment,
    set_environment,
)
from windows_mcp.system.event_log import read_event_log
from windows_mcp.system.file_assoc import list_associations
from windows_mcp.system.file_hash import file_hash_info
from windows_mcp.system.firewall import firewall_status
from windows_mcp.system.fonts import installed_fonts
from windows_mcp.system.fw_rules import firewall_rules
from windows_mcp.system.hardware import hardware_inventory
from windows_mcp.system.hosts_file import read_hosts
from windows_mcp.system.ime import ime_status
from windows_mcp.system.kbd_layouts import list_keyboard_layouts
from windows_mcp.system.locale import locale_info
from windows_mcp.system.license_info import windows_license_info
from windows_mcp.system.mapped_drives import mapped_drives
from windows_mcp.system.netconfig import network_config
from windows_mcp.system.net_adapters import network_adapters
from windows_mcp.system.net_throughput import network_throughput
from windows_mcp.system.net_summary import network_connection_summary
from windows_mcp.system.pagefile import pagefile_info
from windows_mcp.system.perf_score import system_performance_score
from windows_mcp.system.ping import ping_host
from windows_mcp.system.port_map import port_process_map
from windows_mcp.system.power_plan import get_active_plan, list_plans, set_active_plan
from windows_mcp.system.printers import list_printers
from windows_mcp.system.priority import list_priorities, set_priority
from windows_mcp.system.proc_cmdline import list_process_command_lines
from windows_mcp.system.proc_detail import process_detail
from windows_mcp.system.proc_affinity import process_affinity
from windows_mcp.system.proc_io import process_io_stats
from windows_mcp.system.proc_tree import process_tree
from windows_mcp.system.program_sizes import programs_by_size
from windows_mcp.system.proxy import proxy_settings
from windows_mcp.system.rdp_status import remote_desktop_status
from windows_mcp.system.reg_search import search_registry
from windows_mcp.system.recent_files import recent_files
from windows_mcp.system.recycle_bin import recycle_bin_info
from windows_mcp.system.shares import list_shares
from windows_mcp.system.scheduled_task import (
    create_task,
    delete_task,
    end_task,
    list_tasks,
    run_task,
)
from windows_mcp.system.sessions import session_info
from windows_mcp.system.session_procs import session_processes
from windows_mcp.system.service_control import control_service, list_services
from windows_mcp.system.sleep_control import (
    disable_sleep_prevention,
    enable_sleep_prevention,
    get_sleep_prevention_status,
)
from windows_mcp.system.sound import list_sound_devices
from windows_mcp.system.startup import add_startup, list_startup, remove_startup
from windows_mcp.system.status import system_status
from windows_mcp.system.sysinfo import system_info
from windows_mcp.system.timezone import timezone_info
from windows_mcp.system.timesync import time_sync_status
from windows_mcp.system.top_procs import top_processes
from windows_mcp.system.trace_route import trace_route
from windows_mcp.system.updates import list_updates
from windows_mcp.system.usb_history import usb_device_history
from windows_mcp.system.volumes import list_volumes
from windows_mcp.system.wake_source import wake_source_info
from windows_mcp.system.wifi import wifi_networks, wifi_status

__all__ = [
    "list_accounts",
    "list_apps",
    "auto_logon_check",
    "bluetooth_devices",
    "boot_timing",
    "brightness_status",
    "browser_extensions",
    "list_certificates",
    "crash_report_list",
    "defender_status",
    "list_devices",
    "device_errors",
    "directory_size",
    "disk_io_stats",
    "dns_lookup",
    "domain_membership",
    "drive_health",
    "list_drivers",
    "check_elevation_status",
    "elevate_process",
    "verify_process_elevation",
    "delete_environment",
    "list_environment",
    "set_environment",
    "read_event_log",
    "list_associations",
    "file_hash_info",
    "firewall_status",
    "installed_fonts",
    "firewall_rules",
    "hardware_inventory",
    "read_hosts",
    "list_keyboard_layouts",
    "locale_info",
    "windows_license_info",
    "mapped_drives",
    "network_config",
    "network_adapters",
    "network_throughput",
    "network_connection_summary",
    "pagefile_info",
    "system_performance_score",
    "ping_host",
    "port_process_map",
    "ime_status",
    "get_active_plan",
    "list_plans",
    "set_active_plan",
    "list_printers",
    "list_priorities",
    "set_priority",
    "list_process_command_lines",
    "process_detail",
    "process_affinity",
    "process_io_stats",
    "process_tree",
    "programs_by_size",
    "proxy_settings",
    "remote_desktop_status",
    "search_registry",
    "recent_files",
    "recycle_bin_info",
    "list_shares",
    "create_task",
    "delete_task",
    "end_task",
    "list_tasks",
    "run_task",
    "session_info",
    "session_processes",
    "control_service",
    "list_services",
    "disable_sleep_prevention",
    "enable_sleep_prevention",
    "get_sleep_prevention_status",
    "list_sound_devices",
    "add_startup",
    "list_startup",
    "remove_startup",
    "system_status",
    "system_info",
    "timezone_info",
    "time_sync_status",
    "top_processes",
    "trace_route",
    "list_updates",
    "usb_device_history",
    "list_volumes",
    "wake_source_info",
    "wifi_networks",
    "wifi_status",
]
