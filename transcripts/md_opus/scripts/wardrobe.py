from common import *
from plan2d import plan2d
import pickle
B = R_of([(0,1,0),(0,0,1),(1,0,0)])
Rf = inst.final("wardrobe")[:3,:3]
resA = pickle.load(open("wardA_res.pk", "rb"))
u, v, th = resA[0]
p = Path("wardrobe", pose(B, (-262, 643, v)))   # in staging: x -262..-30
for (u, v, th) in resA:
    p.goto(pose(rotm("y", -th) @ B, (u, 643, v)))
print("A end", np.round(p.T,3).tolist(), np.abs(p.T[:3,:3]-Rf).max())
p.goto(pose(Rf, (125, 643, 4.5)))
# stage B: y-z plane
free = [((480,0),(720,258)), ((460,0),(480,205)), ((200,0),(460,238))]
piece = [((0,0),(60,232))]
resB = plan2d(free, piece, np.arange(0, 91, 1.0), (180, 740, -20, 260), 1.5, (643.5, 4.5, 0), (439.5, 4.5, 90), dil=2)
for (u, v, th) in resB:
    p.goto(pose(rotm("x", th) @ Rf, (125, u, v)))
L2 = rotm("x", 90) @ Rf
# bedroom: lift, roll, yaw, pitch up
def center(): 
    W = p._wv(p.T); return (W.min(0) + W.max(0)) / 2
p.move((0, 0, 45 - center()[2]))
c = center(); p.move((200 - c[0], 330 - c[1], 0))
p.rotate("y", 90, center())
p.rotate("z", 90, center())
print("before pitch", np.round(p.T[:3,:3]).tolist())
def place_minz(R, xmin, y):
    W = p.V @ R.T
    return pose(R, (xmin - W[:,0].min(), y, 0.6 - W[:,2].min()))
R0 = p.T[:3,:3]
y0 = p.T[1,3]
p.goto(place_minz(R0, 30, y0))
for a in np.linspace(0, 90, 181)[1:]:
    p.goto(place_minz(rotm("y", -a) @ R0, 30, y0))
print("after pitch", np.round(p.T[:3,:3]).tolist(), np.abs(p.T[:3,:3]-Rf).max())
F = inst.final("wardrobe")
p.move_to(F[:3,3] + (0, 0, 0.6))
p.goto(F)
print(fmt_messages("wardrobe", p.poses))
check("wardrobe", p.poses, placed_dict(["sofa", "bookcase"]))
pickle.dump({"wardrobe": p.poses}, open("wardrobe.pkl", "wb"))
