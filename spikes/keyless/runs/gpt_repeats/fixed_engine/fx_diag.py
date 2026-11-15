import sys,math; sys.path.insert(0,'/w/spikes/keyless')
import grade as Gr, engine as E
sub=sys.argv[1]
spec,parts,sup,defs=Gr.load(sub,'/w/spikes/keyless/data')
orig=E.World.resolve; LOG=[]
def wrapped(self):
    ok=orig(self)
    if not ok:
        pens={}
        for n,b in self.bodies.items():
            if b.kind=='fixed': continue
            for o in self.bodies:
                if o!=n and self.pairs_ok(b,self.bodies[o]):
                    v=self._pen1(b,only={o})
                    if v>E.TOL: pens[tuple(sorted((n,o)))]=round(v,5)
        LOG.append((dict(self.dqs and {k:(round(math.degrees(a),4),round(p,4)) for k,(a,p) in self.dqs.items()}),pens))
    return ok
E.World.resolve=wrapped
for sgn,lab in ((-1,'FORWARD'),(+1,'BACKWARD')):
    w=Gr.make_world(parts,sup,defs); w.settle(); LOG.clear()
    q0={n:b.q for n,b in w.bodies.items()}
    ok=w.step('stem',dq=math.radians(3*sgn))
    moved={n:round(math.degrees(b.q-q0[n]),3) for n,b in w.bodies.items() if abs(b.q-q0[n])>1e-7}
    print(lab,'first 3deg step ok=',ok,'moved',moved)
    for l in LOG[-2:]: print('   failed resolve: moves',l[0],'overlaps>TOL',l[1])
