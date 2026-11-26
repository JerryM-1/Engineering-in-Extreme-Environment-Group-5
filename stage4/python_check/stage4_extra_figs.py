"""Stage 4 explanatory figures (no ANSYS needed). Run from anywhere:
    python stage4/python_check/stage4_extra_figs.py [--no-anim]

1. figures/stage4_frequency_map.png      loop modes vs geometry/guides against the water-hammer band
2. figures/stage4_bend_forcing.png       pressure at the four bends, arrival lags, modal forces
3. figures/stage4_loop_response.mp4/.gif animated loop response, 0.02 s vs 0.50 s closure (W = 8 m)

Inputs: stage3_loop/results/v5/stage3_results.csv, stage4/python_inputs/*,
stage4/python_response/frequencies_and_damping.csv, stage4/python_forces/moc_solver.py.
The animation is a 12-mode superposition of the ANSYS mode shapes; its bend displacements are
checked against Jerry's Python response (python_response/response_tc_*.csv) and printed.
"""
import os, sys
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation

S4 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(S4)
FIG = os.path.join(S4, 'figures')
sys.path.insert(0, os.path.join(S4, 'python_forces'))
from moc_solver import simulate_water_hammer

BLUE, ORANGE, AQUA, YELLOW, GREY, RED = '#257de0', '#f47230', '#00b894', '#f2a600', '#9c9c9c', '#dc3c3d'
INK, INK2 = '#191919', '#666666'
plt.rcParams.update({'font.size': 11, 'axes.edgecolor': INK2, 'axes.labelcolor': INK,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.grid': True, 'grid.color': '#e6e6e6',
                     'grid.linewidth': 0.8, 'legend.frameon': False})

# hydraulic inputs (Stage 1 / brief)
g = 9.81; p_atm = 101325.0; p0 = 700000.0; L = 100.0; D = 0.79394; c = 1100.0; rho = 455.0; u0 = 1.5
A = np.pi * D**2 / 4
F_HAM = c / (4 * L)                    # 2.75 Hz
F_HAM_WALL = 998.0 / (4 * L)           # wall-elasticity-corrected wave speed

# ---------------------------------------------------------------- 1. frequency map
r = pd.read_csv(os.path.join(ROOT, 'stage3_loop', 'results', 'v5', 'stage3_results.csv'), skipinitialspace=True)
fr = r.pivot(index='case', columns='mode', values='freq_Hz')
fr.index = fr.index.astype(int)
groups = [('Loop width W (m)', [(4, 4), (8, 1), (12, 5)], 'W = 8 m'),
          ('Loop height H (m)', [(8, 2), (12, 1), (16, 3)], 'H = 12 m'),
          ('First guide distance from loop (m)', [(3, 6), (6, 1), (12, 7)], '6 m')]
fig, axs = plt.subplots(1, 3, figsize=(13.5, 5.0), sharey=True)
for ax, (xl, pts, base) in zip(axs, groups):
    xs = [p[0] for p in pts]
    ax.axhspan(F_HAM_WALL, F_HAM, color=RED, alpha=0.13, lw=0)
    ax.axhline(F_HAM, color=RED, lw=1.2, ls='--')
    for m, col, lab, lw in ((1, GREY, 'mode 1 (sway)', 1.6), (2, BLUE, 'mode 2 (loop opening)', 1.8),
                            (3, ORANGE, 'mode 3 (rocking, driven)', 2.6)):
        ys = [fr.loc[p[1], float(m)] for p in pts]
        ax.plot(xs, ys, '-o', color=col, lw=lw, ms=8, label=lab, markeredgecolor='white', markeredgewidth=1.5)
    bx = [p[0] for p in pts if p[1] == 1][0]
    ax.axvline(bx, color=INK2, lw=0.8, ls=':')
    ax.text(bx, 5.55, ' baseline', color=INK2, fontsize=9.5, va='top')
    ax.set_xlabel(xl); ax.set_xticks(xs); ax.set_ylim(0, 5.6)
axs[0].set_ylabel('natural frequency (Hz)')
axs[0].text(4.1, F_HAM + 0.05, 'water hammer 2.5–2.75 Hz', color=INK, fontsize=9.5, va='bottom')
# annotate the danger points
axs[0].annotate('W = 12 m: mode 3 at 2.77 Hz\n→ resonance (Stage 4 run)', (12, fr.loc[5, 3.0]),
                xytext=(-150, 48), textcoords='offset points', fontsize=9.5, color=INK,
                arrowprops=dict(arrowstyle='-', color=INK2))
axs[1].annotate('H = 16 m: mode 3 at 2.71 Hz', (16, fr.loc[3, 3.0]), xytext=(-150, -52),
                textcoords='offset points', fontsize=9.5, color=INK, arrowprops=dict(arrowstyle='-', color=INK2))
