# Stage 3 – checks on the ANSYS results

## 1. Mesh and section convergence (baseline loop)

| case vs baseline (%) | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 0.5 m, 4/bend | +0.09 | +0.23 | +0.17 | +0.02 | -0.43 | -0.56 |
| 0.125 m, 16/bend | -0.07 | -0.34 | -0.20 | -0.02 | -0.11 | -0.13 |
| 0.25 m, 16/bend | -0.02 | -0.00 | -0.01 | -0.00 | -0.00 | -0.00 |
| 0.125 m, 8/bend | -0.05 | -0.33 | -0.19 | -0.02 | -0.11 | -0.13 |
| 0.25 m, 8/bend, **4 Fourier terms** | -27.11 | -6.64 | -12.88 | -5.02 | -0.72 | -0.61 |

- Element size and elements per bend change all six frequencies by at most 0.56%, so the beam mesh is converged.
- **The number of ovalisation (Fourier) terms is NOT converged.** Going from 2 to 4 terms lowers mode 1 by 27% (1.81 → 1.32 Hz) and mode 3 by 13%. The bend's cross-section needs more terms to deform freely; the baseline must be rerun with more terms (4, 6, 8) until it settles.

## 2. Independent check against the Python frame model

| model (baseline loop), Hz | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| ANSYS PIPE289 (stiff bends) | 3.41 | 3.49 | 5.02 | 13.62 | 13.86 | 15.04 |
| Python frame, k = 1 | 3.45 | 3.55 | 5.07 | 14.04 | 14.35 | 15.56 |
| ANSYS ELBOW290, 2 Fourier | 1.81 | 2.67 | 3.61 | 12.70 | 13.79 | 14.00 |
| ANSYS ELBOW290, 4 Fourier | 1.32 | 2.49 | 3.15 | 12.06 | 13.69 | 13.92 |
| Python frame, B31.3 k = 20 | 1.23 | 2.46 | 3.06 | 11.36 | 13.67 | 14.29 |

- Stiff bends: ANSYS PIPE289 and the Python frame model agree within 3.4% on all six modes. Geometry, supports and fluid mass are therefore consistent between the two independent models.
- Flexible bends: ELBOW290 moves towards the B31.3 code value as more ovalisation terms are used (mode 1: 2 terms 1.81 Hz → 4 terms 1.32 Hz vs code 1.23 Hz). Some stiffening relative to B31.3 is expected because the straight tangent pipe restrains ovalisation at the bend ends.

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
- Modes 2 and 3 have the largest bend projections and sit at 2.67 and 3.61 Hz, either side of the 2.75 Hz water-hammer fundamental: these are the modes Stage 4 must watch.

## 4. Effect of loop size and guides (ANSYS ELBOW290, 2 Fourier terms)

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

- A taller loop lowers every mode (more flexible legs); width matters less.
- Moving the first guide closer (3 m) stiffens modes 2–3 to 4.9–5.6 Hz, clear of 2.75 Hz; moving it to 12 m or removing guides drops them onto or below 2.75 Hz.
