import sys,math
sys.path.insert(0,'/app/scripts')
exec(open('/app/scripts/chain.py').read().split('# chain:')[0])
w.stem_x=0.9
fx=[cache_f[f] for f in w.fixed]
for sgn in (-1,1):
  w.stem_a=0; w.q['setting_wheel']=0; w.q['minute_wheel']=0
  for step in range(30):
    w.stem_a+=sgn*math.radians(3)
    G=B('stem')
    for n,pusher in (('setting_wheel',[G]),('minute_wheel',['setting_wheel'])):
        bs=[B(p) if isinstance(p,str) else p for p in pusher]+fx
        d=resolve(n,bs,8.0)
        if d is None: print('JAM',n,step); break
        w.q[n]+=math.radians(d)
    if step%6==5: print(sgn,step,'stem',round(math.degrees(w.stem_a)),'S',round(math.degrees(w.q['setting_wheel']),1),'MW',round(math.degrees(w.q['minute_wheel']),2),flush=True)
