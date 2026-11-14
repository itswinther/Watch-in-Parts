#!/bin/bash
# usage: grade.sh STEP. Writes 0 first, then the step score.
set -u
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt
cd /tests
python3 -I - "$1" <<'PY'
import json, sys
sys.path.insert(0, '/tests')
import movement as M
step = int(sys.argv[1])
inst = json.load(open('/tests/instance.json'))
ref = json.load(open('/tests/ref_step%d.json' % step))
try:
    des = json.load(open('/app/design.json'))
    rep = M.grade(inst, des, step) if isinstance(des, dict) else {'valid': False, 'violations': ['not a JSON object']}
except Exception as ex:
    rep = {'valid': False, 'violations': ['no readable design (%s)' % type(ex).__name__]}
s = M.score(rep, ref)
rep['score'] = s
json.dump(rep, open('/logs/verifier/details.json', 'w'), indent=1)
open('/logs/verifier/reward.txt', 'w').write('%s\n' % s)
print(json.dumps(rep, indent=1))
PY
