# Worked Calculation Examples

Three calculations in the shape every DS calculation must take: **topology and
assumptions, equation, inputs with their source, working, result, status**, with
the margin or budget each is judged against. Values are illustrative, not from
any project. Imitate the form, not the numbers.

Conventions used in all three:

- Units on every line. Intermediate values to at least three significant figures.
- Every input names its source and the source's rank (SKILL.md Section 4).
- The worst case is stated explicitly (which corner, which temperature interval).
- The value status is one of Confirmed / Candidate / Starting value / Open Item /
  Superseded (SKILL.md Section 5), and the reason for anything other than
  Confirmed is given with the Open Item it depends on.
- Percent errors are expressed relative to the quantity they perturb (an output
  voltage error is divided by V_out, not by V_ref).

---

## Example 1 — Feedback divider and set-point tolerance (power, regulation)

**Topology / assumptions.** Any topology with a resistive divider to an FB pin
regulating to an internal reference; linear regulation, loop closed, no trim.
Resistor tolerances specified at 25 °C; drift evaluated over the board's local
ambient interval, not the device's full rated range.

**Purpose.** Set V_out = 3.30 V and check the resulting DC set-point error
against the ±1.0 % accuracy budget (REQ-04).

**Equations.**

    V_out = V_ref × (1 + R_top / R_bottom)                         (ideal divider)
    R_top = R_bottom × (V_out / V_ref − 1)
    ΔV_out(bias) = I_FB × R_top                                      (bias current into FB pin raises V_out by this absolute amount)
    Sensitivity of V_out to the ratio:  S = ∂V_out/V_out ÷ ∂(R_top/R_bottom)/(R_top/R_bottom)
                                       = (R_top/R_bottom) / (1 + R_top/R_bottom) = 1 − V_ref/V_out

**Inputs.**

| Symbol | Value | Source (rank) |
|---|---|---|
| V_out target | 3.300 V | REQ-04, project requirements (1) |
| Accuracy budget | ±1.0 % of V_out | REQ-04 (1) |
| V_ref | 0.800 V ± 1.0 % over −40 to +125 °C | Controller datasheet §7.5 (4) |
| I_FB (FB pin bias current) | ≤ 50 nA | Controller datasheet §7.5 (4) |
| R_bottom | 10.0 kΩ, ±0.1 %, 25 ppm/°C | Chosen, E96, BOM line 17 (3) |
| Local ambient | 0 to +70 °C | REQ-11 (1) |
| Temperature interval for drift | +25 °C (tolerance reference) to +70 °C = 45 °C | Derived from REQ-11 and the resistor datasheet's 25 °C reference |

**Working.**

    R_top (ideal)  = 10.0 kΩ × (3.300 / 0.800 − 1) = 10.0 kΩ × 3.125 = 31.25 kΩ
    Nearest E96    = 31.6 kΩ  → V_out = 0.800 × (1 + 3.16)  = 3.328 V  (+0.85 %)
    Next lower E96 = 30.9 kΩ  → V_out = 0.800 × (1 + 3.09)  = 3.272 V  (−0.85 %)
    Series pair    = 30.9 kΩ + 348 Ω = 31.248 kΩ → V_out = 0.800 × 4.1248 = 3.2998 V  (−0.005 %)

    Chosen: R_top = 30.9 kΩ + 348 Ω (two 0.1 % parts in series).

    Sensitivity    S = 1 − 0.800 / 3.300 = 0.7576
      (a 1 % change in the ratio moves V_out by 0.758 %)

    Ratio tolerance (worst case, R_top high and R_bottom low):
      ratio error  = 0.1 % + 0.1 % = 0.20 %     → V_out error = 0.7576 × 0.20 % = ±0.152 %

    Ratio drift over 45 °C, worst case with R_top and R_bottom drifting in opposite directions:
      ratio error  = 2 × 25 ppm/°C × 45 °C = 2250 ppm = 0.225 %
                                                  → V_out error = 0.7576 × 0.225 % = ±0.170 %
      (same-lot parts would track and partially cancel; the worst case is used)

    Bias current:  ΔV_out = 50 nA × 31.25 kΩ = 1.56 mV absolute on V_out
                   as a fraction of V_out: 1.56 mV / 3.300 V = 0.047 %
                   (dividing by V_ref would overstate this as 0.20 %)

    E96 quantisation of the series pair: −0.005 %

**Tolerance stack.**

| Contributor | Effect on V_out | Basis |
|---|---|---|
| V_ref, −40 to +125 °C | ±1.000 % | datasheet limit, applied in full |
| Resistor ratio tolerance, 2 × 0.1 % | ±0.152 % | 0.20 % × S |
| Resistor ratio drift, 45 °C, 2 × 25 ppm/°C | ±0.170 % | 0.225 % × S |
| FB bias current × R_top | ±0.047 % | 1.56 mV / 3.300 V |
| Series-pair quantisation | −0.005 % | fixed offset |
| **Linear worst case** | **±1.37 %** | sum |
| **Root-sum-square** | **±1.03 %** | sqrt(1.000² + 0.152² + 0.170² + 0.047²) |

