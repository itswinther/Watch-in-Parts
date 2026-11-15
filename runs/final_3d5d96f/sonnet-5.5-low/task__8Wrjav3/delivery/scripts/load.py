import sys,time,pickle,os
sys.path.insert(0,'/app/tools')
import kernel
def loadall(folder='/app/work/parts'):
    M={}
    for f in sorted(os.listdir(folder)):
        if f.endswith('.step'):
            t=time.time()
            M[f[:-5]]=kernel.load_step_part(os.path.join(folder,f),16777216,200000,0.001,0.1,500,120,4096,0.005)
    return M
if __name__=='__main__':
    t=time.time(); M=loadall(); print(time.time()-t)
    for k,m in M.items(): print(k,round(m.volume(),2),[round(x,3) for x in m.bounding_box()], m.num_tri())
    pickle.dump({k:(m.to_mesh().vert_properties[:,:3].copy(),m.to_mesh().tri_verts.copy()) for k,m in M.items()},open('meshes.pkl','wb'))
