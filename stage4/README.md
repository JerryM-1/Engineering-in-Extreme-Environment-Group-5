# Stage 4 – Coupled response of the loop to water hammer

**Question (brief):** take the Stage 1 bend forces and apply them to the Stage 3 loop. Then:

- compare thermal movement, displacement, support forces and nominal stress;
- test at least two modifications;
- carry out mesh, hydraulic-resolution, damping and longer-run checks;
- apply the design codes and give recommendations.

**Status (26 Nov): complete.** Every result below has an input file in `scripts/` and a results folder in this directory.

---

## 1. Method

1. **Bend forces (Stage 1 to Stage 4).**
   - The MOC solver (400 reaches, c = 1100 m/s, friction 0) gives pressure head h(t) and flow Q(t) at the four bend stations, s = 34.90, 46.30, 53.70 and 65.10 m.
   - The force at each bend is F = (ρghA + ρQ²/A)(e₁ − e₂), which is about **700 kN per MPa**. It is applied as a point load at the bend midpoint, sampled every 1 ms.
   - Under uniform pressure, ΣF = 0 and ΣM = 0, so there is no net load on the anchors. The loop is rocked by the **time lag** between bends (Δs/c ≈ 7–10 ms).
   - Code: `python_forces/regen_bend_forces.py`. It reproduces Jerry's ANSYS force tables to < 1e-5 N.
2. **Structure (Stage 3 model).**
   - ELBOW290 elements throughout (8 Fourier terms for ovalisation), 0.25 m elements, 8 elements per bend.
   - Anchors at both ends; guides fixed in UY at 6 m and then every 12 m; in-plane only.
   - LNG mass included through ρ_eff = 17,364 kg/m³.
3. **ANSYS solution sequence.**
   - Static preload: cooldown to 111 K plus the initial bend forces (296.9 kN per component).
   - Modal analysis: 288 modes.
   - MSUP transient: 2 s at 1 ms steps, with Rayleigh damping set to 2 % at modes 2 and 3.
   - Expansion pass.
   - APDL post-processing loop over the 2,000 time steps.
4. **Why the response looks the way it does** (`figures/stage4_modal_forcing.png`).
   - The water hammer repeats at 4L/c = 0.364 s, i.e. **2.75 Hz**.
   - Mode 3 (antisymmetric rocking, 3.10 Hz) is the mode that gets driven: its modal force at 2.75 Hz is about 34× that of mode 2.
   - Mode 2 is symmetric, so the four bend forces almost cancel on it.
5. **Code check (ASME B31.3).**
   - At the bend elements, the in-plane stress intensification factor i = 0.9/h^(2/3) = **4.74** (h = tR/r² = 0.083) is applied to the beam bending moments.
   - Allowables (304 stainless, S_h = 138 MPa, to be checked against Table A-1):
     - water hammer (occasional): 1.33 S_h = **184 MPa**;
     - thermal (expansion): S_A = **207 MPa**.
   - Full working is in `stage4_code_check.md`.

## 2. Results

| Case | Peak displacement (from preload) | Peak nominal stress | Peak support force | Bend code check |
|---|---|---|---|---|
| Cooldown only, W = 8 m | 87.8 mm (loop)¹ | 19.6 MPa | 14.1 kN (anchor) | 90.9 MPa vs S_A 207: **pass, 44 %** |
| Cooldown only, W = 12 m | 82.7 mm | 18.6 MPa | – | 86.0 MPa vs S_A 207: **pass, 42 %** |
| Water hammer 0.02 s, W = 8 m² | 189.8 mm | 437.5 MPa | 954 kN | ≥ 228 % (nominal only): **fail** |
| Water hammer 0.10 s, W = 8 m² | 167.4 mm | 378.9 MPa | 800 kN | ≥ 196 % (nominal only): **fail** |
| **Water hammer 0.50 s, W = 8 m** | **48.2 mm** | **120.0 MPa** | **435.5 kN** | **≈ 176 MPa vs 184: pass at 96 %** |
| Water hammer 0.02 s, **W = 12 m** | 396.9 mm, still growing | 902.5 MPa | 1,202 kN | 1,064 MPa: **fail (resonance)** |

¹ The anchor-to-anchor span would contract freely by 199.8 mm. The loop absorbs this, so the anchors carry only 14 kN.

² The 0.02 s and 0.10 s figures come from Jerry's full 2 s runs. Their results folders aren't in the repo, but they're reproducible from `scripts/stage4_closure_0p02_v2.inp` and `..._0p10_v2.inp`. They also agree with the independent Python modal model (190.1 and 167.6 mm).

**Modification 1: closure time** (0.02 → 0.10 → 0.50 s).