axs[2].annotate('guide at 3 m: modes 2–3\nabove 4.5 Hz, clear of band', (3, fr.loc[6, 2.0]), xytext=(150, 6),
                textcoords='offset points', fontsize=9.5, color=INK, arrowprops=dict(arrowstyle='-', color=INK2))
fig.legend(*axs[0].get_legend_handles_labels(), loc='lower center', ncol=3, fontsize=10, bbox_to_anchor=(0.5, 0.0))
fig.suptitle('Stage 3 parametric study vs the Stage 1 forcing frequency 4L/c (ANSYS ELBOW290, v5)',
             x=0.01, ha='left', fontsize=12.5, color=INK)
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(os.path.join(FIG, 'stage4_frequency_map.png'), dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- 2. bend pressures and modal forces
geo = pd.read_csv(os.path.join(S4, 'python_inputs', 'geometry.csv'), skipinitialspace=True)
S = geo['s_from_reservoir_m'].values


def moc(tc, tend):
    res = simulate_water_hammer(length=L, diameter=D, wave_speed=c, density=rho, initial_velocity=u0,
                                closure_time=tc, friction_factor=0.0, reservoir_head=(p0 - p_atm) / (rho * g),
                                n_reaches=400, simulation_time=tend + 0.01)
    x, t, H, Q = res['x'], res['time'], res['H'], res['Q']
    P = np.zeros((len(t), 4)); C = np.zeros((len(t), 4))
    for i, s in enumerate(S):
        j = int(np.floor(s / res['dx'])); w = (s - x[j]) / res['dx']
        h = (1 - w) * H[:, j] + w * H[:, j + 1]; q = (1 - w) * Q[:, j] + w * Q[:, j + 1]
        P[:, i] = rho * g * h
        C[:, i] = rho * g * h * A + rho * q**2 / A
    return t, P, C


bs = pd.read_csv(os.path.join(S4, 'python_inputs', 'bend_shapes.csv'), skipinitialspace=True)
mfc = bs.pivot(index='mode', columns='bend', values='modal_force_component_per_unit_pA').values  # (12,4)
t, P, C = moc(0.02, 1.0)
dC = C - C[0]
Qm = dC @ mfc[:3].T                         # mfc = sqrt(2)*(phi . e_F) already, per unit pA
cols = [BLUE, ORANGE, AQUA, YELLOW]
fig, axs = plt.subplots(1, 3, figsize=(14, 4.9), gridspec_kw={'width_ratios': [1.25, 0.8, 1.25]})
for i in range(4):
    axs[0].plot(t, P[:, i] / 1e6, color=cols[i], lw=1.6, label=f'bend {i+1} (s = {S[i]:.1f} m)')
    axs[1].plot(t * 1000, P[:, i] / 1e6, color=cols[i], lw=2)
axs[0].set_xlim(0, 1.0); axs[0].set_xlabel('time (s)'); axs[0].set_ylabel('gauge pressure (MPa)')
axs[0].set_title('Pressure at the four bends, 0.02 s closure', loc='left', fontsize=11.5, color=INK)
axs[0].legend(fontsize=9.5, loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2)
axs[1].set_xlim(25, 75); axs[1].set_xlabel('time (ms)')
axs[1].set_title('Zoom: the front reaches each bend\n7–10 ms apart', loc='left', fontsize=11.5, color=INK)
for k, lab in ((2, 'mode 2'), (3, 'mode 3')):
    axs[2].plot(t, Qm[:, k - 1] / 1e3, color=BLUE if k == 2 else ORANGE, lw=1.6 if k == 2 else 2.2,
                label=f'{lab} generalised force')
axs[2].set_xlim(0, 1.0); axs[2].set_xlabel('time (s)'); axs[2].set_ylabel('generalised force (kN/√kg)')
axs[2].set_title('Net forcing on each mode: uniform pressure\ncancels, the lag between bends does not',
                 loc='left', fontsize=11.5, color=INK)
axs[2].legend(fontsize=9.5, loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'stage4_bend_forcing.png'), dpi=200, bbox_inches='tight')
plt.close(fig)
print('peak |Q| mode2, mode3 (0.02 s):', np.abs(Qm[:, 1]).max(), np.abs(Qm[:, 2]).max())

# ---------------------------------------------------------------- 3. animation (modal superposition)
if '--no-anim' in sys.argv:
    sys.exit()
sh = pd.read_csv(os.path.join(S4, 'python_inputs', 'shapes.csv'), skipinitialspace=True)
fd = pd.read_csv(os.path.join(S4, 'python_response', 'frequencies_and_damping.csv'))
NM = 12
nodes = sh[sh['mode'] == 1].sort_values('node')
# order nodes along the pipe: walk the centreline by nearest neighbour from the reservoir anchor
xy = nodes[['x_m', 'y_m']].values
order = [int(np.argmin(np.hypot(xy[:, 0], xy[:, 1])))]
left = set(range(len(xy))) - set(order)
while left:
    last = xy[order[-1]]
    nxt = min(left, key=lambda k: (xy[k, 0] - last[0])**2 + (xy[k, 1] - last[1])**2)
    order.append(nxt); left.remove(nxt)
