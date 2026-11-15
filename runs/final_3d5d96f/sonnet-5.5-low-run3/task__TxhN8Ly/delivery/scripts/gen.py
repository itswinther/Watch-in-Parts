import sys; sys.path.insert(0,'/app/work')
from build import *
from posts import pick,free_post,free_pillar
import shutil
posts=[tuple(map(float,p)) for p in pick(free_post)[1]]
pillars=[tuple(map(float,p)) for p in pick(free_pillar)[1]]
json.dump(dict(posts=posts,pillars=pillars),open('pp.json','w'))
pl,mp,tp=plates(posts,pillars)
save('PL',pl);save('MP',mp);save('TP',tp)
p8=build(False)
p6=build(True)
for k,v in p8.items(): save(k,v)
for k in ('I_c6','M_din6'): save(k,p6[k])
ZH=dict(h1=H1,h2=H2,h3=H3)
save('hour_hand',hand(C,H2,0.7,1.15,5.5))
save('minute_hand',hand(C,H3,0.3,0.7,7.5))
save('sec_hand',hand(S,H1,0.3,0.7,5.5))
save('day_hand',hand(DD,H1,0.3,0.7,3.5))
print('done')
