"""
MECH0074 CW1 - Stage 3 independent check: 2D frame FE of the expansion loop.

Same geometry, supports and LNG mass as ansys/stage3_loop_modal.inp, but
built from simple 2D Euler-Bernoulli frame elements (axial + in-plane
bending). Bend flexibility from ovalisation is represented with the
ASME B31.3 flexibility factor k = 1.65/h, h = t*R/r^2 (bend EI divided
by k); k = 1 reproduces a stiff, non-ovalising bend (ANSYS BENDEL = 0).

Run:  python stage3_loop_beam_check.py   -> results/stage3_beam_check.csv
"""
import os
import numpy as np
import scipy.linalg as sl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results")

Do, Di, E = 0.813, 0.79394, 213.233e9
rho_s, rho_f = 8000.0, 455.0
R, LTOT, GSPC = 1.4, 100.0, 12.0
t = (Do - Di) / 2
A = np.pi / 4 * (Do**2 - Di**2)
I = np.pi / 64 * (Do**4 - Di**4)
m = rho_s * A + rho_f * np.pi / 4 * Di**2          # kg/m, steel + LNG
r2 = (Do - t) / 2                                   # mean radius
k_B313 = 1.65 / (t * R / r2**2)                     # ~19.9


def geometry(H, W, esz, nb):
    """Node list along the line, plus a flag for elements inside bends."""
    drnd = 4 * (2 * R - np.pi * R / 2)
    Lin = (LTOT - 2 * H - W + drnd) / 2
    pts, inbend = [np.array([0.0, 0.0])], []

    def straight(p0, p1):
        n = max(1, int(round(np.linalg.norm(p1 - p0) / esz)))
        for i in range(1, n + 1):
            pts.append(p0 + (p1 - p0) * i / n)
            inbend.append(False)

    def arc(c, a0, a1):
        for i in range(1, nb + 1):
            a = a0 + (a1 - a0) * i / nb
            pts.append(c + R * np.array([np.cos(a), np.sin(a)]))
            inbend.append(True)

    h = np.pi / 2
    straight(pts[-1], np.array([Lin - R, 0]))
    arc(np.array([Lin - R, R]), -h, 0)
    straight(pts[-1], np.array([Lin, H - R]))
    arc(np.array([Lin + R, H - R]), np.pi, h)
    straight(pts[-1], np.array([Lin + W - R, H]))
    arc(np.array([Lin + W - R, H - R]), h, 0)
    straight(pts[-1], np.array([Lin + W, R]))
    arc(np.array([Lin + W + R, R]), np.pi, 3 * h)
    straight(pts[-1], np.array([2 * Lin + W, 0]))
    return np.array(pts), np.array(inbend), Lin


