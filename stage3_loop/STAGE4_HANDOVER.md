# Stage 3 → Stage 4 handover (baseline loop)

**Status (19 Nov):**
- **Geometry and supports:** fixed, unless Frank and Ashmit change the loop size.
- **Frequencies and mode shapes:** these are **provisional** values from the Python frame model (`python_check/`). The ANSYS ELBOW290 run (`ansys/stage3_loop_modal.inp`) will replace them, and it writes all the CSVs listed at the end.

## 1. Geometry

The geometry is a plan view in the horizontal XY plane, with flow in the +x direction from the reservoir to the valve.

| Item | Value |
|---|---|
| Developed length (reservoir → valve) | 100.0 m, the same as the Stage 1 benchmark |
| Loop height H / width W | 12 m / 8 m, measured on the centreline between leg axes |
| Bend radius | 1.4 m, four 90° tangent bends |
| Inlet leg | x = 0 → 33.80 m along y = 0. The bend 1 tangent is at x = 35.20 − 1.4 m |
| Loop legs | Up leg at x = 35.20 m; top leg at y = 12 m; down leg at x = 43.20 m |
| Outlet leg | x = 44.60 → 78.40 m along y = 0 |
| Anchor-to-anchor distance | 78.40 m, so the cooldown contraction to absorb is 1.4×10⁻⁵ × 182 × 78.4 ≈ **200 mm** |

### Bends

- *s* is the developed distance from the reservoir to the bend midpoint, which is the hydraulic station.
- The force direction is the unit vector for the **fluid force on the bend**. It points from the arc centre to the outside corner.
- Magnitude: |F| = √2 · p · A, with A = 0.4951 m², so **700 kN per MPa** of gauge pressure. The momentum term is negligible at 1.5 m/s.

| Bend | s (m) | Arc centre (x, y) | Midpoint (x, y) | Flow turns | Force direction (ex, ey) |
|---|---|---|---|---|---|
| 1 | 34.901 | (33.802, 1.400) | (34.792, 0.410) | +x → +y, left | (+0.707, −0.707) |
| 2 | 46.300 | (36.602, 10.600) | (35.612, 11.590) | +y → +x, right | (−0.707, +0.707) |
| 3 | 53.700 | (41.802, 10.600) | (42.792, 11.590) | +x → −y, right | (+0.707, +0.707) |
| 4 | 65.099 | (44.602, 1.400) | (43.612, 0.410) | −y → +x, left | (−0.707, −0.707) |

**Check (uniform pressure):** the four bend forces add to zero (ΣF = 0), and their moments about the origin also add to zero (ΣM = 0). So a uniform pressure loads only the loop's internal stresses. It doesn't move the line as a whole or load the anchors. Only the *differences* in pressure between bends, which come from the wave travel time (Δs/c ≈ 10.4, 6.7 and 10.4 ms), can excite the modes.

## 2. Supports and restraints

| Support | Location | Restraint |
|---|---|---|
| Anchors | x = 0 (reservoir end) and x = 78.40 m (valve end) | All DOF fixed |
| Guides, inlet | x = 27.80, 15.80, 3.80 m | Lateral movement (UY) fixed; free to slide axially without friction (PTFE, see Part A) |
| Guides, outlet | x = 50.60, 62.60, 74.60 m | Same as the inlet guides |
| Vertical | All nodes | UZ, ROTX and ROTY fixed (sleepers), so the model is in-plane only |

The loop itself is unguided. The first guide is 6 m from each loop leg, and the rest are spaced 12 m apart.

## 3. Fluid mass

- **Mass per metre:** LNG 225.3 kg/m plus steel 192.4 kg/m, giving **417.7 kg/m**.
- **How it's applied:** as an effective steel density of 17,364 kg/m³. E is unchanged, so EI is the real steel value.
- **What that assumes:** the fluid moves rigidly with the pipe in every direction. Fluid–structure interaction is not modelled; Stage 4 brings in the fluid effect through the bend forces.

## 4. Natural frequencies (provisional: Python frame model, B31.3 bend flexibility k = 20)

| Mode | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| f (Hz) | 1.23 | 2.46 | 3.06 | 11.4 | 13.7 | 14.3 |

- **Modes 2 and 3 bracket the 2.75 Hz water-hammer fundamental (4L/c), so they are the ones to watch.**
- **With stiff bends** (no ovalisation), modes 1–3 move to 3.45, 3.55 and 5.07 Hz.
- **The mode shapes** are in `figures/stage3_python_modes_baseline.png`:
  - Mode 1: sideways sway of the loop.
  - Mode 2: the loop "breathing" axially, with the top leg moving in y.
  - Mode 3: an antisymmetric rocking of the loop.
  - Modes 4–6: higher-order bending of the loop and the guided legs.

## 5. Files

Already in the repo:
- `python_check/stage3_loop_beam_check.py`, the Python frame model
- `results/stage3_beam_check.csv`, its results
- `figures/stage3_python_modes_baseline.png`, the provisional mode shapes

From the ANSYS run (to follow):

| File | What it contains |
|---|---|
| `stage3_results.csv` | Frequencies for all 14 cases |
| `stage3_bend_geometry.csv` | The bend table above |
| `stage3_modeshapes_baseline.csv` | UX, UY and ROTZ at every node, modes 1–6 |
| `stage3_modeshapes_at_bends.csv` | Mode shape at each bend midpoint, plus φ·F̂ (the modal force per unit pA) |
| Mode-shape PNGs | Baseline modes 1–6 |
