"""
Unified WatchDog Service for monitoring UI Automation events.
Allows single instantiation to handle multiple monitors (Focus, Structure) safely in one STA thread.
"""

from windows_mcp.uia.core import _AutomationClient
from windows_mcp.uia.enums import TreeScope
from threading import Thread, Event
import comtypes.client
import comtypes
import logging
import time

from .event_handlers import (
    FocusChangedEventHandler,
    StructureChangedEventHandler,
    PropertyChangedEventHandler,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

FAIL_THRESHOLD = 5
MAX_BACKOFF_SECONDS = 30.0
HEALTHY_RUN_SECONDS = 60.0


class WatchDog:
    def __init__(self):
        self.uia_client = _AutomationClient.instance()
        self.uia = None
        self.is_running = Event()
        self.thread = None
        self._needs_rebuild = Event()

        self._focus_callback = None
        self._structure_callback = None
        self._structure_element = None
        self._property_callback = None
        self._property_element = None
        self._property_ids = None

        self._focus_handler = None
        self._structure_handler = None
        self._active_structure_element = None
        self._property_handler = None
        self._active_property_element = None
        self._active_property_ids = None

        self._focus_fail_count = 0
        self._structure_fail_count = 0
        self._property_fail_count = 0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        """Start the watchdog service thread."""
        if self.is_running.is_set():
            return
        self.is_running.set()
        self.thread = Thread(target=self._run, name="WatchDogThread")
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop the watchdog service thread."""
        if not self.is_running.is_set():
            return
        self.is_running.clear()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

    def set_focus_callback(self, callback):
        self._focus_callback = callback

    def set_structure_callback(self, callback, element=None):
        self._structure_callback = callback
        self._structure_element = element

    def set_property_callback(self, callback, element=None, property_ids=None):
        self._property_callback = callback
        self._property_element = element
        self._property_ids = property_ids

    def request_rebuild(self):
        """Signal that the current UIA client/subscriptions should be torn
        down and recreated. Safe to call from event-handler callbacks."""
        self._needs_rebuild.set()

    def _create_uia(self):
        return comtypes.client.CreateObject(
            "{ff48dba4-60ef-4201-aa87-54103eef594e}",
            interface=self.uia_client.UIAutomationCore.IUIAutomation,
        )

    def _run(self):
        backoff = 1.0
        while self.is_running.is_set():
            comtypes.CoInitialize()
            started = time.monotonic()
            try:
                self.uia = self._create_uia()
                self._needs_rebuild.clear()
                self._focus_fail_count = 0
                self._structure_fail_count = 0
                self._property_fail_count = 0
                self._event_loop()
            except Exception as e:
                logger.warning(f"WatchDog degraded, rebuilding UIA client: {e}")
            finally:
                self._teardown_handlers()
                comtypes.CoUninitialize()

            if time.monotonic() - started >= HEALTHY_RUN_SECONDS:
                backoff = 1.0

            if self.is_running.is_set():
                self.is_running.wait(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF_SECONDS)

    def _event_loop(self):
        while self.is_running.is_set() and not self._needs_rebuild.is_set():
            if self._focus_callback and not self._focus_handler:
                try:
                    self._focus_handler = FocusChangedEventHandler(self)
                    self.uia.AddFocusChangedEventHandler(None, self._focus_handler)
                except Exception as e:
                    logger.debug(f"Failed to add focus handler: {e}")
            elif not self._focus_callback and self._focus_handler:
                try:
                    self.uia.RemoveFocusChangedEventHandler(self._focus_handler)
                except Exception as e:
                    logger.debug(f"Failed to remove focus handler: {e}")
                self._focus_handler = None

            config_changed = self._structure_element != self._active_structure_element
            should_be_active = self._structure_callback is not None
            is_active = self._structure_handler is not None

            if is_active and (not should_be_active or config_changed):
                try:
                    target = (
                        self._active_structure_element
                        if self._active_structure_element
                        else self.uia.GetRootElement()
                    )
                    self.uia.RemoveStructureChangedEventHandler(target, self._structure_handler)
                except Exception as e:
                    logger.debug(f"Failed to remove structure handler: {e}")
                self._structure_handler = None
                self._active_structure_element = None
                is_active = False

            if should_be_active and not is_active:
                try:
                    target = (
                        self._structure_element
                        if self._structure_element
                        else self.uia.GetRootElement()
                    )
                    scope = TreeScope.TreeScope_Subtree

                    self._structure_handler = StructureChangedEventHandler(self)
                    self.uia.AddStructureChangedEventHandler(
                        target, scope, None, self._structure_handler
                    )
                    self._active_structure_element = target
                except Exception as e:
                    logger.debug(f"Failed to add structure handler: {e}")

            config_changed = (self._property_element != self._active_property_element) or (
                self._property_ids != self._active_property_ids
            )
            should_be_active = self._property_callback is not None
            is_active = self._property_handler is not None

            if is_active and (not should_be_active or config_changed):
                try:
                    target = (
                        self._active_property_element
                        if self._active_property_element
                        else self.uia.GetRootElement()
                    )
                    self.uia.RemovePropertyChangedEventHandler(target, self._property_handler)
                except Exception as e:
                    logger.debug(f"Failed to remove property handler: {e}")
                self._property_handler = None
                self._active_property_element = None
                self._active_property_ids = None
                is_active = False

            if should_be_active and not is_active:
                try:
                    target = (
                        self._property_element
                        if self._property_element
                        else self.uia.GetRootElement()
                    )
                    scope = TreeScope.TreeScope_Subtree

                    p_ids = (
                        self._property_ids if self._property_ids else [30005, 30045, 30093, 30128]
                    )

                    self._property_handler = PropertyChangedEventHandler(self)
                    self.uia.AddPropertyChangedEventHandler(
                        target, scope, None, self._property_handler, p_ids
                    )

                    self._active_property_element = target
                    self._active_property_ids = p_ids
                except Exception as e:
                    logger.debug(f"Failed to add property handler: {e}")

            comtypes.client.PumpEvents(0.1)

        if self._needs_rebuild.is_set():
            logger.warning("WatchDog event pipeline degraded, rebuilding UIA client")

    def _teardown_handlers(self):
        if not self.uia:
            return

        if self._focus_handler:
            try:
                self.uia.RemoveFocusChangedEventHandler(self._focus_handler)
            except Exception:
                pass
            self._focus_handler = None

        if self._structure_handler:
            try:
                target = (
                    self._active_structure_element
                    if self._active_structure_element
                    else self.uia.GetRootElement()
                )
                self.uia.RemoveStructureChangedEventHandler(target, self._structure_handler)
            except Exception:
                pass
            self._structure_handler = None
            self._active_structure_element = None

        if self._property_handler:
            try:
                target = (
                    self._active_property_element
                    if self._active_property_element
                    else self.uia.GetRootElement()
                )
                self.uia.RemovePropertyChangedEventHandler(target, self._property_handler)
            except Exception:
                pass
            self._property_handler = None
            self._active_property_element = None
            self._active_property_ids = None

        self.uia = None
