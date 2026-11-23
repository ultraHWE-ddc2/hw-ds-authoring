# Calculation Checklists

Each item must appear in the DS as a worked calculation: the equation, the input
numbers with their source, the result, and a status (Confirmed / Candidate /
Starting value / Open Item). Mark every item Applicable or Not applicable with a
one-line reason. Never present a component value without its derivation.

## A. Universal core (every DS)

- [ ] **Requirement traceability** — each requirement mapped to the sub-section that meets it.
- [ ] **Derating** — actual vs rated voltage, current, power and temperature for every critical part, with the margin rule stated.
- [ ] **Tolerance stack** — for each accuracy budget: nominal, component tolerances, temperature drift, and the worst-case total vs the budget.
- [ ] **Thermal estimate** — junction or hot-spot temperature = ambient (worst case) + P_loss x R_th, for each dissipating part.
- [ ] **Budget roll-up** — power, signal or timing budget with each stage listed and the total against the limit.
- [ ] **Sensitivity** — which inputs move the answer most, and by how much. Rank them only when their uncertainty ranges are known; otherwise name them as screening drivers, not a ranking.
- [ ] **Assumption register** — every assumed value that is not from a source, listed with its Open Item.

## B. Power module

Every power equation below is tagged with the topology and operating mode it
holds for. **State both in the DS before using it.** The ripple, RMS and stress
equations differ by topology; applying the buck form to a boost or flyback gives
wrong component stresses. Where the converter, mode (CCM / DCM / BCM /
resonant) or control scheme is not listed here, take the equations from the
controller datasheet or an authoritative design reference (vendor application
note, a textbook such as Erickson & Maksimović), cite them, and state the
assumptions you inherit. Do not apply a generic form.

Common assumptions unless stated otherwise: steady state, ideal switches for the
duty-cycle relations, inductor current ripple ΔI_L defined peak-to-peak, f_sw
the switching frequency, D the duty cycle of the main switch, η the assumed
efficiency where it enters D.

### Regulation and reference (topology-independent)
- [ ] **Feedback divider** — V_out = V_ref × (1 + R_top / R_bottom). Show the ratio and the output at the tolerance corners. Include FB-pin bias current × R_top as an **absolute** V_out error (divide by V_out, not V_ref, to express it in %).
- [ ] **Trim / DAC mapping** — code to output voltage; quantisation vs the requested set; default state when unprogrammed.
- [ ] **Line and load regulation** — stated and bounded from the datasheet or the loop gain.

### Duty cycle and inductor ripple, by topology (CCM unless noted)

Turns ratio convention for every transformer topology below: **n = N_s / N_p**
(secondary over primary), so reflected primary quantities are V_out / n and
reflected secondary quantities are n × V_in. State n explicitly in the DS; many
datasheets use the inverse.

| Topology | D (CCM, ideal) and waveform convention | ΔI_L peak-to-peak (CCM) | Notes and source |
|---|---|---|---|
| Buck | D = V_out / V_in; D = switch on-time / T_sw | ΔI_L = (V_in − V_out) × D / (L × f_sw) | Worst-case ripple at V_in,max. Erickson & Maksimović, *Fundamentals of Power Electronics*, 3rd ed. (2020), ch. 2 (steady-state analysis; buck) — section-level support unverified, see note below |
| Boost | D = 1 − V_in / V_out; D = switch on-time / T_sw | ΔI_L = V_in × D / (L × f_sw) | Inductor carries input current: I_L,avg = I_out / (1 − D). Worst-case ripple at D = 0.5. Erickson & Maksimović 3rd ed., ch. 2 (boost) — unverified at section level |
| Inverting buck-boost | D = abs(V_out) / (V_in + abs(V_out)); D = switch on-time / T_sw | ΔI_L = V_in × D / (L × f_sw) | I_L,avg = I_out / (1 − D); switch and diode see V_in + abs(V_out). Erickson & Maksimović 3rd ed., ch. 2 (buck-boost) — unverified at section level |
| Four-switch buck-boost | Buck region: D = V_out / V_in; boost region: D = 1 − V_in / V_out; the transition region is controller-specific | Use the region's equation; take transition-region behaviour from the controller datasheet | Ripple and RMS peak near V_in ≈ V_out; confirm the controller's mode scheme and cite it |
| Flyback (CCM) | D = V_out / (V_out + n × V_in); D = primary switch on-time / T_sw | ΔI_mag (primary) = V_in × D / (L_m × f_sw) | Magnetising current, not an output inductor; DCM is common at light load — check both. Primary switch sees V_in + (V_out + V_f) / n + leakage spike. Erickson & Maksimović 3rd ed., §6.3.4 (flyback) |
| Forward (single-switch) | D = V_out / (n × V_in); D = switch on-time / T_sw, limited by core reset (≤ 0.5 with a 1:1 reset winding) | Output inductor: ΔI_L = (n × V_in − V_out) × D / (L × f_sw) | Erickson & Maksimović 3rd ed., §6.3.2 (forward) |
| Half-bridge / full-bridge, symmetric PWM | Each switch (half-bridge) or each diagonal pair (full-bridge) conducts for D_sw × T_sw per half-cycle, D_sw ≤ 0.5 less dead time. The secondary sees a rectified waveform at 2 × f_sw with effective duty D_eff = 2 × D_sw. V_out = D_eff × n × V_pri, where V_pri = V_in (full-bridge) or V_in / 2 (half-bridge). Quote D_sw and D_eff separately; they are not interchangeable | Output inductor: ΔI_L = (n × V_pri − V_out) × D_eff / (2 × f_sw × L), i.e. computed over the on-time D_sw × T_sw | Volt-second balance and dead time apply. Phase-shifted full bridge: D_eff is further reduced by duty-cycle loss from leakage inductance — take D_eff from the controller datasheet or TI SLUP414 §2 (phase-shifted full-bridge duty-cycle loss) and state it. Symmetric-PWM relations: Erickson & Maksimović 3rd ed., §6.3.1. **Convention note:** Erickson defines the switching period as one half-cycle of the transformer, so his D equals D_eff here, his T_s = T_sw / 2 and his f_s = 2 f_sw; translate before quoting |
| LLC (resonant, FHA) | Gain set by f_sw relative to f_r; no PWM duty cycle — do not quote a D | No output inductor; resonant tank currents from first-harmonic approximation | Tank design (L_r, L_m, C_r, Q, m) from the controller / transformer design reference; FHA is an approximation — state it. TI SLUP263 §II and its design procedure (LLC, FHA) |

