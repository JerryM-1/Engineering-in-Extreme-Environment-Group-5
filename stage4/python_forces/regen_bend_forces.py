"""Regenerate Stage 4 bend-force histories with the Stage 1 MOC solver and check them
against the tables embedded in Jerry's ANSYS scripts (run: python regen_bend_forces.py)."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from moc_solver import simulate_water_hammer
g=9.81; p_atm=101325.0; p0=700000.0; L=100.0; D=0.79394; c=1100.0; rho=455.0; u0=1.5
A=np.pi*D**2/4
S=[34.9013,46.3004,53.6996,65.0987]
DIR={'B1':(1,-1),'B2':(-1,1),'B3':(1,1),'B4':(-1,-1)}   # (e1-e2) components, unnormalised
def forces(tc, tend=2.0, nre=400, interp='linear'):
    r=simulate_water_hammer(length=L,diameter=D,wave_speed=c,density=rho,initial_velocity=u0,
        closure_time=tc,friction_factor=0.0,reservoir_head=(p0-p_atm)/(rho*g),n_reaches=nre,simulation_time=tend+0.01)
    x,t,H,Q=r['x'],r['time'],r['H'],r['Q']
    out={}
    for i,s in enumerate(S):
        if interp=='linear':
            j=int(np.floor(s/r['dx'])); w=(s-x[j])/r['dx']
            h=(1-w)*H[:,j]+w*H[:,j+1]; q=(1-w)*Q[:,j]+w*Q[:,j+1]
        else:
            j=int(np.argmin(abs(x-s))); h=H[:,j]; q=Q[:,j]
        C=rho*g*h*A+rho*q**2/A
        out[f'B{i+1}']=(t,C)
    ts=np.round(np.arange(0,tend+1e-9,0.001),6)
    df=pd.DataFrame({'t':ts})
    for b,(t,C) in out.items():
        Ci=np.interp(ts,t,C); ex,ey=DIR[b]
        df[b+'X']=ex*Ci; df[b+'Y']=ey*Ci
    return df
if __name__=='__main__':
    j002=pd.read_csv(os.path.join(HERE, 'jerry_tables', 'tab_0p02_total.csv'))
    j050=pd.read_csv(os.path.join(HERE, 'jerry_tables', 'tab_0p50_incr.csv'))
    j002['t']=(j002['t']-1).round(6)
    cols=[c for c in j002.columns if c!='t']
    for interp in ('linear','nearest'):
        m=forces(0.02,interp=interp)
        print(interp,'0.02 total: max abs diff (N)',(m[cols]-j002[cols].values).abs().max().max(),
              ' peak',j002[cols].abs().max().max())
        m5=forces(0.5,interp=interp); base=m5.iloc[0][cols]
        inc=m5[cols]-base
        print(interp,'0.50 incr : max abs diff (N)',(inc-j050[cols].values).abs().max().max(),
              ' peak',j050[cols].abs().max().max())
