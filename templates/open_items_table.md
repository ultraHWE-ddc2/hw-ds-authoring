# Open Items Register (template)

Every unresolved question, unverified assumption, or unclosed source conflict
becomes an Open Item. Do not leave a TBD only in prose; mirror it here.

## Rules

- Id format `OI-01`, `OI-02`, ... Stable. Do not renumber closed items.
- Every Open Item has an **owner** (team or role) and the **gate it blocks**.
  When no assignment authority exists (sparse inputs, early draft), write the
  role followed by "(proposed)" — e.g. `Hardware (proposed)` — rather than
  leaving the cell empty or inventing a name. The checker accepts it; a reviewer
  sees it is unassigned.
- Reference the DS section(s) that analyse the item.
- When an item closes, record how and by which source. Keep the row for traceability.

## Gates (use these names consistently)

- Requirements freeze
- Schematic freeze
- Layout release
- BOM release
- First power-up / first bring-up
- Reduced-scope or phase-1 test
- Full-scope verification
- Final stress or reliability sign-off

## Table format

| Open Item | Question / unknown | Owner | Gate it blocks | DS section(s) | Status |
|---|---|---|---|---|---|
| OI-01 | {QUESTION_STATED_PRECISELY} | {TEAM_OR_ROLE} | {GATE} | {X.Y} | Open |

## Worked example (generic)

| Open Item | Question / unknown | Owner | Gate it blocks | DS section(s) | Status |
|---|---|---|---|---|---|
| OI-01 | Absolute maximum device rating, including transient overshoot, is not established | Systems | Transient testing at top of range | 9.x | Open |
| OI-02 | Effective sense resistance (parallel, series or split) is unconfirmed and sets the current limit | Hardware | First power-up; current-limit calculation | 8.x | Open |
| OI-03 | Whether two headline limits (for example maximum current and maximum power) apply at the same time | Systems | Final stress sign-off | 3.x | Open |

## Anti-patterns

- A TBD in a sentence with no matching Open Item.
- An Open Item with no owner or no gate.
- Silently choosing one source to "resolve" a conflict, with no row here.
- Gating a reduced-scope test on items that only the full-scope test needs.