Citation note: the chapter-2 references above were not verified at section level; treat them as pointers, and cite the exact section in the DS once checked.

Mode check (inductor-based topologies): the inductor current reaches zero when ΔI_L / 2 > I_L,avg. What happens then depends on the controller: a diode or diode-emulation rectifier enters DCM (pulse skipping or burst may follow); a synchronous stage in forced-PWM mode stays in CCM with negative current instead. State which, from the controller datasheet — it is not universal.
State the load at which that happens and whether the controller changes
behaviour (pulse skipping, burst) there.

### Device stresses, by topology

- [ ] **Switch voltage stress** — buck: V_in,max; boost: V_out,max; inverting buck-boost: V_in,max + abs(V_out); flyback: V_in,max + (V_out + V_f) / n + leakage spike (n = N_s/N_p); forward: 2 V_in,max (1:1 reset); bridges: V_in,max. Add switch-node ringing / overshoot, then compare with the device rating under the stated derating rule.
- [ ] **Diode / synchronous rectifier stress** — reverse voltage per topology (buck: V_in; boost: V_out; flyback secondary: V_out + n × V_in with n = N_s/N_p; forward and bridge secondaries: n × V_pri), average and RMS current.
- [ ] **Switch RMS current** — buck: I_rms ≈ I_out × sqrt(D) (ripple neglected) or sqrt(D) × sqrt(I_out² + ΔI_L²/12); boost / inverting: I_L,avg × sqrt(D) with I_L,avg = I_out/(1−D); flyback: from the primary current waveform (triangular in DCM, trapezoidal in CCM).
- [ ] **Conduction loss** — P_cond = I_rms² × R_DS(on) at the hot R_DS(on) (datasheet maximum at the junction temperature assumed).
- [ ] **Switching loss** — P_sw ≈ 0.5 × V_sw × I_sw × (t_r + t_f) × f_sw for hard switching, with V_sw and I_sw at the switching instant for the topology; plus C_oss loss. Note ZVS/ZCS where the topology provides it (LLC, bridges with adequate dead time) and the conditions under which it is lost.
- [ ] **Gate-drive loss** — P_gate = Q_g × V_drive × f_sw per device.
- [ ] **Current sense and current limit** — effective sense resistance (topology stated: which current is sensed — switch, inductor, or input), limit current = V_limit / R_sense, vs the required peak for this topology (peak = I_L,avg + ΔI_L/2, with I_L,avg per the table). Topology unknowns become Open Items.
- [ ] **Inductor / transformer** — peak current vs saturation across temperature; RMS vs the winding rating; for flyback, the energy balance ½ L_m I_pk² f_sw ≥ P_out / η in DCM, and the turns ratio vs the reflected voltage.

### Capacitors and ripple, by topology

- [ ] **Input capacitor RMS current** — buck: I_out × sqrt(D (1 − D)) (max I_out/2 at D = 0.5); boost: ΔI_L / sqrt(12) (continuous input current); flyback / inverting buck-boost: pulsating input — I_in,rms from the switch current waveform; bridges: per leg.
- [ ] **Output capacitor RMS current and ripple** — buck: I_C,rms = ΔI_L / sqrt(12), ΔV ≈ ΔI_L / (8 f_sw C) + ESR × ΔI_L; boost / inverting buck-boost / flyback: pulsating output current, I_C,rms = I_out × sqrt(D / (1 − D)), ΔV ≈ I_out × D / (f_sw C) + ESR × I_pk; LLC: from the rectified sinusoidal current.
- [ ] **DC-bias derating** — use the ceramic capacitor's capacitance-vs-bias curve at the operating voltage before computing ripple.

