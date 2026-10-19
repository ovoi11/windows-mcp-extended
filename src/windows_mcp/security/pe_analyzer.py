"""PE file analysis service — header, sections, imports/exports, entropy, packer fingerprint.

Built on the `pefile` library (no re-implementation of the PE format parser).
Packer fingerprinting uses well-known public signatures: section names, import
characteristics and structural heuristics (entry point placement, entropy).
It is a heuristic detector, not an exhaustive official signature database.
"""

from __future__ import annotations

import math
from collections import Counter

import pefile

__all__ = ["analyze_pe", "detect_packer"]

# IMAGE_DIRECTORY_ENTRY indexes used below.
_ENTRY_SECURITY = 4
_ENTRY_COM_DESCRIPTOR = 14

# Public packer signatures keyed by section name (case-insensitive, NUL-stripped).
_SECTION_PACKER_MAP: dict[str, tuple[str, str, str]] = {
    "upx0": ("UPX", "UPX 压缩壳（UPX0/UPX1 节区）", "high"),
    "upx1": ("UPX", "UPX 压缩壳（UPX0/UPX1 节区）", "high"),
    "upx2": ("UPX", "UPX 压缩壳（UPX2 辅助节区）", "medium"),
    "upx!": ("UPX", "UPX 压缩壳（UPX! 节区）", "high"),
    ".vmp0": ("VMProtect", "VMProtect 虚拟化保护（.vmp0 节区）", "high"),
    ".vmp1": ("VMProtect", "VMProtect 虚拟化保护（.vmp1 节区）", "high"),
    ".themida": ("Themida", "Themida/WinLicense 保护（.themida 节区）", "high"),
    ".enigma1": ("Enigma", "Enigma Protector（.enigma1 节区）", "high"),
    ".enigma2": ("Enigma", "Enigma Protector（.enigma2 节区）", "high"),
    ".aspack": ("ASPack", "ASPack 压缩壳（.aspack 节区）", "high"),
    ".mpress1": ("MPRESS", "MPRESS 压缩壳（.MPRESS1 节区）", "high"),
    ".mpress2": ("MPRESS", "MPRESS 压缩壳（.MPRESS2 节区）", "high"),
    ".pec1": ("PECompact", "PECompact 压缩壳（.pec1 节区）", "high"),
    ".pec2": ("PECompact", "PECompact 压缩壳（.pec2 节区）", "high"),
    ".nsp0": ("NsPack", "NsPack 压缩壳（.nsp0 节区）", "high"),
    ".nsp1": ("NsPack", "NsPack 压缩壳（.nsp1 节区）", "high"),
    ".petite": ("Petite", "Petite 压缩壳（.petite 节区）", "high"),
    ".sforce3": ("SafeEngine", "SafeEngine 保护（.sforce3 节区）", "high"),
    ".packed": ("Packed", "通用加壳节区（.packed）", "medium"),
    ".pepack": ("Packed", "通用加壳节区（.pepack）", "medium"),
    ".adata": ("Packed", "可疑附加数据节区（.adata，常见于加壳变体）", "low"),
    ".code": ("Packed", "可疑节区名（.code，常见于加壳变体）", "low"),
}

# Import-name signatures for packers that leave bootstrap imports behind.
_IMPORT_PACKER_MAP: list[tuple[str, str, str]] = [
    ("pyi_", "PyInstaller", "PyInstaller 引导导入（pyi_* 运行时）", "high"),
    ("VMProtectSDK", "VMProtect", "VMProtect SDK 导入", "high"),
    ("TheMida", "Themida", "Themida SDK 导入", "high"),
]


def _entropy(data: bytes) -> float:
    """Shannon entropy in bits per byte (0.0 for empty data)."""
    if not data:
        return 0.0
    counts = Counter(data)
    total = len(data)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def _section_name(section) -> str:
    raw = getattr(section, "Name", b"") or b""
    return raw.split(b"\x00", 1)[0].decode("latin-1", errors="replace")


def detect_packer(pe: pefile.PE) -> list[dict[str, str]]:
    """Return a list of packer/protector fingerprints with evidence and confidence."""
    hits: list[dict[str, str]] = []

    # 1. Section-name signatures.
    for section in pe.sections:
        name = _section_name(section).lower()
        sig = _SECTION_PACKER_MAP.get(name)
        if sig:
            hits.append({"name": sig[0], "evidence": sig[1], "confidence": sig[2]})

    # 2. Import signatures.
    imports = getattr(pe, "DIRECTORY_ENTRY_IMPORT", None) or []
    import_names = [
        (imp.dll or b"").decode("latin-1", errors="replace").lower() for imp in imports
    ]
    for marker, name, evidence, confidence in _IMPORT_PACKER_MAP:
        if any(marker.lower() in n for n in import_names):
            hits.append({"name": name, "evidence": evidence, "confidence": confidence})

    # 3. Managed assembly.
    com_dir = pe.OPTIONAL_HEADER.DATA_DIRECTORY[_ENTRY_COM_DESCRIPTOR]
    if com_dir and com_dir.VirtualAddress:
        hits.append(
            {
                "name": ".NET",
                "evidence": "存在 CLR COM Descriptor（托管程序集）",
                "confidence": "high",
            }
        )

    # 4. Structural heuristics.
    ep = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    text_section = None
    for section in pe.sections:
        chars = section.Characteristics
        if chars & 0x60000020 and _section_name(section).lower() in (".text", "text"):
            text_section = section
            break
    ep_section = None
    for section in pe.sections:
        va = section.VirtualAddress
        size = section.Misc_VirtualSize or section.SizeOfRawData
        if va <= ep < va + size:
            ep_section = section
            break
    if ep_section is not None:
        ep_name = _section_name(ep_section).lower()
        if ep_name not in (".text", "text") and ep_name not in (".vmp0", ".vmp1"):
            hits.append(
                {
                    "name": "Packed",
                    "evidence": f"入口点位于非代码节「{_section_name(ep_section)}」",
                    "confidence": "medium",
                }
            )
    elif text_section is not None:
        hits.append(
            {
                "name": "Packed",
                "evidence": "入口点不在任何节区范围内（可疑）",
                "confidence": "medium",
            }
        )

    # 5. High-entropy sections suggest compression/encryption.
    high_entropy = [
        _section_name(s) for s in pe.sections if _entropy(s.get_data()) > 7.0
    ]
    if high_entropy:
        hits.append(
            {
                "name": "Packed",
                "evidence": f"高熵节区（熵 > 7.0）：{', '.join(high_entropy[:5])}",
                "confidence": "low",
            }
        )

    # 6. Authenticode signature presence.
    sec_dir = pe.OPTIONAL_HEADER.DATA_DIRECTORY[_ENTRY_SECURITY]
    if sec_dir and sec_dir.VirtualAddress:
        hits.append(
            {
                "name": "Signed",
                "evidence": "存在 Authenticode 签名目录",
                "confidence": "high",
            }
        )

    return hits


