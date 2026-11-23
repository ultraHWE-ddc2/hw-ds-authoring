# DS Section Structure

Use the house template's order if one exists (see SKILL.md Section 2). Otherwise
use the default contract below. Keep the numbering stable once a document is
released; do not renumber closed sections between revisions.

## Default contract

**Front matter** (unnumbered, in this order)

- Cover / title page — title, subtitle, document number, official revision, status.
- Abstract — three to six sentences: what the block is, its envelope, its key risks.
- Revisions table — official revisions only (revision, date or `Draft`/`TBD`, description, author).
- Acknowledgments / legal front matter.
- Draft Working History — AI/tool passes only; carries the disclaimer in SKILL.md Section 5.
- Table of contents.

**Body** (numbered from 1; these numbers are the ones cited as "section x.y" in the
open-items and risk registers and used by `templates/ds_skeleton.md`)

1. Introduction and scope — purpose, what is in and out of scope, DS vs EVS vs EVR note.
2. System context and block diagram — where the block sits; one block diagram with every interface named.
3. Requirements and operating envelope — every requirement in a table with its source, status, and a notes column. Include input/output ranges, transients, environment, efficiency, accuracy, lifetime.
4. External interface table — connectors, cables, host-facing signals. Relevant rows only.
5. Internal interface table — control, sense, reference, and inter-block signals. Pin names verified against the datasheet; per-row status.
6. Design description — topology, operating modes, control scheme, protection features, with reasoning.
7. Component selection rationale — per critical part: why chosen, key ratings, derating, alternates, status.
8. Calculations — the worked calculations from `calculation_checklists.md`.
9. Derating and margin analysis — table of actual vs rated for voltage, current, power, temperature, with margin rule stated.
10. Start-up / shut-down or sequencing — ordered events, timing, thresholds, fault behaviour during each.
11. Power, signal or resource budget — consumption, tolerance, efficiency roll-up, timing budget as applicable.
12. Implementation, schematic and BOM reconciliation — mismatch table with one action per row.
13. Risks and marginal areas — risk register (`risk_register_table.md`).
14. Open items and review questions — open items register (`open_items_table.md`).
15. Future-spin recommendations — changes for the next build only; kept separate from current-build actions.
16. Appendix and acronyms.
17. Reference documents — every cited source with its number and revision.

## Block-type extras

Insert these where they fit the flow of the document. Each is required only when
the block type applies.

| Block type | Extra content |
|---|---|
| Power converter | Regulation and reference section (feedback, trim, accuracy); switching-device and magnetics section; protection (OCP, OVP, UVLO, thermal); soft-start and load-step behaviour |
| Analog / mixed-signal | Signal chain and gain table; noise and linearity budget; stability and compensation |
| Digital / FPGA / processor | Power-rail map and sequencing table; clock tree summary; configuration and reset; high-speed interface section |
| RF / clock | Link or gain budget; matching network; spur and phase-noise budget; shielding and grounding |
| Interface / I-O | Protection and ESD section; connector pinout; cable assumptions |
| Electromechanical | Mechanical constraints; thermal interface; fastener and contact data |

## Section content rules

- A requirement without a source is not a requirement; mark it `Open Item` instead.
- Do not paste a whole datasheet into the DS. Quote the value, the condition and the page.
- Diagrams need captions, numbered as Figure X-n. Tables need captions, numbered as Table X-n.
- Interface tables list only signals that exist on this block. Delete rows that belong to a neighbouring block, and say in one line what was removed and why if the removal matters to a reviewer.

## Reference: one organisation's DS order

The following order comes from a large OEM's power-subsystem DS template. It is
an example of a house profile, not a required order. Use it as the default only when the user
says their template follows it. Note that this profile numbers front matter and
body continuously (1–23); the default contract above does not.

1. Cover, 2. Abstract, 3. Revisions, 4. Acknowledgments, 5. Draft Working History,
6. Table of Contents, 7. Introduction and Scope, 8. System Context and Block Diagram,
9. Requirements and Operating Envelope, 10. External Interface, 11. Internal Interface,
12. Design Description, 13. Component Selection Rationale, 14. Calculations,
15. Derating and Margin Analysis, 16. Power-Up / Power-Down Sequence,
17. Power Requirements, Consumption and Tolerance, 18. Implementation / Schematic /
BOM Reconciliation, 19. Risks and Marginal Areas, 20. Open Items and Review
Questions, 21. Future-Spin Recommendations, 22. Appendix / Acronyms,
23. Reference Documents.
