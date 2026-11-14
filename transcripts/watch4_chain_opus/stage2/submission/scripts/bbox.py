from common import *
m=mv()
names=m['fixed']+[p for mo in m['mobiles'].values() for p in mo['parts']]
for n in names:
    s=load(n); b=s.bounding_box()
    print(n, np.round(b,3), round(s.volume(),3))
