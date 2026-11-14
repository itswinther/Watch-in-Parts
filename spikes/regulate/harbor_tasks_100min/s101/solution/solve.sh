#!/bin/bash
cd /app
python3 timer.py measure CU full 18
python3 timer.py measure CD full 18
python3 timer.py measure CL full 18
python3 timer.py measure CR full 18
python3 timer.py remove 7 0.82
python3 timer.py remove 0 0.5
python3 timer.py measure DU full 18
python3 timer.py regulate -0.43844318463959403
