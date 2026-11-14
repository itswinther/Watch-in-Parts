#!/bin/bash
set -u
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt
python3 -I - <<'PY'
import json, math
a = json.load(open('/tests/anchors.json'))
try:
    f = json.load(open('/tmp/final.json'))
    e = float(f['error_s_per_day'])
except Exception as ex:
    print('no final state:', type(ex).__name__); raise SystemExit
if not math.isfinite(e):
    raise SystemExit
n, r = a['untouched_error'], a['reference_error']
s = max(0.0, min(1.0, (n - e) / (n - r))) if n > r else 0.0
json.dump({'error': e, 'untouched': n, 'reference': r, 'score': s, 'actions': len(f.get('log', []))}, open('/logs/verifier/details.json', 'w'), indent=1)
open('/logs/verifier/reward.txt', 'w').write('%.4f\n' % s)
print('error %.2f untouched %.2f reference %.2f score %.4f' % (e, n, r, s))
PY
