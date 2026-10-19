"""
UIA Caching Utilities for Performance Optimization

This module provides utilities for implementing UI Automation caching
to reduce cross-process COM calls during tree traversal.
"""

from _ctypes import COMError

from windows_mcp.uia import (
    CacheRequest,
    PropertyId,
    PatternId,
    TreeScope,
    Control,
    UIADeadElementError,
    from_com_error,
)
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


def is_uia_dead_element_error(error: BaseException) -> bool:
    """Return True for UIA failures that mean the element no longer exists."""
    if isinstance(error, UIADeadElementError):
        return True
    if isinstance(error, COMError):
        return isinstance(from_com_error(error), UIADeadElementError)
    return False


class CacheRequestFactory:
    """Factory for creating optimized cache requests for different scenarios."""

    @staticmethod
    def create_tree_traversal_cache() -> CacheRequest:
        cache_request = CacheRequest()

        cache_request.TreeScope = TreeScope.TreeScope_Element | TreeScope.TreeScope_Children

        cache_request.AddProperty(PropertyId.NameProperty)
        cache_request.AddProperty(PropertyId.AutomationIdProperty)
        cache_request.AddProperty(PropertyId.LocalizedControlTypeProperty)
        cache_request.AddProperty(PropertyId.AcceleratorKeyProperty)
        cache_request.AddProperty(PropertyId.ClassNameProperty)
        cache_request.AddProperty(PropertyId.ControlTypeProperty)
        cache_request.AddProperty(PropertyId.RuntimeIdProperty)
        cache_request.AddProperty(PropertyId.IsContentElementProperty)
        cache_request.AddProperty(PropertyId.FrameworkIdProperty)
        cache_request.AddProperty(PropertyId.ClickablePointProperty)

        cache_request.AddProperty(PropertyId.IsEnabledProperty)
        cache_request.AddProperty(PropertyId.IsOffscreenProperty)
        cache_request.AddProperty(PropertyId.IsControlElementProperty)
        cache_request.AddProperty(PropertyId.HasKeyboardFocusProperty)
        cache_request.AddProperty(PropertyId.IsKeyboardFocusableProperty)
        cache_request.AddProperty(PropertyId.IsPasswordProperty)

        cache_request.AddProperty(PropertyId.BoundingRectangleProperty)
        cache_request.AddProperty(PropertyId.HelpTextProperty)

        cache_request.AddPattern(PatternId.LegacyIAccessiblePattern)
        cache_request.AddPattern(PatternId.ScrollPattern)
        cache_request.AddPattern(PatternId.WindowPattern)

        cache_request.AddProperty(PropertyId.LegacyIAccessibleRoleProperty)
        cache_request.AddProperty(PropertyId.LegacyIAccessibleValueProperty)
        cache_request.AddProperty(PropertyId.LegacyIAccessibleDefaultActionProperty)
        cache_request.AddProperty(PropertyId.LegacyIAccessibleStateProperty)

        cache_request.AddProperty(PropertyId.ScrollHorizontallyScrollableProperty)
        cache_request.AddProperty(PropertyId.ScrollVerticallyScrollableProperty)
        cache_request.AddProperty(PropertyId.ScrollHorizontalScrollPercentProperty)
        cache_request.AddProperty(PropertyId.ScrollVerticalScrollPercentProperty)

        cache_request.AddProperty(PropertyId.ExpandCollapseExpandCollapseStateProperty)

        cache_request.AddProperty(PropertyId.SelectionCanSelectMultipleProperty)
        cache_request.AddProperty(PropertyId.SelectionIsSelectionRequiredProperty)
        cache_request.AddProperty(PropertyId.SelectionSelectionProperty)

        cache_request.AddProperty(PropertyId.SelectionItemIsSelectedProperty)
        cache_request.AddProperty(PropertyId.SelectionItemSelectionContainerProperty)

        cache_request.AddProperty(PropertyId.WindowIsModalProperty)

        cache_request.AddProperty(PropertyId.ToggleToggleStateProperty)

        cache_request.AddProperty(PropertyId.RangeValueValueProperty)
        cache_request.AddProperty(PropertyId.RangeValueMinimumProperty)
        cache_request.AddProperty(PropertyId.RangeValueMaximumProperty)

        return cache_request


class CachedControlHelper:
    """Helper class for working with cached controls."""

    @staticmethod
    def build_cached_control(node: Control, cache_request: Optional[CacheRequest] = None) -> Control:
        if cache_request is None:
            cache_request = CacheRequestFactory.create_tree_traversal_cache()

        try:
            cached_node = node.BuildUpdatedCache(cache_request)
            cached_node._is_cached = True
            return cached_node
        except Exception as e:
            logger.debug(f"Failed to build cached control: {e}")
            return node

    @staticmethod
    def get_cached_children(node: Control, cache_request: Optional[CacheRequest] = None) -> list[Control]:
        if cache_request is None:
            cache_request = CacheRequestFactory.create_tree_traversal_cache()

        req_clone = cache_request.Clone()
        req_clone.TreeScope = TreeScope.TreeScope_Children

        try:
            updated_element = node.Element.BuildUpdatedCache(req_clone.check_request)
            element_array = updated_element.GetCachedChildren()

            children = []
            if element_array:
                length = element_array.Length
                for i in range(length):
                    child_elem = element_array.GetElement(i)
                    child_control = Control.CreateControlFromElement(child_elem)
                    if child_control:
                        child_control._is_cached = True
                        children.append(child_control)

            logger.debug(f"Retrieved {len(children)} cached children (newly built)")
            return children

        except Exception as e:
            if is_uia_dead_element_error(e):
                logger.debug("UIA element is no longer available; pruning stale subtree")
                return []

            logger.debug(f"Failed to get cached children, falling back to regular access: {e}")
            try:
                return node.GetChildren()
            except Exception as fallback_error:
                if is_uia_dead_element_error(fallback_error):
                    logger.debug("UIA element died during fallback; pruning stale subtree")
                    return []
                raise
