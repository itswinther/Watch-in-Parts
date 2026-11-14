import sys,math; sys.path.insert(0,'/w/spikes/keyless')
import grade as Gr, engine as E
spec,parts,sup,defs=Gr.load('/s','/w/spikes/keyless/data')
w=Gr.make_world(parts,sup,defs); w.settle()
P=w.bodies['winding_pinion']; F=w.bodies['winding_face_wheel']; St=w.bodies['stem']; C=w.bodies['sliding_clutch']
for a in (0.5,1,2,3):
    St.q-=0; 
w2=Gr.make_world(parts,sup,defs); w2.settle()
w2.bodies['stem'].q-=math.radians(3)
print('stem fwd 3deg: clutch<->pinion overlap %.5f'%w2._pen1(w2.bodies['winding_pinion'],only={'sliding_clutch'}))
p=w2.bodies['winding_pinion']; q=p.q
for d in (-3,-2.85,-1,1,2.85,3):
    p.q=q+math.radians(d); print('  pinion %+.2f: clutch overlap %.5f, face-wheel overlap %.5f'%(d,w2._pen1(p,only={'sliding_clutch'}),w2._pen1(p,only={'winding_face_wheel'})))
p.q=q-math.radians(2.85)
f=w2.bodies['winding_face_wheel']; fq=f.q
for d in (-3,-1.5,1.5,3):
    f.q=fq+math.radians(d); print('    with pinion -2.85: face wheel %+.1f -> overlap %.5f'%(d,w2._pen1(f,only={'winding_pinion'})))
