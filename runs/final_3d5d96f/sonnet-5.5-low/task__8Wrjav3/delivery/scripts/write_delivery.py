import sys,os,json,pickle,math,shutil
sys.argv=['x','1']
sys.path.insert(0,'/app/work')
import layout as LO
from build import *
D='/app/delivery'
def mats(rows): return rows
def mov_json(P,variant):
    C=P['C']
    key2mob={'M1':'m1','X':'x','Y':'y','C':'minute','H':'hour','A':'a','B':'b','J':'j','I':'i','D':'d','S1':'s1','S2':'s2','S3':'s3','S':'sec'}
    parts={'m1':['m1_6h' if variant else 'm1'],'x':['x_6h' if variant else 'x'],'y':['y'],'minute':['minute_tube','minute_hand'],
           'hour':['hour_tube','hour_hand'],'a':['a'],'b':['b'],'j':['j'],'i':['i'],'d':['d_wheel','d_hand'],
           's1':['s1'],'s2':['s2'],'s3':['s3'],'sec':['s_wheel','s_hand']}
    rev={v:k for k,v in key2mob.items()}
    mobiles={}
    for mob,ps in parts.items():
        key=rev[mob]
        mobiles[mob]={'axis':[round(float(P[key][0]),6),round(float(P[key][1]),6)],'parts':ps,'material':'AD-C100-HT'}
    teeth={(m,g):z for m,gs in LO.G.items() for g,z in gs.items()}
    if variant: teeth[('M1','w')]=18; teeth[('X','a')]=24
    else: teeth[('M1','w')]=21; teeth[('X','a')]=21
    meshes=[{'driver':'barrel','driver_teeth':96,'driven':'m1','driven_teeth':12}]
    for a,b in LO.MESH:
        meshes.append({'driver':key2mob[a[0]],'driver_teeth':teeth[a],'driven':key2mob[b[0]],'driven_teeth':teeth[b]})
    return {'barrel':'BR-096-30','case_centre':[round(float(C[0]),6),round(float(C[1]),6)],
            'fixed':['plate_lower','plate_mid','plate_top'],'mobiles':mobiles,'meshes':meshes,
            'hands':{'hour':{'mobile':'hour','part':'hour_hand'},'minute':{'mobile':'minute','part':'minute_hand'},
                     'seconds':{'mobile':'sec','part':'s_hand'},'day':{'mobile':'d','part':'d_hand'}}}
if __name__=='__main__':
    v,L,pil=pickle.load(open('/app/work/gen_meta.pkl','rb'))
    P=LO.positions(v)
    os.makedirs(D+'/parts',exist_ok=True)
    for f in os.listdir('/app/work/parts'):
        shutil.copy('/app/work/parts/'+f,D+'/parts/'+f)
    json.dump(mov_json(P,False),open(D+'/movement.json','w'),indent=1)
    json.dump(mov_json(P,True),open(D+'/variant_6h.json','w'),indent=1)
    print('written')
