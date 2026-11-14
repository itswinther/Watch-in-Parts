exec(open('scripts/plan.py').read().split("ORDER=")[0])
for a in ('arb_a','arb_day'):
  for q in ('day_cock','wa','pa','wd','gh'):
    print(a,q,[round(inter(moved(a,dz),S[q]),3) for dz in (-1,-0.3,-0.1,0,0.1,0.3,1)])
c=S['day_cock']
for x,y in ((5.46,4.06),(3.86,2.85)):
    print([ (z, c.slice(z) is not None) for z in ()])
