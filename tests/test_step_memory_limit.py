"""The STEP reader's child process still reads a part when the platform refuses the memory limit
(macOS refuses RLIMIT_AS) or has no `resource` module. Runs the real child code in a fresh interpreter
with setrlimit forced to fail.
    python3 tests/test_step_memory_limit.py"""
import os
import subprocess
import sys
import tempfile
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ROOT)
from geometry import watch as W
from geometry import core

CHILD = """
import sys
sys.path.insert(0, %(root)r)
MODE = %(mode)r
if MODE == "refuse":
    import resource
    def refuse(*a):
        raise ValueError("current limit exceeds maximum limit")     # what macOS raises
    resource.setrlimit = refuse
elif MODE == "missing":
    sys.modules["resource"] = None                                  # import resource -> ImportError
from geometry import core
print("limit set:", core._limit_memory(%(mb)d), file=sys.stderr)
core._step_child(%(path)r, %(lin)r, %(ang)r, %(tris)d, %(faces)d, %(mb)d)
"""


def main():
    import cadquery as cq
    d = tempfile.mkdtemp()
    path = os.path.join(d, "disc.step")
    core.write_step(path, cq.Workplane("XY").circle(3.0).extrude(1.0))
    want = core.read_step(path, W.MAX_STEP_BYTES, W.MAX_TRIANGLES, W.STEP_LINEAR_DEFLECTION, W.STEP_ANGULAR_DEFLECTION,
                          W.STEP_MAX_TRIANGLE_FACES, W.STEP_TIMEOUT_S, W.STEP_MEMORY_MB)
    bad = 0
    for mode in ("refuse", "missing"):
        code = CHILD % dict(root=ROOT, mode=mode, path=path, lin=W.STEP_LINEAR_DEFLECTION, ang=W.STEP_ANGULAR_DEFLECTION,
                            tris=W.MAX_TRIANGLES, faces=W.STEP_MAX_TRIANGLE_FACES, mb=W.STEP_MEMORY_MB)
        r = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, timeout=W.STEP_TIMEOUT_S)
        ok = r.returncode == 0 and r.stdout[:3] == b"OK\n"
        if ok:
            tris = np.frombuffer(r.stdout[3:], dtype="<f8").reshape(-1, 3, 3)
            ok = tris.shape == want.shape and np.allclose(tris, want)
        bad += not ok
        print("%-4s %-8s %s; %d triangles (normal read: %d)" % ("ok" if ok else "FAIL", mode, r.stderr.decode().strip().splitlines()[-1] if r.stderr else "",
                                                               (len(r.stdout) - 3) // 72, len(want)))
    m = core.load_step_part(path, W.MAX_STEP_BYTES, W.MAX_TRIANGLES, W.STEP_LINEAR_DEFLECTION, W.STEP_ANGULAR_DEFLECTION,
                            W.STEP_MAX_TRIANGLE_FACES, W.STEP_TIMEOUT_S, W.STEP_MEMORY_MB, W.SELF_UNION_TOL)
    print("normal load with the limit: volume %.4f (pi*9 = %.4f)" % (m.volume(), 9 * np.pi))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
