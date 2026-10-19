"""Snapshot / Screenshot shared helpers."""

import io
import json
import logging
import os
import time

from fastmcp.utilities.types import Image
from textwrap import dedent
from windows_mcp.desktop.service import Desktop, Size
from windows_mcp.desktop.utils import remove_private_use_chars, repair_surrogates


logger = logging.getLogger(__name__)

MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = 1920, 1080


def _screenshot_scale() -> float:
    value = os.getenv("WINDOWS_MCP_SCREENSHOT_SCALE", "1.0")
    try:
        scale = float(value)
    except ValueError:
        logger.warning("Invalid WINDOWS_MCP_SCREENSHOT_SCALE value %r, using 1.0", value)
        scale = 1.0
    if not (0.1 <= scale <= 1.0):
        logger.warning("WINDOWS_MCP_SCREENSHOT_SCALE %r out of range [0.1, 1.0], clamping", scale)
        scale = max(0.1, min(1.0, scale))
    return scale


def _snapshot_profile_enabled() -> bool:
    value = os.getenv("WINDOWS_MCP_PROFILE_SNAPSHOT", "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_bool(value: bool | str) -> bool:
    return value is True or (isinstance(value, str) and value.lower() == "true")


def _as_region(value: list | str | None) -> list | None:
    if value is None or isinstance(value, list):
        return value
    return json.loads(value)


def capture_desktop_state(desktop, *, use_vision, use_dom, use_annotation, use_ui_tree, width_reference_line, height_reference_line, display, region, tool_name):
    profile_enabled = _snapshot_profile_enabled()
    profile_started_at = time.perf_counter()
    stage_started_at = profile_started_at
    desktop_state_ms = 0.0
    metadata_render_ms = 0.0
    screenshot_encode_ms = 0.0

    if use_dom and not use_ui_tree:
        raise ValueError("use_dom=True requires use_ui_tree=True")

    display_indices = Desktop.parse_display_selection(display)

    grid_lines = None
    if width_reference_line and height_reference_line:
        grid_lines = (int(width_reference_line), int(height_reference_line))

    desktop_state = desktop.get_state(
        use_vision=use_vision,
        use_dom=use_dom,
        use_annotation=use_annotation,
        use_ui_tree=use_ui_tree,
        as_bytes=False,
        scale=_screenshot_scale(),
        grid_lines=grid_lines,
        display_indices=display_indices,
        region=region,
        max_image_size=Size(width=MAX_IMAGE_WIDTH, height=MAX_IMAGE_HEIGHT),
    )
    if profile_enabled:
        desktop_state_ms = (time.perf_counter() - stage_started_at) * 1000
        stage_started_at = time.perf_counter()

    interactive_elements = desktop_state.tree_state.interactive_elements_to_string()
    scrollable_elements = desktop_state.tree_state.scrollable_elements_to_string()
    semantic_tree = desktop_state.tree_state.semantic_tree_to_string()
    windows = desktop_state.windows_to_string()
    active_window = desktop_state.active_window_to_string()
    active_desktop = desktop_state.active_desktop_to_string()
    all_desktops = desktop_state.desktops_to_string()
    if profile_enabled:
        metadata_render_ms = (time.perf_counter() - stage_started_at) * 1000
        stage_started_at = time.perf_counter()

    screenshot_bytes = None
    if use_vision and desktop_state.screenshot is not None:
        buffered = io.BytesIO()
        desktop_state.screenshot.save(buffered, format="PNG")
        screenshot_bytes = buffered.getvalue()
        buffered.close()
    if profile_enabled:
        screenshot_encode_ms = (time.perf_counter() - stage_started_at) * 1000
        logger.info("%s profile: desktop_state_ms=%.1f metadata_render_ms=%.1f png_encode_ms=%.1f total_ms=%.1f", tool_name, desktop_state_ms, metadata_render_ms, screenshot_encode_ms, (time.perf_counter() - profile_started_at) * 1000)

    return {
        "desktop_state": desktop_state,
        "interactive_elements": interactive_elements,
        "scrollable_elements": scrollable_elements,
        "semantic_tree": semantic_tree,
        "windows": windows,
        "active_window": active_window,
        "active_desktop": active_desktop,
        "all_desktops": all_desktops,
        "screenshot_bytes": screenshot_bytes,
    }


def build_snapshot_response(capture_result, *, include_ui_details, ui_detail_note=None):
    desktop_state = capture_result["desktop_state"]
    interactive_elements = capture_result["interactive_elements"]
    scrollable_elements = capture_result["scrollable_elements"]
    semantic_tree = capture_result["semantic_tree"]
    windows = capture_result["windows"]
    active_window = capture_result["active_window"]
    active_desktop = capture_result["active_desktop"]
    all_desktops = capture_result["all_desktops"]
    screenshot_bytes = capture_result["screenshot_bytes"]

    interactive_elements = remove_private_use_chars(interactive_elements)
    scrollable_elements = remove_private_use_chars(scrollable_elements)
    semantic_tree = remove_private_use_chars(semantic_tree)

    interactive_elements = repair_surrogates(interactive_elements)
    scrollable_elements = repair_surrogates(scrollable_elements)
    semantic_tree = repair_surrogates(semantic_tree)
    windows = repair_surrogates(windows)
    active_window = repair_surrogates(active_window)
    active_desktop = repair_surrogates(active_desktop)
    all_desktops = repair_surrogates(all_desktops)

    def display_to_string(display):
        primary = " primary" if display.primary else ""
        return f"{display.index}:{display.device_name} {display.bounding_box.xyxy_to_string()}{primary}"

    metadata_text = f"Cursor Position: {desktop_state.cursor_position}\n"
    if desktop_state.screenshot_original_size:
        orig = desktop_state.screenshot_original_size
        scale = desktop_state.screenshot_scale or 1.0
        if scale < 1.0:
            coord_scale = round(1.0 / scale, 6)
            metadata_text += f"Screenshot Original Size: {orig.to_string()}\n"
            metadata_text += f"Screenshot Coordinate Scale: {coord_scale} — multiply every image pixel coordinate by {coord_scale} before passing to Click/Move/Scroll/any loc= argument\n"
        else:
            metadata_text += f"Screenshot Size: {orig.to_string()}\n"
    if desktop_state.available_displays:
        metadata_text += "Visible Displays: " + "; ".join(display_to_string(display) for display in desktop_state.available_displays) + "\n"
    if desktop_state.screenshot_displays:
        metadata_text += f"Selected Displays: {','.join(str(index) for index in desktop_state.screenshot_displays)}\n"
    if desktop_state.screenshot_region:
        metadata_text += f"Screenshot Region: {desktop_state.screenshot_region.xyxy_to_string()}\n"
        metadata_text += "Coordinate Space: Virtual desktop coordinates\n"
    if desktop_state.screenshot_backend:
        metadata_text += f"Screenshot Backend: {desktop_state.screenshot_backend}\n"
    if ui_detail_note:
        metadata_text += f"{ui_detail_note}\n"

    response_text = dedent(f'''
    {metadata_text}
    Active Desktop:
    {active_desktop}

    All Desktops:
    {all_desktops}

    Focused Window:
    {active_window}

    Opened Windows:
    {windows}
    ''')
    if include_ui_details:
        response_text += dedent(f'''

    UI Tree:
    {semantic_tree or "No elements found."}''')

    response = [response_text]
    if screenshot_bytes:
        response.append(Image(data=screenshot_bytes, format="png"))
    return response
