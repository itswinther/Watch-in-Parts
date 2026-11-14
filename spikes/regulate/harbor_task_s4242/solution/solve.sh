#!/bin/bash
cd /app
python3 timer.py measure DU full 30
python3 timer.py measure CU full 30
python3 timer.py measure CD full 30
python3 timer.py measure CL full 30
python3 timer.py measure CR full 30
python3 timer.py remove 2 0.11
python3 timer.py remove 3 0.86
python3 timer.py measure CU full 30
python3 timer.py measure CD full 30
python3 timer.py measure CL full 30
python3 timer.py measure CR full 30
python3 timer.py remove 4 0.17
python3 timer.py remove 5 0.07
python3 timer.py measure CU full 30
python3 timer.py measure CD full 30
python3 timer.py measure CL full 30
python3 timer.py measure CR full 30
python3 timer.py measure DU full 15
python3 timer.py measure DU 24h 15
python3 timer.py measure DD full 15
python3 timer.py regulate -1.0
