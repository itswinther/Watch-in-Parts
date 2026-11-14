from common import *
import sys
mv,P=load_all('previous')
for n in sys.argv[1:]:
    p=P[n];bb=p.bounding_box()
    zs=np.arange(np.floor(bb[2]*10)/10+0.05,bb[5],0.1)
    last=None
    for z in zs:
        polys=p.slice(z).to_polygons()
        desc=[]
        for q in polys:
            q=np.asarray(q);c=(q.min(0)+q.max(0))/2;r=(q.max(0)-q.min(0))/2
            x,y=q[:,0],q[:,1];a=0.5*np.sum(x*np.roll(y,-1)-y*np.roll(x,-1))
            desc.append('c(%.2f,%.2f) r(%.2f,%.2f) a%.1f n%d'%(c[0],c[1],r[0],r[1],a,len(q)))
        desc=sorted(desc)
        if desc!=last:
            print(n,'z=%.2f'%z);[print('   ',d) for d in desc]
            last=desc
