# Lessons Learned from DS Passes (generalised)

These lessons were drawn from real power-subsystem DS work. They are kept
generic: no part numbers, values or project identifiers. Use them to recognise
patterns, not to copy values.

## 1. Re-check derating against the final operating point
A switching device selected early did not meet its voltage-derating target once
the top of the output range and switch-node ringing were included. A higher-
voltage, footprint-compatible alternative was proposed.

**Lesson:** recompute voltage derating against the final top of range **including
ringing**, and state the margin rule. Describe the timeline neutrally ("selected
before the operating point and ringing were reconciled") rather than assigning
blame.

## 2. Label older load models as bounding, not final
Headline per-branch power and load slew-rate figures came from older material and
were not signed off.

**Lesson:** label pending or older requirements as bounding, analysis-case, or
pending sign-off. Raise an Open Item for the final load model.

## 3. Separate required transitions from stress cases
The commanded transitions that must be supported were narrower than the full-span
stress cases quoted elsewhere.

**Lesson:** separate confirmed required cases from stress or feasibility cases.
Size the design to the confirmed case; say that the full-span case is bounding.

## 4. Split must-fix items by test phase
Full-range parts and the final trim network were listed as "must fix before first
power-up". That would have blocked a safe reduced-voltage bring-up.

**Lesson:** split must-fix items by phase: a reduced-scope phase 1 (existing
lower-rated parts, trim depopulated, no load) and a full-scope phase 2 (final parts,
full trim, closed sense and load model). Phase 2 gates must not block phase 1.

## 5. Back-annotation is a release gate
The schematic properties, BOM and DS disagreed. The BOM had been corrected while the
schematic still carried early placeholders.

**Lesson:** prefer the verified BOM or latest design reference; treat schematic
back-annotation as a release gate; open an Open Item for any value that cannot be
verified (for example a sense topology or a third-party symbol).

## 6. Audit interface tables against the datasheet
Pin numbers and names were verified against the controller datasheet. A bootstrap
pin name was corrected, and sense and trim rows were given per-row status. This
caught a stale symbol polarity and a transposed configuration pin before freeze.

**Lesson:** audit every interface row against the datasheet, add a status column,
and keep visible TBD or verify flags for anything that still depends on a released
netlist or library symbol.

## 7. Keep the official revision apart from AI working history
The official revision had to stay fixed while several AI-assisted passes ran.

**Lesson:** keep a separate Draft Working History placed before the table of
contents, with the disclaimer. Never merge it into the official Revisions table.
Never future-date it. Never bump the official revision because a pass ran.

## 8. Clean the package, not just the text
Template footer and header artifacts and cached page numbers survived into the
generated file. Word re-cached the page fields on save.

**Lesson:** after updating fields, run a final package scrub that clears stale cached
page numbers and placeholders from every header and footer part, keeps the live
footer, and then runs the package scan and the PDF text scan. Both must be clean.
