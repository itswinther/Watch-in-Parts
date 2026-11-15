import random,sys,json
from layout2 import *
cl={'s':'D','d':'C','dd':'A','p':'B'}; lay=['B','C','D','B']
rnd=random.Random(int(sys.argv[1])); best=(-9,)
for rep in range(8):
    s,ang=opt(cl,lay,rnd,3000,4000)
    # refine with ext X2
    from layout2 import score
    s2=score(ang,cl,lay,{'X2'})
    if s2>best[0]: best=(s2,ang); print(round(s,3),round(s2,3),flush=True)
json.dump([float(best[0]),cl,lay,[float(a) for a in best[1]]],open('lay4_%s.json'%sys.argv[1],'w'))
