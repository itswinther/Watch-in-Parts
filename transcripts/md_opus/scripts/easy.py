from common import *
import pickle
I = np.eye(3)
# bookcase
b = Path("bookcase", pose(I, (-130, 640, 0.5)))
b.move_to((200, 640, 0.5)); b.move_to((200, 595.5, 0.5)); b.move_to((400, 595.5, 0.5)); b.goto(inst.final("bookcase"))
# chest
c = Path("chest", pose(I, (-110, 645, 0.5)))
c.move_to((63, 645, 0.5)); c.move_to((63, 400, 0.5)); c.goto(inst.final("chest"))
for p in (b, c):
    print(fmt_messages(p.name, p.poses))
pickle.dump({"bookcase": b.poses, "chest": c.poses}, open("easy.pkl", "wb"))
