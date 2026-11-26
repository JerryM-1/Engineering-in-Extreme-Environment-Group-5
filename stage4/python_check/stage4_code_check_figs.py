"""Stage 4 code-check figures (B31.3 bend stress). Run from anywhere:
    python stage4/python_check/stage4_code_check_figs.py
Reads the v2/v3 ANSYS result folders and writes figures/ + results table."""
import os, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S4=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG=os.path.join(S4,'figures')
BLUE,ORANGE,RED,INK,INK2='#257de0','#f47230','#dc3c3d','#191919','#666666'
plt.rcParams.update({'font.size':11,'axes.edgecolor':INK2,'axes.labelcolor':INK,'xtick.color':INK2,
    'ytick.color':INK2,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,
    'grid.color':'#e6e6e6','grid.linewidth':0.8})
def hist(d): return pd.read_csv(os.path.join(S4,d,'stage4_msup_history.csv'),skipinitialspace=True)
def tsum(d):
    L=open(os.path.join(S4,d,'stage4_thermal_summary.csv')).read().split('\n'); return [float(x) for x in L[5].split(',')]
def nom(d):
    e=pd.read_csv(os.path.join(S4,d,'stage4_thermal_nominal_stress.csv'),skipinitialspace=True); return e
SH=138e6; OCC=1.33*SH; SA=1.25*SH+0.25*SH
D=0.813; Di=0.79394; A=np.pi/4*(D**2-Di**2); I=np.pi/64*(D**4-Di**4)

h50=hist('closure_0p50s_msup_v2'); h12=hist('loop_width_12m_0p02s_v2')
th8=tsum('thermal_v3_W8'); th12=tsum('thermal_v3_W12'); SIF=th8[2]
# thermal bend stress at the element where the 0.50 s total peaks (from summary)
s50=open(os.path.join(S4,'closure_0p50s_msup_v2','stage4_msup_summary.csv')).read().split('\n')
pk=[float(x) for x in s50[5].split(',')]; epk=int(pk[2])
e=nom('thermal_v3_W8').set_index('element').loc[float(epk)]
th_at=max(abs(e.N_I_N)/A+SIF*D/2*np.hypot(e.My_I_Nm,e.Mz_I_Nm)/I, abs(e.N_J_N)/A+SIF*D/2*np.hypot(e.My_J_Nm,e.Mz_J_Nm)/I)
occ50=pk[0]-th_at

# ---- figure 1: bend stress histories ----
fig,ax=plt.subplots(1,2,figsize=(13,4.6))
for a,h,col,ttl,thv in ((ax[0],h50,BLUE,'W = 8 m, 0.50 s closure (recommended)',th_at),
                        (ax[1],h12,ORANGE,'W = 12 m, 0.02 s closure (resonant)',th12[0])):
    a.plot(h.valve_t_s,h.Sbend_SIF_total_Pa/1e6,color=col,lw=2)
    lim=(OCC+thv)/1e6
    a.axhline(lim,color=RED,ls='--',lw=1.5,label=f'occasional limit 184 MPa + thermal share {thv/1e6:.0f} MPa')
    a.axhline(h.Sbend_SIF_total_Pa.iloc[0]/1e6,color=INK2,ls=':',lw=1.2,label='before closure (thermal + pressure)')
    a.legend(loc='upper left',frameon=False,fontsize=9.5)
    a.set_title(ttl,fontsize=11.5,color=INK,loc='left'); a.set_xlabel('time after closure starts (s)')
    a.set_xlim(0,2); a.set_ylim(0,max(h.Sbend_SIF_total_Pa.max()/1e6,lim)*1.3)
ax[0].set_ylabel('peak bend stress with B31.3 SIF (MPa)')
i=h50.Sbend_SIF_total_Pa.idxmax(); ax[0].annotate(f'peak {pk[0]/1e6:.0f} MPa',(h50.valve_t_s[i],pk[0]/1e6),
    xytext=(-22,-4),textcoords='offset points',ha='right',va='center',color=INK,fontsize=10,arrowprops=dict(arrowstyle='-',color=INK2))
