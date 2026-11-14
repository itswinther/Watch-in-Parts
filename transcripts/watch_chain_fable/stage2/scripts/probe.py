import sys;sys.path.insert(0,'tools')
import kernel as K, numpy as np, manifold3d as m3
L=lambda n:K.load_part('previous/parts/%s.stl'%n,200000,1<<25,0.005)
tp=L('top_plate'); hw=L('hour_wheel'); mp=L('main_plate')
C=np.array([9.093266739736606,6.750000000000001])
for z in (5.0,5.6,5.69):
    cs=tp.slice(z); print('top z',z,'area',cs.area(),[ (len(p),np.round(np.min(p,0),2),np.round(np.max(p,0),2)) for p in cs.to_polygons()])
for z in (4.0,4.7):
    cs=mp.slice(z); print('main z',z,'area',cs.area(),[ (len(p),np.round(np.min(p,0),2),np.round(np.max(p,0),2)) for p in cs.to_polygons()])
for z in (7.2,7.7,8.2,8.5,9.0):
    cs=hw.slice(z); ps=cs.to_polygons(); print('hw',z,cs.area(),[(len(p),round(float(np.max(np.linalg.norm(np.asarray(p)-C,axis=1))),3),round(float(np.min(np.linalg.norm(np.asarray(p)-C,axis=1))),3)) for p in ps])
p=np.concatenate(hw.slice(7.7).to_polygons())-C
r=np.linalg.norm(p,axis=1); a=np.degrees(np.arctan2(p[:,1],p[:,0]))
sel=r>4.99
print(sorted(np.round(a[sel]%7.5,3))[:40], r.max())
