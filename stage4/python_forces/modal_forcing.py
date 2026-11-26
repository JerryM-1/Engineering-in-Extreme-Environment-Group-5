"""Stage 4: modal forcing vs natural frequencies (brief: 'compare modal forcing with the natural frequencies').
Generalised force on mode m:  Q_m(t) = sum_b  phi_b . F_b(t)  using bend-midpoint mode shapes (Stage 3 v5)
and the incremental bend forces from the Stage 1 MOC solver. Spectrum from a 10 s record."""
import os, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from regen_bend_forces import forces
MS=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'..','..','stage3_loop','results','v5','stage3_modeshapes_at_bends.csv')
OUT=sys.argv[2] if len(sys.argv)>2 else os.path.join(HERE,'..','figures')
os.makedirs(OUT,exist_ok=True)
ms=pd.read_csv(MS,skipinitialspace=True); ms.columns=[c.strip() for c in ms.columns]
ms[['mode','bend']]=ms[['mode','bend']].astype(int)
freq=ms.groupby('mode')['freq_Hz'].first()
cols=['B1X','B1Y','B2X','B2Y','B3X','B3Y','B4X','B4Y']
C={"blue":"#2a78d6","orange":"#eb6834","green":"#1baf7a","muted":"#52514e","grid":"#e5e4e0"}
plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False})
rows=[]
fig,axs=plt.subplots(1,2,figsize=(12,4.4),dpi=200,sharey=True)
for ax,tc in zip(axs,(0.02,0.50)):
    df=forces(tc,tend=10.0); inc=df[cols]-df.iloc[0][cols]; t=df['t'].values; dt=t[1]-t[0]
    for m,col in zip([1,2,3],[C["blue"],C["orange"],C["green"]]):
        q=np.zeros(len(t))
        for b in range(1,5):
            r=ms[(ms['mode']==m)&(ms['bend']==b)].iloc[0]
            q+=r['UX']*inc[f'B{b}X'].values+r['UY']*inc[f'B{b}Y'].values
        Qf=np.abs(np.fft.rfft(q))*2/len(q); f=np.fft.rfftfreq(len(q),dt)
        ax.plot(f,Qf,color=col,lw=1.6,label=f"mode {m} ({freq[m]:.2f} Hz)")
        ax.axvline(freq[m],color=col,ls=":",lw=1.2)
        k=np.argmin(abs(f-freq[m])); kw=np.argmin(abs(f-2.75))
        rows.append(dict(closure_s=tc,mode=m,f_n_Hz=round(freq[m],3),peak_Q=q.__abs__().max(),
                         Q_amp_at_fn=Qf[k],Q_amp_at_2p75Hz=Qf[kw]))
    for h in (2.75,8.25,13.75): ax.axvline(h,color=C["muted"],ls="--",lw=0.8)
    ax.set_xlim(0,16); ax.set_xlabel("Frequency (Hz)"); ax.grid(axis="y",color=C["grid"])
    ax.set_title(f"Closure {tc:.2f} s",loc="left",fontsize=11)
axs[0].set_ylabel("Modal force amplitude (mass-normalised)")
axs[0].text(2.85,axs[0].get_ylim()[1]*0.95,"2.75 Hz = c/4L",fontsize=9,color=C["muted"],va="top")
axs[1].legend(frameon=False,loc="upper right")
fig.suptitle("Stage 4: modal forcing vs natural frequencies  (dashed = 2.75 Hz and odd harmonics, dotted = loop modes 1-3)",x=0.01,ha="left",fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"stage4_modal_forcing.png"))
pd.DataFrame(rows).to_csv(os.path.join(OUT,"stage4_modal_forcing.csv"),index=False)
print(pd.DataFrame(rows).round(3).to_string(index=False))
