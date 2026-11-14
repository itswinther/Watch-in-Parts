import sys,os,json,pickle
sys.path.insert(0,'tools')
import numpy as np, kernel, manifold3d as m3
def load(p):
    return kernel.load_step_part(p,16777216,200000,0.001,0.1,500,120,4096,0.005)
def barrel():
    return kernel.tris_to_manifold(kernel.read_stl('meshes/barrel.stl',200000,33554432))
def load_all(d='work'):
    mv=json.load(open(d+'/movement.json'))
    names=list(mv['fixed'])+[p for m in mv['mobiles'].values() for p in m['parts']]
    P={n:load('%s/parts/%s.step'%(d,n)) for n in names}
    return mv,P
def rotz(deg,axis):
    a=np.radians(deg);c,s=np.cos(a),np.sin(a);x,y=axis
    T=np.eye(4);T[0,0]=c;T[0,1]=-s;T[1,0]=s;T[1,1]=c
    T[0,3]=x-c*x+s*y;T[1,3]=y-s*x-c*y
    return T
