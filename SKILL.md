---
name: hw-ds-authoring
description: >-
  Author, restructure, complete or review a Hardware Design Specification (DS)
  for any hardware block: power supplies and converters (buck, boost,
  buck-boost, flyback, LLC, point-of-load, housekeeping rails), analog and
  mixed-signal front ends, digital/FPGA/processor boards, RF and clock
  sub-blocks, sensor and interface circuits, or electromechanical assemblies.
  Use this when the user asks to write, draft, update or review a Design Spec,
  Hardware Design Specification or "DS", or to turn schematics, BOMs, design
  references and datasheets into one. Enforces a fixed section contract,
  source-priority conflict handling, worked calculations with derivations,
  derating and margin analysis, an open-items register, and separation of the
  official document revision from AI/tool working history. It does NOT write an
  EVS (verification plan) or an EVR (measured results report).
---

# Hardware Design Specification (DS) Authoring

## 1. Purpose

A DS is written before or during schematic implementation. It records:

- design intent and the operating envelope,
- external and internal interfaces,
- component choices **and the calculations that justify each value**,
- derating, tolerance and thermal margins,
- start-up / shut-down or sequencing behaviour where it applies,
- marginal, unresolved or measurement-dependent areas,
- risks and open items that gate schematic freeze, layout, BOM release and bring-up.

The DS exists to **remove ambiguity** for schematic capture, layout, BOM release
and prototype bring-up, and to **flag marginal areas** that need extra care.

### DS vs EVS vs EVR

| Document | Purpose | Measured results? |
|---|---|---|
| **DS** (this skill) | Intent, derivations, assumptions, margins, risks, open items | **No.** Design targets only, plus clearly-labelled background reference data |
| **EVS** | Verification plan: what is tested, how, pass/fail criteria | No results, only the plan |
| **EVR** | Verification report: measured results and pass/fail determinations | Yes |

Never put EVR-style measured results into a DS. Background data from an earlier
reference (for example a published efficiency curve used in a budget) may appear
**only if clearly marked as background reference data**, never as a result of
this design.

## 2. Intake: find the house profile before drafting

Every organisation has its own DS template, document-control scheme and section
naming. Before drafting, establish these inputs (ask once, in one message, only
for what is missing and cannot be read from the files):

1. **Block type(s)** — power, analog, digital, RF, clock, interface, mechanical,
   or a mix. This selects the extra calculation modules (Section 7).
2. **House template** — a Word/DOCX template or an existing approved DS to match.
   If one exists, its section order, section numbering and style **override** the
   default in `references/section_structure.md`, and every "section x.y"
   cross-reference in the registers uses the template's numbers.
3. **Document control** — official document number, official revision, release
   status. Read them; do not invent them.
4. **Sources** — the official requirements, design references, released
   schematic/netlist, BOM, datasheets, vendor tools, legacy DS/EVR/EVS, notes.
5. **Output folder and format** — Markdown source only, DOCX, PDF, or all.
   When the user asks for Markdown only, the job ends after the Markdown checks
   (`check_open_items.py`, `scan_artifacts.py` on the `.md`); do not run or
   report DOCX/PDF steps as pending.

If no house template exists, use the default section contract in
`references/section_structure.md` and say so in the summary.

**Default house profile.** The skill ships the Dominion Dynamics logo at
`assets/dominion_dynamics_logo.jpg`, and the skeleton places it on the cover.
It applies when the DS is a Dominion Dynamics document — the default when the
user says nothing about the organisation. It does **not** apply when the user
names another organisation, or when the DS is for a customer or supplier under
their own document control. If the supplied house template carries the logo in
its **header or footer**, delete the skeleton's logo line — headers and footers
are inherited by the build, so it would appear twice. A logo on the template's
**cover page** is *not* inherited (Section 11), so in that case keep the
skeleton's logo. When in doubt, ask in the intake message.

