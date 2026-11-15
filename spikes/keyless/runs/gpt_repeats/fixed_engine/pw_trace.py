import sys,math,json; sys.path.insert(0,'/w/spikes/keyless')
import grade as Gr, engine as E, constants as C
WHEEL,CL,PIN=sys.argv[1:4]          # named wheel meshing with the barrel, the clutch, the pinion it drives
spec,parts,sup,defs=Gr.load('/s','/w/spikes/keyless/data')
STEP=C.WIND_SENSE*math.radians(C.FREE_RUN_STEP)
def fresh():
    w=Gr.make_world(parts,sup,defs); w.phase(); return w
def deg(x): return round(math.degrees(x),3)
def ov(w,a,b): return w._pen1(w.bodies[a],only={b})
def prewind(w,n=90,stop_at_first=False):
    Gr._set_kind(w,'barrel','driven'); bl=0; first=None; snap_before=None
    for i in range(n):
        s=w.snapshot()
        if not w.step('barrel',dq=STEP):
            bl+=1
            if first is None:
                first=i; snap_before=s
                if stop_at_first: break
    return bl,first,snap_before
orig_pairs=E.World.pairs_ok
def ignoring(pairs):
    def p(self,a,b):
        if {a.name,b.name} in pairs: return False
        return orig_pairs(self,a,b)
    return p
out={}
# 0. rest clearance of the named pair, and whether min_gap exists
w=fresh(); q0={n:b.q for n,b in w.bodies.items()}
out['rest_overlap_barrel_wheel']=ov(w,'barrel',WHEEL)
try:
    out['rest_min_gap_barrel_wheel_mm']=round(w.posed(w.bodies['barrel']).min_gap(w.posed(w.bodies[WHEEL]),0.5),4)
except Exception as e: out['rest_min_gap']='n/a '+str(e)[:60]
# 1. baseline pre-wind
w=fresh(); bl,first,sb=prewind(w,stop_at_first=True)
out['baseline']={'blocked_first_step':first,'barrel_deg_at_stall':deg(sb['barrel'][0]-q0['barrel'])}
w.restore(sb)
out['stall_pose_deg']={n:deg(w.bodies[n].q-q0[n]) for n in w.bodies if abs(w.bodies[n].q-q0[n])>1e-9 and w.bodies[n].dof=='rot'}
out['stall_pose_slide_mm']={n:round(w.bodies[n].q-q0[n],4) for n in w.bodies if abs(w.bodies[n].q-q0[n])>1e-9 and w.bodies[n].dof!='rot'}
# push log of the failing step
LOG=[]; op=E.World.push
def lp(self,b,dmax,only=None,signs=(1.0,-1.0)):
    r=op(self,b,dmax,only,signs); LOG.append((b.name,round(dmax,5),signs,r)); return r
E.World.push=lp
Gr._set_kind(w,'barrel','driven'); ok=w.step('barrel',dq=STEP); E.World.push=op
out['failing_step_ok']=ok
out['failing_step_push_calls_last12']=LOG[-12:]
# 2. raw geometry at the stall pose: barrel advanced one step, nothing resolved
w.restore(sb); w.bodies['barrel'].q+=STEP
out['raw_overlaps_after_barrel_step']={f'{a}<->{b}':round(ov(w,a,b),5) for a,b in [('barrel',WHEEL),(WHEEL,PIN),(PIN,CL)] }
wq=w.bodies[WHEEL].q; scan=[]
for k in range(-40,41):
    w.bodies[WHEEL].q=wq+math.radians(0.25*k); scan.append((0.25*k,round(ov(w,'barrel',WHEEL),5)))
w.bodies[WHEEL].q=wq
out['barrel_wheel_overlap_vs_wheel_turn_min']=min(scan,key=lambda x:x[1])
out['barrel_wheel_overlap_vs_wheel_turn_sample']=[s for s in scan if s[0] in (-10,-5,-2,-1,-0.5,0,0.5,1,2,5,10)]
# what does the wheel's own other mesh allow? overlap wheel<->pinion as the wheel turns
pq=w.bodies[PIN].q
out['wheel_pinion_overlap_vs_wheel_turn']=[(d,round((lambda: (setattr(w.bodies[WHEEL],'q',wq+math.radians(d)), ov(w,WHEEL,PIN))[1])(),5)) for d in (-2,-1,-0.5,0.5,1,2)]
w.bodies[WHEEL].q=wq
# 3. counterfactuals from a fresh world: drop one contact pair and pre-wind again
for lab,pairs in (('no_clutch_pinion_contact',[{CL,PIN}]),('no_wheel_pinion_contact',[{WHEEL,PIN}])):
    E.World.pairs_ok=ignoring(pairs); w=fresh(); bl,first,_=prewind(w); E.World.pairs_ok=orig_pairs
    out['prewind_'+lab]={'blocked':bl,'first':first}
# 4. same barrel angles crown-driven (AT-1 path): does a forward crown turn take the barrel past the stall angle?
w=fresh(); b0=w.bodies['barrel'].q; bl=0; maxb=0
for i in range(120):
    if not w.step('stem',dq=C.FORWARD*math.radians(3)): bl+=1
    maxb=max(maxb,deg(w.bodies['barrel'].q-b0))
out['crown_driven']={'blocked':bl,'barrel_deg_reached':maxb}
print(json.dumps(out,indent=1,default=str))
