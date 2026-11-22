# Stage 3 → Stage 4 handover (baseline loop)

**Status (19 Nov):**
- **Geometry and supports:** fixed, unless Frank and Ashmit change the loop size.
- **ANSYS:** **final results are from run v5** (`results/v5/`), with converged bend ovalisation (8 terms) and a converged mesh.

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

**Check (uniform pressure):** the four bend forces add to zero (ΣF = 0), and their moments about the origin also add to zero (ΣM = 0). So a uniform pressure puts **no net load on the anchors**. It does still push the loop open, though, so it **can** excite the symmetric "loop-opening" modes. Only the antisymmetric modes (1, 3, 5) cancel by symmetry, and those are driven only by pressure *differences* between bends (wave travel times Δs/c ≈ 10.4, 6.7 and 10.4 ms). **Apply the four bend forces individually; don't assume they cancel.**

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

## 4. Natural frequencies (final: ANSYS ELBOW290, v5)

| Mode | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| **f (Hz)** | **1.27** | **2.48** | **3.10** | **11.97** | **13.67** | **13.91** |
| Shape | sway (antisym.) | loop opening (sym.) | rocking (antisym.) | loop legs in-out (sym.) | guided legs | guided legs |

- **Modes 2 and 3 bracket the 2.75 Hz water-hammer fundamental, at −10% and +13%. These are the modes to watch.** Mode 2 is symmetric, so a uniform pressure rise can excite it. Mode 3 needs the pressure differences between bends.
- **Checks:**
  - The mesh is converged (≤ 0.5%), and the bend ovalisation is converged (7 → 8 terms changes frequencies by 0.02%).
  - The results are within 3.3% of the Python B31.3 frame model.
  - With stiff bends, ANSYS matches the Python model to within 1.9%.
- **Use these files:**
  - `results/v5/stage3_modeshapes_at_bends.csv`: UX and UY at each bend midpoint, plus φ·F̂ (modal force per unit pA).
  - `results/v5/stage3_modeshapes_baseline.csv`: every centreline node.
  - `figures/v5/stage3_ansys_modes_baseline.png`: mode-shape plots.
- **Damping:** modal analysis gives none. Stage 4 must choose a damping ratio and test its sensitivity, as the brief asks.

## 5. Files

Already in the repo:
- `python_check/stage3_loop_beam_check.py`, the Python frame model
- `results/stage3_beam_check.csv`, its results
- `figures/stage3_python_modes_baseline.png`, Python frame-model mode shapes (independent check)

From the ANSYS run (to follow):

| File | What it contains |
|---|---|
| `stage3_results.csv` | Frequencies for all 14 cases |
| `stage3_bend_geometry.csv` | The bend table above |
| `stage3_modeshapes_baseline.csv` | UX, UY and ROTZ at every node, modes 1–6 |
| `stage3_modeshapes_at_bends.csv` | Mode shape at each bend midpoint, plus φ·F̂ (the modal force per unit pA) |
| Mode-shape PNGs | Baseline modes 1–6 |
