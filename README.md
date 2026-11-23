# hw-ds-authoring

A Claude skill for authoring, editing and reviewing **Hardware Design
Specifications (DS)** for any hardware block: power converters, analog and
mixed-signal front ends, digital/FPGA boards, RF/clock, interfaces and
electromechanical assemblies.

It enforces a fixed section contract, a source-priority order for conflicting
inputs, worked calculations with topology-tagged equations, derating and margin
analysis, a risk register, an open-items register where every TBD must land,
and a separation between the official document revision and AI working
history. It does not write an EVS (verification plan) or an EVR (results).

The contract itself is in [`SKILL.md`](SKILL.md). Start there.

## Install

**Claude Code** (full authoring flow: reads your sources from disk, builds DOCX
from a house template, runs the checks):

```bash
git clone https://github.com/ultraHWE-ddc2/hw-ds-authoring.git "$HOME/.claude/skills/hw-ds-authoring"
```

Windows PowerShell:

```powershell
git clone https://github.com/ultraHWE-ddc2/hw-ds-authoring.git "$env:USERPROFILE\.claude\skills\hw-ds-authoring"
```

Then open a new Claude Code session; type `/hw-ds-authoring` or just ask for a
DS. To update later:

```bash
git -C "$HOME/.claude/skills/hw-ds-authoring" pull
```

**claude.ai chat** (quick reviews and calculation checks; the build pipeline
does not run there): zip the folder so `SKILL.md` is at the root of a
`hw-ds-authoring/` directory, then Settings → Plugins → Your plugins → Add →
Upload.

## Optional tooling

- [pandoc](https://pandoc.org) for `scripts/build_docx.py` (`winget install JohnMacFarlane.Pandoc`).
- `pdftotext` (poppler) or `pip install pypdf` for scanning PDFs.

## Layout

| Path | Purpose |
|---|---|
| `SKILL.md` | The contract Claude follows |
| `references/` | Section structure; calculation checklists per block type |
| `templates/` | Markdown skeleton, authoring prompt, review checklist, registers, source-priority rules |
| `examples/` | Three worked calculations, a sparse-input example, lessons learned |
| `scripts/` | `check_open_items.py`, `scan_artifacts.py`, `build_docx.py`, and `tests/run_tests.py` |
| `assets/` | Default cover logo |

## Tests

```bash
python -I scripts/tests/run_tests.py
```

25 cases covering the scanner, the open-item checker and (when pandoc is
installed) a real build of the skeleton. Run them after any change to
`scripts/`.
