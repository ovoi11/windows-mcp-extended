"""EnvironmentVariables tool — manage user/process environment variables."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import delete_environment, list_environment, set_environment


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="EnvironmentVariables",
        description='Manage environment variables. Keywords: environment variable, PATH, set env, get env, unset env. Use mode="list" to enumerate variables (scope="user" reads the registry, scope="process" reads the current process), mode="set" with name/value to create or update, mode="delete" with name to remove. User-scope changes take effect for new processes. Setting or deleting variables changes system state — obtain permission before modifying variables that were not explicitly requested.',
        annotations=ToolAnnotations(
            title="EnvironmentVariables",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "EnvironmentVariables-Tool")
    def environment_variables_tool(
        mode: Literal["list", "set", "delete"],
        name: str | None = None,
        value: str | None = None,
        scope: Literal["user", "process"] = "user",
        ctx: Context = None,
    ) -> str:
        if mode == "list":
            return list_environment(scope=scope)
        if not name:
            return "Error: name is required for set/delete modes."
        if mode == "set":
            if value is None:
                return "Error: value is required for set mode."
            return set_environment(name, value, scope=scope)
        if mode == "delete":
            return delete_environment(name, scope=scope)
        return "Error: unknown mode."
