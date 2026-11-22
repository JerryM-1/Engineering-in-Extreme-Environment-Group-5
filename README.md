# MECH0074 CW1 – LNG expansion loop under water hammer (Group 5)

This is the group's computational work for MECH0074 Engineering in Extreme Environments, CW1 (2026–27). The system is a 304 stainless steel LNG line (OD 0.813 m, wall 9.53 mm, 111 K, 0.7 MPa) with a four-bend expansion loop, loaded by a rapid valve closure.

Each stage folder has its own README covering what was done, how to run it, the assumptions and the key results.

| Stage | Folder / file | Question (brief) | Status |
|---|---|---|---|
| Part A | Part A write-up (shared document) | Why loops are needed; codes; anchors and guides | Draft revised 19 Nov |
| 1 – Pressure waves | `MECH0074_Stage1_LNG.ipynb` (supplied solver: `water_hammer_valve_closure_and_bend_forces2-3.ipynb`) | Does the MOC solver reproduce the benchmark? | Complete |
| 2 – Cantilever verification | `stage2_cantilever/` | Does the FEM reproduce liquid-filled pipe bending? | Complete |
| 3 – Loop modes | `stage3_loop/` | How do geometry and supports affect vibration? | Complete (v5, converged): modes 1–6 = 1.27, 2.48, 3.10, 11.97, 13.67, 13.91 Hz |
| 4 – Coupled response | *(Jerry, in progress)* | Bend forces → loop response, modifications, codes | Started; inputs in `stage3_loop/STAGE4_HANDOVER.md` |

## Stage 1 – Pressure waves (summary)

- **Method:** 1D method of characteristics (MOC), using the supplied teaching solver with the brief's LNG inputs. Run: L = 100 m, D = 0.794 m, c = 1100 m/s, ρ = 455 kg/m³, u = 1.5 m/s, linear valve closure in 0.02 s. The reservoir end is at constant head; the valve end has prescribed flow.
- **Results against theory:**

  | Check | MOC | Theory |
  |---|---|---|
  | First valve pressure rise | 0.7508 MPa | Joukowsky ρcΔu = 0.7508 MPa |
  | Wave arrival at 10, 25, 50 m | Within one time step (0.46 ms) | Theoretical arrival times |
  | Period | 0.3636 s (2.75 Hz) | 4L/c |
  | Resolution check (100–400 cells) | No change in pressure rise or period | – |

  The closure is rapid: Tc / (2L/c) = 0.11.
- **Limitation:** after reflection, the ideal model predicts −0.05 MPa absolute at the valve. A real LNG line would form vapour cavities (column separation), which this single-phase model cannot represent. The later oscillation is therefore an idealised benchmark.
- **Link to Stages 3–4:** the 2.75 Hz fundamental lands between loop modes 2 and 3, so the pressure histories at the bend stations (`stage3_loop/STAGE4_HANDOVER.md`) drive Stage 4.

## Common inputs and assumptions

- **Pipe:** OD 0.813 m, ID 0.79394 m, E = 213.233 GPa at 111 K. ν = 0.3 (assumed). ρ_steel = 8000 kg/m³, ρ_LNG = 455 kg/m³.
- **LNG mass:** 417.7 kg/m in total, moving rigidly with the pipe. FE models apply it as an effective density of 17,364 kg/m³ (ANSYS) or as non-structural mass (Abaqus).
- **Thermal contraction:** 1.4×10⁻⁵ K⁻¹ × 182 K ≈ 255 mm per 100 m.
- **Bend flexibility:** ASME B31.3 flexibility factor k = 1.65/h ≈ 20 for these bends. ANSYS models it directly with ELBOW290 elements.

## Running the code

- **Python:**
  - Install the packages with `python -m pip install numpy pandas scipy matplotlib`.
  - Run each script from the repo root, e.g. `python stage3_loop/python_check/stage3_analysis.py`. Scripts find their data relative to their own folder.
- **ANSYS (Mechanical APDL 2023 R1, UCL remote desktop):**
  1. Open MAPDL. Use *File → Change Directory* to pick an empty folder.
  2. Use *File → Read Input from…* to load the stage's `.inp`.
  3. Keep the Output Window minimised, not closed.
  4. Copy the CSVs and PNGs back into the stage's `results/` and `figures/` folders.
- **Script versions:** script versions are numbered (`stage3_loop_v5.inp` …). Each `results/<run>/` folder records which version produced it.
