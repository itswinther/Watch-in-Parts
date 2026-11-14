#!/bin/bash
cd /app
python3 timer.py measure CU full 18
python3 timer.py measure CD full 18
python3 timer.py measure CL full 18
python3 timer.py measure CR full 18
python3 timer.py remove 5 0.35
python3 timer.py remove 6 0.94
python3 timer.py measure DU full 18
python3 timer.py regulate 0.34310824114398836
