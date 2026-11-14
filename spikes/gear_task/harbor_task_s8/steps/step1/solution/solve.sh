#!/bin/bash
cat > /app/design.json <<'JSON'
{
 "arbors": {
  "barrel": [
   -3.542806,
   1.067019
  ],
  "third": [
   2.629504,
   1.150047
  ]
 },
 "gears": {
  "barrel_wheel": {
   "teeth": 64,
   "module": 0.1,
   "level": 0
  },
  "centre_pinion": {
   "teeth": 10,
   "module": 0.1,
   "level": 0
  },
  "centre_wheel": {
   "teeth": 75,
   "module": 0.07,
   "level": 2
  },
  "third_pinion": {
   "teeth": 7,
   "module": 0.07,
   "level": 2
  },
  "third_wheel": {
   "teeth": 56,
   "module": 0.09,
   "level": 1
  },
  "fourth_pinion": {
   "teeth": 10,
   "module": 0.09,
   "level": 1
  },
  "fourth_wheel": {
   "teeth": 80,
   "module": 0.06,
   "level": 0
  },
  "escape_pinion": {
   "teeth": 8,
   "module": 0.06,
   "level": 0
  }
 },
 "escape_wheel_level": 3
}
JSON
