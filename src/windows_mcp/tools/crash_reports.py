"""CrashReportList tool — recent Windows Error Reporting entries."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import crash_report_list


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="CrashReportList",
        description='List recent Windows Error Reporting (WER) entries: crash/hang reports with age and app signature. Keywords: crash report, wer, app crash, blue screen reports, 崩溃报告. Read-only.',
        annotations=ToolAnnotations(
            title="CrashReportList",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "CrashReportList-Tool")
    def crash_report_list_tool(
        limit: int = 15,
        ctx: Context = None,
    ) -> str:
        return crash_report_list(limit=limit)
