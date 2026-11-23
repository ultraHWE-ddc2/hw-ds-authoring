# Reusable DS Authoring Prompt

Fill in the placeholders and give this to the agent. Write `TBD` for anything
unknown. The agent must open an Open Item rather than guess.

---

## Task

Author a **Hardware Design Specification (DS)** — not an EVS and not an EVR — for
the block below, using the `hw-ds-authoring` skill.

## Block context

- Program / product: `{PROJECT_NAME}`
- Block: `{BLOCK_NAME}`
- Block type(s): `{BLOCK_TYPES}` (power / analog / digital / RF / clock / interface / electromechanical)
- Build this DS describes: `{CURRENT_BUILD}`
- Next-spin build (future recommendations only): `{FUTURE_BUILD}`
- Official document number: `{DOC_NUMBER}`
- Official revision (do not change without asking): `{OFFICIAL_REV}`
- Output folder: `{OUTPUT_FOLDER}`

## Inputs (highest authority first)

1. Official requirements: `{REQUIREMENTS_PATHS}`
2. Latest design reference documents: `{DESIGN_REFERENCE_PATHS}`
3. Released schematic / netlist: `{SCHEMATIC_PATH}`
4. Released BOM: `{BOM_PATH}`
5. Datasheets: `{DATASHEET_PATHS}`
6. Vendor tools / reference designs: `{VENDOR_TOOL_PATHS}`
7. Legacy DS / EVR / EVS: `{LEGACY_DS_PATHS}`
8. Notes and emails: `{NOTES_PATHS}`

## Templates and tooling

- House DS template (DOCX or other), or `none` to use the default contract: `{DS_TEMPLATE_PATH}`
- Build tool (Markdown to deliverable), or `none`: `{BUILD_TOOL_PATH}`
- Artifact scan script: `scripts/scan_artifacts.py` in this skill, or `{SCAN_TOOL_PATH}`

## What to produce

A DS that follows the contract in `SKILL.md` Section 3, including:

- requirements table, each row with a source and a status;
- external and internal interface tables relevant to this block only;
- component selection rationale for every critical part;
- worked calculations for every applicable item in the universal core and in the
  module(s) for `{BLOCK_TYPES}` (`references/calculation_checklists.md`);
- derating and margin analysis with the margin rule stated;
- start-up / sequencing section, where the block has one;
- budget roll-up (power, signal or timing);
- reconciliation of schematic, BOM and design reference;
- risk register (`templates/risk_register_table.md`);
- open items register (`templates/open_items_table.md`);
- future-spin recommendations, separate from current-build actions.

## Rules

- Rank sources with `templates/source_priority_rules.md`. If a conflict is
  unresolved or unverified, open an **Open Item**.
- Value status uses only: Confirmed / Candidate / Starting value / Open Item (OI-nn) / Superseded.
  Open-item register rows use Open / Closed (how). Do not mix the two families.
- State topology and operating mode for every power equation; where the
  checklist does not cover the topology, cite the controller datasheet or design
  reference for the equations used.
- Keep the official revision in the Revisions table. Track AI/tool passes in a
  separate Draft Working History with the required disclaimer. Do not future-date.
  Ask before changing official metadata.
- No measured results. Label any background reference data as such.
- Every value needs a derivation or a source. Every TBD needs an Open Item.
- Do not copy interface rows that belong to another block.
- Do not describe a simulation load model as a control mode of the device.
- Do not invent company names, document numbers, or template text.
- If a listed input is `TBD` or missing, say so in the source map, open an Open
  Item for the missing evidence, and mark dependent values Candidate / Open Item.
- If the output format is Markdown only, stop after the Markdown checks.

## Build and verify

1. Write the Markdown source from `templates/ds_skeleton.md`.
2. Run `scripts/check_open_items.py` on it; fix every error.
3. Generate the deliverable with `scripts/build_docx.py --reference {DS_TEMPLATE_PATH}`,
   or with the `docx` skill if there is no house template. Note: the template's
   styles, headers and footers are inherited; its body (cover art, TOC) is not —
   the cover comes from the Markdown and the TOC is the field the skeleton
   carries under its Table of Contents heading, updated in Word (F9).
4. Update fields and the table of contents; export PDF if required.
5. Run the final package scrub (stale page numbers and placeholders out of
   header/footer parts; the live footer stays).
6. Run `scripts/scan_artifacts.py` on the DOCX and, if produced, the PDF. Zero
   findings required.
7. Run `templates/ds_review_checklist.md`.

## Report back

- Deliverable paths (Markdown source, DOCX, PDF as produced).
- Short authoring summary, with the source-priority decisions made.
- Open-items list with owners and the gates they block.
- Scan result (must be zero findings).
- Confirmation that `{OFFICIAL_REV}` is unchanged.
- Automated steps that ran (checks, build, scan) listed separately from manual
  steps still needed (field/TOC update in Word, visual check of cover and
  headers, PDF export, sign-offs). Manual steps are reported as not done.