j=h12.Sbend_SIF_total_Pa.idxmax(); ax[1].annotate(f'{h12.Sbend_SIF_total_Pa.max()/1e6:.0f} MPa, still growing',
    (h12.valve_t_s[j],h12.Sbend_SIF_total_Pa.max()/1e6),xytext=(-170,-10),textcoords='offset points',color=INK,fontsize=10,
    arrowprops=dict(arrowstyle='-',color=INK2))
fig.suptitle(f'Bend stress (thermal + pressure + water hammer), i = {SIF:.2f}',x=0.01,ha='left',fontsize=12.5,color=INK)
fig.tight_layout(); fig.savefig(os.path.join(FIG,'stage4_bend_stress_history.png'),dpi=200); plt.close(fig)

# ---- figure 2: utilisation ----
nomsum=lambda d: float(open(os.path.join(S4,d,'stage4_msup_summary.csv')).read().split('\n')[1].split(',')[3])
rows=[('Thermal, W = 8 m','Thermal vs S_A',th8[0]/SA,False),
      ('Thermal, W = 12 m','Thermal vs S_A',th12[0]/SA,False),
      ('Water hammer 0.50 s, W = 8 m','Occasional vs 1.33 S_h',occ50/OCC,False),
      ('Water hammer 0.10 s, W = 8 m','Occasional vs 1.33 S_h',(378.91e6-th8[0]/SIF)/OCC,True),
      ('Water hammer 0.02 s, W = 8 m','Occasional vs 1.33 S_h',(437.48e6-th8[0]/SIF)/OCC,True),
      ('Water hammer 0.02 s, W = 12 m','Occasional vs 1.33 S_h',(nomsum('loop_width_12m_0p02s_v2')-th12[0]/SIF)/OCC,True)]
fig,a=plt.subplots(figsize=(10,4.8)); a.grid(axis='y',visible=False)
for k,(lab,kind,u,lb) in enumerate(rows):
    col=BLUE if kind.startswith('Thermal') else ORANGE
    a.barh(k,u*100,color=col,height=0.62,hatch='//' if lb else None,edgecolor='white',linewidth=0)
    txt=(f'≥ {u*100:.0f} %  FAIL*' if lb else f'{u*100:.0f} %  '+('PASS' if u<=1 else 'FAIL'))
    a.text(u*100+6,k,txt,va='center',color=INK,fontsize=10)
a.axvline(100,color=RED,ls='--',lw=1.5); a.text(101,-0.75,'code limit',color=INK,fontsize=9.5)
a.set_yticks(range(len(rows)),[r[0] for r in rows]); a.invert_yaxis()
a.set_xlabel('utilisation of the ASME B31.3 allowable (%)'); a.set_xlim(0,max(r[2] for r in rows)*100*1.3)
from matplotlib.patches import Patch
a.legend(handles=[Patch(color=BLUE,label='thermal expansion vs S_A = 207 MPa'),Patch(color=ORANGE,label='water hammer vs 1.33 S_h = 184 MPa')],
    loc='upper right',frameon=False,fontsize=9.5)
fig.text(0.01,0.01,'* hatched: nominal stress (no SIF) minus thermal share, so a lower bound; already above the limit.',color=INK2,fontsize=9)
fig.tight_layout(rect=(0,0.04,1,1)); fig.savefig(os.path.join(FIG,'stage4_code_check_utilisation.png'),dpi=200); plt.close(fig)

pd.DataFrame([dict(case=r[0],check=r[1],utilisation_pct=round(r[2]*100,1),lower_bound=r[3]) for r in rows]).to_csv(
    os.path.join(FIG,'stage4_code_check_utilisation.csv'),index=False)
print('SIF',SIF,'thermal at peak elem',epk,th_at/1e6,'occ50',occ50/1e6, [round(r[2]*100,1) for r in rows])
