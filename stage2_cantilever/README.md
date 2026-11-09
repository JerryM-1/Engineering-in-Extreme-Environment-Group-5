# Stage 2 – Cantilever verification (liquid-filled pipe bending)

**Question (brief):** does the FEM reproduce liquid-filled pipe bending?
4, 10 and 20 m cantilevers, first six bending frequencies vs Euler–Bernoulli theory, plus a mesh sensitivity check.

## Contents

| Path | What it is |
|---|---|
| `ansys/stage2_cantilever.inp` | Full sweep in Mechanical APDL: 3 lengths × 5 meshes × empty/filled. Writes `stage2_results.csv` |
| `ansys/stage2_mode_shape_plots.inp` | Solves one case and saves mode-shape PNGs for the slides |
| `results/stage2_results_ansys.csv` | ANSYS output (run 9 Nov 2026, Mechanical APDL 2023 R1, UCL remote desktop) |
| `python_check/stage2_compare.py` | Independent Timoshenko beam FE, the comparison table and the figures |
| `results/stage2_timoshenko.csv`, `results/stage2_summary_table.csv` | Outputs of the Python check |
| `figures/` | Slide-ready plots |

## How to run

1. **ANSYS:** open Mechanical APDL 2023 R1, then *File → Change Directory* to this folder.
   - Run *File → Read Input from… → `ansys/stage2_cantilever.inp`*. It takes under a minute.
   - Copy the resulting `stage2_results.csv` to `results/stage2_results_ansys.csv`.
2. **Python:** run `cd python_check && python stage2_compare.py`. It needs numpy, scipy, pandas and matplotlib.

## Model assumptions

- **Element:** PIPE289, a 3-node Timoshenko element that includes shear deformation and rotary inertia. The section is OD 0.813 m with a 9.53 mm wall.
- **Material:** E = 213.233 GPa (NIST fit at 111 K). ν = 0.3 is assumed because the brief doesn't give it. Steel density is 8000 kg/m³.
- **LNG mass:** added through an effective density, ρ_eff = (m_steel + m_LNG)/A_steel = 17,364 kg/m³, with EI unchanged. The side effect is that rotary inertia is slightly overstated.
- **Constraints:**
  - bending is restricted to the XY plane;
  - axial movement (UX) and twisting (ROTX) are suppressed, so the six modes are pure in-plane bending modes and there are no duplicate pairs;
  - the root is fully clamped.

## Key results (LNG-filled)

- **Fluid mass:** f_filled / f_empty = 0.6788 for every case, which matches √(m_steel/m_total).
- **Mesh:** 20 elements gives mode 6 within 0.1 % of the 80-element result. Use elements of 0.5 m or smaller, and 0.25 m or smaller in the loop model.
- **ANSYS vs Timoshenko beam FE:**

  | Length | Modes | Agreement |
  |---|---|---|
  | 20 m | 1–6 | ≤ 0.5 % |
  | 10 m | 1–4 | ≤ 1.4 % |
  | 4 m | 1–2 | ≤ 1.2 % |

- **Euler–Bernoulli comparison:** EB overpredicts as L/D falls and mode number rises, because it ignores shear and rotary inertia. The gap is −0.3 % for 20 m mode 1 and −70 % for 4 m mode 6.
- **Beam validity limit:** for 4 m modes 3–6 and 10 m modes 5–6, the bending half-wavelength (≈ L/(n − 0.5)) is ≤ 3 diameters. In this range the two beam models disagree by 4–46 %, and shell (ovalling) behaviour would matter. These modes are outside 1D beam validity. The loop modes driven by water hammer (≈ 2.5–2.75 Hz plus harmonics) are well inside the range where the models agree.
