import sys,glob,numpy as np
sys.path.insert(0,'/app/tools');import kernel as k
for path in glob.glob('/app/*.stl'):
 name=path.split('/')[-1][:-4]
 if name=='barrel':continue
 m=k.tris_to_manifold(k.read_stl(path,200000,16777216));bb=np.asarray(m.bounding_box());h=.05
 start=np.floor((bb[:3]-.2-.0113)/h)*h+.0113
 shape=tuple((np.ceil((bb[3:]+.2-start)/h)+1).astype(int))
 # kernel uses cell corners; requested grid is at centres.
 out=k.opening_test_slabs(m,start-h/2,shape,h,1.5,1,6)
 print(name,out,'deviation_mm',out[1]*h,flush=True)