- Displacement drops from 190 mm to 48 mm.
- Only the 0.50 s closure passes the code, with 4 % margin.

**Modification 2: loop width** (8 → 12 m).

- Thermal stress is about 5 % lower, because the wider loop is more flexible.
- But mode 3 drops from 3.10 to **2.77 Hz**, on top of the 2.75 Hz forcing. The response grows by about 100 mm every 0.5 s and is unbounded within the run.
- Reject.

## 3. Checks

| Check | Result |
|---|---|
| Mesh (0.50 s run, finer mesh, `mesh_check_0p50s`) | Peak displacement +0.25 % |
| Modal truncation (Python model, 3 / 6 / 12 modes) | 190.3 / 190.6 / 190.1 mm |
| Time step (half step) | 190.12 vs 190.12 mm |
| Longer run (Python, 2 / 5 / 10 s) | Peak unchanged: it occurs within the first 2 s |
| Damping (0.02 s closure, 0.5 / 2 / 5 %) | 226 / 191 / 151 mm |
| Damping (0.50 s closure, 0.5 / 2 / 5 %) | 57.3 / 49.2 / 37.7 mm |
| ANSYS vs Python (short run, `support_validation_0p10s`) | 32.36 vs 32.64 mm (0.8 %) |
| Hydraulic resolution (Stage 1, 100–400 cells) | No change in Joukowsky rise or period |
| Reproducibility (rebuilt inputs, `_v2` runs) | 0.50 s and W = 12 m runs match Jerry's to rounding at every step; thermal W = 8 m matches exactly |

## 4. Recommendations

1. **Valve closure time of at least 0.5 s.** This is the minimum. **Specify about 1 s** for margin against lower damping (+16 % at 0.5 %) and wave-speed uncertainty. As a reference, 2L/c = 0.18 s.
2. **Move the first guide to 3 m from the loop.** This is the most effective change: it lifts modes 2 and 3 to 4.6 and 5.1 Hz, well clear of the 2.5–2.75 Hz forcing band (`figures/stage4_frequency_map.png`). It needs a transient run to confirm the response before it is adopted.
3. **Keep mode 3 away from 2.75 Hz.** Don't make the loop wider (W = 12 m resonates at 2.77 Hz) or taller (H = 16 m puts mode 3 at 2.71 Hz). Any geometry change must be re-checked against the hydraulic period 4L/c.
4. **Thermal design is fine** at 44 % of S_A. The governing load is water hammer, not cooldown.

## 5. Limitations