**When something is missing.** Report the limitation; never fill the gap.
- A source the DS needs (requirement, datasheet, schematic, BOM) is not
  available: state what is missing in the source map, open an Open Item
  "missing evidence: <source>" with an owner, and mark every value that depends
  on it **Candidate** or **Open Item**. Do not cite a document you have not seen.
- The EVS does not exist yet: write "verification pending; EVS not yet written
  (OI-nn)" and open that Open Item. Never write "verified" for a test that has no
  plan yet, and do not invent test numbers.
- Tooling is absent (pandoc, Word, a house template): deliver what can be built
  (the Markdown and its checks), list the remaining steps as manual actions in
  the report, and say plainly that the DOCX/PDF was not produced. Never report a
  step as done that did not run.
- **Substitutions that are never made silently** when the real input is
  missing: a ceramic-capacitor DC-bias loss percentage; a derating rule
  (e.g. "80 %"); a hot R_DS(on) multiplier; a loop bandwidth or crossover; a
  transient allowance taken from the DC tolerance; a control mode (DCM vs
  forced PWM); a thermal resistance. Each is an Open Item, and the calculation
  that needs it is shown with the input named as missing.
- **Requirement authority is tracked, not assumed.** The requirements table's
  Source cell carries the document, revision and approval state ("rev 0.9,
  pending signoff"). Unsigned requirements are provisional analysis targets:
  every result that depends on them is at most **Candidate** until the
  requirement is signed off, and the Open Item that tracks signoff is cited.
- Owners and gates that nobody has assigned are written as
  "<role> (proposed)" — never left blank and never invented as a name.

Never use any other company name, document number or template in the output
that did not come from the user's files or the user's message.

## 3. Mandatory DS contract

Produce the document in the order given by `references/section_structure.md`.
Do not omit sections. If a section does not apply, state why in one line.
Under the default contract the front matter is unnumbered and the body is
numbered from 1 (Introduction) to 17 (Reference Documents); every "section x.y"
cross-reference in the risk and open-items registers uses those body numbers.
When a house template is supplied, its numbering replaces this one throughout
(Section 2).

The contract, in short:

- **Front matter:** cover, abstract, official revisions table, legal /
  acknowledgments, Draft Working History (kept separate; see Section 5), table of
  contents.
- **Body:** scope; system context and block diagram; requirements and operating
  envelope; external and internal interface tables; design description;
  component selection rationale; calculations; derating and margin analysis;
  start-up / sequencing; power or signal budget; implementation and BOM /
  schematic reconciliation; risks and marginal areas; open items and review
  questions; future-spin recommendations; appendix / acronyms; reference
  documents.

## 4. Source-priority order

When sources disagree, rank them with `templates/source_priority_rules.md`.
Default order, highest authority first:

1. Official project requirements
2. Latest design reference documents from detailed review
3. Released schematic / netlist / BOM
4. Datasheets
5. Vendor tools and reference designs
6. Legacy DS / EVR / EVS documents
7. Emails and meeting notes
8. Internet and general best practice

Rules:

- Prefer the latest design reference or the released schematic/BOM **when it is
  clearly verified**.
- Datasheets win for pin numbers, names and absolute maximum ratings, because
  schematic symbols can be wrong. If symbol and datasheet disagree, keep the
  datasheet value and open an Open Item to confirm the library symbol and land
  pattern.
- If a conflict is unresolved, **do not guess** — raise an Open Item.
- Never silently pick one source. Name the source chosen and why.

## 5. Status vocabulary and revision discipline

### Status vocabulary

There are two separate status families. Do not mix them in one column.

**Value status** — the technical confidence in a number, requirement or
decision. Every value-bearing row and every calculation carries exactly one of
these five labels:

- **Confirmed** — calculated or specified, source identified, implementable as
  written. Correct arithmetic alone does not make a value Confirmed; the inputs
  must be sourced and approved. "Arithmetic checked" may be noted separately.
- **Candidate** — believed correct, but rests on a named assumption, approval or
  verification that has not happened yet. Name it, and the Open Item if one exists.
- **Starting value** — defensible initial value; the final value comes from bench
  measurement defined in the EVS. Name the EVS test.
- **Open Item (OI-nn)** — the value cannot be stated until the referenced Open
  Item closes. Use this when there is no defensible number yet; use Candidate
  when there is one.
- **Superseded** — the value shown has been replaced by a higher-ranked or newer
  source. It is a historical marker, not a confidence level: the row keeps the
  old value and names the replacing source and the row that now governs, so a
  reviewer sees the change rather than wondering where the old number went.

**Open-item lifecycle** — the state of a row in the open-items register:
**Open** or **Closed (how, by which source)**. A closed Open Item stays in the
register; the values that depended on it move from Open Item / Candidate to
Confirmed, Starting value or Superseded as appropriate.

### Revisions

- The **official revision** lives in the Revisions table and is the only revision
  record the organisation recognises.
- AI/tool passes go in a **separate Draft Working History** table, placed before
  the table of contents, with this disclaimer:
  > "This internal working history is not part of the official document revision.
  > Official document revision remains {OFFICIAL_REV}."
- Never merge working history into the official Revisions table.
- Never change the official revision because an AI/tool pass ran.
- Never future-date a revision. If the real date is unknown, use `Draft` or `TBD`.
- Ask the user before setting or changing official release metadata (revision,
  revision date, document number, release status).

## 6. Common mistakes to prevent

Do not:

- copy interface rows that do not belong to this block (for example RF rows in a
  power DS);
- overclaim old or pending-signoff requirements as final;
- describe a simulation load model (constant current, constant power, a
  resistor) as if it were a control mode of the device;
- confuse DS, EVS and EVR;
- leave a TBD only in prose — every TBD needs an Open Item;
- leave stale template artifacts (placeholders, dropdown defaults, cached page
  numbers, test strings);
- present a value with no equation, no inputs and no source;
- produce a generic document with no risk or margin analysis;
- claim a measurement that was never performed;
- mix current-build actions with future-spin recommendations;
- future-date anything, or change the official revision because a working pass ran.

## 7. Calculations and analysis modules

Every item that applies to the block must appear as a **worked calculation**:
equation, input numbers with their source, result, and status. Mark each item
Applicable or Not applicable with a one-line reason. `examples/calculation_examples.md`
shows the required shape; match it.

Every equation states the **topology, operating mode and assumptions** it holds
for. The power checklist gives equations per topology (buck, boost, inverting
buck-boost, four-switch buck-boost, flyback, forward, half/full-bridge, LLC);
for any topology or mode it does not cover, take the equations from the
controller datasheet or an authoritative design reference, cite them, and do
not apply a generic (buck) form.

Start from the universal core, then add the module(s) for each block type. The
full checklists are in `references/calculation_checklists.md`.

- **Universal core (every DS):** requirement traceability; component selection
  justification; derating (voltage, current, power, temperature); tolerance stack
  for every output or threshold that has an accuracy budget; thermal estimate at
  worst-case ambient; power or signal budget; sensitivity of the result to its
  main inputs (ranked only when uncertainty ranges are known).
- **Power module:** feedback and reference mapping, switching-device voltage and
  conduction/switching loss, current sense and limit, inductor ripple and
  saturation, input and output ripple, transient response, UVLO and soft-start,
  snubber dissipation, efficiency roll-up.
- **Analog / mixed-signal module:** gain and bandwidth, noise budget, input and
  output range, offset and drift, stability / phase margin, ADC/DAC resolution
  and reference.
- **Digital / FPGA / processor module:** supply sequencing and decoupling,
  impedance and reference-plane continuity, timing budget (setup/hold, skew, jitter),
  signal integrity (termination, edge rate), configuration and reset.
- **RF / clock module:** link or gain budget, impedance and matching, phase
  noise and jitter budget, harmonic and spur analysis, thermal and power handling.
- **Interface / connector / EMC module:** current rating per pin or contact,
  creepage and clearance, ESD and surge protection, filter attenuation vs limit.
- **Mechanical / electrical assembly module:** conductor and trace current
  capacity, fastener or contact resistance, vibration and shock where stated.

Where an input to a calculation is unconfirmed, raise an Open Item. If bounds
were supplied, show the result at each bound; if not, show the nominal result
and the sensitivity, with any illustrative value labelled as such — never invent
a tolerance to manufacture a case. A calculation whose inputs are missing is
still a complete entry: equation, the missing inputs named, status Open Item.
Where a value can only be finalised by measurement, mark it **Starting value**
and point to the EVS test (or to the Open Item that says the EVS is not yet
written). `examples/sparse_input_example.md` shows what a correct DS looks like
when most inputs are absent: conditional results and an honest register, not a
design assembled from assumed values.

## 8. Recommended workflow

1. Run the intake in Section 2. Read the house template and all sources.
2. Build a source map and rank each source per Section 4.
3. Extract requirements; give each a source.
4. Reconcile schematic / BOM / design-reference conflicts. Open an OI for each
   unresolved one.
5. Draft the outline in the house or default section order.
6. Populate the interface tables; keep only rows relevant to this block.
7. Work every calculation in the universal core and the matching modules.
8. Write the component selection rationale.
9. Write the derating and margin analysis; quantify marginal areas.
10. Write the start-up / sequencing section and the budget.
11. Write the risk register and the open-items register.
12. Write future-spin recommendations, kept apart from current-build actions.
13. Build the deliverable (Section 11) and run the review gates (Section 12).
14. Report the summary, open items, output paths and scan results.

## 9. Editing an existing DS

Most DS work is maintenance, not creation. When the user asks for a change to a
DS that already exists:

- **Read before you write.** Read the current DS and the sources it cites before
  editing anything. Do not assume any earlier chat or session history; continue
  from the files on disk. If memory and a file disagree, the file wins.
- **Make narrow, targeted edits.** Change only what was asked. Do not regenerate
  the whole document for a small fix, and do not re-scope, expand or add
  sections beyond the request.
- **Preserve existing technical content:** tables, pin audits, per-row status
  columns, TBD / verify flags, open items and their ids, and the official
  revision. Renumber nothing that a reviewer may already have cited.
- **Log the pass** in the Draft Working History, not in the official Revisions
  table (Section 5).
- **Re-run the checks** (`scripts/check_open_items.py` and
  `scripts/scan_artifacts.py`) on the edited document, because a small edit can
  orphan an Open Item or leave a TBD without one.
- If the requested change contradicts a higher-ranked source (Section 4), say so
  and ask before making it.

## 10. Review mode

When the user asks for a review of a DS rather than a change to it:

1. Read the whole DS and its cited sources.
2. Run `scripts/check_open_items.py` and `scripts/scan_artifacts.py` on it.
3. Walk `templates/ds_review_checklist.md` and the calculation checklist for the
   block type, recording each failure.
4. Check every calculation's arithmetic and units, and every derating against its
   stated margin rule. Recompute; do not take the result on trust.
5. Report findings in this table, most severe first, and **do not edit the
   document** unless the user then asks you to:

| # | DS section | Finding | Severity | Suggested fix |
|---|---|---|---|---|
| F-01 | 9.2 | MOSFET derating uses V_in,max without ringing; margin shrinks from 35 % to 12 % with the 20 % overshoot stated in 6.1 | High | Recompute with overshoot; raise OI if ringing is unmeasured |

Severity follows the risk register: High = damage, safety or missed hard
requirement; Medium = rework or schedule; Low = nuisance or style.

## 11. Build and verify

- Author the DS as maintainable **Markdown source** (skeleton in
  `templates/ds_skeleton.md`). Markdown is the source; the DOCX (or the house
  format) is the deliverable.
- Before building, run `scripts/check_open_items.py` on the Markdown. It fails
  on any TBD without an Open Item, any OI cited in the text but missing from the
  register, and any register row without an owner or a gate.
- The Markdown source stays plain. `scripts/build_docx.py` applies every
  DOCX-specific transformation to a temporary copy at build time: the cover
  `#` title becomes the non-outline `Title` style; the front-matter `##`
  headings (everything before `## 1.`) become a non-outline style (`TOC
  Heading` by default) so the TOC lists neither the cover nor itself; and a
  Word TOC field is inserted under the "Table of Contents" heading, after the
  Draft Working History. Pandoc's own `--toc` is not used (it lands before the
  cover). Then it runs `pandoc --reference-doc` and the artifact scan.