**Result.** Nominal V_out = 3.2998 V. Set-point error is ±1.37 % linear worst
case, ±1.03 % RSS, against a ±1.0 % budget. **The budget is not met under
either method**, because the reference tolerance alone consumes it.

**Status: Open Item (OI-05).** The ±1.0 % reference figure is the datasheet
limit over −40 to +125 °C; the board operates 0 to +70 °C (REQ-11), but the
datasheet publishes no limit for a narrower interval. Resolution paths, in
order of preference: (a) obtain a 0–70 °C reference limit from the vendor;
(b) relax REQ-04 to ±2 % with Systems' agreement; (c) add a trim. Owner:
Hardware. Gate: schematic freeze. Risk register R-06.

---

## Example 2 — Switch voltage derating (power, power stage)

**Topology / assumptions.** Synchronous buck, CCM, low-side MOSFET. In a buck
the switch node swings between ground and V_in, so the drain-source stress on
the low-side device is V_in plus the switch-node overshoot. Overshoot is
expressed as a fraction k_ring of V_in. The derating rule is "V_peak ≤ 80 % of
the rated V_DS" (house policy).

**Equations.**

    V_peak  = V_in,max × (1 + k_ring)
    V_limit = V_DS,rated × 0.80
    Margin  = 1 − V_peak / V_limit

**Inputs.**

| Symbol | Value | Source (rank) |
|---|---|---|
| V_in,max (steady state) | 48.0 V | REQ-01 (1) |
| V_in transient, ≤ 100 ms | 60.0 V | REQ-02 (1) |
| k_ring | 0.20 | **Assumed.** No bench data for this layout; design reference §4.2 reports 15–25 % on a similar stage (2) |
| V_DS,rated | 100 V | MOSFET datasheet, Absolute Maximum Ratings (4) |
| Derating rule | 80 % of rated | House derating policy, design reference §2.1 (2) |

**Working.**

    V_limit = 100 V × 0.80 = 80.0 V

    Steady state:  V_peak = 48.0 V × 1.20 = 57.6 V     Margin = 1 − 57.6 / 80.0 = 28.0 %
    Transient:     V_peak = 60.0 V × 1.20 = 72.0 V     Margin = 1 − 72.0 / 80.0 = 10.0 %

    Sensitivity to k_ring during the 60 V transient:
      k_ring = 0.25 → V_peak = 75.0 V → margin = 6.25 %
      k_ring = 0.33 → V_peak = 79.8 V → margin ≈ 0 %

**Result.** 28 % margin at steady state and 10 % during the 60 V transient with
the assumed 20 % overshoot. Overshoot of about 33 % during the transient
consumes the whole derating allowance.

**Status: Candidate.** The device passes the 80 % rule in every stated case,
but the result rests on an assumed k_ring. k_ring is a **Starting value** to be
measured in EVS test T-07 (switch-node overshoot at the 60 V transient, cold,
before snubber tuning); the EVS is in draft, tracked as OI-07. If measured
overshoot exceeds 25 %, retune the snubber (§8.9) or substitute the 120 V
footprint-compatible part listed in Future-Spin §15.2. Risk register R-01.

---

## Example 3 — Sensor front end: resolution, range and noise (analog module)

**Topology / assumptions.** Bridge sensor → three-op-amp instrumentation
amplifier on a single 5.0 V supply → 12-bit SAR ADC with a 2.500 V reference.
The in-amp REF pin sets the output offset and must be driven from a
low-impedance source. Noise is evaluated white above the amplifier's 1/f corner;
the anti-alias filter is first order.

**Purpose.** Confirm that the chain resolves the 0–10 mV full-scale sensor
signal to 50 µV referred to input (REQ-07), that every node stays within its
valid range over the whole signal span, and that front-end noise does not
consume the resolution.

**Equations.**

    LSB (at ADC input)        = V_ref,ADC / 2^N
    LSB (referred to input)   = LSB / G
    G (in-amp)                = 1 + 49.4 kΩ / R_g
    V_out,inamp               = G × V_diff + V_REF
    e_n,total (RTI, per √Hz)  = sqrt( e_n,amp² + 2 × (i_n,amp × R_s)² + 4 k T × (2 R_s) )
                                (two independent source legs of R_s each: their noise powers add)
    BW_n (1st-order filter)   = 1.57 × f_c
    e_n,rms                   = e_n,total × sqrt(BW_n);   peak-to-peak ≈ 6.6 × e_n,rms

**Inputs.**

