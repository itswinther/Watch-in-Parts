import sys,math,json; sys.path.insert(0,'/w/spikes/keyless')
import grade as Gr, engine as E, constants as C
CL,PIN,N=sys.argv[1],sys.argv[2],int(sys.argv[3])
spec,parts,sup,defs=Gr.load('/s','/w/spikes/keyless/data')
STEP=C.WIND_SENSE*math.radians(C.FREE_RUN_STEP)
w=Gr.make_world(parts,sup,defs); w.phase(); Gr._set_kind(w,'barrel','driven')
for i in range(N): assert w.step('barrel',dq=STEP)
CAP={}; op=E.World.push
def lp(self,b,dmax,only=None,signs=(1.0,-1.0)):
    if b.name==CL and 'snap' not in CAP:
        CAP['snap']=self.snapshot(); CAP['dqs']=dict(self.dqs); CAP['dmax']=dmax; CAP['only']=sorted(only) if only else None; CAP['signs']=signs
    return op(self,b,dmax,only,signs)
E.World.push=lp; ok=w.step('barrel',dq=STEP); E.World.push=op
out={'step_ok':ok,'clutch_push_dmax':CAP.get('dmax'),'signs':CAP.get('signs'),'only':CAP.get('only'),
     'dqs':{k:(round(math.degrees(a),4),round(p,5)) for k,(a,p) in CAP.get('dqs',{}).items()}}
w.restore(CAP['snap']); w.dqs=CAP['dqs']; c=w.bodies[CL]
out['clutch_overlaps']={o:round(w._pen1(c,only={o}),5) for o in w.bodies if o!=CL and w.pairs_ok(c,w.bodies[o]) and w._pen1(c,only={o})>1e-6}
p=c.q; sc=[]
for d in (0.005,0.01,0.02,0.03,0.05,0.08,0.12,-0.005,-0.01,-0.02):
    c.q=p+d; sc.append((d,round(w.pen(c),5),{o:round(w._pen1(c,only={o}),5) for o in w.bodies if o!=CL and w.pairs_ok(c,w.bodies[o]) and w._pen1(c,only={o})>E.TOL}))
c.q=p; out['clutch_slide_scan(own coord mm, max pen, pairs>TOL)']=sc
# budget pieces at each patch with the pinion
v=w.posed(c)^w.posed(w.bodies[PIN]); comps=v.decompose()
import numpy as np
pk=[]
for comp in comps:
    pts=np.asarray(comp.to_mesh().vert_properties,float)[:,:3]
    if not len(pts): continue
    cc=pts.mean(axis=0); pk.append({'vol':round(comp.volume(),6),'centre':[round(x,3) for x in cc],
        'travel_pinion':round(w.travel(w.bodies[PIN],cc),5),'travel_clutch':round(w.travel(c,cc),5)})
out['clutch_pinion_patches']=pk; out['TOL']=E.TOL; out['K']=E.K
out['clutch_lo_hi_q']=(c.lo,c.hi,round(c.q,4))
print(json.dumps(out,indent=1,default=str))
