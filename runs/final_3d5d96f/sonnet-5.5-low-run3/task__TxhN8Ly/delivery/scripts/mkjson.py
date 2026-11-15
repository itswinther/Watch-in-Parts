import sys; sys.path.insert(0,'/app/work')
import json
from geom import *
ST='AD-C100-HT'; BR='AD-CW614N'
def mov(v6):
    c='I_c6' if v6 else 'I_c'; d='M_din6' if v6 else 'M_din'
    zc=T['c6'] if v6 else T['c']; zd=T['d6'] if v6 else T['d']
    mob={
     'I':dict(axis=list(map(float,I+OFF)),parts=['I_shaft',c],material=ST),
     'M':dict(axis=list(map(float,OFF)),parts=['M_shaft','M_dd','M_p',d,'minute_hand'],material=ST,part_materials={'minute_hand':BR}),
     'H':dict(axis=list(map(float,OFF)),parts=['H_tube','hour_hand'],material=ST,part_materials={'hour_hand':BR}),
     'X1':dict(axis=list(map(float,X1+OFF)),parts=['X1'],material=ST),
     'X2':dict(axis=list(map(float,X2+OFF)),parts=['X2'],material=ST),
     'X3':dict(axis=list(map(float,X3+OFF)),parts=['X3'],material=ST),
     'S':dict(axis=list(map(float,S+OFF)),parts=['S_shaft','sec_hand'],material=ST,part_materials={'sec_hand':BR}),
     'J':dict(axis=list(map(float,J+OFF)),parts=['J'],material=ST),
     'K':dict(axis=list(map(float,K+OFF)),parts=['K'],material=ST),
     'D':dict(axis=list(map(float,DD+OFF)),parts=['D_shaft','day_hand'],material=ST,part_materials={'day_hand':BR}),
    }
    me=[('barrel',96,'I',12),('I',zc,'M',zd),('M',36,'X1',12),('X1',36,'X2',12),('X2',30,'X3',12),('X3',32,'S',12),
        ('M',14,'J',42),('J',12,'H',48),('H',48,'K',24),('K',12,'D',48)]
    meshes=[dict(driver=a,driver_teeth=b,driven=c_,driven_teeth=e) for a,b,c_,e in me]
    return dict(barrel='BR-096-30',case_centre=list(map(float,OFF)),fixed=['PL','MP','TP'],mobiles=mob,meshes=meshes,
      hands=dict(hour=dict(mobile='H',part='hour_hand'),minute=dict(mobile='M',part='minute_hand'),
                 seconds=dict(mobile='S',part='sec_hand'),day=dict(mobile='D',part='day_hand')))
json.dump(mov(False),open('/app/delivery/movement.json','w'),indent=1)
json.dump(mov(True),open('/app/delivery/variant_6h.json','w'),indent=1)
