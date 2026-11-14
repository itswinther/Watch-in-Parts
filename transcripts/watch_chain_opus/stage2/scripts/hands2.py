import sys,json,numpy as np
sys.path.insert(0,'tools'); import kernel as K
d=json.load(open('work/movement.json'))
for h,e in d['hands'].items():
    ax=np.array(d['mobiles'][e['mobile']]['axis'])
    V=K.verts(K.load_part(f"work/parts/{e['part']}.stl",200000,1<<25,0.005))
    r=np.hypot(V[:,0]-ax[0],V[:,1]-ax[1]); sel=V[r>2.0]
    c=sel[:,:2].mean(0)-ax; a=np.degrees(np.arctan2(c[1],c[0]))
    print(h,'clock angle',round((90-a)%360,3))
