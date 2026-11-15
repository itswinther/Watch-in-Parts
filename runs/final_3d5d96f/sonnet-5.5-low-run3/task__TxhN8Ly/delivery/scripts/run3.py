import random,sys,json
from layout2 import *
cl={'s':'D','d':'C','dd':'A','p':'B'}
rnd=random.Random(int(sys.argv[1]))
best=(-9,)
for lay in (['B','D','A','A'],['B','D','C','B'],['B','C','A','A'],['B','D','A','B'],['B','D','C','A'],['B','C','D','B'],['B','D','A','C'],['B','D','D','B']):
    if lay[0]==cl['dd']: continue
    for rep in range(6):
        s,ang=opt(cl,lay,rnd,1500,1500)
        if s>best[0]:
            best=(s,lay,ang); print(round(s,3),lay,flush=True)
json.dump([float(best[0]),cl,best[1],[float(a) for a in best[2]]],open('lay3_%s.json'%sys.argv[1],'w'))
