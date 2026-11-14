import sys,json,numpy as np
sys.path.insert(0,'tools'); import kernel as K
d=json.load(open('work/movement.json'))
def L(n): return K.load_part(f'work/parts/{n}.stl',200000,1<<25,0.005)
for n in d['fixed']:
    b=L(n).bounding_box(); print('FIXED',n,np.round(b,3))
for m,v in d['mobiles'].items():
    ax=np.array(v['axis'])
    for n in v['parts']:
        p=L(n); b=p.bounding_box(); V=K.verts(p); r=np.hypot(V[:,0]-ax[0],V[:,1]-ax[1])
        print(m,n,'z',round(b[2],3),round(b[5],3),'rmin',round(r.min(),3),'rmax',round(r.max(),3))
