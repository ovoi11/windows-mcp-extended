"""PowerPlan tool — list and switch Windows power schemes."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import get_active_plan, list_plans, set_active_plan


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="PowerPlan",
        description='Manage Windows power schemes. Keywords: power plan, power scheme, battery saver, high performance, balanced. Use mode="list" to enumerate schemes with GUIDs, mode="active" to report the current scheme, mode="set" with a scheme GUID to switch. Switching the power plan changes system behavior — obtain permission before switching away from an explicitly requested target.',
        annotations=ToolAnnotations(
            title="PowerPlan",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "PowerPlan-Tool")
    def power_plan_tool(
        mode: Literal["list", "active", "set"] = "list",
        guid: str | None = None,
        ctx: Context = None,
    ) -> str:
        if mode == "list":
            return list_plans()
        if mode == "active":
            return get_active_plan()
        if mode == "set":
            if not guid:
                return "Error: guid is required for set mode."
            return set_active_plan(guid)
        return "Error: unknown mode."
