# Slides guide – which figure goes where (all stages)

This is for whoever is building the deck. For each stage it gives a suggested slide list, the figure to use (path from the repo root), a one-line message for the slide, and the numbers to quote.

All figures are PNG, at 200 dpi or above. The stage READMEs have the full method and the reasoning behind each result.

**General tips**

- **One message per slide.** Put the message as the slide title, e.g. "Mode 3 is the one the water hammer drives", not "Modal forcing".
- **ANSYS screenshots** (`*/ansys_raw/`) have a small legend. Crop the white margins and state the units in the slide text.
- **Units:** pressures are gauge unless the slide says otherwise. Displacements from the water-hammer runs are measured from the state just before closure (cooldown plus pressure).

---

## Stage 1 – Pressure waves (MOC)

| Slide | Figure | Message | Numbers |
|---|---|---|---|
| Method | None. Use the equations: Joukowsky Δp = ρcΔu, period 4L/c | 1D method of characteristics: reservoir at constant head, valve closing linearly | L = 100 m, c = 1100 m/s, ρ = 455 kg/m³, u = 1.5 m/s, Tc = 0.02 s, 400 reaches |
| Pressure waves | `stage1_figures/stage1_pressure_first_second.png` | The pressure front travels from the valve to the reservoir and reflects. Its arrival at each station matches L/c | Rise of 0.7508 MPa, which equals Joukowsky to 4 s.f. Arrival within one time step (0.46 ms) |
| Period / frequency | `stage1_figures/stage1_long_run_period.png` | The FFT peak sits on c/4L. The odd harmonics follow | Period 0.364 s → **2.75 Hz**, then 8.25 and 13.75 Hz |
| Limits | None | Below vapour pressure, the ideal model is no longer valid | The valve reaches −0.05 MPa absolute → column separation (cavitation), which is not modelled |

*Both Stage 1 PNGs were exported from `MECH0074_Stage1_LNG.ipynb`. Re-run the notebook if you need them restyled.*

---

## Stage 2 – Cantilever verification

| Slide | Figure | Message | Numbers |
|---|---|---|---|
| Set-up | None (sketch of the clamped–free pipe) | A 1D pipe model, with the LNG carried as distributed mass and no applied load | 4, 10 and 20 m; empty and filled; 5–80 elements; ρ_eff = 17,364 kg/m³ |
| Mode shapes | `stage2_cantilever/figures/stage2_mode_shapes_20m.png` (or the ANSYS screenshots `stage2_cantilever/figures/ansys_raw/L20_mode1-4.png`) | The FEM reproduces the classical cantilever shapes | 20 m mode 1 = 1.389 Hz (filled) |
| FEM vs theory | `stage2_cantilever/figures/stage2_fem_vs_theory.png` | The FEM matches theory. Differences grow only where Euler–Bernoulli itself stops being valid | Abaqus B23 vs EB: ≤ 0.01 %. ANSYS vs the Timoshenko beam model: ≤ 0.5 % (20 m) |
| Why EB drifts | `stage2_cantilever/figures/stage2_EB_slenderness.png` | Shear and rotary inertia matter once the half-wavelength is a few diameters long | −0.3 % (20 m, mode 1) to −70 % (4 m, mode 6) |
| Mesh | `stage2_cantilever/figures/stage2_mesh_convergence.png` | 20 elements is converged, which sets the 0.25 m element size for the loop | Mode 6 within 0.1 % of the 80-element result |
| Fluid effect | None (one line) | The LNG lowers every frequency by the same ratio | f_filled / f_empty = 0.679 = √(m_steel/m_total) |

**Note for slide 20 of the current deck:** don't call the 4 m mode-6 difference "unresolved". It's the beam validity limit (half-wavelength ≤ 3D), which is *why* the frequencies that drive the loop (2.5–14 Hz) sit in the range where the beam models agree.

---

## Stage 3 – Loop modes

| Slide | Figure | Message | Numbers |
|---|---|---|---|
| Model | `stage3_loop/figures/stage3_model_schematic.png` | Expansion loop with anchors and guides. Bends modelled with ELBOW290 so that ovalisation is included | H = 12 m, W = 8 m, R = 1.4 m, 100 m developed; guides at 6 m, then every 12 m |
| Mode shapes | `stage3_loop/figures/v5/stage3_ansys_modes_baseline.png` (or the 6 screenshots in `stage3_loop/figures/v5/ansys_raw/`) | The first three modes are global loop modes; modes 4–6 are the guided legs | **1.27, 2.48, 3.10**, 11.97, 13.67, 13.91 Hz |
| Bend flexibility | `stage3_loop/figures/v5/stage3_fourier_convergence.png` | Bend ovalisation lowers mode 1 by about 2.7×. It needs 8 Fourier terms to converge | 2 → 8 terms changes mode 1 by 30 %; 7 → 8 terms by 0.02 % |
| Verification | `stage3_loop/figures/v5/stage3_model_comparison.png` | ANSYS agrees with an independent Python frame model that uses the B31.3 flexibility factor | Within 3.3 % (flexible bends), 1.9 % (stiff bends) |
| Parametric | `stage3_loop/figures/v5/stage3_parametric.png`, or better **`stage4/figures/stage4_frequency_map.png`**, which adds the forcing band | Taller or wider loops get softer; guides control modes 2–3 | W 4/8/12 m → mode 3 at 4.72 / 3.10 / 2.77 Hz. First guide at 3 m → modes 2–3 at 4.60 / 5.13 Hz |
| Link to Stage 4 | `stage4/figures/stage4_frequency_map.png` | Modes 2 and 3 bracket the 2.75 Hz water hammer, so these are the modes to watch | Mode 2 at −10 %, mode 3 at +13 % of 2.75 Hz |

