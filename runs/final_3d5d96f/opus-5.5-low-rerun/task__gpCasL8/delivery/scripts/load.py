import sys,os,json,numpy as np
sys.path.insert(0,'/app/tools'); import kernel, manifold3d as m3
CACHE='/app/work/cache'; os.makedirs(CACHE,exist_ok=True)
def part(name):
    p='/app/delivery/parts/%s.step'%name; c='%s/%s.stl'%(CACHE,name)
    if os.path.exists(c) and os.path.getmtime(c)>os.path.getmtime(p):
        tris=kernel.read_stl(c,10**7,10**9); return kernel.tris_to_part(tris,0.005)
    man=kernel.load_step_part(p,16777216,200000,0.001,0.1,500,120,4096,0.005)
    kernel.write_stl(c,man); return man
def barrel(no='BR-096-30'):
    tris=kernel.read_stl('/app/supplied/%s.stl'%no,10**7,10**9); return kernel.tris_to_manifold(tris)
def rotz(man,x,y,ang):
    c,s=np.cos(ang),np.sin(ang)
    T=[[c,-s,0,x-c*x+s*y],[s,c,0,y-s*x-c*y],[0,0,1,0]]
    return man.transform(T)
