import sys
exec(open('scripts/check.py').read().split('bad=0')[0])
from fractions import Fraction as F
sp={'barrel':F(-1,6)}
for me in mv['meshes']:
    sp[me['driven']]=-sp[me['driver']]*F(me['driver_teeth'],me['driven_teeth'])
print(sp)
meshed={frozenset((m['driver'],m['driven'])) for m in mv['meshes']}
names=['barrel']+list(mv['mobiles'])
for i,a in enumerate(names):
  for b in names[i+1:]:
    if frozenset((a,b)) in meshed: continue
    if not ({a,b}&{'train1','barrel'}): continue
    A,ax=mob(a);B,bx=mob(b);sa,sb=float(sp[a]),float(sp[b])
    fast=max(abs(sa),abs(sb)); w=0
    for k in range(288):
        if k<144: t=k/144/fast
        else:
            rel=abs(sa-sb); t=(k-144)/144/rel
            # relative: hold b still, a turns at rel
            r=(k-144)/144*360*(1 if sa>sb else -1)
            w=max(w,kernel.ivol(rot(A,ax,r),B)); continue
        w=max(w,kernel.ivol(rot(A,ax,360*sa*t),rot(B,bx,360*sb*t)))
    print(a,b,round(w,4),flush=True)
