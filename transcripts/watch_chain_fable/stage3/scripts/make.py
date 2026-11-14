import sys,json,numpy as np
sys.path.insert(0,'scripts'); sys.path.insert(0,'tools')
import kernel
from block import P,mob,names
exec(open('scripts/order.py').read().replace("print(dis[::-1])",""))
seq=dis[::-1]
lo=np.min([P[n].bounding_box()[:3] for n in names],0); hi=np.max([P[n].bounding_box()[3:] for n in names],0)
print('bbox',lo,hi)
paths={}
for a,d in seq:
    bb=P[a].bounding_box(); s=1 if d=='+z' else -1
    D=(hi[2]+5-bb[2]) if s>0 else (bb[5]-(lo[2]-5)); D+=0.1
    n=int(np.ceil(D/0.19))
    ps=[]
    for i in range(n,-1,-1):
        T=np.eye(4); T[2,3]=s*D*i/n; ps.append(T.tolist())
    paths[a]=ps
json.dump({'order':[a for a,_ in seq],'paths':paths},open('work/assembly.json','w'))
