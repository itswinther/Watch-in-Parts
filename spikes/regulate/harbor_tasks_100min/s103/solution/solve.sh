#!/bin/bash
cd /app
python3 timer.py measure CU full 18
python3 timer.py measure CD full 18
python3 timer.py measure CL full 18
python3 timer.py measure CR full 18
python3 timer.py remove 5 0.41
python3 timer.py remove 6 0.28
python3 timer.py measure DU full 18
python3 timer.py regulate -1.0
