import re
from pathlib import Path
import numpy as np
for p in Path('work/parts').glob('*.step'):
 pts=np.array([list(map(float,x.split(','))) for x in re.findall(r'CARTESIAN_POINT\([^,]*,\(([^)]+)\)\)',p.read_text()) if len(x.split(','))==3]); print(p.stem, pts.min(0).round(3),pts.max(0).round(3))
