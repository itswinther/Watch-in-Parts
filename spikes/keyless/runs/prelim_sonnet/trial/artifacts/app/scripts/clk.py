import sys,math
sys.path.insert(0,'/app/scripts')
from sim import *
w=World(); EPS=2e-4
fixed=[w.parts['stud_click']]
def clear(qb,cq):
    c=w.body('click',q=cq)
    return max(overlap(c,w.body('barrel',q=qb)),overlap(c,fixed[0]))
print('rest overlap',clear(0,0))
for deg in [-3,-1,-0.3,0,0.5,2,5,9,12,16,17.5,18,19,25]:
    qb=math.radians(deg)
    res=[]
    for dc in np.arange(-15,15.01,0.25):
        if clear(qb,math.radians(dc))<=EPS: res.append(dc)
    print(deg, (min(res,key=abs) if res else None), (min(res),max(res)) if res else '')
