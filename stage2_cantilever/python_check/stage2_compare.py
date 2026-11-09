"""
MECH0074 CW1 - Stage 2 independent check and figures.

Reads the ANSYS results (results/stage2_results_ansys.csv, written by
ansys/stage2_cantilever.inp), computes an independent Timoshenko beam
finite-element solution (shear deformation + rotary inertia, 400 elements,
Cowper shear coefficient for a thin tube, and k = 0.5 for sensitivity), and writes:
  results/stage2_timoshenko.csv   independent beam-FE frequencies
  results/stage2_summary_table.csv  EB vs Timoshenko vs ANSYS (filled, 80 el.)
  figures/stage2_fem_vs_theory.png
  figures/stage2_mesh_convergence.png

Run:  python stage2_compare.py     (needs numpy, scipy, pandas, matplotlib)
Same inputs/assumptions as the ANSYS model: effective density for LNG mass,
nu = 0.3, E = 213.233 GPa, in-plane bending only.
"""
import os
HERE=os.path.dirname(os.path.abspath(__file__))
RES=os.path.join(HERE,'..','results'); FIG=os.path.join(HERE,'..','figures')
import numpy as np, scipy.linalg as sl, pandas as pd
Do,Di,E,nu=0.813,0.79394,213.233e9,0.3
As=np.pi/4*(Do**2-Di**2);I=np.pi/64*(Do**4-Di**4);G=E/(2*(1+nu))
ms=8000*As;mf=455*np.pi/4*Di**2
def timo(L,m,rhoI,k,n=400):
    le=L/n;phi=12*E*I/(k*G*As*le**2)
    c=E*I/((1+phi)*le**3)
    Ke=c*np.array([[12,6*le,-12,6*le],[6*le,(4+phi)*le**2,-6*le,(2-phi)*le**2],[-12,-6*le,12,-6*le],[6*le,(2-phi)*le**2,-6*le,(4+phi)*le**2]])
    Mt=m*le/420*np.array([[156,22*le,54,-13*le],[22*le,4*le**2,13*le,-3*le**2],[54,13*le,156,-22*le],[-13*le,-3*le**2,-22*le,4*le**2]])
    Mr=rhoI/(30*le)*np.array([[36,3*le,-36,3*le],[3*le,4*le**2,-3*le,-le**2],[-36,-3*le,36,-3*le],[3*le,-le**2,-3*le,4*le**2]])
    N=2*(n+1);K=np.zeros((N,N));M=np.zeros((N,N))
    for e in range(n):
        s=slice(2*e,2*e+4);K[s,s]+=Ke;M[s,s]+=Mt+Mr
    K=K[2:,2:];M=M[2:,2:]
    w=sl.eigh(K,M,eigvals_only=True,subset_by_index=[0,5])
    return np.sqrt(w)/(2*np.pi)
rows=[]
for filled in (0,1):
    m=ms+mf*filled; rho=m/As
    for L in (4,10,20):
        fa=timo(L,m,rho*I,0.5)
        fb=timo(L,m,rho*I,2*(1+nu)/(4+3*nu))
        for i in range(6): rows.append((filled,L,i+1,fa[i],fb[i]))
pd.DataFrame(rows,columns=['filled','L_m','mode','f_timo_k050','f_timo_cowper']).to_csv(os.path.join(RES,'stage2_timoshenko.csv'),index=False)

# ---------------- figures and table ----------------
import pandas as pd, numpy as np, matplotlib
import matplotlib.ticker
matplotlib.use('Agg'); import matplotlib.pyplot as plt
a=pd.read_csv(os.path.join(RES,'stage2_results_ansys.csv'),skipinitialspace=True)
a.columns=[c.strip() for c in a.columns]; t=pd.read_csv(os.path.join(RES,'stage2_timoshenko.csv'))
C={4:'#2a78d6',10:'#eb6834',20:'#1baf7a'}
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#52514e','axes.labelcolor':'#0b0b0b','xtick.color':'#52514e','ytick.color':'#52514e'})
f=a[(a.filled==1)&(a.n_elem==80)].merge(t[t.filled==1],on=['filled','L_m','mode'])
fig,ax=plt.subplots(figsize=(9,5.2),dpi=200); fig.patch.set_facecolor('white')
for L in (4,10,20):
    d=f[f.L_m==L]
    ax.plot(d['mode'],d.f_FEM_Hz/d.f_EB_Hz,'-o',color=C[L],lw=2,ms=8,label=f'ANSYS PIPE289, L = {L} m')
    ax.plot(d['mode'],d.f_timo_cowper/d.f_EB_Hz,'--s',color=C[L],lw=2,ms=6,mfc='white',label=f'Timoshenko beam, L = {L} m')
ax.axhline(1,color='#52514e',lw=1); ax.text(6.0,1.012,'Euler–Bernoulli',va='bottom',ha='right',fontsize=10,color='#52514e')
ax.set_xlabel('Bending mode number'); ax.set_ylabel('f / f$_{Euler–Bernoulli}$ (–)')
ax.set_title('Stage 2: LNG-filled cantilever, FEM vs beam theory',loc='left',fontsize=13)
ax.grid(axis='y',color='#e5e4e0',lw=0.8); ax.set_xticks(range(1,7)); ax.set_xlim(0.8,6.9)
ax.legend(frameon=False,fontsize=9,ncol=2,loc='lower left')
fig.tight_layout(); fig.savefig(os.path.join(FIG,'stage2_fem_vs_theory.png'))
fig,ax=plt.subplots(figsize=(9,5.2),dpi=200)
for L in (4,10,20):
    d=a[(a.filled==1)&(a.L_m==L)&(a['mode']==6)].sort_values('n_elem')
    ref=d.f_FEM_Hz.iloc[-1]; d=d.iloc[:-1]
    ax.plot(d.n_elem,100*abs(d.f_FEM_Hz-ref)/ref,'-o',color=C[L],lw=2,ms=8,label=f'L = {L} m')
    ax.text(d.n_elem.iloc[-1]*1.08,100*abs(d.f_FEM_Hz.iloc[-1]-ref)/ref,f'{L} m',color='#0b0b0b',va='center',fontsize=10)
ax.axhline(0.1,color='#52514e',lw=1,ls=':'); ax.text(5.2,0.12,'0.1 % tolerance',fontsize=10,color='#52514e')
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xticks([5,10,20,40]); ax.set_xticklabels(['5','10','20','40']); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.set_xlabel('Number of PIPE289 elements'); ax.set_ylabel('Mode 6 change vs 80-element mesh (%)')
ax.set_title('Stage 2: mesh convergence (mode 6, LNG-filled)',loc='left',fontsize=13)
ax.grid(color='#e5e4e0',lw=0.8,which='major'); ax.legend(frameon=False,fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(FIG,'stage2_mesh_convergence.png'))
# table
f['L/D']=f.L_m/0.813
tab=f[['L_m','mode','f_EB_Hz','f_timo_cowper','f_FEM_Hz']].copy()
tab['FEM_vs_EB_%']=100*(f.f_FEM_Hz/f.f_EB_Hz-1); tab['FEM_vs_Timo_%']=100*(f.f_FEM_Hz/f.f_timo_cowper-1)
tab['half_wavelength_m']=f.L_m/(f['mode']-0.5)
tab.round(2).to_csv(os.path.join(RES,'stage2_summary_table.csv'),index=False)
r=a[a.n_elem==80].pivot_table(index=['L_m','mode'],columns='filled',values='f_FEM_Hz'); print((r[1]/r[0]).describe())
print(tab.round(2).to_string())
