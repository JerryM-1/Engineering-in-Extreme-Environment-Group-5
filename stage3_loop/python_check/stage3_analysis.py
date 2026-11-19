"""
MECH0074 CW1 - Stage 3 post-processing of the ANSYS expansion-loop results.

Reads the CSVs written by ansys/stage3_loop_modal.inp (in ../results) and the
Python frame-model check (stage3_beam_check.csv), then:
  1. checks mesh / section convergence of the baseline,
  2. compares ANSYS ELBOW290 and PIPE289 with the Python frame model,
  3. checks the bend-force projections (uniform pressure must not excite modes),
  4. plots the baseline mode shapes and the parametric trends.

Run (VS Code or terminal):  python stage3_analysis.py
Outputs: ../results/<RUN>/stage3_checks.md and ../figures/<RUN>/stage3_*.png
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "v4_2fourier"   # results folder for this ANSYS run (case numbering of the v4 script)
RES = os.path.join(HERE, "..", "results", RUN)
FIG = os.path.join(HERE, "..", "figures", RUN)
os.makedirs(FIG, exist_ok=True)
F_WH = 2.75                      # Stage 1 water-hammer fundamental, 4L/c [Hz]

C = {"blue": "#2a78d6", "orange": "#eb6834", "green": "#1baf7a",
     "grey": "#b8b7b2", "ink": "#0b0b0b", "muted": "#52514e", "grid": "#e5e4e0"}
plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": C["muted"],
                     "xtick.color": C["muted"], "ytick.color": C["muted"]})


def load(name):
    df = pd.read_csv(os.path.join(RES, name), skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    return df


res = load("stage3_results.csv")
res[["case", "mode"]] = res[["case", "mode"]].astype(int)
f = res.pivot(index="case", columns="mode", values="freq_Hz")
py = load("stage3_beam_check.csv").pivot(index="case", columns="mode", values="freq_Hz")
bends = load("stage3_modeshapes_at_bends.csv")
shapes = load("stage3_modeshapes_baseline.csv")

lines = ["# Stage 3 – checks on the ANSYS results", ""]


def table(df, fmt="{:.3f}"):
    head = "| " + " | ".join(str(c) for c in [df.index.name or ""] + list(df.columns)) + " |"
    sep = "|" + "---|" * (len(df.columns) + 1)
    rows = ["| " + " | ".join([str(i)] + [fmt.format(v) for v in r]) + " |"
            for i, r in zip(df.index, df.values)]
    return [head, sep] + rows


# ---------------------------------------------------------------- 1. convergence
labels = {1: "baseline: 0.25 m, 8/bend, 2 Fourier", 10: "0.5 m, 4/bend",
          11: "0.125 m, 16/bend", 12: "0.25 m, 16/bend", 14: "0.125 m, 8/bend",
          13: "0.25 m, 8/bend, **4 Fourier terms**"}
conv = (f.loc[[10, 11, 12, 14, 13]] / f.loc[1] - 1) * 100
conv.index = [labels[i] for i in conv.index]
conv.index.name = "case vs baseline (%)"
lines += ["## 1. Mesh and section convergence (baseline loop)", ""]
lines += table(conv, "{:+.2f}")
lines += ["",
          f"- Element size and elements per bend change all six frequencies by at most "
          f"{conv.iloc[:4].abs().values.max():.2f}%, so the beam mesh is converged.",
          f"- **The number of ovalisation (Fourier) terms is NOT converged.** Going from 2 to 4 "
          f"terms lowers mode 1 by {abs(conv.iloc[4][1]):.0f}% "
          f"({f.loc[1][1]:.2f} → {f.loc[13][1]:.2f} Hz) and mode 3 by {abs(conv.iloc[4][3]):.0f}%. "
          "The bend's cross-section needs more terms to deform freely; the baseline must be rerun "
          "with more terms (4, 6, 8) until it settles.", ""]

# ---------------------------------------------------------------- 2. model comparison
comp = pd.DataFrame({"ANSYS PIPE289 (stiff bends)": f.loc[9],
                     "Python frame, k = 1": py.loc[9],
                     "ANSYS ELBOW290, 2 Fourier": f.loc[1],
                     "ANSYS ELBOW290, 4 Fourier": f.loc[13],
                     "Python frame, B31.3 k = 20": py.loc[1]}).T
comp.index.name = "model (baseline loop), Hz"
lines += ["## 2. Independent check against the Python frame model", ""]
lines += table(comp, "{:.2f}")
d = (f.loc[9] / py.loc[9] - 1) * 100
lines += ["",
          f"- Stiff bends: ANSYS PIPE289 and the Python frame model agree within "
          f"{d.abs().max():.1f}% on all six modes. Geometry, supports and fluid mass are "
          "therefore consistent between the two independent models.",
          "- Flexible bends: ELBOW290 moves towards the B31.3 code value as more ovalisation "
          "terms are used (mode 1: 2 terms 1.81 Hz → 4 terms "
          f"{f.loc[13][1]:.2f} Hz vs code {py.loc[1][1]:.2f} Hz). Some stiffening relative to "
          "B31.3 is expected because the straight tangent pipe restrains ovalisation at the bend ends.",
          ""]

# ---------------------------------------------------------------- 3. bend forces
proj = bends.pivot(index="mode", columns="bend", values="modal_force_component_per_unit_pA")
proj.columns = [f"bend {int(c)}" for c in proj.columns]
proj["sum (uniform p)"] = proj.sum(axis=1)
proj["max |bend|"] = proj.iloc[:, :4].abs().max(axis=1)
proj.index = [f"mode {int(m)} ({fr:.2f} Hz)" for m, fr in
              zip(proj.index, bends.groupby("mode")["freq_Hz"].first())]
proj.index.name = "φ·F̂ per unit pA"
lines += ["## 3. Bend-force projections (input to Stage 4)", ""]
lines += table(proj, "{:+.2e}")
lines += ["",
          "- Antisymmetric modes (1, 3, 5) sum to ~0: by symmetry a uniform pressure cannot excite "
          "them; only pressure *differences* between bends (wave travel time) drive them.",
          "- Symmetric modes do NOT cancel in general (mode 4 sum is larger than any single "
          "bend term; mode 2 cancels to ~4%). The four bend forces are self-equilibrated (no net "
          "force or moment on the anchors), but they still push the loop open, so a uniform "
          "pressure rise excites the symmetric 'loop-opening' modes. Stage 4 must apply the bend "
          "forces individually rather than assume they cancel.",
          "- Modes 2 and 3 have the largest bend projections and sit at 2.67 and 3.61 Hz, either "
          "side of the 2.75 Hz water-hammer fundamental: these are the modes Stage 4 must watch.",
          ""]

# ---------------------------------------------------------------- 4. parametric
lines += ["## 4. Effect of loop size and guides (ANSYS ELBOW290, 2 Fourier terms)", ""]
par = f.loc[[2, 1, 3, 4, 5, 6, 7, 8], [1, 2, 3]].copy()
par.index = ["H = 8 m", "H = 12 m (baseline)", "H = 16 m", "W = 4 m", "W = 12 m",
             "first guide 3 m", "first guide 12 m", "no guides"]
par.index.name = "case, Hz"
lines += table(par, "{:.2f}")
lines += ["",
          "- A taller loop lowers every mode (more flexible legs); width matters less.",
          "- Moving the first guide closer (3 m) stiffens modes 2–3 to 4.9–5.6 Hz, clear of "
          "2.75 Hz; moving it to 12 m or removing guides drops them onto or below 2.75 Hz.",
          ""]
open(os.path.join(RES, "stage3_checks.md"), "w").write("\n".join(lines))
print("\n".join(lines))

# ---------------------------------------------------------------- figures
# mode shapes from the exported centreline displacements
fig, axs = plt.subplots(2, 3, figsize=(12, 5.2), dpi=200, sharex=True, sharey=True)
for m, ax in zip(range(1, 7), axs.flat):
    d = shapes[shapes["mode"].astype(int) == m]
    xy = d[["x_m", "y_m"]].to_numpy()
    uv = d[["UX", "UY"]].to_numpy()
    # order nodes along the pipe by chaining nearest neighbours from x = 0
    order, left = [int(np.argmin(np.hypot(*xy.T)))], set(range(len(xy)))
    left.discard(order[0])
    while left:
        idx = np.fromiter(left, int)
        j = idx[np.argmin(np.hypot(*(xy[idx] - xy[order[-1]]).T))]
        order.append(j); left.discard(j)
    xy, uv = xy[order], uv[order]
    s = 3.0 / np.abs(uv).max()
    ax.plot(xy[:, 0], xy[:, 1], color=C["grey"], lw=1.4)
    ax.plot(xy[:, 0] + s * uv[:, 0], xy[:, 1] + s * uv[:, 1], color=C["blue"], lw=2)
    ax.set_title(f"Mode {m}: {d['freq_Hz'].iloc[0]:.2f} Hz", loc="left", fontsize=11)
    ax.set_aspect("equal"); ax.set_ylim(-5, 17)
fig.suptitle("Stage 3 baseline loop (H = 12 m, W = 8 m): in-plane modes, ANSYS ELBOW290",
             x=0.01, ha="left", fontsize=12)
fig.supxlabel("x (m)"); fig.supylabel("y (m)")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "stage3_ansys_modes_baseline.png"))

# parametric trends
fig, axs = plt.subplots(1, 3, figsize=(12, 4), dpi=200, sharey=True)
groups = [("Loop height H (m)", [2, 1, 3], [8, 12, 16]),
          ("Loop width W (m)", [4, 1, 5], [4, 8, 12]),
          ("First guide from loop (m)", [6, 1, 7], [3, 6, 12])]
for ax, (lab, cases, xs) in zip(axs, groups):
    for m, col in zip([1, 2, 3], [C["blue"], C["orange"], C["green"]]):
        ax.plot(xs, f.loc[cases, m], "-o", color=col, lw=2, ms=7, label=f"mode {m}")
    ax.axhline(F_WH, color=C["muted"], ls="--", lw=1)
    ax.set_xlabel(lab); ax.set_xticks(xs); ax.grid(axis="y", color=C["grid"])
axs[0].set_ylabel("Natural frequency (Hz)")
axs[1].text(12.2, F_WH, "water hammer\n2.75 Hz", fontsize=9, color=C["muted"], va="center")
axs[2].legend(frameon=False, loc="upper right")
fig.suptitle("Stage 3: effect of loop size and guide position on the first three in-plane modes",
             x=0.01, ha="left", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "stage3_parametric.png"))

# model comparison (modes 1-3, where the bend model matters)
fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
cols = [C["grey"], C["muted"], C["blue"], C["green"], C["orange"]]
marks = ["s", "D", "o", "o", "^"]
offs = np.linspace(-0.2, 0.2, len(comp))
for (name, row), col, mk, dx in zip(comp.iterrows(), cols, marks, offs):
    ax.plot(np.arange(1, 4) + dx, row.values[:3], mk, color=col, ms=9, mec="white",
            mew=1.2, label=name)
ax.axhline(F_WH, color=C["muted"], ls="--", lw=1)
ax.text(3.45, F_WH + 0.05, "water hammer 2.75 Hz", fontsize=9, color=C["muted"], ha="right")
ax.set_xticks([1, 2, 3]); ax.set_xlim(0.5, 3.5); ax.set_ylim(0, 5.6)
ax.set_xlabel("Mode"); ax.set_ylabel("Natural frequency (Hz)")
ax.grid(axis="y", color=C["grid"])
ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_title("Stage 3 baseline: the bend model controls modes 1-3", loc="left", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "stage3_model_comparison.png"))
print("figures written to", os.path.abspath(FIG))
