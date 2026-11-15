import sys,pickle,time,os
sys.argv=['x','1']
from build import *
e,v,L=pickle.load(open('final_layout.pkl','rb'))
out='/app/work/parts'; os.makedirs(out,exist_ok=True)
t=time.time()
P,teeth,ph,parts,pil,fl=build_all(v,L,False)
print('noup/nolow',fl)
P6,teeth6,ph6,parts6,_,_=build_all(v,L,True)
allp=dict(parts)
allp['m1_6h']=parts6['m1']; allp['x_6h']=parts6['x']
for n,s in allp.items():
    kernel.write_step(f'{out}/{n}.step',s)
    print(n,os.path.getsize(f'{out}/{n}.step'),round(time.time()-t,1),flush=True)
pickle.dump((v,L,pil),open('/app/work/gen_meta.pkl','wb'))
