# Stage 3 – checks on the ANSYS results

## 1. Convergence of the baseline loop (ELBOW290, 8 ovalisation terms)

### Beam mesh

| mesh vs baseline (0.25 m, 8/bend), % | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 0.5 m, 4/bend | +0.36 | +0.29 | +0.30 | +0.09 | -0.31 | -0.52 |
| 0.125 m, 16/bend | -0.12 | -0.35 | -0.27 | -0.03 | -0.10 | -0.13 |
| 0.25 m, 16/bend | -0.09 | -0.01 | -0.03 | -0.02 | -0.00 | -0.00 |

- Element size and elements per bend change all six frequencies by at most 0.52%: the beam mesh is converged.

### Ovalisation (Fourier) terms, KEYOPT(2)

| terms | 1 | Δ1 % | 2 | Δ2 % | 3 | Δ3 % |
|---|---|---|---|---|---|---|
| 2 | 1.814 | 0.000 | 2.672 | 0.000 | 3.610 | 0.000 |
| 3 | 1.679 | -7.436 | 2.618 | -2.019 | 3.477 | -3.680 |
| 4 | 1.322 | -21.258 | 2.495 | -4.712 | 3.145 | -9.553 |
| 5 | 1.300 | -1.637 | 2.487 | -0.303 | 3.125 | -0.644 |
| 6 | 1.274 | -2.019 | 2.479 | -0.326 | 3.101 | -0.748 |
| 7 | 1.272 | -0.166 | 2.479 | -0.027 | 3.100 | -0.061 |
| 8 | 1.272 | -0.021 | 2.479 | -0.003 | 3.099 | -0.008 |

- Mode 1 falls from 1.81 Hz with the default 2 terms to 1.27 Hz with 8 terms (-30%). The thin wall (D/t ≈ 85) needs many terms for the bend cross-section to ovalise freely.
- The last step (7 → 8 terms) changes modes 1–3 by at most 0.02%: converged.

## 2. Independent check against the Python frame model

| model (baseline loop), Hz | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| ANSYS PIPE289 (stiff bends) | 3.41 | 3.49 | 5.02 | 13.62 | 13.86 | 15.04 |
| Python frame, k = 1 | 3.45 | 3.55 | 5.07 | 14.04 | 14.35 | 15.56 |
| ANSYS ELBOW290, 2 terms | 1.81 | 2.67 | 3.61 | 12.70 | 13.79 | 14.00 |
| ANSYS ELBOW290, 8 terms (converged) | 1.27 | 2.48 | 3.10 | 11.97 | 13.67 | 13.91 |
| Python frame, B31.3 k = 20 | 1.23 | 2.46 | 3.06 | 11.36 | 13.67 | 14.29 |

- Stiff bends: ANSYS PIPE289 and the Python frame model agree within 1.9% on modes 1–3 (3.4% on all six). Geometry, supports and fluid mass are consistent between two independent models.
- Flexible bends: converged ELBOW290 (8 terms) is within 3.3% of the B31.3 flexibility-factor model on modes 1–3 (ANSYS +3.3% on mode 1). The small stiffening is expected, because the straight tangent pipe restrains ovalisation at the bend ends, which the code factor ignores.
- Ignoring bend ovalisation (stiff bends) would over-predict mode 1 by 168%.

## 3. Bend-force projections (input to Stage 4)

| φ·F̂ per unit pA | bend 1 | bend 2 | bend 3 | bend 4 | sum (uniform p) | max |bend| |
|---|---|---|---|---|---|---|
| mode 1 (1.27 Hz) | -4.17e-04 | -1.24e-02 | +1.24e-02 | +4.17e-04 | +2.20e-07 | +1.24e-02 |
| mode 2 (2.48 Hz) | -8.44e-03 | +8.26e-03 | +8.25e-03 | -8.44e-03 | -3.65e-04 | +8.44e-03 |
| mode 3 (3.10 Hz) | +9.04e-03 | -8.35e-03 | +8.36e-03 | -9.04e-03 | +8.00e-08 | +9.04e-03 |
| mode 4 (11.97 Hz) | +1.55e-03 | -6.25e-04 | -6.42e-04 | +1.53e-03 | +1.82e-03 | +1.55e-03 |
| mode 5 (13.67 Hz) | -1.55e-03 | -2.26e-03 | +2.36e-03 | +1.46e-03 | +1.01e-05 | +2.36e-03 |
| mode 6 (13.91 Hz) | -6.21e-04 | +1.06e-03 | +6.66e-04 | -8.16e-04 | +2.92e-04 | +1.06e-03 |

- Antisymmetric modes (1, 3, 5) sum to ~0: by symmetry a uniform pressure cannot excite them; only pressure *differences* between bends (wave travel time) drive them.
- Symmetric modes do NOT cancel in general (mode 4 sum is larger than any single bend term; mode 2 cancels to ~4%). The four bend forces are self-equilibrated (no net force or moment on the anchors), but they still push the loop open, so a uniform pressure rise excites the symmetric 'loop-opening' modes. Stage 4 must apply the bend forces individually rather than assume they cancel.
- Modes 2 and 3 have the largest bend projections and sit at 2.48 and 3.10 Hz, either side of the 2.75 Hz water-hammer fundamental (-10% / +13%): these are the modes Stage 4 must watch.

## 4. Effect of loop size and guides (ANSYS ELBOW290, 8 terms)

| case, Hz | 1 | 2 | 3 |
|---|---|---|---|
| H = 8 m | 2.24 | 2.86 | 3.67 |
| H = 12 m (baseline) | 1.27 | 2.48 | 3.10 |
| H = 16 m | 0.85 | 2.22 | 2.71 |
| W = 4 m | 1.42 | 2.63 | 4.72 |
| W = 12 m | 1.10 | 2.35 | 2.77 |
| first guide 3 m | 1.31 | 4.60 | 5.13 |
| first guide 12 m | 1.09 | 1.14 | 2.10 |
| no guides | 0.34 | 0.71 | 1.74 |

- A taller or wider loop lowers every mode (more flexible legs).
- Moving the first guide to 3 m lifts modes 2–3 to 4.6–5.1 Hz, well clear of 2.75 Hz. A guide at 12 m or no guides puts them at 1.14–2.10 Hz and 0.71–1.74 Hz.
- Cases within ±10% of 2.75 Hz (resonance risk): H = 8 m mode 2 2.86 Hz, H = 12 m (baseline) mode 2 2.48 Hz, H = 16 m mode 3 2.71 Hz, W = 4 m mode 2 2.63 Hz, W = 12 m mode 3 2.77 Hz.
