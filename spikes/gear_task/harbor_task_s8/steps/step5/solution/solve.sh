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
  ],
  "minute": [
   -1.539081,
   0.437298
  ],
  "date": [
   0.844493,
   3.499547
  ],
  "wind1": [
   -0.057154,
   2.029195
  ],
  "wind2": [
   -2.23376,
   3.451301
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
  },
  "cannon_pinion": {
   "teeth": 8,
   "module": 0.08,
   "dial_level": 0
  },
  "minute_wheel": {
   "teeth": 32,
   "module": 0.08,
   "dial_level": 0
  },
  "minute_pinion": {
   "teeth": 10,
   "module": 0.08,
   "dial_level": 1
  },
  "hour_wheel": {
   "teeth": 30,
   "module": 0.08,
   "dial_level": 1
  },
  "date_wheel": {
   "teeth": 60,
   "module": 0.08,
   "dial_level": 1
  },
  "rotor_pinion": {
   "teeth": 11,
   "module": 0.07,
   "wind_level": 0
  },
  "wind1_wheel": {
   "teeth": 47,
   "module": 0.07,
   "wind_level": 0
  },
  "wind1_pinion": {
   "teeth": 12,
   "module": 0.08,
   "wind_level": 1
  },
  "wind2_wheel": {
   "teeth": 53,
   "module": 0.08,
   "wind_level": 1
  },
  "wind2_pinion": {
   "teeth": 12,
   "module": 0.08,
   "wind_level": 2
  },
  "ratchet_wheel": {
   "teeth": 56,
   "module": 0.08,
   "wind_level": 2
  }
 },
 "escape_wheel_level": 3
}
JSON
