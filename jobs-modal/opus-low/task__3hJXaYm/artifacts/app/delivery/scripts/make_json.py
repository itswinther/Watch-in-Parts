import json, numpy as np
g=json.load(open('/app/delivery/scripts/geom.json')); P=g['POS']; Z=g['Z']
ST='AD-C100-HT'
def build(var):
    I='inter8' if var==8 else 'inter6'; Ip=P['I8'] if var==8 else P['I6']; a=9 if var==8 else 12
    mob={
     I:dict(axis=Ip,parts=[I+'_arbor',I+'_wheel'],material=ST),
     'centre':dict(axis=P['C'],parts=['centre','hand_minute'],material=ST),
     'hour':dict(axis=P['C'],parts=['hourwheel','hand_hour'],material=ST),
     'third':dict(axis=P['T'],parts=['third'],material=ST),
     'seconds':dict(axis=P['S'],parts=['secondswheel','hand_seconds'],material=ST),
     'minutewheel':dict(axis=P['M'],parts=['minutewheel'],material=ST),
     'day':dict(axis=P['D'],parts=['daywheel','hand_day'],material=ST)}
    meshes=[dict(driver='barrel',driver_teeth=96,driven=I,driven_teeth=a),
            dict(driver=I,driver_teeth=48,driven='centre',driven_teeth=64),
            dict(driver='centre',driver_teeth=64,driven='third',driven_teeth=8),
            dict(driver='third',driver_teeth=60,driven='seconds',driven_teeth=8),
            dict(driver='centre',driver_teeth=8,driven='minutewheel',driven_teeth=32),
            dict(driver='minutewheel',driver_teeth=8,driven='hour',driven_teeth=24),
            dict(driver='minutewheel',driver_teeth=8,driven='day',driven_teeth=48)]
    hands=dict(hour=dict(mobile='hour',part='hand_hour'),minute=dict(mobile='centre',part='hand_minute'),
               seconds=dict(mobile='seconds',part='hand_seconds'),day=dict(mobile='day',part='hand_day'))
    return dict(barrel='BR-096-30',case_centre=P['C'],fixed=['plate','midplate','upperplate','motionplate','dial'],
                mobiles=mob,meshes=meshes,hands=hands)
json.dump(build(8),open('/app/delivery/movement.json','w'),indent=1)
json.dump(build(6),open('/app/delivery/variant_6h.json','w'),indent=1)
