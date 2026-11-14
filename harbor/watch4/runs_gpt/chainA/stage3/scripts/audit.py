exec(open('scripts/check.py').read().split('mode=sys.argv')[0])
old=json.load(open('previous/movement.json'))
oldnames=old['fixed']+sum((v['parts'] for v in old['mobiles'].values()),[])
kept=[];changed=[]
for n in oldnames:
 identical=n in names and open('previous/parts/'+n+'.step','rb').read()==open('work/parts/'+n+'.step','rb').read()
 if n in old['fixed']: placed=n in m['fixed']
 else:
  mobile=next(a for a,v in old['mobiles'].items() if n in v['parts'])
  placed=mobile in m['mobiles'] and m['mobiles'][mobile]['axis']==old['mobiles'][mobile]['axis'] and n in m['mobiles'][mobile]['parts']
 (kept if identical and placed else changed).append(n)
print('KEPT',len(kept),'/',len(oldnames),'CHANGED_OR_REMOVED',changed)
for name,h in m['hands'].items():
 axis=axes[h['mobile']];s=parts[h['part']]
 radius=np.linalg.norm(k.verts(s)[:,:2]-axis,axis=1).max()
 print('HAND_REACH',name,radius,'AXIS',axis,'Z',s.bounding_box()[2:6:3])
print('DAY_AXIS_DISTANCE',math.dist(axes[m['hands']['day']['mobile']],axes[m['hands']['hour']['mobile']]))
print('MAIN_HAND_AXES_COINCIDE',len({tuple(axes[m['hands'][h]['mobile']]) for h in ('hour','minute','seconds')})==1)
