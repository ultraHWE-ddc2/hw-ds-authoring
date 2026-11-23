"""Regression tests for the hw-ds-authoring scripts.

Run:  python -I scripts/tests/run_tests.py

Every fixture is built in a temporary directory and removed afterwards. Each
case states whether it is expected to PASS (no findings / no errors) or FAIL
(findings / errors), so a change that merely weakens a check shows up as an
expected-FAIL case starting to pass.

The pandoc build test runs only when pandoc is on PATH; otherwise it is
reported as SKIPPED, not as passed.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL_ROOT = SCRIPTS.parent


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod  # dataclasses look the module up here
    spec.loader.exec_module(mod)
    return mod


scan = load("scan_artifacts")
oi = load("check_open_items")
build = load("build_docx")

W_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def para(*runs: str) -> str:
    """Paragraph with each argument as its own run (so text is split across runs)."""
    return "<w:p>" + "".join(f"<w:r><w:t xml:space=\"preserve\">{r}</w:t></w:r>" for r in runs) + "</w:p>"


def complex_field(instr: str, cached: str) -> str:
    return (
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r><w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r><w:t>{cached}</w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    )


def make_docx(path: Path, body_paras: str = "", footer_paras: str = "", core_title: str = "DS") -> Path:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", f"<w:document {W_NS}><w:body>{body_paras}</w:body></w:document>")
        z.writestr("word/footer1.xml", f"<w:ftr {W_NS}>{footer_paras}</w:ftr>")
        z.writestr("docProps/core.xml",
                   f'<cp:coreProperties xmlns:cp="x" xmlns:dc="http://purl.org/dc/elements/1.1/">'
                   f"<dc:title>{core_title}</dc:title></cp:coreProperties>")
    return path


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dsscan_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def findings(self, docx: Path):
        return [str(f) for f in scan.scan_docx(docx, scan.LITERAL_PATTERNS)]

    # expected PASS
    def test_clean_docx_passes(self):
        d = make_docx(self.tmp / "clean.docx", para("Body text."), para("Rev A1 | Design Specification"))
        self.assertEqual(self.findings(d), [])

    # expected FAIL
    def test_split_run_placeholder_is_found(self):
        d = make_docx(self.tmp / "split.docx", para("Choose an ", "item."))
        f = self.findings(d)
        self.assertEqual(len(f), 1, f)
        self.assertIn("'Choose an item.'", f[0])
        self.assertIn("word/document.xml", f[0])

    # expected FAIL
    def test_escaped_placeholder_is_found(self):
        d = make_docx(self.tmp / "esc.docx", para("Copyright &lt;Year&gt; Company"))
        f = self.findings(d)
        self.assertEqual(len(f), 1, f)
        self.assertIn("'<Year>'", f[0])

    # expected FAIL
    def test_escaped_placeholder_in_docprops_is_found(self):
        d = make_docx(self.tmp / "props.docx", para("ok"), core_title="&lt;XXXXX&gt; Spec")
        f = self.findings(d)
        self.assertTrue(any("docProps/core.xml" in x and "'<XXXXX>'" in x for x in f), f)

    # expected PASS: live PAGE / NUMPAGES fields are legitimate even when cached as "1 of 2"
    def test_live_page_field_complex_is_accepted(self):
        footer = ("<w:p>" + '<w:r><w:t xml:space="preserve">Page: </w:t></w:r>'
                  + complex_field("PAGE", "1")
                  + '<w:r><w:t xml:space="preserve"> of </w:t></w:r>'
                  + complex_field("NUMPAGES", "2") + "</w:p>")
        d = make_docx(self.tmp / "field.docx", para("ok"), footer)
        self.assertEqual(self.findings(d), [])

    # expected PASS: fldSimple variant
    def test_live_page_field_simple_is_accepted(self):
        footer = ('<w:p><w:r><w:t xml:space="preserve">Page: </w:t></w:r>'
                  '<w:fldSimple w:instr=" PAGE "><w:r><w:t>15</w:t></w:r></w:fldSimple>'
                  '<w:r><w:t xml:space="preserve"> of </w:t></w:r>'
                  '<w:fldSimple w:instr=" NUMPAGES "><w:r><w:t>15</w:t></w:r></w:fldSimple></w:p>')
        d = make_docx(self.tmp / "simple.docx", para("ok"), footer)
        self.assertEqual(self.findings(d), [])

    # expected FAIL: same text typed as plain characters is a stale cached value
    def test_static_page_text_is_flagged(self):
        d = make_docx(self.tmp / "static.docx", para("ok"), para("Page: 1 of 2"))
        f = self.findings(d)
        self.assertEqual(len(f), 1, f)
        self.assertIn("stale page text", f[0])
        self.assertIn("word/footer1.xml", f[0])

    # expected FAIL: a page string where only part is a field (number typed by hand)
    def test_partially_static_page_text_is_flagged(self):
        footer = ("<w:p>" + '<w:r><w:t xml:space="preserve">Page: </w:t></w:r>'
                  + complex_field("PAGE", "3")
                  + '<w:r><w:t xml:space="preserve"> of 20</w:t></w:r></w:p>')
        d = make_docx(self.tmp / "partial.docx", para("ok"), footer)
        self.assertEqual(len(self.findings(d)), 1)

    # expected FAIL
    def test_unfilled_placeholder_token(self):
        d = make_docx(self.tmp / "tok.docx", para("Official revision remains {OFFICIAL_REV}."))
        f = self.findings(d)
        self.assertEqual(len(f), 1, f)
        self.assertIn("{OFFICIAL_REV}", f[0])

    # expected PASS: field instruction text is not visible text
    def test_field_instruction_text_not_scanned(self):
        body = ("<w:p>" + complex_field('TOC \\o "1-3" \\h \\z \\u', "Right-click to update") + "</w:p>")
        d = make_docx(self.tmp / "instr.docx", body)
        self.assertEqual(self.findings(d), [])

    # Markdown: expected PASS / FAIL
    def test_markdown_pass_and_fail(self):
        good = self.tmp / "good.md"; good.write_text("# DS\n\nAll filled.\n", encoding="utf-8")
        bad = self.tmp / "bad.md"; bad.write_text("# {BLOCK_NAME}\n\nChoose an item.\n", encoding="utf-8")
        self.assertEqual(scan.scan_plain(good, scan.LITERAL_PATTERNS), [])
        self.assertEqual(len(scan.scan_plain(bad, scan.LITERAL_PATTERNS)), 2)

    # CLI exit codes
    def test_cli_exit_codes(self):
        d = make_docx(self.tmp / "cli.docx", para("Choose an item."))
        self.assertEqual(scan.main([str(d)]), 1)
        clean = make_docx(self.tmp / "cli2.docx", para("ok"))
        self.assertEqual(scan.main([str(clean)]), 0)
        self.assertEqual(scan.main([str(self.tmp / "missing.docx")]), 2)


REGISTER_HEADER = "| Open Item | Question | Owner | Gate | Section | Status |\n|---|---|---|---|---|---|\n"


class OpenItemTests(unittest.TestCase):
    def run_check(self, text: str):
        errors, warnings, register = oi.check(text, 2, 3)
        return errors, warnings

    # expected PASS
    def test_clean_document(self):
        md = ("# DS\n\nRinging is unconfirmed (OI-01).\n\n"
              + REGISTER_HEADER + "| OI-01 | Ringing? | Hardware | First power-up | 8.2 | Open |\n")
        errors, warnings = self.run_check(md)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    # expected FAIL
    def test_tbd_without_open_item(self):
        md = "# DS\n\nThe current limit is TBD.\n"
        errors, _ = self.run_check(md)
        self.assertEqual(len(errors), 1)
        self.assertIn("TBD without an Open Item", errors[0])

    # expected PASS: TBD with OI on same row
    def test_tbd_with_open_item_on_row(self):
        md = ("| ID | Value |\n|---|---|\n| REQ-1 | TBD, see OI-02 |\n\n"
              + REGISTER_HEADER + "| OI-02 | Value? | Systems | Requirements freeze | 3 | Open |\n")
        errors, _ = self.run_check(md)
        self.assertEqual(errors, [])

    # expected FAIL: reference INSIDE a register row to a missing id
    def test_reference_inside_register_row_to_missing_id_fails(self):
        md = ("# DS\n\nSee OI-01.\n\n"
              + REGISTER_HEADER
              + "| OI-01 | Sense topology? Depends on OI-99 | Hardware | Layout release | 8 | Open |\n")
        errors, _ = self.run_check(md)
        self.assertTrue(any("OI-99 is cited but has no register row" in e for e in errors), errors)

    # expected PASS: reference inside a register row to an EXISTING id is fine and counts as a citation
    def test_reference_inside_register_row_to_existing_id_passes(self):
        md = ("# DS\n\nSee OI-01.\n\n"
              + REGISTER_HEADER
              + "| OI-01 | Sense topology? Depends on OI-02 | Hardware | Layout release | 8 | Open |\n"
              + "| OI-02 | Symbol check | Library | Schematic freeze | 5 | Open |\n")
        errors, warnings = self.run_check(md)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    # expected FAIL
    def test_duplicate_id(self):
        md = (REGISTER_HEADER
              + "| OI-01 | A | Hardware | Layout release | 8 | Open |\n"
              + "| OI-01 | B | Hardware | Layout release | 8 | Open |\n")
        errors, _ = self.run_check(md)
        self.assertTrue(any("duplicate register row for OI-01" in e for e in errors), errors)

    # expected FAIL
    def test_missing_owner_and_gate(self):
        md = (REGISTER_HEADER
              + "| OI-01 | A |  | Layout release | 8 | Open |\n"
              + "| OI-02 | B | Hardware | TBD | 8 | Open |\n")
        errors, _ = self.run_check(md)
        self.assertTrue(any("OI-01 has no owner" in e for e in errors), errors)
        self.assertTrue(any("OI-02 has no gate" in e for e in errors), errors)

    # expected FAIL
    def test_cited_but_missing(self):
        md = "# DS\n\nSee OI-07 for the load model.\n"
        errors, _ = self.run_check(md)
        self.assertTrue(any("OI-07 is cited but has no register row" in e for e in errors), errors)

    # warning only
    def test_orphan_row_warns_not_fails(self):
        md = REGISTER_HEADER + "| OI-03 | Orphan | Hardware | Layout release | 9 | Open |\n"
        errors, warnings = self.run_check(md)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)

    # expected PASS: TBD inside an HTML comment is ignored
    def test_html_comment_ignored(self):
        md = "# DS\n\n<!-- TBD: fill this in -->\n\nAll good.\n"
        errors, _ = self.run_check(md)
        self.assertEqual(errors, [])


@unittest.skipUnless(shutil.which("pandoc"), "pandoc not on PATH - build test SKIPPED")
class BuildTests(unittest.TestCase):
    """Documents pandoc --reference-doc behaviour rather than assuming it."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dsbuild_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_reference_with_body_marker(self) -> Path:
        ref = self.tmp / "ref.docx"
        subprocess.run(["pandoc", "-o", str(ref), "--print-default-data-file", "reference.docx"], check=True)
        # inject a body paragraph into the reference so we can prove it is NOT carried over
        marked = self.tmp / "ref_marked.docx"
        with zipfile.ZipFile(ref) as zin, zipfile.ZipFile(marked, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    text = data.decode("utf-8")
                    text = text.replace("<w:body>", "<w:body><w:p><w:r><w:t>TEMPLATE_BODY_MARKER</w:t></w:r></w:p>", 1)
                    data = text.encode("utf-8")
                zout.writestr(item, data)
        return marked

    def test_build_from_skeleton_order_styles_and_inheritance(self):
        """Builds the real skeleton and checks what pandoc actually produced."""
        ref = self.make_reference_with_body_marker()
        src = SKILL_ROOT / "templates" / "ds_skeleton.md"
        self.assertNotIn("{=openxml}", src.read_text(encoding="utf-8"), "skeleton must stay plain Markdown")
        out = self.tmp / "out.docx"
        rc = subprocess.run([sys.executable, "-I", str(SCRIPTS / "build_docx.py"), str(src),
                             "--reference", str(ref), "-o", str(out), "--no-scan"],
                            capture_output=True, text=True)
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
        facts = build.inspect_output(out)
        paras = facts["paras"]
        texts = [t for _, t, _ in paras]
        # reference body is NOT inherited; cover logo embedded
        self.assertFalse(any("TEMPLATE_BODY_MARKER" in t for t in texts))
        self.assertTrue(facts["images"], "cover logo was not embedded")
        # exactly one TOC field
        self.assertEqual(sum(1 for _, _, f in paras if f), 1)
        toc = facts["toc_index"]
        # order: cover -> ... -> Draft Working History -> Table of Contents -> TOC field -> 1. Introduction
        i_title = next(i for i, (_, t, _) in enumerate(paras) if "Hardware Design Specification" in t)
        i_hist = next(i for i, (_, t, _) in enumerate(paras) if t.strip() == "Draft Working History")
        i_tochead = next(i for i, (_, t, _) in enumerate(paras) if t.strip() == "Table of Contents")
        i_intro = next(i for i, (_, t, _) in enumerate(paras) if t.startswith("1. Introduction"))
        self.assertTrue(i_title < i_hist < i_tochead < toc < i_intro, (i_title, i_hist, i_tochead, toc, i_intro))
        # styles: cover is Title, front matter is the non-outline style, body headings are Heading1
        self.assertEqual(paras[i_title][0], "Title")
        self.assertEqual(paras[i_hist][0], "TOCHeading")
        self.assertEqual(paras[i_tochead][0], "TOCHeading")
        self.assertEqual(paras[i_intro][0], "Heading1")
        # nothing the TOC would list appears before the TOC field
        self.assertEqual(facts["headings_before_toc"], [])
        # the front-matter style is not an outline level in the styles part
        with zipfile.ZipFile(out) as z:
            styles = z.read("word/styles.xml").decode("utf-8")
        m = re.search(r'<w:style [^>]*w:styleId="TOCHeading".*?</w:style>', styles, re.DOTALL)
        self.assertIsNotNone(m, "TOCHeading style not defined in output")
        lvl = re.search(r'<w:outlineLvl w:val="(\d+)"', m.group(0))
        self.assertTrue(lvl is None or lvl.group(1) == "9", "TOCHeading has an outline level; TOC would list it")


class PrepareSourceTests(unittest.TestCase):
    def test_transforms(self):
        md = ("# My Block — HW DS\n\n## Abstract\n\ntext\n\n## Table of Contents\n\n"
              "## 1. Introduction\n\nbody\n\n## 2. Next\n")
        out = build.prepare_source(md, "TOC Heading")
        self.assertIn('::: {custom-style="Title"}\nMy Block — HW DS\n:::', out)
        self.assertIn('::: {custom-style="TOC Heading"}\nAbstract\n:::', out)
        self.assertEqual(out.count("{=openxml}"), 1)
        self.assertLess(out.index("Table of Contents"), out.index("{=openxml}"))
        self.assertLess(out.index("{=openxml}"), out.index("\n# 1. Introduction"))
        self.assertIn("\n# 1. Introduction", out)   # body headings promoted one level
        self.assertIn("\n# 2. Next", out)
        self.assertNotIn("## 1. Introduction", out)


class MarkdownTableTests(unittest.TestCase):
    """Every pipe table in the skill's Markdown has the same cell count on every row.

    An unescaped '|' inside a cell (e.g. absolute-value bars) silently splits the
    row when rendered; this catches it before pandoc does.
    """

    def test_table_rows_have_consistent_cell_counts(self):
        problems = []
        for md in list((SKILL_ROOT / "references").glob("*.md")) + list((SKILL_ROOT / "templates").glob("*.md")) \
                + list((SKILL_ROOT / "examples").glob("*.md")) + [SKILL_ROOT / "SKILL.md"]:
            lines = md.read_text(encoding="utf-8").splitlines()
            i = 0
            while i < len(lines) - 1:
                if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
                    width = lines[i].count("|")
                    j = i + 2
                    while j < len(lines) and lines[j].lstrip().startswith("|"):
                        if lines[j].count("|") != width:
                            problems.append(f"{md.relative_to(SKILL_ROOT)}:{j + 1}: {lines[j].count('|')} bars, header has {width}")
                        j += 1
                    i = j
                else:
                    i += 1
        self.assertEqual(problems, [], "\n".join(problems))


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    sys.exit(0 if result.wasSuccessful() else 1)
