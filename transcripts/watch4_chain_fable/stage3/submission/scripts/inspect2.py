from common import *
mv = json.load(open(os.path.join(ROOT, 'previous/movement.json')))
for n, mob in [('intermediate_wheel_50t_m025','intermediate'),('minute_drive_pinion_25t_m025','minute'),('intermediate_arbor','intermediate'),('minute_tube','minute')]:
    ax = np.array(mv['mobiles'][mob]['axis'])
    m = load(n, 'previous')
    b = m.bounding_box()
    zs = sorted(set(np.round(kernel.verts(m)[:,2],4)))
    print(n, 'z levels', zs[:20])
    for z in [ (zs[i]+zs[i+1])/2 for i in range(len(zs)-1)][:8]:
        polys = m.slice(z).to_polygons()
        out=[]
        for p in polys:
            p = np.asarray(p)-ax
            r = np.hypot(p[:,0],p[:,1])
            a = np.degrees(np.arctan2(p[:,1],p[:,0]))
            out.append((len(p), round(r.min(),4), round(r.max(),4), round(a[r.argmax()],3)))
        print('  z=%.3f'%z, out)