def analyze_pe(path: str, *, max_imports: int = 30, max_exports: int = 20) -> str:
    """Analyze a PE file and return a human-readable structured report."""
    try:
        pe = pefile.PE(path, fast_load=False)
    except pefile.PEFormatError as e:
        return f"Error: 不是有效的 PE 文件或无法解析：{e}"
    except OSError as e:
        return f"Error: 无法读取文件：{e}"

    from tabulate import tabulate

    try:
        fh = pe.FILE_HEADER
        oh = pe.OPTIONAL_HEADER

        machine = f"0x{fh.Machine:04X}"
        bits = "64 位" if oh.Magic == 0x20B else "32 位"
        ep = f"0x{oh.AddressOfEntryPoint:08X}"
        image_base = f"0x{oh.ImageBase:08X}"
        subsystem = oh.Subsystem
        tds = fh.TimeDateStamp

        lines = [
            "PE 文件分析报告",
            "=================",
            f"文件      : {path}",
            f"架构      : {bits}（Machine={machine}）",
            f"节区数    : {fh.NumberOfSections}",
            f"入口点    : {ep}",
            f"映像基址  : {image_base}",
            f"子系统    : {subsystem}（1=Native 2=GUI 3=CUI）",
            f"编译时间戳: {tds}",
            "",
        ]

        # Sections.
        section_rows = []
        for section in pe.sections:
            section_rows.append(
                [
                    _section_name(section),
                    f"0x{section.VirtualAddress:08X}",
                    section.Misc_VirtualSize or section.SizeOfRawData,
                    section.SizeOfRawData,
                    f"{_entropy(section.get_data()):.2f}",
                    f"0x{section.Characteristics:08X}",
                ]
            )
        lines.append(
            "节区表（Name / VA / VirtualSize / RawSize / 熵 / Characteristics）:"
        )
        lines.append(
            tabulate(
                section_rows,
                headers=["Name", "VA", "VSize", "RawSize", "Entropy", "Chars"],
                tablefmt="simple",
            )
        )
        lines.append("")

        # Imports.
        imports = getattr(pe, "DIRECTORY_ENTRY_IMPORT", None) or []
        if imports:
            import_rows = []
            total_imports = 0
            for imp in imports:
                dll = (imp.dll or b"").decode("latin-1", errors="replace")
                funcs = [
                    f.name.decode("latin-1", errors="replace")
                    for f in imp.imports
                    if f.name
                ]
                total_imports += len(funcs)
                import_rows.append([dll, len(funcs), ", ".join(funcs[:8])])
            lines.append(f"导入表（共 {len(imports)} 个 DLL，{total_imports} 个函数，最多显示 {max_imports} 个 DLL）:")
            lines.append(
                tabulate(import_rows[:max_imports], headers=["DLL", "Funcs", "示例"], tablefmt="simple")
            )
            lines.append("")
        else:
            lines.append("导入表：无（可能被加壳/静态链接）")
            lines.append("")

        # Exports.
        exports = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
        if exports and exports.symbols:
            export_names = [
                s.name.decode("latin-1", errors="replace") for s in exports.symbols if s.name
            ]
            lines.append(f"导出表（{len(export_names)} 个符号，最多显示 {max_exports} 个）:")
            lines.append(", ".join(export_names[:max_exports]))
            lines.append("")
        else:
            lines.append("导出表：无")
            lines.append("")

        # Resources.
        resources = getattr(pe, "DIRECTORY_ENTRY_RESOURCE", None)
        res_count = len(resources.entries) if resources and hasattr(resources, "entries") else 0
        lines.append(f"资源目录条目数: {res_count}")
        lines.append("")

        # Packer fingerprint.
        fingerprints = detect_packer(pe)
        if fingerprints:
            fp_rows = [
                [f["name"], f["evidence"], f["confidence"]] for f in fingerprints
            ]
            lines.append("壳/保护指纹（启发式）:")
            lines.append(
                tabulate(fp_rows, headers=["Name", "Evidence", "Confidence"], tablefmt="simple")
            )
        else:
            lines.append("壳/保护指纹：未匹配到已知特征（不保证未加壳）")
        lines.append("")

        # Authenticode / signatures.
        sec_dir = oh.DATA_DIRECTORY[_ENTRY_SECURITY]
        if sec_dir and sec_dir.VirtualAddress:
            lines.append(f"数字签名: 存在 Authenticode 签名（目录大小 {sec_dir.Size} 字节）")
        else:
            lines.append("数字签名: 无 Authenticode 签名")

        return "\n".join(lines)
    finally:
        pe.close()
