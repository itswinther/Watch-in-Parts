from common import *
import sys
for n in sys.argv[1:]:
    s=load(n); b=np.array(s.bounding_box())
    for j in [0.0,0.017,0.033]:
        lo,shape=kernel.grid_for(b[:3],b[3:],0.05,j)
        g=kernel.voxelize(s,lo,shape,0.05)
        print(n,j,kernel.opening_test(g,1.5,1.0))