def modes(H, W, GD, kflex, esz=0.25, nb=8, nmode=6, full=False):
    X, inbend, Lin = geometry(H, W, esz, nb)
    n = len(X)
    K = np.zeros((3 * n, 3 * n))
    M = np.zeros((3 * n, 3 * n))
    for e in range(n - 1):
        d = X[e + 1] - X[e]
        L = np.linalg.norm(d)
        c, s = d / L
        EI = E * I / (kflex if inbend[e] else 1.0)
        a, b = E * A / L, EI / L**3
        k = np.array([[a, 0, 0, -a, 0, 0],
                      [0, 12*b, 6*b*L, 0, -12*b, 6*b*L],
                      [0, 6*b*L, 4*b*L*L, 0, -6*b*L, 2*b*L*L],
                      [-a, 0, 0, a, 0, 0],
                      [0, -12*b, -6*b*L, 0, 12*b, -6*b*L],
                      [0, 6*b*L, 2*b*L*L, 0, -6*b*L, 4*b*L*L]])
        q = m * L / 420
        mm = q * np.array([[140, 0, 0, 70, 0, 0],
                           [0, 156, 22*L, 0, 54, -13*L],
                           [0, 22*L, 4*L*L, 0, 13*L, -3*L*L],
                           [70, 0, 0, 140, 0, 0],
                           [0, 54, 13*L, 0, 156, -22*L],
                           [0, -13*L, -3*L*L, 0, -22*L, 4*L*L]])
        T = np.zeros((6, 6))
        for j in (0, 3):
            T[j:j+2, j:j+2] = [[c, s], [-s, c]]
            T[j+2, j+2] = 1
        idx = np.r_[3*e:3*e+6]
        K[np.ix_(idx, idx)] += T.T @ k @ T
        M[np.ix_(idx, idx)] += T.T @ mm @ T
    fixed = [0, 1, 2, 3*(n-1), 3*(n-1)+1, 3*(n-1)+2]      # anchors
    if GD > 0:                                             # guides: UY = 0
        xend = 2 * Lin + W
        for kg in range(21):
            xg = Lin - R - GD - kg * GSPC
            if xg < 1:
                break
            for xt in (xg, xend - xg):
                j = np.argmin(np.hypot(X[:, 0] - xt, X[:, 1]))
                fixed.append(3 * j + 1)
    free = np.setdiff1d(np.arange(3 * n), fixed)
    w2, v = sl.eigh(K[np.ix_(free, free)], M[np.ix_(free, free)],
                    subset_by_index=[0, nmode - 1])
    f = np.sqrt(w2) / (2 * np.pi)
    if not full:
        return f
    phi = np.zeros((3 * n, nmode))
    phi[free] = v
    return f, phi, X


if __name__ == "__main__":
    cases = [(1, 12, 8, 6, k_B313), (2, 8, 8, 6, k_B313), (3, 16, 8, 6, k_B313),
             (4, 12, 4, 6, k_B313), (5, 12, 12, 6, k_B313),
             (6, 12, 8, 3, k_B313), (7, 12, 8, 12, k_B313), (8, 12, 8, -1, k_B313),
             (9, 12, 8, 6, 1.0)]
    rows = ["case,H_m,W_m,guide_dist_m,flex_factor,mode,freq_Hz"]
    print(f"B31.3 flexibility factor k = {k_B313:.1f}")
    for cid, H, W, GD, kf in cases:
        f = modes(H, W, GD, kf)
        print(f"case {cid:2d} H={H:>2} W={W:>2} GD={GD:>3} k={kf:4.1f}: " +
              " ".join(f"{x:6.2f}" for x in f))
        rows += [f"{cid},{H},{W},{GD},{kf:.2f},{i+1},{x:.5f}" for i, x in enumerate(f)]
    f1 = modes(12, 8, 6, k_B313, esz=0.125, nb=16)
    print("baseline, finer mesh:      " + " ".join(f"{x:6.2f}" for x in f1))
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "stage3_beam_check.csv"), "w").write("\n".join(rows) + "\n")

    # provisional baseline mode shapes (plan view)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    f, phi, X = modes(12, 8, 6, k_B313, full=True)
    fig, axs = plt.subplots(2, 3, figsize=(12, 6.2), dpi=200, sharex=True, sharey=True)
    for i, ax in enumerate(axs.flat):
        u = phi[0::3, i]; v = phi[1::3, i]
        s_ = 3.0 / np.max(np.hypot(u, v))
        ax.plot(X[:, 0], X[:, 1], color="#b8b7b2", lw=1.5)
        ax.plot(X[:, 0] + s_ * u, X[:, 1] + s_ * v, color="#2a78d6", lw=2)
        ax.set_title(f"Mode {i+1}: {f[i]:.2f} Hz", loc="left", fontsize=11)
        ax.set_aspect("equal"); ax.set_ylim(-5, 17)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    fig.suptitle("Stage 3 baseline loop (H = 12 m, W = 8 m), in-plane modes - Python frame model, B31.3 k = 20 (provisional)",
                 x=0.01, ha="left", fontsize=11)
    fig.supxlabel("x (m)"); fig.supylabel("y (m)")
    fig.tight_layout()
    os.makedirs(os.path.join(HERE, "..", "figures"), exist_ok=True)
    fig.savefig(os.path.join(HERE, "..", "figures", "stage3_python_modes_baseline.png"))
