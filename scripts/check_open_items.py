"""Check TBD / Open Item consistency in a DS written in Markdown.

Enforces the rules from SKILL.md that are most often broken:

  1. Every "TBD" in the body has an Open Item (an OI-nn id) on the same line or
     in the same paragraph.
  2. Every OI-nn cited anywhere - body text, and other OI ids mentioned inside a
     register row ("depends on OI-99") - has a row in the register. A row's own
     defining id is the only id excluded from this check for that row.
  3. Every register row has an owner and a gate (non-empty cells), and no id is
     defined twice.
  4. Every register row is cited at least once outside its own row (a row nobody
     points at is usually an orphan from an earlier edit) - a warning.

The register is any Markdown table whose first-column cells are OI-nn ids.

Exit status is 0 when rules 1-3 pass, 1 otherwise. Warnings do not fail the run.

Usage:
  python check_open_items.py <ds.md> [--register-cols OWNER GATE]

--register-cols gives the 1-based column numbers of the owner and gate cells in
the register table; the default (3 4) matches templates/open_items_table.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

OI_ID = re.compile(r"\bOI-\d{2,}\b")
TBD = re.compile(r"\bTBD\b")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
EMPTY_CELL = {"", "-", "—", "TBD", "?"}


def split_cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def paragraphs(lines: list[str]) -> list[tuple[int, str]]:
    """Return (start_line_number, text) per blank-line-delimited paragraph.

    Table rows are their own paragraph so a TBD and its OI must sit on the same row.
    """
    out: list[tuple[int, str]] = []
    buf: list[str] = []
    start = 0
    for i, line in enumerate(lines, start=1):
        if not line.strip() or TABLE_ROW.match(line):
            if buf:
                out.append((start, " ".join(buf)))
                buf = []
            if TABLE_ROW.match(line):
                out.append((i, line))
            continue
        if not buf:
            start = i
        buf.append(line)
    if buf:
        out.append((start, " ".join(buf)))
    return out


def check(text: str, owner_col: int, gate_col: int) -> tuple[list[str], list[str], dict[str, int]]:
    """Return (errors, warnings, register) for a DS Markdown text."""
    text = HTML_COMMENT.sub("", text)
    lines = text.splitlines()
    errors: list[str] = []
    warnings: list[str] = []

    # Register discovery and rule 3.
    register: dict[str, int] = {}
    register_rows: dict[int, str] = {}  # line -> defining id
    for i, line in enumerate(lines, start=1):
        if not TABLE_ROW.match(line):
            continue
        cells = split_cells(line)
        if not cells or not OI_ID.fullmatch(cells[0]):
            continue
        oi = cells[0]
        register_rows[i] = oi
        if oi in register:
            errors.append(f"line {i}: duplicate register row for {oi} (first at line {register[oi]})")
            continue
        register[oi] = i
        for name, col in (("owner", owner_col), ("gate", gate_col)):
            if col >= len(cells) or cells[col] in EMPTY_CELL:
                errors.append(f"line {i}: {oi} has no {name}")

    # Rules 1, 2, 4.
    cited: dict[str, int] = {}
    for start, para in paragraphs(lines):
        ids = set(OI_ID.findall(para))
        defining = register_rows.get(start)
        if defining is not None:
            ids.discard(defining)          # the row's own id is a definition, not a citation
        for oi in ids:
            cited.setdefault(oi, start)
        if defining is None and TBD.search(para) and not ids:
            snippet = para.strip()[:90]
            errors.append(f"line {start}: TBD without an Open Item: {snippet!r}")

    for oi, line in sorted(cited.items()):
        if oi not in register:
            errors.append(f"line {line}: {oi} is cited but has no register row")
    for oi, line in sorted(register.items()):
        if oi not in cited:
            warnings.append(f"line {line}: {oi} is in the register but never cited elsewhere")
    return errors, warnings, register


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ds", type=Path, help="DS Markdown file")
    parser.add_argument("--register-cols", nargs=2, type=int, default=(3, 4), metavar=("OWNER", "GATE"),
                        help="1-based owner and gate column numbers in the register (default 3 4)")
    args = parser.parse_args(argv)
    if not args.ds.is_file():
        print(f"[ERROR] not found: {args.ds}")
        return 2

    owner_col, gate_col = (c - 1 for c in args.register_cols)
    errors, warnings, register = check(args.ds.read_text(encoding="utf-8", errors="replace"), owner_col, gate_col)

    for w in warnings:
        print(f"[WARN] {w}")
    for e in errors:
        print(f"[FAIL] {e}")
    if errors:
        print(f"{len(errors)} error(s), {len(warnings)} warning(s) in {args.ds}")
        return 1
    print(f"[PASS] {args.ds}: {len(register)} open item(s), {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
