"""
MECH0074 CW1 - Stage 3 post-processing of the ANSYS expansion-loop results.

Reads the CSVs written by ansys/stage3_loop_modal.inp (in ../results) and the
Python frame-model check (stage3_beam_check.csv), then:
  1. checks mesh / section convergence of the baseline,
  2. compares ANSYS ELBOW290 and PIPE289 with the Python frame model,
  3. checks the bend-force projections (uniform pressure must not excite modes),
  4. plots the baseline mode shapes and the parametric trends.

Run (VS Code or terminal):  python stage3_analysis.py [v5 | v4_2fourier]
Outputs: ../results/<RUN>/stage3_checks.md and ../figures/<RUN>/stage3_*.png
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
RUN = sys.argv[1] if len(sys.argv) > 1 else "v5"   # results folder of the ANSYS run
# case numbering differs between script versions
CFG = {
    "v4_2fourier": dict(terms=2, stiff=9,
                        mesh={10: "0.5 m, 4/bend", 11: "0.125 m, 16/bend",
                              12: "0.25 m, 16/bend", 14: "0.125 m, 8/bend"},
                        fourier={2: 1, 4: 13}),
    "v5": dict(terms=8, stiff=9,
               mesh={10: "0.5 m, 4/bend", 11: "0.125 m, 16/bend", 12: "0.25 m, 16/bend"},
               fourier={2: 13, 3: 14, 4: 15, 5: 16, 6: 17, 7: 18, 8: 1}),
}[RUN]
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
T = CFG["terms"]
mesh = (f.loc[list(CFG["mesh"])] / f.loc[1] - 1) * 100
mesh.index = list(CFG["mesh"].values())
mesh.index.name = f"mesh vs baseline (0.25 m, 8/bend), %"
lines += [f"## 1. Convergence of the baseline loop (ELBOW290, {T} ovalisation terms)", "",
          "### Beam mesh", ""]
lines += table(mesh, "{:+.2f}")
lines += ["", f"- Element size and elements per bend change all six frequencies by at most "
          f"{mesh.abs().values.max():.2f}%: the beam mesh is converged.", "",
          "### Ovalisation (Fourier) terms, KEYOPT(2)", ""]
four = pd.DataFrame({k: f.loc[c, [1, 2, 3]] for k, c in sorted(CFG["fourier"].items())}).T
four.index.name = "terms"
chg = four.pct_change() * 100
ft = four.copy()
for m in [1, 2, 3]:
    ft[f"Δ{m} %"] = chg[m]
ft = ft[[1, "Δ1 %", 2, "Δ2 %", 3, "Δ3 %"]].fillna(0)
lines += table(ft, "{:.3f}")
last = abs(chg.iloc[-1]).max()
lines += ["",
          f"- Mode 1 falls from {four.iloc[0][1]:.2f} Hz with the default 2 terms to "
          f"{four.iloc[-1][1]:.2f} Hz with {four.index[-1]} terms "
          f"({100*(four.iloc[-1][1]/four.iloc[0][1]-1):+.0f}%). The thin wall (D/t ≈ 85) needs many "
          "terms for the bend cross-section to ovalise freely.",
          f"- The last step ({four.index[-2]} → {four.index[-1]} terms) changes modes 1–3 by at most "
          f"{last:.2f}%: " + ("converged." if last < 0.5 else "**not yet converged**."), ""]

# ---------------------------------------------------------------- 2. model comparison
fr4 = CFG["fourier"]
cols = {"ANSYS PIPE289 (stiff bends)": f.loc[CFG["stiff"]],
        "Python frame, k = 1": py.loc[9],
        "ANSYS ELBOW290, 2 terms": f.loc[fr4[2]]}
if T > 2:
    cols[f"ANSYS ELBOW290, {T} terms (converged)"] = f.loc[1]
cols["Python frame, B31.3 k = 20"] = py.loc[1]
comp = pd.DataFrame(cols).T
comp.index.name = "model (baseline loop), Hz"
lines += ["## 2. Independent check against the Python frame model", ""]
lines += table(comp, "{:.2f}")
d_stiff = (f.loc[CFG["stiff"]] / py.loc[9] - 1) * 100
d_flex = (f.loc[1] / py.loc[1] - 1) * 100
lines += ["",
          f"- Stiff bends: ANSYS PIPE289 and the Python frame model agree within "
          f"{d_stiff[[1, 2, 3]].abs().max():.1f}% on modes 1–3 ({d_stiff.abs().max():.1f}% on all six). "
          "Geometry, supports and fluid mass are consistent between two independent models.",
          f"- Flexible bends: converged ELBOW290 ({T} terms) is within "
          f"{d_flex[[1, 2, 3]].abs().max():.1f}% of the B31.3 flexibility-factor model on modes 1–3 "
          f"(ANSYS {d_flex[1]:+.1f}% on mode 1). The small stiffening is expected, because the straight "
          "tangent pipe restrains ovalisation at the bend ends, which the code factor ignores.",
          f"- Ignoring bend ovalisation (stiff bends) would over-predict mode 1 by "
          f"{100*(f.loc[CFG['stiff']][1]/f.loc[1][1]-1):.0f}%.", ""]

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
          f"- Modes 2 and 3 have the largest bend projections and sit at {f.loc[1][2]:.2f} and "
          f"{f.loc[1][3]:.2f} Hz, either side of the 2.75 Hz water-hammer fundamental "
          f"({100*(f.loc[1][2]/F_WH-1):+.0f}% / {100*(f.loc[1][3]/F_WH-1):+.0f}%): these are the "
          "modes Stage 4 must watch.",
          ""]

# ---------------------------------------------------------------- 4. parametric
lines += [f"## 4. Effect of loop size and guides (ANSYS ELBOW290, {T} terms)", ""]
par = f.loc[[2, 1, 3, 4, 5, 6, 7, 8], [1, 2, 3]].copy()
par.index = ["H = 8 m", "H = 12 m (baseline)", "H = 16 m", "W = 4 m", "W = 12 m",
             "first guide 3 m", "first guide 12 m", "no guides"]
par.index.name = "case, Hz"
lines += table(par, "{:.2f}")
lines += ["",
          "- A taller or wider loop lowers every mode (more flexible legs).",
          f"- Moving the first guide to 3 m lifts modes 2–3 to {f.loc[6][2]:.1f}–{f.loc[6][3]:.1f} Hz, "
          f"well clear of 2.75 Hz. A guide at 12 m or no guides puts them at "
          f"{f.loc[7][2]:.2f}–{f.loc[7][3]:.2f} Hz and {f.loc[8][2]:.2f}–{f.loc[8][3]:.2f} Hz.",
          "- Cases within ±10% of 2.75 Hz (resonance risk): " + ", ".join(
              f"{n} mode {m} {par.loc[n, m]:.2f} Hz" for n in par.index for m in [1, 2, 3]
              if abs(par.loc[n, m] / F_WH - 1) <= 0.10) + ".",
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
fig.suptitle(f"Stage 3 baseline loop (H = 12 m, W = 8 m): in-plane modes, ANSYS ELBOW290 ({T} ovalisation terms)",
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
# ovalisation-term convergence
if len(four) > 2:
    fig, ax = plt.subplots(figsize=(9, 4.4), dpi=200)
    for m, col in zip([1, 2, 3], [C["blue"], C["orange"], C["green"]]):
        ax.plot(four.index, four[m], "-o", color=col, lw=2, ms=7, label=f"mode {m}")
        ax.axhline(py.loc[1][m], color=col, ls=":", lw=1)
    ax.axhline(F_WH, color=C["muted"], ls="--", lw=1)
    ax.text(8, F_WH + 0.05, "water hammer 2.75 Hz", ha="right", fontsize=9, color=C["muted"])
    fig.text(0.01, 0.01, "Dotted lines: Python frame model with B31.3 flexibility factor k = 20.", fontsize=9, color=C["muted"])
    ax.set_xlabel("ELBOW290 ovalisation terms, KEYOPT(2)"); ax.set_ylabel("Natural frequency (Hz)")
    ax.set_xticks(list(four.index)); ax.grid(axis="y", color=C["grid"])
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1))
    ax.set_ylim(1.0, 3.9)
    ax.set_title("Stage 3: bend ovalisation must be converged (default 2 terms is too stiff)",
                 loc="left", fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(os.path.join(FIG, "stage3_fourier_convergence.png"))
print("figures written to", os.path.abspath(FIG))
