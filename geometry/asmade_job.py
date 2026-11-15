"""The switch and the one number of the as-made checks (geometry/asmade.py), in a module with no heavy imports so
the grader can read them before it loads the geometry kernel."""
import os

# Off: the one-job grader is unchanged. On (or WATCH_AS_MADE=1): Parts 1 and 3 gain made_free, made_mesh, made_clear.
AS_MADE_IN_JOB = os.environ.get("WATCH_AS_MADE", "") == "1"
# mm: the print process's size accuracy: every surface of a printed part lies within this of its drawn position.
# PROVISIONAL (SESSION.md, G 05:05): to be set to what the house reference passes as made, then stated in DS-W03.
PRINT_TOLERANCE = float(os.environ.get("WATCH_PRINT_TOLERANCE", "0.01"))
