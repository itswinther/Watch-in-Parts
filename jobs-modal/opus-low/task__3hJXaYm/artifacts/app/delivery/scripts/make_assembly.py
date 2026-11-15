import json, numpy as np
order=['plate','barrel','inter8_arbor','midplate','third','secondswheel','upperplate','inter8_wheel','centre',
       'motionplate','minutewheel','daywheel','hourwheel','dial','hand_hour','hand_minute','hand_seconds','hand_day']
DZ=10.5; n=int(np.ceil(DZ/0.18))
def path():
    out=[]
    for k in range(n+1):
        z=DZ*(1-k/n)
        out.append([[1,0,0,0],[0,1,0,0],[0,0,1,round(z,6) if k<n else 0.0],[0,0,0,1]])
    return out
json.dump(dict(order=order,paths={p:path() for p in order}),open('/app/delivery/assembly.json','w'))
