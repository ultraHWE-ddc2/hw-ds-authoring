"""Scan a DS deliverable for stale template artifacts.

Works on:
  * .docx  - every WordprocessingML part (document, headers, footers, footnotes,
             endnotes, comments) is parsed as XML and the text of each paragraph
             is reassembled from its runs, so a placeholder split across runs
             ("Choose an " + "item.") or XML-escaped ("&lt;Year&gt;") is found.
             Field results are tracked, so "Page: 3 of 20" produced by a live
             PAGE / NUMPAGES field is accepted, while the same text typed as
             plain characters (a stale cached value) is reported.
             Other XML parts (docProps, settings, styles) are scanned as text.
  * .pdf   - text is extracted with `pdftotext` if on PATH, else `pypdf`.
             A "Page: n of m" string is reported only when m differs from the
             PDF's real page count or n exceeds it, since a correctly updated
             live field prints true numbers.
  * .txt / .md - searched as plain text.

Exit status: 0 when nothing is found, 1 when at least one finding, 2 on a
usage error (missing file, unsupported type, no PDF reader).

Usage:
  python scan_artifacts.py <file> [<file> ...] [--extra LITERAL ...]
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

# Literal strings that must never survive into a delivered DS.
LITERAL_PATTERNS = [
    "Choose an item.",
    "Error!",
    "TEMPLATE ONLY",
    "<Year>",
    "<XXXXX>",
    "Rev: <XX>",
    "asdsd",
    "sdsdsd",
    "TBD_PLACEHOLDER",
]

# Unfilled {PLACEHOLDER} tokens from ds_skeleton.md or the prompt.
PLACEHOLDER_RE = re.compile(r"\{[A-Z][A-Z0-9_]*\}")

# "Page: n of m" in any spacing/case. Legitimate as a live field result; stale
# as plain text.
PAGE_RE = re.compile(r"Page:?\s*(\d+)\s+of\s+(\d+)", re.IGNORECASE)

WORD_TEXT_PARTS = re.compile(
    r"^word/(document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$"
)


@dataclass
class Finding:
    part: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.part} [{self.where}]: {self.message}"


# --------------------------------------------------------------------------- #
# DOCX
# --------------------------------------------------------------------------- #

def _tag(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def paragraph_text_with_fields(p: ET.Element) -> tuple[str, list[bool]]:
    """Reassemble a paragraph's text and, per character, whether it is a field result.

    Handles both complex fields (fldChar begin / separate / end) and simple
    fields (fldSimple). Text inside a field's instruction (between begin and
    separate) is not visible text and is skipped.
    """
    chars: list[str] = []
    in_field: list[bool] = []
    depth = 0            # nesting of complex fields
    in_instr = 0         # >0 while between begin and separate (instruction text)

    def emit(text: str, field: bool) -> None:
        chars.extend(text)
        in_field.extend([field] * len(text))

    def walk(el: ET.Element, simple_depth: int) -> None:
        nonlocal depth, in_instr
        for child in el:
            t = _tag(child)
            if t == "fldChar":
                kind = child.get(f"{{{W}}}fldCharType")
                if kind == "begin":
                    depth += 1
                    in_instr += 1
                elif kind == "separate":
                    in_instr = max(0, in_instr - 1)
                elif kind == "end":
                    depth = max(0, depth - 1)
                    # a field with no 'separate' (no cached result) closes its instr too
                    if in_instr > depth:
                        in_instr = depth
                continue
            if t == "fldSimple":
                walk(child, simple_depth + 1)
                continue
            if t == "instrText":
                continue
            if t == "t":
                if in_instr:
                    continue
                emit(child.text or "", depth > 0 or simple_depth > 0)
            elif t == "tab":
                emit("\t", depth > 0 or simple_depth > 0)
            elif t in ("br", "cr"):
                emit("\n", depth > 0 or simple_depth > 0)
            elif t == "delText":
                continue  # tracked deletion, not visible
            else:
                walk(child, simple_depth)

    walk(p, 0)
    return "".join(chars), in_field


def scan_text_block(text: str, field_mask: list[bool] | None, literals: list[str],
                    part: str, where: str, findings: list[Finding]) -> None:
    for literal in literals:
        n = text.count(literal)
        if n:
            findings.append(Finding(part, where, f"literal {literal!r} x{n}"))
    for m in PLACEHOLDER_RE.finditer(text):
        findings.append(Finding(part, where, f"unfilled placeholder {m.group(0)!r}"))
    for m in PAGE_RE.finditer(text):
        # "Page: " and " of " are normally typed label text; the two NUMBERS must
        # each come from a field result (PAGE / NUMPAGES) to be legitimate.
        if field_mask is not None and all(
            field_mask[a:b] and all(field_mask[a:b]) for a, b in (m.span(1), m.span(2))
        ):
            continue
        findings.append(Finding(part, where,
                                f"stale page text {m.group(0)!r} (page numbers are plain characters, not field results)"))


def scan_docx(path: Path, literals: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    with zipfile.ZipFile(path) as package:
        for name in package.namelist():
            if not name.endswith(".xml"):
                continue
            data = package.read(name)
            try:
                root = ET.fromstring(data)
            except ET.ParseError as exc:
                findings.append(Finding(name, "xml", f"unparseable part: {exc}"))
                continue
            if WORD_TEXT_PARTS.match(name):
                for i, p in enumerate(root.iter(f"{{{W}}}p"), start=1):
                    text, mask = paragraph_text_with_fields(p)
                    if text:
                        scan_text_block(text, mask, literals, name, f"paragraph {i}", findings)
            else:
                # docProps, settings, styles, numbering: plain text nodes + attribute values
                pieces = [t for t in root.itertext() if t]
                for el in root.iter():
                    pieces.extend(v for v in el.attrib.values() if v)
                text = "\n".join(pieces)
                if text:
                    # no field tracking here; page strings in these parts are never legitimate
                    scan_text_block(text, None, literals, name, "text", findings)
    return findings


# --------------------------------------------------------------------------- #
# PDF and plain text
# --------------------------------------------------------------------------- #

def extract_pdf(path: Path) -> tuple[str, int]:
    """Return (text, page_count)."""
    if shutil.which("pdftotext"):
        result = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                                capture_output=True, text=True, check=True)
        text = result.stdout
        pages = text.count("\f") or 1
        return text, pages
    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]
    except ImportError:
        raise SystemExit(f"Cannot read {path.name}: install poppler (pdftotext) or `pip install pypdf`.")
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages), len(reader.pages)


def scan_pdf(path: Path, literals: list[str]) -> list[Finding]:
    text, pages = extract_pdf(path)
    findings: list[Finding] = []
    part = path.name
    for literal in literals:
        n = text.count(literal)
        if n:
            findings.append(Finding(part, "pdf text", f"literal {literal!r} x{n}"))
    for m in PLACEHOLDER_RE.finditer(text):
        findings.append(Finding(part, "pdf text", f"unfilled placeholder {m.group(0)!r}"))
    for m in PAGE_RE.finditer(text):
        n, total = int(m.group(1)), int(m.group(2))
        if total != pages or n > pages:
            findings.append(Finding(part, "pdf text",
                                    f"page text {m.group(0)!r} disagrees with the PDF's {pages} pages (stale field)"))
    return findings


def scan_plain(path: Path, literals: list[str]) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []
    scan_text_block(text, None, literals, path.name, "text", findings)
    return findings


def scan_file(path: Path, literals: list[str]) -> list[Finding]:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return scan_docx(path, literals)
    if suffix == ".pdf":
        return scan_pdf(path, literals)
    if suffix in {".txt", ".md"}:
        return scan_plain(path, literals)
    raise SystemExit(f"Unsupported file type: {path}")


# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path, help="deliverables to scan")
    parser.add_argument("--extra", action="append", default=[], metavar="LITERAL",
                        help="additional house-specific literal to flag (repeatable)")
    args = parser.parse_args(argv)

    literals = LITERAL_PATTERNS + args.extra
    total = 0
    usage_error = False
    for path in args.files:
        if not path.is_file():
            print(f"[ERROR] not found: {path}")
            usage_error = True
            continue
        try:
            findings = scan_file(path, literals)
        except SystemExit as exc:
            print(f"[ERROR] {exc}")
            usage_error = True
            continue
        if findings:
            total += len(findings)
            print(f"[FAIL] {path}")
            for f in findings:
                print(f"       {f}")
        else:
            print(f"[PASS] {path}: no stale artifacts")
    if usage_error:
        return 2
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
