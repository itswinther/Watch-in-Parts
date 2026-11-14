import sys,math; sys.path.insert(0,'/w/spikes/keyless')
import grade as Gr, engine as E, constants as C
spec,parts,sup,defs=Gr.load('/s','/w/spikes/keyless/data')
orig=E.World.resolve; LOG=[]
def wrapped(self):
    ok=orig(self)
    if not ok and len(LOG)<1:
        pens={}
        for n,b in self.bodies.items():
            if b.kind=='fixed': continue
            for o in self.bodies:
                if o!=n and self.pairs_ok(b,self.bodies[o]):
                    v=self._pen1(b,only={o})
                    if v>E.TOL: pens[tuple(sorted((n,o)))]=round(v,5)
        LOG.append(({k:(round(math.degrees(a),3),round(p,4)) for k,(a,p) in self.dqs.items()},pens))
    return ok
E.World.resolve=wrapped
def fresh():
    w=Gr.make_world(parts,sup,defs); w.phase(); return w
# 1. rig pre-wind: arbor driven in the winding sense, crown held
w=fresh(); LOG.clear(); Gr._set_kind(w,'barrel','driven'); bl=0; first=None
for i in range(90):
    if not w.step('barrel',dq=C.WIND_SENSE*math.radians(C.FREE_RUN_STEP)):
        bl+=1; first=first if first is not None else i
print('PREWIND blocked',bl,'/90 first at step',first,'first failed resolve:',LOG[:1])
# 2. backward crown from rest
w=fresh(); LOG.clear(); bl=0; first=None
for i in range(40):
    if not w.step('stem',dq=-C.FORWARD*math.radians(3)):
        bl+=1; first=first if first is not None else i
print('BACKWARD 120deg from rest blocked',bl,'/40 first at',first,'first failed resolve:',LOG[:1])
# 3. pull from rest
w=fresh(); LOG.clear(); P=Gr.pull_of(spec)
pb=Gr._pull(w,P)
print('PULL to',P,'from rest: blocked',pb,'first failed resolve:',LOG[:1])