*Don't use `stage3_loop/figures/v4_2fourier/`. That run is superseded: its ovalisation was not converged.*

---

## Stage 4 – Coupled response

Suggested order: 9–10 slides plus the video clip.

| # | Slide | Figure | Message | Numbers |
|---|---|---|---|---|
| 1 | Method | `stage4/figures/stage4_bend_forcing.png` (left and middle panels) | The MOC pressure at each bend becomes a force F = (pA + ρQ²/A)(e₁ − e₂), applied to the Stage 3 model, followed by an MSUP transient | 700 kN per MPa; 288 modes; 1 ms steps; 2 s; 2 % Rayleigh damping at modes 2–3 |
| 2 | Why mode 3 | `stage4/figures/stage4_bend_forcing.png` (right panel) and `stage4/figures/stage4_modal_forcing.png` | Uniform pressure cancels (ΣF = ΣM = 0). The 7–10 ms lag between bends rocks the loop, so **mode 3 (3.10 Hz) is the mode that gets driven** | Mode 3's forcing at 2.75 Hz is about 34× mode 2's |
| 3 | Thermal | `stage4/figures/ansys_raw/thermal_W8_displacement_3d.png` | The loop absorbs the cooldown easily | 199.8 mm free contraction; loop moves 87.8 mm; 19.6 MPa nominal; anchors 14 kN |
| 4 | Closure time | Results table (`stage4/README.md` section 2) and `stage4/python_response/response_comparison.png` | A slower closure cuts the response by about 4× | 0.02 / 0.10 / 0.50 s → 190 / 167 / 48 mm; 437 / 379 / 120 MPa nominal |
| 5 | Deformed shape | `stage4/figures/ansys_raw/wh_0p50s_W8_displacement_3d_t1p625.png` and `wh_0p50s_W8_moment_t1p625.png` | At the peak (t = 1.63 s) the loop rocks, and the bending moment peaks in the guided legs beside the loop | 48 mm |
| 6 | Modification: loop width | `stage4/figures/loop_width_comparison.png` and `stage4/figures/ansys_raw/wh_0p02s_W12_displacement_3d_t1p992.png` | A wider loop is better thermally but **resonates**: mode 3 drops to 2.77 Hz | 397 mm and still growing at 2 s; 902 MPa nominal; 1,202 kN |
| 7 | Code check | `stage4/figures/stage4_code_check_utilisation.png` and `stage4/figures/stage4_bend_stress_history.png` | B31.3 with the bend factor i = 4.74. Thermal passes easily. **Only the 0.50 s closure passes the water-hammer check, with 4 % margin** | Thermal 91 vs 207 MPa (44 %); 0.50 s: 176 vs 184 MPa (96 %) |
| 8 | Why the bends | `stage4/figures/ansys_raw/thermal_W8_bend_hotspot_vonmises.png` | The bend cross-section ovalises, and the stress concentrates on the bend's side walls. This is what the code factor represents | Local von Mises 161 MPa vs 91 MPa from the code method. The SIF is fatigue-based, not a peak-stress factor |
| 9 | Checks | Table from `stage4/README.md` section 3 | Mesh, time step, modes, run length, damping, and an independent Python model all agree | Mesh +0.25 %; ANSYS vs Python 0.8 %; damping 0.5–5 % → 226–151 mm |
| 10 | Recommendations | `stage4/figures/stage4_frequency_map.png` | (1) Close in ≥ 0.5 s, specify about 1 s. (2) First guide at 3 m moves modes 2–3 above 4.5 Hz. (3) Don't make the loop wider or taller | W = 12 m → 2.77 Hz; H = 16 m → 2.71 Hz |
| 11 | Limitations | None | Cavitation, one-way coupling (no FSI), wave speed (998 vs 1100 m/s), frictionless guides, beam stress | See `stage4/README.md` section 5 |
| 12 | 1D vs shell | None (bullets from `stage4/README.md` section 6) | The brief asks for global quantities. ELBOW290 captures ovalisation, B31.3 is itself beam-based, and shells would add cost without adding answers | — |

---

## Video assets

| File | Use |
|---|---|
| `stage4/figures/stage4_loop_response.mp4` (`.gif` for PowerPoint) | 8 s clip: 0.02 s vs 0.50 s closure, deformation ×15, 4× slow motion, live peak counter. It reproduces the ANSYS peaks (190 / 48 mm) |
| ANSYS GUI animation (optional) | For the W = 12 m resonance: open the run in MAPDL and use PlotCtrls → Animate → Over Time (see `stage4/scripts/stage4_transient_plots.inp`) |

## Don't use

- `stage3_loop/figures/v4_2fourier/`: superseded (ovalisation not converged).
- `stage4/thermal/file000.png` and the `*_v3000.png` files in `stage4/thermal_v3_*/`: automatic line plots. Use `stage4/figures/ansys_raw/thermal_*` instead.
- Any figure that quotes 22 % for the fluid frequency drop: the correct figure is **32 %** (ratio 0.679).
