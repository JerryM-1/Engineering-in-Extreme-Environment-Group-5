# Stage 3 – Expansion-loop in-plane modes

**Question (brief):** how do geometry and supports affect vibration? The task is to show the first six in-plane frequencies and mode shapes, vary the loop dimensions and guide restraints, and justify all restraints and the fluid mass.

## Contents

| Path | What it is |
|---|---|
| `ansys/stage3_loop_modal.inp` | Mechanical APDL script. It runs 14 cases and writes `stage3_results.csv`, then exports the baseline bend geometry and mode shapes for Stage 4 as CSVs and saves the mode-shape PNGs. |
| `python_check/stage3_loop_beam_check.py` | An independent 2D frame FE model of the same loop. It uses the ASME B31.3 bend flexibility factor (k ≈ 20) and writes `results/stage3_beam_check.csv`. |

## How to run

1. **ANSYS:** open Mechanical APDL 2023 R1 and point it at an empty folder with *File → Change Directory*. Then load the script with *File → Read Input from… → `stage3_loop_modal.inp`*. Copy the two CSVs and the PNGs into `results/` and `figures/`.
   - **Workbench alternative:** add a *Mechanical APDL* component system, right-click *Analysis → Add Input File*, pick the script, then click *Update*.
2. **Python:** run `python python_check/stage3_loop_beam_check.py`. It needs numpy and scipy.

## Geometry and supports (baseline)

- **Developed length:** 100 m, from the reservoir anchor to the valve anchor. This is the same as the Stage 1 benchmark, so the bend positions map directly onto the hydraulic stations.
- **Loop:** H = 12 m high and W = 8 m wide, with four 90° tangent bends of R = 1.4 m. The inlet and outlet legs are about 41 m each.
- **Anchors:** at both ends, with all DOF fixed.
- **Guides:** these fix lateral movement (UY) and let the pipe slide axially. The first guide on each side is 6 m from the bend, and the rest are spaced every 12 m towards the anchor.
- **In-plane only:** vertical movement is assumed to be restrained by the sleepers.
- **LNG mass:** added as an effective density (17,364 kg/m³), the same as in Stage 2.

## Case matrix

| Cases | Varies |
|---|---|
| 1 | Baseline |
| 2–3 | Loop height H = 8 and 16 m |
| 4–5 | Loop width W = 4 and 12 m |
| 6–8 | First-guide distance of 3 m, 12 m, and no guides |
| 9 | PIPE289 bends (no ovalisation), to isolate the bend-flexibility effect |
| 10–14 | Mesh checks: element size, elements per bend, and the number of ELBOW290 Fourier terms |

## Expected results (Python check, before ANSYS)

| Case | Modes 1–6 (Hz) |
|---|---|
| Baseline (k = 20) | 1.23, 2.46, 3.06, 11.4, 13.7, 14.3 |
| Stiff bends (k = 1) | 3.45, 3.55, 5.07, 14.0, 14.4, 15.6 |
| No guides | 0.34, 0.69, 1.68, 2.38, 2.53, 6.86 |

- **Bend flexibility matters a lot:** the first mode drops about threefold when ovalisation is included.
- **The baseline modes sit on the water-hammer frequency:** modes 2–3 (2.46 and 3.06 Hz) bracket the 2.75 Hz water-hammer fundamental from Stage 1. This is the key link to Stage 4.
- **Guides matter:** removing them puts five modes below 3 Hz.

ANSYS ELBOW290 should fall between the k = 1 and k = 20 results. It is expected to land closer to k = 20, because the straight tangent pipe partly resists the bend ovalising.

See `STAGE4_HANDOVER.md` for the geometry, supports and bend data passed to Stage 4.
