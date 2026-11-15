import random
from dbg import detail
from layout2 import *
cl={'s':'D','d':'C','dd':'A','p':'B'}; lay=['B','D','A','B']
rnd=random.Random(5)
s,ang=opt(cl,lay,rnd,400,600); print(s,ang)
for o in detail(ang,cl,lay): print(o)
