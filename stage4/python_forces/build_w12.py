"""Build W=12 m Stage 4 inputs: (1) 0.02 s MSUP transient with forces at the shifted bend
stations, (2) cooldown thermal cases for W=8 and W=12 with the B31.3 bend SIF stress."""
import os, re, sys, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0,HERE)
OUT=os.path.join(ROOT,'scripts')
import regen_bend_forces as rb
R=1.4; L=100.0; H=12.0; PI=np.pi
def geom(W):
    drnd=4*(2*R-PI*R/2); lin=(L-2*H-W+drnd)/2; q=PI*R/4
    s1=lin-R+q; s2=s1+2*q+(H-2*R); s3=s2+2*q+(W-2*R); s4=s3+2*q+(H-2*R)
    d=R/np.sqrt(2)
    mids=[(lin-R+d,R-d),(lin+R-d,H-R+d),(lin+W-R+d,H-R+d),(lin+W+R-d,R-d)]
    return lin,[s1,s2,s3,s4],mids
lin8,S8,M8=geom(8); print('W=8 check',np.round(S8,4),np.round(M8,4))
lin12,S12,M12=geom(12); print('W=12',round(lin12,4),np.round(S12,4),np.round(M12,4))

# ---------- (1) transient ----------
tpl=open(os.path.join(OUT,'stage4_closure_0p02_v2.inp'),newline='').read().replace('\r\n','\n')
assert tpl.count('\nWL=8\n')==1
tpl=tpl.replace('\nWL=8\n','\nWL=12\n')
for i,(x,y) in enumerate(M8):
    old=[l for l in tpl.split('\n') if l.startswith(f'BNODE({i+1})=NODE(')]
    assert len(old)==1
    x2,y2=M12[i]
    tpl=tpl.replace(old[0],f'BNODE({i+1})=NODE({x2:.8f},{y2:.8f},0)')
rb.S=S12
df=rb.forces(0.02); cols=['B1X','B1Y','B2X','B2Y','B3X','B3Y','B4X','B4Y']
inc=df[cols]-df.iloc[0][cols]
print('W12 preload per comp',df.iloc[0][cols].values[:2])
line_re=re.compile(r'^(B[1-4][XY])\((\d+),([01])\)=.*$')
out=[]
for line in tpl.split('\n'):
    m=line_re.match(line)
    if m:
        k,i,j=m.group(1),int(m.group(2)),int(m.group(3))
        if i>=1:
            v=df['t'].iloc[i-1] if j==0 else inc[k].iloc[i-1]
            line=f'{k}({i},{j})={v:.12e}'
    out.append(line)
lines=out
assert lines[0].startswith('! Stage 4 closure comparison')
hdr=['! Stage 4 modification: loop width W=12 m (H=12 m), Tc=0.02 s, duration 2.000 s (v2).',
 '! Same as stage4_closure_0p02_v2.inp except WL=12, bend load nodes at the W=12 midpoints,',
 f'! and MOC bend forces taken at the shifted stations s = {S12[0]:.3f}, {S12[1]:.3f}, {S12[2]:.3f}, {S12[3]:.3f} m.',
 '! Reproduces Jerry\'s loop_width_12m_0p02s run (reproducible input) and adds the B31.3 bend SIF stress.']
k=0
while lines[k].startswith('!'): k+=1
s='\n'.join(hdr+lines[k:])
open(os.path.join(OUT,'stage4_loop_width_12m_0p02_v2.inp'),'w',newline='').write(s.replace('\n','\r\n'))

# ---------- (2) thermal ----------
th=open(os.path.join(ROOT,'thermal','stage4_loop_response_v2.inp'),newline='').read().replace('\r\n','\n')
add_sif='''! ---- v3 addition: B31.3 in-plane SIF stress on the bend elements ----
*GET,EMAXID,ELEM,0,NUM,MAX
*DIM,ISB,ARRAY,EMAXID
LSEL,S,LINE,,NLST+1,NLST+4
ESLL,S
*GET,NEB,ELEM,0,COUNT
EE=0
*DO,JJ,1,NEB
  EE=ELNEXT(EE)
  ISB(EE)=1
*ENDDO
ALLSEL,ALL
HFLEX=TWALL*RBEND/((DOUT-TWALL)/2)**2
SIFI=0.9/HFLEX**(2/3)
SBPK=0
EPKB=0
*GET,NELEM,ELEM,0,COUNT
'''
old='*GET,NELEM,ELEM,0,COUNT\n*CFOPEN,stage4_thermal_nominal_stress,csv'
assert th.count(old)==1
th=th.replace(old,add_sif+'*CFOPEN,stage4_thermal_nominal_stress,csv')
old='''    SMAX=SNOM
    EMAX=EE
  *ENDIF
'''
assert th.count(old)==1
th=th.replace(old,old+'''  IBND=ISB(EE)
  *IF,IBND,EQ,1,THEN
    SBI=ABS(NI)/ASTL+SIFI*DOUT/2*SQRT(MY1**2+MZ1**2)/IZZ
    SBJ=ABS(NJ)/ASTL+SIFI*DOUT/2*SQRT(MY2**2+MZ2**2)/IZZ
    SBV=MAX(SBI,SBJ)
    *IF,SBV,GT,SBPK,THEN
      SBPK=SBV
      EPKB=EE
    *ENDIF
  *ENDIF
''')
old='''*VWRITE,FREEAX,SUMFX,SUMFY,SUMMZ
(E20.12,3(',',E20.12))
*CFCLOS'''
assert th.count(old)==1
th=th.replace(old,'''*VWRITE,FREEAX,SUMFX,SUMFY,SUMMZ
(E20.12,3(',',E20.12))
*VWRITE
('peak_bend_SIF_Pa,element,SIF_inplane,loop_width_m')
*VWRITE,SBPK,EPKB,SIFI,WL
(E20.12,',',F9.0,',',E20.12,',',E20.12)
*CFCLOS''')
assert th.count('\nWL=8\n')==1
for W in (8,12):
    t=th.replace('\nWL=8\n',f'\nWL={W}\n').replace('/TITLE,Stage 4 baseline cooldown 293 K to 111 K',f'/TITLE,Stage 4 cooldown 293 K to 111 K, loop width {W} m')
    t=t.replace('SAVE,stage4_cooldown_v2,db',f'SAVE,stage4_cooldown_W{W},db')
    t=t.replace('! MECH0074 Stage 4 - baseline cooldown only, revision 2',
      f'! MECH0074 Stage 4 - cooldown only, loop width W={W} m, revision 3\n! v3 adds peak_bend_SIF_Pa (B31.3 in-plane SIF on bend-element bending) to the summary.')
    open(os.path.join(OUT,f'stage4_thermal_W{W}_v3.inp'),'w',newline='').write(t.replace('\n','\r\n'))
print('done')