- Know exactly what `--reference-doc` inherits: the template's **styles, page
  setup, headers and footers**. It does **not** carry over the template's body —
  a cover page, cover art or a pre-built TOC in the template body are discarded,
  so the cover is generated from the Markdown (logo image and title block). If
  the house cover must be reproduced exactly, that is a manual step in Word, or
  a `docx`-skill build from the template; say which was done. If no template
  exists, build with the `docx` skill using the default section numbering.
- **Markdown-only deliverable:** the source is already clean (no DOCX markup).
  Delete the empty "Table of Contents" heading or replace it with links to the
  body sections; run `check_open_items.py` and `scan_artifacts.py` on the `.md`;
  stop there.
- **Automated vs manual, kept distinct in the report.** Automated:
  `check_open_items.py`, the pandoc build, `scan_artifacts.py`. Manual, by a
  person in Word: update all fields and the TOC (F9), check the cover and
  headers visually, save, export PDF. The report lists the manual steps as not
  done until the user confirms them.
- Run a **final package scrub** that clears stale cached page numbers and
  template placeholders from every header and footer part, without removing the
  live footer (page field, official revision, document type, title).
- Run `scripts/scan_artifacts.py` on the final DOCX and, where available, on the
  PDF text. It must report zero stale artifacts, including unfilled
  `{PLACEHOLDER}` tokens. Extend its pattern list with the house placeholders
  using `--extra`.

