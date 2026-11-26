# Stage 4 – ASME B31.3 bend code check (26 Nov)

**Method:** ELBOW290 beam end forces and moments, with the B31.3 Appendix D in-plane stress intensification factor applied to bending at the bend elements:

- h = tR/r² = 0.083
- i = 0.9/h^(2/3) = **4.74**

Code stress: σ = |N|/A + i·M·r/I.

**Allowables** (304 stainless; S_h = S_c = 138 MPa, to be checked against Table A-1):

- Occasional load (sustained + water hammer): 1.33 S_h = **184 MPa**
- Expansion: S_A = 1.25 S_c + 0.25 S_h = **207 MPa**

## Expansion: cooldown 293 → 111 K (thermal only)

| Run | Peak displacement | Peak nominal stress | Peak bend stress (with SIF) | Limit S_A | Result |
|---|---|---|---|---|---|
| W = 8 m (`thermal_v3_W8`) | 87.8 mm | 19.6 MPa | **90.9 MPa** | 207 MPa | Pass (44 % of limit) |
| W = 12 m (`thermal_v3_W12`) | 82.7 mm | 18.6 MPa | **86.0 MPa** | 207 MPa | Pass (42 % of limit) |

The W = 8 m run reproduces Jerry's thermal v2 exactly (87.80 mm, 19.63 MPa). The anchor span contracts 199.8 mm in both cases.

## Occasional load: water hammer, W = 8 m, 0.50 s closure (`closure_0p50s_msup_v2`)

- Reproduces Jerry's run exactly: 48.19 mm, 119.97 MPa nominal, 435.5 kN.
- Total bend stress (thermal + pressure + surge) is **145 MPa** before closure and **251 MPa** at its peak (t = 1.625 s, element 391).
- Thermal bend stress at element 391 is **74.5 MPa** (thermal v3 run).
- B31.3 checks the occasional load without thermal. Taking the thermal moment off at the same element gives about **251 − 74.5 ≈ 176 MPa**.
- This includes the longitudinal pressure stress, because the bend thrust puts each leg in tension of about pA.
- **176 MPa is 96 % of the 184 MPa limit: a pass, but with only about 4 % margin.**

### Sensitivity

- **Damping:** at 0.5 % damping the 0.50 s response is about 16 % higher (Python check: 57.3 mm vs 49.2 mm), which would push the stress over the limit.
- **Wave speed:** a wall-corrected wave speed of about 998 m/s moves the forcing frequency to about 2.5 Hz.

So 0.50 s should be treated as the **minimum** closure time. The recommendation is about 1 s, or detuning mode 3 away from 2.75 Hz.

## 0.02 s and 0.10 s closures

Nominal stress alone is 437 MPa and 379 MPa, which already exceeds 184 MPa before the SIF is applied. **Both fail.**
