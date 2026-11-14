import sys,math; sys.path.insert(0,'/w/spikes/keyless')
import grade as Gr, engine as E
sub,body=sys.argv[1],sys.argv[2]
spec,parts,sup,defs=Gr.load(sub,'/w/spikes/keyless/data')
for sgn in (-1,1):
    w=Gr.make_world(parts,sup,defs); w.settle()
    q0={n:b.q for n,b in w.bodies.items()}; bl=0
    for i in range(10):
        if not w.step(body,dq=math.radians(1*sgn)): bl+=1
    moved={n:round(math.degrees(b.q-q0[n]),2) for n,b in w.bodies.items() if abs(b.q-q0[n])>1e-7}
    print('drive',body,'by',10*sgn,'deg: blocked',bl,'/10 moved',moved)
