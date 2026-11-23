# DS Review Checklist (final gates)

Run before delivering any DS. Mark each item `[x]` when it passes. Anything that
does not pass needs a documented reason in the summary.

## Revision and front matter
- [ ] Official revisions table present and correct (revision, date or `Draft`/`TBD`, description, author).
- [ ] Official revision unchanged unless the user authorised the change.
- [ ] No future dates anywhere.
- [ ] Draft Working History is a separate table, placed before the table of contents, with the disclaimer.
- [ ] Cover title, subtitle and abstract are filled. No template placeholders.

## Structure
- [ ] Every section of the contract (or of the house template) present, in order.
- [ ] Any non-applicable section has a one-line justification.
- [ ] Every table and figure has a numbered caption.

## Interfaces
- [ ] External interface table lists only signals relevant to this block.
- [ ] Internal interface pins and names verified against the datasheet.
- [ ] Per-row status present where a value or symbol is unconfirmed.

## Requirements and content integrity
- [ ] Every requirement row has a source.
- [ ] Pending or older requirements are labelled as such, not stated as final.
- [ ] Simulation load models are described as models, not control modes.
- [ ] No measured results; background data clearly labelled.
- [ ] No company names, document numbers or template text that did not come from the sources or the user; Dominion Dynamics branding used only when the DS is a Dominion Dynamics document.
- [ ] Every missing source, missing EVS or missing tool is reported as a limitation with an Open Item or a manual action; nothing is cited that was not read, and no step is reported done that did not run.

## Calculations, derating, margins
- [ ] Every applicable item in the universal core and the block-type module has a worked calculation (equation, inputs with source, result, status).
- [ ] Every power equation states the topology and operating mode (CCM/DCM/resonant) it holds for; no buck-form equation applied to another topology.
- [ ] Percent errors are relative to the quantity they perturb (output error / V_out, not / V_ref).
- [ ] No value is called Confirmed on the strength of a typical-only datasheet figure or an arbitrary margin factor; such values are Candidate with an Open Item or an EVS test.
- [ ] Each not-applicable item has a one-line reason.
- [ ] Derating and margin analysis present, with the margin rule stated.
- [ ] Thermal estimate present for every dissipating part.
- [ ] Marginal areas identified and quantified.

## Risks, open items, reconciliation
- [ ] Risk register present, with severities assigned.
- [ ] Every TBD in the document has a matching Open Item.
- [ ] Every Open Item has an id (OI-nn), an owner and the gate it blocks.
- [ ] Schematic / BOM / reference mismatches captured, with an action per row.
- [ ] Future-spin recommendations separate from current-build actions.

## Source handling
- [ ] Source-priority order applied; each resolved conflict names the chosen source and why.
- [ ] Unresolved conflicts are Open Items, not guesses.

## Build and scans
- [ ] `scripts/check_open_items.py` run on the Markdown source: zero errors.
- [ ] If the user asked for Markdown only: stop here; the remaining build items are not applicable and are not reported as pending.
- [ ] Report separates automated steps (checks, pandoc build, scan) from manual steps (field/TOC update, visual check of cover and headers, PDF export); manual steps are listed as not done until the user confirms.
- [ ] Deliverable built with the house template as pandoc reference (styles, page setup, headers, footers inherited). The template's body — cover art, pre-built TOC — is **not** inherited; the cover comes from the Markdown and the TOC is a field. Say so in the report.
- [ ] Fields and table of contents updated.
- [ ] Live footer intact, if the house template has one.
- [ ] `scripts/scan_artifacts.py` run on the DOCX: zero findings.
- [ ] `scripts/scan_artifacts.py` run on the PDF text, if a PDF was produced: zero findings.

## Handover
- [ ] Reported: deliverable paths, change summary, open-items list, scan result, official-revision confirmation, manual actions.
