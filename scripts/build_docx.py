"""Build a DS DOCX from clean Markdown source with pandoc and a house reference template.

The Markdown source stays plain (readable as a Markdown deliverable on its own).
Everything DOCX-specific is applied here, to a temporary copy, just before pandoc:

  1. The first `# ` line (the cover title) becomes a paragraph in the `Title`
     style, which is not an outline level, so the TOC does not list the cover.
  2. Every `## ` heading before the first numbered body heading (`## 1. ...`)
     - Abstract, Revisions, Acknowledgments, Draft Working History, Table of
     Contents - becomes a paragraph in a non-outline front-matter style
     (`TOC Heading` by default), so the TOC does not list front matter or itself.
  3. Body headings are promoted one level (`## 1.` -> Heading 1, `### 1.1` ->
     Heading 2, ...) because the source reserves the single `#` for the cover.
  4. A Word TOC *field* is inserted directly under the "Table of Contents"
     front-matter heading. It carries placeholder text until fields are updated
     in Word (F9). Pandoc's own --toc is deliberately not used: it always places
     the TOC at the very start of the body, before the cover.

What `pandoc --reference-doc` does, and does not do (pandoc manual):
  * USES the reference document's styles, page setup, margins, and the headers
    and footers in its section properties.
  * IGNORES the reference document's body. A cover page, cover art or a TOC that
    lives in the template's body is NOT carried into the output. The cover is
    therefore generated from the Markdown (logo image + title block).

Pandoc is required (status 2 if missing). The reference must be a plain .docx:
open the house .dotx in Word, delete the body, Save As .docx; keep its headers
and footers. If the reference lacks the front-matter style, pandoc falls back to
Normal for those headings - check them visually (the report says so).

After a build the script prints what ran automatically and what a person must
still do in Word. The build is not "done" until those manual steps are.

Usage:
  python build_docx.py <ds.md> --reference <house_template.docx> -o <out.docx>
                       [--front-matter-style "TOC Heading"] [--keep-prepared <path.md>]
                       [--extra PATTERN ...] [--no-scan]
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCANNER = HERE / "scan_artifacts.py"
SKILL_ROOT = HERE.parent
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

INSTALL_HINT = (
    "pandoc not found on PATH.\n"
    "  Windows: winget install JohnMacFarlane.Pandoc\n"
    "  macOS:   brew install pandoc\n"
    "  Debian:  sudo apt install pandoc\n"
    "Then re-run this script."
)

TOC_FIELD = (
    '```{=openxml}\n'
    '<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
    '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    '<w:r><w:t>Update fields (F9) in Word to build the table of contents.</w:t></w:r>'
    '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>\n'
    '```\n'
)

BODY_HEADING = re.compile(r"^## \d+\.\s")
H1 = re.compile(r"^# (.+?)\s*$")
H2 = re.compile(r"^## (.+?)\s*$")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def styled(text: str, style: str) -> str:
    return f'::: {{custom-style="{style}"}}\n{text}\n:::\n'


def prepare_source(md: str, front_matter_style: str) -> str:
    """Apply the DOCX-only transformations to Markdown text and return the result."""
    md = HTML_COMMENT.sub("", md)
    lines = md.splitlines()
    out: list[str] = []
    title_done = False
    in_body = False
    in_fence = False
    for line in lines:
        if line.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        if not title_done and (m := H1.match(line)):
            out.append(styled(m.group(1), "Title"))
            title_done = True
            continue
        if not in_body and BODY_HEADING.match(line):
            in_body = True
        if in_body and line.startswith("##"):
            # body headings are written one level down in the source (## 1., ### 1.1)
            # because the cover holds the single #; promote them so top-level
            # sections use the template's Heading 1, sub-sections Heading 2, etc.
            out.append(line[1:])
            continue
        if not in_body and (m := H2.match(line)):
            heading = m.group(1)
            out.append(styled(heading, front_matter_style))
            if re.search(r"table of contents", heading, re.IGNORECASE):
                out.append("")
                out.append(TOC_FIELD)
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def inspect_output(docx: Path) -> dict:
    """Report what the generated package actually contains, by parsing it."""
    with zipfile.ZipFile(docx) as z:
        names = z.namelist()
        body = ET.fromstring(z.read("word/document.xml"))
        styles = ET.fromstring(z.read("word/styles.xml")) if "word/styles.xml" in names else None
    paras: list[tuple[str, str, bool]] = []  # (style, text, has_toc_field)
    for p in body.iter(f"{{{W}}}p"):
        ps = p.find(f"{{{W}}}pPr/{{{W}}}pStyle")
        style = ps.get(f"{{{W}}}val") if ps is not None else ""
        text = "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
        instr = "".join(i.text or "" for i in p.iter(f"{{{W}}}instrText"))
        paras.append((style, text, "TOC" in instr))
    toc_index = next((i for i, (_, _, f) in enumerate(paras) if f), None)
    headings_before_toc = [s for s, _, _ in paras[: toc_index or 0] if re.fullmatch(r"Heading[1-3]", s or "")]
    fm_style_defined = None
    if styles is not None:
        fm_style_defined = {s.get(f"{{{W}}}styleId") for s in styles.iter(f"{{{W}}}style")}
    return {
        "paras": paras,
        "toc_index": toc_index,
        "headings_before_toc": headings_before_toc,
        "images": any(n.startswith("word/media/") for n in names),
        "headers_footers": any(n.startswith(("word/header", "word/footer")) for n in names),
        "style_ids": fm_style_defined,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="DS Markdown source (plain; no DOCX markup needed)")
    parser.add_argument("--reference", type=Path, required=True, help="house template .docx (styles, headers, footers)")
    parser.add_argument("-o", "--output", type=Path, required=True, help="output .docx")
    parser.add_argument("--front-matter-style", default="TOC Heading",
                        help='non-outline Word style for front-matter headings (default "TOC Heading")')
    parser.add_argument("--keep-prepared", type=Path, help="also save the transformed Markdown here for inspection")
    parser.add_argument("--extra", action="append", default=[], metavar="LITERAL",
                        help="extra house placeholder for the scan (repeatable)")
    parser.add_argument("--no-scan", action="store_true", help="skip scan_artifacts.py after building")
    args = parser.parse_args(argv)

    if not shutil.which("pandoc"):
        print(INSTALL_HINT)
        return 2
    if not args.source.is_file():
        print(f"[ERROR] source not found: {args.source}")
        return 2
    if not args.reference.is_file() or args.reference.suffix.lower() != ".docx":
        print(f"[ERROR] reference must be an existing .docx: {args.reference}")
        return 2

    source_text = args.source.read_text(encoding="utf-8")
    prepared = prepare_source(source_text, args.front_matter_style)
    if args.keep_prepared:
        args.keep_prepared.write_text(prepared, encoding="utf-8")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    resource_path = os.pathsep.join([str(args.source.resolve().parent), str(SKILL_ROOT)])
    with tempfile.TemporaryDirectory(prefix="dsbuild_") as tmp:
        prepared_path = Path(tmp) / args.source.name
        prepared_path.write_text(prepared, encoding="utf-8")
        cmd = [
            "pandoc", str(prepared_path),
            "--from", "markdown+pipe_tables+grid_tables+implicit_figures+link_attributes+fenced_divs+raw_attribute",
            "--to", "docx",
            "--reference-doc", str(args.reference),
            "--resource-path", resource_path,
            "--output", str(args.output),
        ]
        print("[auto] build:", " ".join(cmd))
        result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode:
        print(result.stderr)
        print(f"[ERROR] pandoc exited {result.returncode}")
        return result.returncode
    if result.stderr.strip():
        print(result.stderr.strip())
    print(f"[auto] built {args.output}")

    facts = inspect_output(args.output)
    print(f"[auto] package: images={'yes' if facts['images'] else 'NO'}, "
          f"headers/footers from template={'yes' if facts['headers_footers'] else 'NO'}, "
          f"TOC field={'yes' if facts['toc_index'] is not None else 'NO'}")
    if facts["toc_index"] is None:
        print("[WARN] no TOC field: the source has no front-matter '## Table of Contents' heading.")
    if facts["headings_before_toc"]:
        print(f"[WARN] outline headings before the TOC field ({facts['headings_before_toc']}); "
              "the TOC will list them. Front matter must come before the first '## 1.' heading.")
    fm_id = args.front_matter_style.replace(" ", "")
    if facts["style_ids"] is not None and fm_id not in facts["style_ids"]:
        print(f"[WARN] style '{args.front_matter_style}' is not defined in the reference template; "
              "front-matter headings fall back to Normal. Check them visually or pass --front-matter-style.")
    if "![" in source_text and not facts["images"]:
        print("[WARN] the Markdown references an image but the package has no media; check the image path.")

    scan_rc = 0
    if not args.no_scan:
        scan_cmd = [sys.executable, "-I", str(SCANNER), str(args.output)]
        for literal in args.extra:
            scan_cmd += ["--extra", literal]
        print("[auto] scan:", " ".join(scan_cmd))
        scan_rc = subprocess.run(scan_cmd, text=True).returncode

    print("\nAutomated steps completed: source preparation, pandoc build" + ("" if args.no_scan else ", artifact scan") + ".")
    print("Manual steps still required (not done by this script):")
    print("  1. Open the DOCX in Word; update all fields (Ctrl+A, F9); confirm the TOC placeholder text is gone; save.")
    print("  2. Check the cover, front-matter headings, headers and footers visually against the house template.")
    print("     The template's own body (cover art, pre-built TOC) is NOT in this file by design.")
    print("  3. Export the PDF, then re-run scan_artifacts.py on the saved DOCX and the PDF.")
    return scan_rc


if __name__ == "__main__":
    sys.exit(main())
