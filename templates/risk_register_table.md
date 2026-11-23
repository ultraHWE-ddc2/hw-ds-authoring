# Risk Register (template)

Record every way the design can fall short if a marginal item is realised and
not detected. Name marginal areas explicitly.

## Severity

- **High** — board or device damage, safety impact, or a missed hard requirement.
- **Medium** — significant rework or schedule loss.
- **Low** — nuisance, acceptable for the current build.

Assess severity as the consequence **if the risk is realised and not detected**.

## Table format

| ID | Risk | Severity | Where analysed | Mitigation | Build |
|---|---|---|---|---|---|
| R-01 | {WHAT_CAN_GO_WRONG} | High / Medium / Low | {DS_SECTIONS} | {WHAT_REDUCES_OR_DETECTS_IT; OI-nn that closes it} | Current / Future spin |

## Guidance

- Tie each risk to the DS section that quantifies it.
- If the mitigation depends on an unresolved question, cite the Open Item.
- Separate **current-build** mitigations (doable now, footprint-compatible) from
  **future-spin** mitigations (need a layout or architecture change). Future-spin
  items also appear in the future-spin section.

## Common risk themes by block type

- **Power:** device over-voltage from switch-node ringing; current limit below the
  required peak; settling or bandwidth margin; snubber over-dissipation; loop
  instability across modes; thermal limit; shared-rail fault coupling.
- **Analog:** offset and drift eating the accuracy budget; noise floor; stability
  with capacitive load; headroom at the rail extremes.
- **Digital:** sequencing violation; timing margin under skew and jitter; reset
  while rails are still settling; strap pins at the wrong default.
- **RF / clock:** matching sensitivity to tolerance; spur or phase-noise limits;
  power handling at high VSWR.
- **Interface:** contact current rating under temperature; ESD clamp margin;
  creepage at the working voltage.
- **Any:** stale placeholder values reaching a released schematic (treat
  back-annotation as a release gate).

## Worked example (generic)

| ID | Risk | Severity | Where analysed | Mitigation | Build |
|---|---|---|---|---|---|
| R-01 | Snubber resistors exceed package power rating if ringing approaches full swing | High | 8.x, 9.x | Measure ringing and resistor temperature early; tune within range (OI-04) | Current |
| R-02 | Current limit set below required peak because effective sense resistance is higher than assumed | High | 8.x | Close sense-topology Open Item (OI-02) before first power-up | Current |
| R-03 | Released schematic carries placeholder values because back-annotation was skipped | Low | 12.x | Make back-annotation a release gate | Current |
| R-04 | Ceramic capacitance at DC bias falls well below nominal, lifting output ripple | Medium | 8.x | Use DC-bias curve in the ripple calculation; larger case size next spin | Future spin |
