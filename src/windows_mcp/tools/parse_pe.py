"""ParsePE tool — analyze a PE file: header, sections, imports/exports, entropy, packer fingerprint."""

from mcp.types import ToolAnnotations

from windows_mcp.infrastructure import with_analytics
from windows_mcp.security import analyze_pe
from fastmcp import Context


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ParsePE",
        description='Analyze a PE file on disk: header, architecture, section table (with entropy), imports, exports, resources, Authenticode signature presence, and heuristic packer/protector fingerprint (UPX, VMProtect, Themida, .NET, PyInstaller and more). Keywords: PE analysis, packer, protector, shellcode-free inspection, section entropy, import table, export table, is it packed, packed executable. Provide an absolute path to the target file. The fingerprint is heuristic, not an official signature database.',
        annotations=ToolAnnotations(
            title="ParsePE",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ParsePE-Tool")
    def parse_pe_tool(
        path: str,
        max_imports: int = 30,
        max_exports: int = 20,
        ctx: Context = None,
    ) -> str:
        return analyze_pe(path, max_imports=max_imports, max_exports=max_exports)
