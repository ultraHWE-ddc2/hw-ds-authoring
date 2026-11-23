# Sparse-Input Example — what a correct DS looks like when most evidence is missing

This is the intended *successful* output of the skill when it is given only an
excerpt of requirements, a datasheet excerpt and a BOM excerpt, and no
schematic, no tolerances, no derating policy and no EVS. The right result is a
set of **conditional** calculations and an honest open-items register — not a
fully populated design assembled from assumed values.

It was produced in a blind run of the skill by a reviewer model; every number
below was recomputed independently afterwards and matched. Condensed here to
show the pattern. Imitate the *behaviour*, not the block.

## The input (everything that was supplied)

- **Block:** 12 V → 3.3 V synchronous buck, point-of-load, 4 A max, housekeeping rail.
- **Requirements (excerpt, rev 0.9, pending signoff):** V_in 10.8–13.2 V steady, 16 V for 10 ms; V_out 3.3 V ±2 %; I_out 0–4 A; load step 1→3 A at 1 A/µs; ripple ≤ 30 mV p-p; ambient 0–60 °C; η ≥ 90 % at 2 A.
- **Controller datasheet (excerpt):** V_ref 0.6 V ±1 %; f_sw 600 kHz fixed; integrated FETs 35/20 mΩ typ (high/low); peak current limit 6.5 A min; FB bias ≤ 100 nA; soft-start 1 ms fixed; input abs max 18 V.
- **BOM (excerpt):** L = 2.2 µH, I_sat 7 A, DCR 15 mΩ; C_out 2 × 22 µF 0805 X5R 10 V; C_in 10 µF 0805 X5R 25 V. No schematic.

## What the run did right

**Source labels without invented identifiers.** Sources were labelled R / D / B
(requirements excerpt, datasheet excerpt, BOM excerpt) with their stated
revision and approval state. No document numbers were made up.

**Requirements treated as provisional.** Rev 0.9 is pending signoff, so every
requirement-dependent result is **Candidate** pending OI-01, not Confirmed.

**Nominal calculations, bounds stated symbolically.** Buck, CCM, nominal L and
f_sw, typical R_DS(on):

    D = 3.3 / V_in;   ΔI_L = (V_in − 3.3) × D / (L × f_sw);   I_pk = 4 + ΔI_L / 2

| V_in | D | ΔI_L p-p | I_pk at 4 A | I_rms at 4 A | Status |
|---|---|---|---|---|---|
| 10.8 V | 0.306 | 1.736 A | 4.868 A | 4.031 A | Candidate |
| 12.0 V | 0.275 | 1.813 A | 4.906 A | 4.034 A | Candidate |
| 13.2 V | 0.250 | 1.875 A | 4.938 A | 4.036 A | Candidate |
| 16.0 V (transient; regulation at 16 V not established by D) | 0.206 | 1.984 A | 4.992 A | 4.041 A | Candidate |

At 16 V the nominal peak is 1.51 A below the *minimum* current limit and 2.01 A
below nominal I_sat. These are **not qualified margins**: L tolerance, bias and
temperature, f_sw tolerance and the saturation criterion were not supplied. The
minimum limit cannot prove the inductor is protected — the *maximum* limit and
fault overshoot are needed (OI-03).

**Conditional limits instead of assumed part data.** Output ripple at 16 V with
nominal 44 µF: 9.40 mV capacitive. Either C_eff ≥ 13.8 µF at zero ESR, or
ESR ≤ 10.4 mΩ at 44 µF — not independent allowances. **No X5R bias-loss
percentage was assumed**; exact part curves are OI-04.

**Rating comparisons, not derating claims.** 18 V abs max vs 16 V transient is
2 V (11 %) headroom; C_in at 64 % of rating; C_out at 34 %. Stated as
comparisons, because no derating policy was supplied (OI-07). Absolute maximum
was not treated as an allowed operating voltage.

**Power-stage slew distinguished from loop settling.** The 2 A step can be
supplied by the inductor in 0.59 µs at minimum input (3.41 A/µs slope); the
charge deficit if the loop does nothing for the 2 µs ramp is 2 µC → 45.5 mV
on 44 µF. The loop's actual delay, the allowed excursion and the settling
criterion were not supplied (OI-01, OI-06). **The ±2 % DC tolerance was not
silently adopted as the transient allowance.**

**Efficiency screened, not proven.** At 12 V / 2 A: conduction losses 0.103 W
(FETs, typical) + 0.064 W (DCR) = 0.167 W against a 0.733 W allowance for 90 %.
That leaves 0.566 W for everything not supplied — hot R_DS(on), switching,
dead-time, drive, core, ESR, PCB. Status Candidate; compliance is OI-08.

**Blocked calculations left blocked.** Thermal: equation written
(T_j ≈ 60 °C + θ × P), inputs listed as missing, status **Open Item OI-08**. No
junction temperature claimed. Snubber: need and dissipation not determinable
without schematic and ringing data (OI-07).

**Sensitivities as screening drivers, not a ranking.** C_eff, L and hot R_DS(on)
were shown with explicitly *illustrative* factors (44→22 µF, 2.2→1.1 µH, ×k),
labelled as not asserted tolerances, because no uncertainty ranges existed to
rank.

**Open items with proposed owners.** Nine OIs, each with a role marked
"(proposed)" because no assignment authority was supplied, and a gate named
from the standard list. OI-09 records that the EVS does not exist:
"verification pending; EVS not yet written".

## What the run was tempted to do, and did not

| Temptation | What the skill required instead |
|---|---|
| Assume 20–40 % X5R capacitance loss at bias | Use nominal, state the conditional limit, open OI-04 for the part curve |
| Apply an 80 % derating rule | Report rating comparisons; the policy is OI-07 |
| Double R_DS(on) for "hot" | Carry the typical value, flag the multiplier k as unknown |
| Assume a loop bandwidth to estimate transient response | Show the power-stage limit and charge deficit; loop response is OI-06 |
| Treat ±2 % DC as the transient allowance | Keep them separate; allowance is OI-01 |
| State "enters DCM below 0.9 A" as fact | Qualify: diode-emulation controllers enter DCM; forced-PWM ones carry negative current (mode is OI-02) |
| Invent an EVS test number | "Verification pending; EVS not yet written (OI-09)" |

## The register (condensed)

| ID | Missing evidence / question | Owner | Gate | Status |
|---|---|---|---|---|
| OI-01 | Signed requirements; whether ±2 % includes ripple; transient allowance; behaviour at 16 V | Systems (proposed) | Requirements freeze | Open |
| OI-02 | Schematic, full controller datasheet, control mode, min on/off time, protection | Hardware (proposed) | Schematic freeze | Open |
| OI-03 | Inductor L vs I/T, saturation criterion, max current limit and overshoot | Hardware (proposed) | BOM release | Open |
| OI-04 | Capacitor effective C, ESR/ESL, ripple-current rating | Hardware (proposed) | BOM release | Open |
| OI-05 | Feedback resistor values, tolerance, drift; full DC budget | Hardware (proposed) | Schematic freeze | Open |
| OI-06 | Loop stability and transient response with real L/C; start-up load and pre-bias | Hardware (proposed) | Schematic freeze | Open |
| OI-07 | Derating policy; ringing bounds; snubber need | Hardware (proposed) | Full-scope verification | Open |
| OI-08 | Hot and switching losses; thermal impedances; efficiency and thermal closure | Hardware (proposed) | Layout release | Open |
| OI-09 | EVS not supplied; verification pending | Verification (proposed) | Full-scope verification | Open |
