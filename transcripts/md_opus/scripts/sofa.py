from common import *
from plan2d import plan2d
import pickle
Z0 = 0.6
O = R_of([(1,0,0),(0,0,1),(0,-1,0)])
p = Path("sofa", pose(O, (-270, 713, Z0)))
p.move_to((340, 713, Z0))
V = p.V
def place_minz(R, xmin, y):
    W = V @ R.T
    return pose(R, (xmin - W[:,0].min(), y, Z0 - W[:,2].min()))
# pitch up: local x -> Z
for a in np.linspace(0, 90, 91)[1:]:
    R = rotm("y", -a) @ O
    p.goto(place_minz(R, 330, 713))
# corner yaw in XY plane
T = p.T
print("after pitch R\n", np.round(T[:3,:3],3), "t", T[:3,3])
ox, oy = T[0,3], T[1,3]
free = [((320,595),(700,720)), ((575,300),(700,720)), ((420,30),(880,300))]
piece = [((-160,-80),(0,0))]
thetas = np.arange(0, -91, -1.0)
# shift start to grid
sx, sy = round(ox/2)*2, round(oy/2)*2
p.move_to((sx, sy, T[2,3]))
res = plan2d(free, piece, thetas, (320, 880, 30, 720), 2.0, (sx, sy, 0), (680, 400, 90), dil=2)
Rb = p.T[:3,:3]; z = p.T[2,3]

for (u, v, th) in res[1:]:
    p.goto(pose(rotm("z", th) @ Rb, (u, v, z)))
print("after yaw R\n", np.round(p.T[:3,:3],3), "t", p.T[:3,3])
p.move_to((680, 60, z))
# pitch down to identity
R0 = p.T[:3,:3]
for a in np.linspace(0, 90, 91)[1:]:
    R = rotm("y", a) @ R0
    p.goto(place_minz(R, 450, 60))
print("after pitchdown R\n", np.round(p.T[:3,:3],3), "t", p.T[:3,3])
F = inst.final("sofa")
p.move_to(F[:3,3] + (0,0,Z0))
p.goto(F)
print(fmt_messages("sofa", p.poses))
check("sofa", p.poses, placed_dict([]))
pickle.dump({"sofa": p.poses}, open("sofa.pkl", "wb"))