- **Cavitation:** the MOC gives −0.05 MPa absolute at the valve, below LNG vapour pressure. Column separation, which could make the peaks higher, is not modelled.
- **One-way coupling:** no fluid–structure interaction at the bends. The bend velocity is about 3 m/s at 0.02 s, against a flow velocity of 1.5 m/s, so FSI could change the 0.02 s results.
- **Wave speed:** c = 1100 m/s ignores wall elasticity. With the wall included, c ≈ 998 m/s and the forcing is 2.5 Hz, which moves the resonance point.
- **Friction:** guides are taken as frictionless. Real PTFE friction would add damping but also axial loads.
- **Stress:** the stress is a beam-resultant stress with a code SIF, not a shell or local peak stress. Section 6 explains why that is the right tool here.
- **Local stress:** the ELBOW290 wall von Mises at the critical bend under cooldown peaks at 161 MPa, against 91 MPa from the code method. The B31.3 SIF is a fatigue-based factor (from Markl's tests) used with the code allowables; it is not a local peak-stress factor, so the two are not directly comparable. The local value is still below yield.
- **Data:** S_h comes from a generic 304 value. Splitting the occasional and thermal stresses assumes their in-plane moments add with the same sign at the critical element.

## 6. Why a 1D beam model and not shells

- **Scope:** the brief asks for **nominal** stress, global modes, support forces and displacements. All of these are beam quantities.
- **Ovalisation:** ELBOW290 models the bend's flexible cross-section directly. It is converged at 8 Fourier terms (Stage 3) and lands within 3.3 % of the B31.3 flexibility-factor frame model.
- **Codes:** B31.3 itself is beam-based (flexibility factor and SIF). Our code check therefore uses the code's own method.
- **Cost:** a 2 s transient with 288 modes takes about 1.5 h on beams. A shell model of a 100 m line would need millions of DOF per time step for no gain in the quantities asked for.
- **What shells would add:** the local stress distribution through the wall at the bends. That is a follow-on detail check, not needed for the global response.

## 7. Folders

**Final results**

| Folder | What it is |
|---|---|
| `closure_0p50s_msup_v2/` | 0.50 s closure (recommended design), rebuilt input with bend code-check output |
| `loop_width_12m_0p02s_v2/` | W = 12 m, 0.02 s closure, rebuilt input with bend code-check output |
| `thermal_v3_W8/`, `thermal_v3_W12/` | Cooldown only, with bend code-check stress |
| `stage4_code_check.md` | Code-check working |
| `figures/` | Slide figures: see section 8 |
| `figures/ansys_raw/` | ANSYS contour plots (GUI-rendered): thermal, 0.50 s and W = 12 m |

**Jerry's original runs, kept as evidence**

| Folder | What it is |
|---|---|
| `closure_0p50s_msup/` | Original 0.50 s run |
| `loop_width_12m_0p02s/` | Original W = 12 m run |
| `thermal/` | Original cooldown run |
| `mesh_check_0p50s/` | Mesh check |
| `support_validation_0p10s/` | Short 0.1 s ANSYS run used for the Python comparison |
| `short_validation_corrected/` | Earlier short run (constraint audit only) |

**Python**

| Folder | What it is |
|---|---|
| `python_inputs/`, `python_response/` | Jerry's independent modal-superposition model: 10 s runs, damping, truncation and time-step checks |
| `python_forces/` | MOC bend-force generator, modal forcing analysis, and the builder for the W = 12 m and thermal inputs |
| `python_check/stage4_code_check_figs.py` | Builds the two code-check figures from the result folders |
| `python_check/stage4_extra_figs.py` | Builds the frequency map, the bend-forcing figure and the animation (a 12-mode superposition that reproduces the ANSYS peaks, 190.1 and 48.3 mm) |

**Inputs:** `scripts/` holds every `.inp`. The `_v2` and `_v3` files are the reproducible final inputs; `stage4_thermal_W8_plots.inp` and `stage4_transient_plots.inp` make the contour plots.

## 8. Figures

The repo-level **`SLIDES_GUIDE.md`** has the full slide-by-slide plan for every stage, with captions and the numbers to quote. Stage 4 figures:

| File | What it shows |
|---|---|
| `figures/stage4_bend_forcing.png` | Pressure at the four bends; the 7–10 ms arrival lag; the net force on modes 2 and 3 |
| `figures/stage4_modal_forcing.png` | Frequency content of the modal forcing: mode 3 is driven at 2.75 Hz, mode 2 barely at all |
| `figures/stage4_frequency_map.png` | Loop modes vs W, H and first-guide distance, against the forcing band |
| `figures/stage4_bend_stress_history.png` | Bend code stress vs time: 0.50 s (under the limit) and W = 12 m (growing) |
| `figures/stage4_code_check_utilisation.png` | % of the B31.3 allowable for every case |
| `figures/loop_width_comparison.png` | Jerry's W = 8 vs 12 m displacement, stress and support-force histories |
| `python_response/response_comparison.png` | Python 3 s response for the three closures; damping sensitivity |
| `figures/stage4_loop_response.mp4` / `.gif` | Animation, 0.02 s vs 0.50 s closure (for the video) |
| `figures/ansys_raw/thermal_W8_bend_hotspot_vonmises.png` | ELBOW290 wall stress at the critical bend: the ovalisation hot-spot |
| `figures/ansys_raw/thermal_W8_displacement_3d.png`, `thermal_W8_vonmises_line.png` | Cooldown displacement and stress, 3D |
| `figures/ansys_raw/wh_0p50s_W8_*_t1p625.png` | 0.50 s closure at its peak: deformed shape (plan and 3D) and bending moment |
| `figures/ansys_raw/wh_0p02s_W12_*_t1p992.png` | W = 12 m at t = 1.99 s: deformed shape (plan and 3D) and bending moment |

## 9. How to reproduce

- **ANSYS:** run each `scripts/*_v2.inp` / `*_v3.inp` in its own empty **local** folder (Mechanical APDL 2024 R1, 4 cores).
  - Transients take about 1.5 h and need about 15 GB of disk; thermal runs take under 1 minute.
  - Copy the `stage4_*.csv` / `.txt` files into a results folder.
- **Force tables:** `python stage4/python_forces/regen_bend_forces.py` (check against Jerry's tables); `build_w12.py` regenerates the W = 12 m and thermal inputs.
- **Figures:** `python stage4/python_check/stage4_code_check_figs.py` and `python stage4/python_check/stage4_extra_figs.py`.
- **ANSYS contour plots:** `scripts/stage4_thermal_W8_plots.inp` (self-contained) and `scripts/stage4_transient_plots.inp` (reads a finished run's `.rst`). Run both in the MAPDL **GUI**, because batch-mode PNGs come out without colour.
