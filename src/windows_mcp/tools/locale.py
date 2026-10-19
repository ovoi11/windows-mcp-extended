"""LocaleInfo tool — system culture, locale and user language list."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import locale_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="LocaleInfo",
        description='Report Windows system locale information. Keywords: locale, culture, region, language, UI language, system language, 区域设置. Returns current culture, system locale and the user language list. Read-only.',
        annotations=ToolAnnotations(
            title="LocaleInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "LocaleInfo-Tool")
    def locale_info_tool(ctx: Context = None) -> str:
        return locale_info()
