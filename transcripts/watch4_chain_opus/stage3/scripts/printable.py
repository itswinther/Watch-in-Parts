import sys, numpy as np; sys.path.insert(0,'tools'); import kernel, manifold3d as m3
h=0.05
for n in sys.argv[1:]:
    d=np.load('scripts/cache/%s.npz'%n); man=m3.Manifold(m3.Mesh(vert_properties=d['v'].astype(np.float32),tri_verts=d['f'].astype(np.uint32)))
    bb=man.bounding_box(); worst=0
    for j in [0,0.013,0.027,0.041]:
        lo,shape=kernel.grid_for(bb[:3],bb[3:],h,j+0.05)
        vox=kernel.voxelize(man,lo,shape,h)
        npc,dev=kernel.opening_test(vox,1.5,1.0)
        worst=max(worst,dev*h); print(n,j,npc,round(dev*h,3))
    print(n,'PASS' if worst<=0.2 else 'FAIL')
