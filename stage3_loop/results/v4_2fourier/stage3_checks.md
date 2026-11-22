# Stage 3 – checks on the ANSYS results

## 1. Convergence of the baseline loop (ELBOW290, 2 ovalisation terms)

### Beam mesh

| mesh vs baseline (0.25 m, 8/bend), % | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 0.5 m, 4/bend | +0.09 | +0.23 | +0.17 | +0.02 | -0.43 | -0.56 |
| 0.125 m, 16/bend | -0.07 | -0.34 | -0.20 | -0.02 | -0.11 | -0.13 |
| 0.25 m, 16/bend | -0.02 | -0.00 | -0.01 | -0.00 | -0.00 | -0.00 |
| 0.125 m, 8/bend | -0.05 | -0.33 | -0.19 | -0.02 | -0.11 | -0.13 |

- Element size and elements per bend change all six frequencies by at most 0.56%: the beam mesh is converged.

### Ovalisation (Fourier) terms, KEYOPT(2)

| terms | 1 | Δ1 % | 2 | Δ2 % | 3 | Δ3 % |
|---|---|---|---|---|---|---|
| 2 | 1.814 | 0.000 | 2.672 | 0.000 | 3.610 | 0.000 |
| 4 | 1.322 | -27.113 | 2.495 | -6.637 | 3.145 | -12.882 |

- Mode 1 falls from 1.81 Hz with the default 2 terms to 1.32 Hz with 4 terms (-27%). The thin wall (D/t ≈ 85) needs many terms for the bend cross-section to ovalise freely.
- The last step (2 → 4 terms) changes modes 1–3 by at most 27.11%: **not yet converged**.

## 2. Independent check against the Python frame model

| model (baseline loop), Hz | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| ANSYS PIPE289 (stiff bends) | 3.41 | 3.49 | 5.02 | 13.62 | 13.86 | 15.04 |
| Python frame, k = 1 | 3.45 | 3.55 | 5.07 | 14.04 | 14.35 | 15.56 |
| ANSYS ELBOW290, 2 terms | 1.81 | 2.67 | 3.61 | 12.70 | 13.79 | 14.00 |
| Python frame, B31.3 k = 20 | 1.23 | 2.46 | 3.06 | 11.36 | 13.67 | 14.29 |

- Stiff bends: ANSYS PIPE289 and the Python frame model agree within 1.9% on modes 1–3 (3.4% on all six). Geometry, supports and fluid mass are consistent between two independent models.
- Flexible bends: converged ELBOW290 (2 terms) is within 47.3% of the B31.3 flexibility-factor model on modes 1–3 (ANSYS +47.3% on mode 1). The small stiffening is expected, because the straight tangent pipe restrains ovalisation at the bend ends, which the code factor ignores.
- Ignoring bend ovalisation (stiff bends) would over-predict mode 1 by 88%.

## 3. Bend-force projections (input to Stage 4)

| φ·F̂ per unit pA | bend 1 | bend 2 | bend 3 | bend 4 | sum (uniform p) | max |bend| |
|---|---|---|---|---|---|---|
| mode 1 (1.81 Hz) | -9.19e-04 | -1.18e-02 | +1.18e-02 | +9.19e-04 | +5.25e-07 | +1.18e-02 |
| mode 2 (2.67 Hz) | -8.40e-03 | +8.24e-03 | +8.24e-03 | -8.40e-03 | -3.13e-04 | +8.40e-03 |
| mode 3 (3.61 Hz) | +8.94e-03 | -8.69e-03 | +8.69e-03 | -8.94e-03 | +3.00e-07 | +8.94e-03 |
| mode 4 (12.70 Hz) | +1.69e-03 | -6.05e-04 | -6.26e-04 | +1.66e-03 | +2.11e-03 | +1.69e-03 |
| mode 5 (13.79 Hz) | -1.39e-03 | -1.00e-03 | +1.12e-03 | +1.33e-03 | +5.37e-05 | +1.39e-03 |
| mode 6 (14.00 Hz) | -3.94e-04 | +9.60e-04 | +7.51e-04 | -6.08e-04 | +7.09e-04 | +9.60e-04 |

- Antisymmetric modes (1, 3, 5) sum to ~0: by symmetry a uniform pressure cannot excite them; only pressure *differences* between bends (wave travel time) drive them.
- Symmetric modes do NOT cancel in general (mode 4 sum is larger than any single bend term; mode 2 cancels to ~4%). The four bend forces are self-equilibrated (no net force or moment on the anchors), but they still push the loop open, so a uniform pressure rise excites the symmetric 'loop-opening' modes. Stage 4 must apply the bend forces individually rather than assume they cancel.
- Modes 2 and 3 have the largest bend projections and sit at 2.67 and 3.61 Hz, either side of the 2.75 Hz water-hammer fundamental (-3% / +31%): these are the modes Stage 4 must watch.

## 4. Effect of loop size and guides (ANSYS ELBOW290, 2 terms)

| case, Hz | 1 | 2 | 3 |
|---|---|---|---|
| H = 8 m | 3.11 | 3.16 | 4.43 |
| H = 12 m (baseline) | 1.81 | 2.67 | 3.61 |
| H = 16 m | 1.20 | 2.37 | 3.08 |
| W = 4 m | 1.94 | 2.83 | 6.05 |
| W = 12 m | 1.58 | 2.53 | 3.08 |
| first guide 3 m | 1.89 | 4.90 | 5.57 |
| first guide 12 m | 1.26 | 1.46 | 2.79 |
| no guides | 0.38 | 0.89 | 2.33 |

- A taller or wider loop lowers every mode (more flexible legs).
- Moving the first guide to 3 m lifts modes 2–3 to 4.9–5.6 Hz, well clear of 2.75 Hz. A guide at 12 m or no guides puts them at 1.46–2.79 Hz and 0.89–2.33 Hz.
- Cases within ±10% of 2.75 Hz (resonance risk): H = 12 m (baseline) mode 2 2.67 Hz, W = 4 m mode 2 2.83 Hz, W = 12 m mode 2 2.53 Hz, first guide 12 m mode 3 2.79 Hz.