## 12. Review gates

Run `templates/ds_review_checklist.md` before delivery. The minimum:

- official revision correct and unchanged; working history separate;
- every section in the contract present, or justified;
- every TBD has an Open Item; every OI has an owner and a gate;
- every value has an equation or a cited source;
- interface tables relevant to the block; per-row status where unconfirmed;
- risk register present with severities;
- future-spin items separate from current-build items;
- no EVR-style measured results;
- `check_open_items.py` clean; package and PDF scans clean.

## 13. Files in this skill

- `SKILL.md` — this contract.
- `references/section_structure.md` — default section order, block-type extras, and
  the reference section order from one organisation's DS.
- `references/calculation_checklists.md` — worked-calculation checklists per module.
- `examples/calculation_examples.md` — three calculations written in the required
  shape (equation, inputs with source, result, status); imitate these.
- `templates/ds_skeleton.md` — Markdown skeleton for a new DS.
- `templates/ds_authoring_prompt.md` — placeholder-driven prompt for handing the job to an agent.
- `templates/ds_review_checklist.md` — review gates.
- `templates/open_items_table.md` — open-items register format.
- `templates/risk_register_table.md` — risk register format.
- `templates/source_priority_rules.md` — source ranking and conflict handling.
- `assets/dominion_dynamics_logo.jpg` — default cover logo; `build_docx.py` resolves it automatically.
- `scripts/check_open_items.py` — TBD-to-Open-Item and register consistency check on the Markdown.
- `scripts/build_docx.py` — Markdown to DOCX via pandoc and a house reference template, then scan.
- `scripts/scan_artifacts.py` — stale-artifact and unfilled-placeholder scan for DOCX (XML-aware, field-aware), PDF text and Markdown.
- `scripts/tests/run_tests.py` — regression tests for the three scripts; run after any script change.
- `examples/sparse_input_example.md` — the intended output when most inputs are missing (from a blind run; numbers verified).
- `examples/lessons_learned.md` — generalised lessons from real DS passes.
