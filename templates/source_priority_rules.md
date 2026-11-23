# Source-Priority Rules and Conflict Handling

Use this ranking whenever two sources disagree, or when choosing the value that
goes into the DS.

## Priority order (highest authority first)

1. **Official project requirements** — what the block must meet.
2. **Latest design reference documents** from detailed review.
3. **Released schematic / netlist / BOM** — the current released design record.
4. **Datasheets** — device-level truth for pins, ratings and behaviour.
5. **Vendor tools and reference designs** — for example a vendor sizing tool.
6. **Legacy DS / EVR / EVS** — prior art, may be stale.
7. **Emails and meeting notes** — informal, easily outdated.
8. **Internet and general best practice** — lowest authority.

If the organisation's own template or policy ranks sources differently, that
policy governs. Say so in the source map.

## How to apply

- Build a **source map** first: list every source given, and its rank.
- For each contested value, quote it from each conflicting source with the rank
  and the location (document, section, page).
- Prefer the latest design reference or the released schematic/BOM when it is
  **clearly verified** (for example a BOM correction that the schematic
  properties confirm is stale).
- Datasheets win for pin numbers, names and absolute maximum ratings, even over a
  schematic symbol. If symbol and datasheet disagree, keep the datasheet value and
  open an Open Item to confirm the library symbol and land pattern.

## Conflict handling

- **Clearly resolvable, winning source verified:** use it, and record the choice and
  the reason in the reconciliation section or the row notes.
- **Unresolved or unverified:** do not guess. Open an Open Item with an owner and a
  gate. Where possible, show the result for each plausible case.
- **Never** silently pick one source. Silence hides the risk from reviewers.

## Typical conflict patterns

- Schematic properties still show early placeholders while the BOM is corrected:
  prefer the verified BOM; flag back-annotation as a release gate.
- A legacy DS or EVR value contradicts a newer design reference: prefer the newer
  reference; note the legacy value as superseded.
- A vendor-tool default contradicts a datasheet limit: the datasheet limit governs.
- A requirement appears only in old material and is pending sign-off: label it as
  older, bounding, or pending sign-off. Do not state it as final.
- Two documents give different pin names for the same device: the datasheet
  governs; the other is an Open Item until the library symbol is checked.