nid = nodes['node'].values[order]
X0, Y0 = xy[order, 0], xy[order, 1]
PHI = np.zeros((NM, len(nid), 2))
for m in range(1, NM + 1):
    d = sh[sh['mode'] == m].set_index('node').loc[nid]
    PHI[m - 1, :, 0] = d['UX'].values; PHI[m - 1, :, 1] = d['UY'].values
om = 2 * np.pi * fd['frequency_Hz'].values[:NM]; ze = fd['rayleigh_damping_ratio'].values[:NM]
dirs = geo[['force_dir_x', 'force_dir_y']].values
bend_mfc = mfc[:NM]                           # phi . F_hat per unit pA (F_hat unit vector) per bend


def respond(tc, tend=2.0, dt=2.5e-4):
    tt, PP, CC = moc(tc, tend)
    ts = np.arange(0, tend + 1e-12, dt)
    dF = np.column_stack([np.interp(ts, tt, CC[:, i] - CC[0, i]) for i in range(4)])
    f = dF @ bend_mfc.T                        # (nt, NM) modal forces
    q = np.zeros((len(ts), NM))
    from scipy.signal import lsim               # exact for piecewise-linear input
    for m in range(NM):
        w, z = om[m], ze[m]
        _, y, _ = lsim(([1.0], [1.0, 2 * z * w, w**2]), f[:, m], ts)
        q[:, m] = y
    return ts, q


resp = {}
for tc in (0.02, 0.50):
    ts, q = respond(tc)
    U = np.einsum('tm,mnd->tnd', q, PHI)
    umax = np.hypot(U[..., 0], U[..., 1]).max(axis=1)
    jr = pd.read_csv(os.path.join(S4, 'python_response', f'response_tc_{tc:.2f}s.csv'))
    jr = jr[jr.valve_time_s <= 2.0]
    print(f'Tc={tc}: peak |U| this script {umax.max()*1000:.1f} mm, Jerry python (first 2 s) '
          f'{jr.max_incremental_U_m.max()*1000:.1f} mm')
    resp[tc] = (ts, U, umax)

SC = 15.0
fps, dur = 25, 2.0
nfr = int(fps * dur * 4)                       # 4x slow motion: 2 s of response over 8 s of video
fig, axs = plt.subplots(2, 1, figsize=(12, 6.4))
lines, dots, txts = [], [], []
for ax, tc, col in zip(axs, (0.02, 0.50), (ORANGE, BLUE)):
    ax.plot(X0, Y0, color='#d0d0d0', lw=1.2)
    ln, = ax.plot(X0, Y0, color=col, lw=3, solid_capstyle='round')
    ax.plot([0, X0[-1]], [0, 0], 's', color=INK, ms=7)
    gx = [3.8, 15.8, 27.8, 50.6, 62.6, 74.6]
    ax.plot(gx, [-0.9] * 6, '^', color=INK2, ms=7)
    ax.set_xlim(-1.5, 80); ax.set_ylim(-4.5, 17); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(f'{tc:.2f} s valve closure  (W = 8 m loop, displacement x{SC:.0f})', loc='left', fontsize=12, color=INK)
    tx = ax.text(80, 15.5, '', ha='right', fontsize=11, color=INK, family='monospace')
    lines.append(ln); txts.append(tx)
fig.text(0.01, 0.01, '■ anchors   ▲ guides (lateral restraint)   grey: undeformed. 12-mode superposition of the ANSYS modes, '
         '2 % Rayleigh damping, 4× slow motion.', fontsize=9, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1))
peak = {tc: 0.0 for tc in resp}


def draw(i):
    tv = i / nfr * dur
    for k, tc in enumerate((0.02, 0.50)):
        ts, U, umax = resp[tc]
        j = int(round(tv / (ts[1] - ts[0])))
        lines[k].set_data(X0 + SC * U[j, :, 0], Y0 + SC * U[j, :, 1])
        peak[tc] = max(peak[tc], umax[:j + 1].max())
        txts[k].set_text(f't = {tv:4.2f} s   max {umax[j]*1000:5.0f} mm   peak so far {peak[tc]*1000:4.0f} mm')
    return lines + txts


ani = animation.FuncAnimation(fig, draw, frames=nfr + 1, blit=False)
ani.save(os.path.join(FIG, 'stage4_loop_response.mp4'), writer=animation.FFMpegWriter(fps=fps, bitrate=3000), dpi=130)
for tc in peak: peak[tc] = 0.0
ani.save(os.path.join(FIG, 'stage4_loop_response.gif'), writer=animation.PillowWriter(fps=12), dpi=70)
plt.close(fig)
print('animation written')
