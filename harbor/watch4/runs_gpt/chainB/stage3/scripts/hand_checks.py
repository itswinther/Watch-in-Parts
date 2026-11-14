exec(open('scripts/check.py').read().split("m=json.loads")[0])
m=json.loads(Path('work/movement.json').read_text())
for n,h in m['hands'].items():
 ax=np.array(m['mobiles'][h['mobile']]['axis']); part=load(h['part']);v=k.verts(part)
 print(n,'axis',ax.tolist(),'reach',np.linalg.norm(v[:,:2]-ax,axis=1).max(),'z',v[:,2].min(),v[:,2].max())
a=np.array(m['mobiles'][m['hands']['day']['mobile']]['axis']);b=np.array(m['mobiles'][m['hands']['hour']['mobile']]['axis'])
print('day-hour axis distance',np.linalg.norm(a-b))