### Transient, protection and start-up (topology-independent form, inputs per topology)
- [ ] **Load-step transient** — charge to move Q = C × ΔV; current slew available (buck: limited by (V_in − V_out)/L on up-step, V_out/L on down-step; boost / buck-boost: right-half-plane zero limits bandwidth — state f_RHPZ = (1 − D)² R_load / (2π L) for boost and the bandwidth you may use). State which mechanism dominates.
- [ ] **UVLO** — thresholds from the divider: V_on = V_ref × (1 + R_top/R_bottom) + hysteresis term.
- [ ] **Soft-start** — t_ss = C_ss × V_ref / I_ss; in-rush into the output capacitance vs the current limit.
- [ ] **Snubber dissipation** — RC snubber: P ≈ C_snub × V_ring² × f_sw (charging and discharging once each per cycle; use ½ C V² f_sw if only one edge is damped); RCD clamp (flyback): P_clamp ≈ ½ L_lk I_pk² f_sw × V_clamp / (V_clamp − V_reflected), where V_reflected = (V_out + V_f) / n with n = N_s/N_p, **V_clamp is the voltage across the clamp capacitor measured above the input rail** (not drain-to-ground), L_lk is the primary-referred leakage inductance, and the expression holds for V_clamp > V_reflected with negligible clamp ripple (TI SLVAF95, RCD clamp design). State the ringing or leakage assumption.
- [ ] **Efficiency roll-up** — sum of the losses above at the worst-case corner vs the assumed η; iterate D and I_L,avg if η differs materially.

## C. Analog / mixed-signal module

- [ ] **Gain and bandwidth** — closed-loop gain from the feedback network; GBW vs the required bandwidth with margin.
- [ ] **Noise budget** — input-referred noise: sqrt(sum of squares) of resistor thermal noise (sqrt(4kTR)), amplifier voltage and current noise over the bandwidth.
- [ ] **Input and output range** — common-mode and output swing vs the rails with headroom.
- [ ] **Offset and drift** — input offset, bias current x source resistance, drift over temperature; total vs the accuracy budget.
- [ ] **Stability** — phase margin from the loop (state the loop-gain assumption); capacitive-load effect on the output stage.
- [ ] **Converter resolution** — LSB = V_ref / 2^N; INL/DNL against the requirement; reference accuracy.

## D. Digital / FPGA / processor module

- [ ] **Power sequencing** — rail order, ramp limits, thresholds and the power-good chain; cross-check against the device's sequencing requirement.
- [ ] **Decoupling** — bulk and high-frequency capacitance per rail vs the device recommendation; placement stated.
- [ ] **Impedance and return path** — target impedance vs frequency for each rail; reference-plane continuity under high-speed signals.
- [ ] **Timing budget** — setup and hold: t_su and t_h margins including clock skew, jitter and propagation variation.
- [ ] **Signal integrity** — termination value, edge rate, overshoot, and the length-match rule.
- [ ] **Reset and configuration** — reset duration vs rail settle; configuration source and boot-mode pins; default state of every strap.

## E. RF / clock module

- [ ] **Link or gain budget** — stage gains, noise figure and cascaded output power, with compression margin.
- [ ] **Matching** — L/C values for the target frequency; return loss and VSWR across band.
- [ ] **Phase-noise and jitter budget** — integrated jitter from the phase-noise profile; contributions summed in quadrature.
- [ ] **Spurs and harmonics** — expected levels vs the emission limit, with filter attenuation.
- [ ] **Power handling** — RF power per component vs its rating at the worst-case VSWR.

## F. Interface, connector and EMC module

- [ ] **Current per contact or pin** — I_contact vs the rated current with the temperature rise assumption.
- [ ] **Creepage and clearance** — against the working voltage and the pollution degree.
- [ ] **ESD and surge** — clamp voltage vs the device maximum; surge energy vs the protection rating.
- [ ] **Filter attenuation** — attenuation at the limit frequency vs the required margin.

## G. Mechanical / electrical assembly module

- [ ] **Conductor current capacity** — trace or busbar width and copper weight vs current, with the temperature-rise rule.
- [ ] **Contact and fastener resistance** — voltage drop and heating at the rated current.
- [ ] **Vibration and shock** — only where the requirement states them; the resonance and the stress margin.

## Reminders

- Where an input is unconfirmed, raise an Open Item. If bounds for it were *supplied*, show the result at each bound. If no bounds exist, show the nominal result and the sensitivity (symbolically, or with a value explicitly labelled **illustrative**); do not invent a tolerance to make a case.
- A calculation whose inputs are missing is still recorded: equation, the list of missing inputs, and status **Open Item (OI-nn)**. That is a complete entry, not a failure to comply.
- A reproduced calculation is not a Confirmed value. "Arithmetic checked" says the working is right; the status says whether the inputs are sourced and the result implementable.
- Where a value can only be finalised by measurement, mark it **Starting value** and point to the EVS.
- Keep the arithmetic reproducible: state units on every line, and keep intermediate values to at least three significant figures.
