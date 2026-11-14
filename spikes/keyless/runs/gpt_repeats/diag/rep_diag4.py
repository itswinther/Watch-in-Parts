import sys,math; sys.path.insert(0,'/w/spikes/keyless')
import grade as Gr, engine as E
sub,clutch,wheel=sys.argv[1:4]
spec,parts,sup,defs=Gr.load(sub,'/w/spikes/keyless/data')
w=Gr.make_world(parts,sup,defs); w.settle()
for n,b in w.bodies.items():
    if b.kind!='fixed': print(n,b.kind,b.dof,'axis',[round(x,3) for x in b.dir],'carrier',b.carrier)
w.bodies['stem'].q-=math.radians(0.5)    # small forward crown turn, no resolve
base=w._pen1(w.bodies[wheel],only={clutch})
print('forward 0.5deg: overlap %s<->%s = %.5f'%(clutch,wheel,base))
b=w.bodies[wheel]; q=b.q
for d in (-2,-1,1,2):
    b.q=q+math.radians(d); print('  turn %s by %+d deg -> overlap %.5f'%(wheel,d,w._pen1(b,only={clutch})))
b.q=q
cb=w.bodies[clutch]; p=cb.q
for d in (-0.05,0.05):
    cb.q=p+d; print('  move %s by %+.2f (own coord) -> overlap %.5f'%(clutch,d,w._pen1(b,only={clutch})))
