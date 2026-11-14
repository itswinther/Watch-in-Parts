from contact_checks import *
checks={}
held=(2.1,-207.9,-173.25,42.0)
for label,start,degree in [('position1_test',held,24),('after_backward',(362.1,-207.9,-173.25,42),30),('return',held,90),('after_run_takeup',(-6.9,-306.9,-255.75,62),21)]:
 rows=wind(start,degree);end=rows[-1]
 checks[label]={'start':start,'end':end,'arbor_wind':end[3]-start[3]}
 print(label,checks[label],flush=True)
json.dump(checks,open('/app/scripts/short_checks.json','w'),indent=2)