| Symbol | Value | Source (rank) |
|---|---|---|
| Required resolution (RTI) | 50 µV | REQ-07 (1) |
| Sensor differential output | 0 to +10.0 mV (unipolar) | Sensor datasheet (4) |
| Sensor output common-mode | 2.50 V (bridge at V_exc/2, V_exc = 5.0 V) | Sensor datasheet and schematic (3, 4) |
| R_s (per-leg source resistance) | 1.00 kΩ | Sensor datasheet (4) |
| In-amp supply | +5.0 V single | Schematic (3) |
| In-amp output swing | 0.10 V to 4.90 V | In-amp datasheet §7.2, typical (4) |
| In-amp input common-mode vs output | Per datasheet "diamond plot" / vendor tool | In-amp datasheet §8.1 (4) |
| e_n,amp | 10 nV/√Hz at 1 kHz, typical; no maximum published | In-amp datasheet §7.3 (4) |
| i_n,amp | 0.1 pA/√Hz, typical | In-amp datasheet §7.3 (4) |
| 1/f corner | ~10 Hz | In-amp datasheet §7.3 (4) |
| ADC V_ref, N | 2.500 V, 12 bits | ADC datasheet §6.2 (4) |
| ADC input range | 0 to V_ref | ADC datasheet (4) |
| f_c (anti-alias) | 1.00 kHz | Chosen from REQ-08 bandwidth (1) |
| T | 343 K (70 °C) | REQ-11 (1) |
| k | 1.38 × 10⁻²³ J/K | constant |

**Working — resolution.**

    LSB at ADC input = 2.500 V / 4096 = 610.4 µV

    G = 10 (R_g = 5.49 kΩ):  LSB RTI = 610.4 / 10 = 61.0 µV   → fails REQ-07 by 22 %
    G = 20 (R_g = 2.60 kΩ):  LSB RTI = 610.4 / 20 = 30.5 µV   → meets REQ-07 with 39 % margin

    Chosen: G = 20.

**Working — range, every node, both ends of the signal span.**

    Output swing floor is 0.10 V, so with V_REF = 0 V the zero-signal output
    (0 V) would be clipped. V_REF must sit above the floor with margin:

      V_REF = 0.250 V (buffered divider; buffer output impedance < 1 Ω at DC)

    In-amp output:   V_diff = 0 mV  → 0.250 V
                     V_diff = 10 mV → 20 × 0.010 + 0.250 = 0.450 V
                     both inside 0.10–4.90 V         → output headroom OK
    ADC input:       0.250–0.450 V inside 0–2.500 V  → OK (uses 8 % of range; 328 codes;
                     resolution is set by LSB RTI, not by range used, but INL
                     over this short span must be checked — see ADC datasheet)
    Firmware:        subtract the 0.250 V offset; the offset's own error
                     (divider + buffer) is calibrated out at zero signal.
    In-amp input common-mode: 2.50 V with the output at 0.25–0.45 V on a 5 V
                     single supply. For a three-op-amp in-amp the internal
                     first-stage outputs sit at V_cm ± G × V_diff / 2 and the
                     allowed (V_cm, V_out) region is bounded — the datasheet's
                     diamond plot. **At low output with mid-supply V_cm this
                     operating point is commonly outside the allowed region.**
                     It cannot be confirmed from the datasheet summary table.

**Working — noise (RTI).**

    Source thermal — two independent 1.00 kΩ legs, noise powers add → 2.00 kΩ equivalent:
      sqrt(4 × 1.38e-23 × 343 × 2000) = 6.15 nV/√Hz
    Current noise — i_n into each leg, uncorrelated: sqrt(2) × 0.1 pA/√Hz × 1.00 kΩ = 0.141 nV/√Hz
    Amplifier voltage noise:            10.0 nV/√Hz (typical)
    Total:  sqrt(10.0² + 0.141² + 6.15²) = 11.7 nV/√Hz

    BW_n = 1.57 × 1.00 kHz = 1.57 kHz
    e_n,rms = 11.7 nV/√Hz × sqrt(1570 Hz) = 0.465 µV RMS RTI
    peak-to-peak (6.6 σ) = 3.07 µV p-p  → 0.10 LSB at G = 20

    White-noise estimate only. The 1/f contribution is unquantified: no lower
    integration frequency / observation interval or 1/f model was supplied.
    Add it once the measurement interval is defined (or bound it in EVS T-12).

**Result.** With G = 20 the chain resolves 30.5 µV RTI (meets 50 µV). Output
and ADC ranges are satisfied over the full 0–10 mV span once V_REF = 0.250 V.
Front-end noise is about 0.1 LSB and is not a constraint **if the typical noise
figure holds**. The in-amp's input common-mode / output operating point is
unverified and is the item most likely to force a design change.

**Status: Candidate**, with two Open Items:

- **OI-09 (High).** In-amp operating point (V_cm = 2.50 V, V_out = 0.25–0.45 V,
  single 5 V) must be verified against the diamond plot or the vendor's
  operating-point tool. If outside the region: raise V_REF toward mid-supply
  and subtract in firmware, or change to an indirect-current-feedback in-amp
  that accepts this point. Owner: Hardware. Gate: schematic freeze.
- **OI-08 (Medium).** Only a typical noise figure is published. A margin
  factor cannot establish a guaranteed maximum. Either obtain a maximum from
  the vendor or add EVS test T-12 (noise floor at the ADC output, shorted
  input, 70 °C). Owner: Hardware. Gate: full-scope verification.

The gain change from R_g = 5.49 kΩ to 2.60 kΩ is recorded in the
reconciliation table (§12): the schematic still shows 5.49 kΩ — that row is
**Superseded** by this calculation and the BOM is updated.
