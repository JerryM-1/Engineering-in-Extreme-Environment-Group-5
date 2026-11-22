# Stage 2 – Cantilever verification (liquid-filled pipe bending)

**Question (brief):** does the FEM reproduce liquid-filled pipe bending?
4, 10 and 20 m cantilevers, first six bending frequencies vs Euler–Bernoulli theory, plus a mesh sensitivity check.

## What we did

- **Model type:** **1D beam (pipe) elements on the pipe centreline, not shells or solids.** Two independent codes were used:
  - **ANSYS Mechanical APDL 2023 R1 (James, Steve):** PIPE289, a Timoshenko pipe element that includes shear and rotary inertia, with a scripted sweep (`ansys/`).
  - **Abaqus (teammate):** B23, an Euler–Bernoulli beam element. It matches EB theory to within 0.01 % for all 18 frequencies and reproduces the analytical mode shapes. This verifies the FE set-up itself.
  - **Python (`python_check/`):** an independent Timoshenko beam FE, used to explain where ANSYS and EB differ.
- **The LNG is distributed mass, not a distributed load.** It is carried as mass per metre (225.3 kg/m of LNG plus 192.4 kg/m of steel, giving 417.7 kg/m) that moves rigidly with the pipe in bending.
  - ANSYS applies it through an effective density.
  - Abaqus applies it as non-structural mass per unit length.
- **No loads were applied.** A modal analysis has no applied loads, so gravity, the weight of the fluid and internal pressure are not included. They would affect static sag and support loads, not the natural frequencies, and were not part of this stage.
- **Cases:** 4, 10 and 20 m clamped–free cantilevers, run empty and LNG-filled, with 5, 10, 20, 40 and 80 elements each. The first six in-plane bending modes were extracted.
- **Figures:**

  | File | What it shows |
  |---|---|
  | `figures/stage2_fem_vs_theory.png` | FEM / EB ratio for each mode |
  | `figures/stage2_EB_slenderness.png` | Difference from EB against the bending half-wavelength / D |
  | `figures/stage2_mesh_convergence.png` | Mesh convergence |
  | `figures/stage2_mode_shapes_20m.png` | ANSYS mode shapes for the 20 m case |

### Why a cantilever?

The brief specifies it as a verification case, because it has an exact analytical answer. It is not a model of the real line. In-plane, the loop legs behave somewhat like cantilevers off the guided straight, because the sliding supports do not restrain lateral movement.

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
