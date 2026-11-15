import sys, json, itertools, numpy as np
sys.path.insert(0,'/app/tools')
import kernel
P='/app/delivery/parts/'
cache={}
def part(n):
    if n not in cache: cache[n]=kernel.load_step_part(P+n+'.step',16777216,200000,0.001,0.1,500,120,4096,0.005)
    return cache[n]
def barrel(n):
    return kernel.tris_to_manifold(kernel.read_stl('/app/supplied/%s.stl'%n,10**6,10**9))
def run(fn):
    mv=json.load(open(fn))
    names=list(mv['fixed']); owner={n:'fixed' for n in names}
    for mn,m in mv['mobiles'].items():
        for p in m['parts']: names.append(p); owner[p]=mn
    mans={n:part(n) for n in names}; mans['barrel']=barrel(mv['barrel']); owner['barrel']='barrel'
    allz=[m.bounding_box() for m in mans.values()]
    print(fn,'z range',min(b[2] for b in allz),max(b[5] for b in allz))
    bad=0
    for a,b in itertools.combinations(names+['barrel'],2):
        A,B=mans[a],mans[b]
        v=kernel.ivol(A,B)
        same=owner[a]==owner[b]
        if v>0.01:
            print('OVERLAP',a,b,round(v,4)); bad+=1
        else:
            if not same:
                d=kernel.min_distance(A,B,0.06) if kernel.bbox_overlap(A,B,0.06) else 9
                if d<0.045: print('close',a,b,round(d,4), 'owners',owner[a],owner[b])
    print('overlaps',bad)
if __name__=="__main__":
    for f in sys.argv[1:]: run(f)
