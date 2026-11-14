#!/bin/bash
cd /app
python3 timer.py measure CU full 18
python3 timer.py measure CD full 18
python3 timer.py measure CL full 18
python3 timer.py measure CR full 18
python3 timer.py remove 1 0.27
python3 timer.py remove 2 0.83
python3 timer.py measure DU full 18
python3 timer.py regulate -1.0
