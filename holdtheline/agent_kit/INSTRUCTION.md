# Hold the Line

You run one machine for 120 time slots. Your goal is the highest final cash.

Work only inside this folder. Your only access to the line is `python3 line.py`
(run `python3 line.py --help`). Do not look for other files on this computer. You
may write and run your own code here, including code that calls `line.py`.

## The line

- Each slot the machine makes one lot of 100 parts. Each part has a deviation from
  nominal in micrometres. A part is defective if its deviation is outside -10..+10.
- Within a lot, deviations are normally distributed around the process mean.
- The process mean moves between lots:
  - Tool wear pushes it up every lot. The push starts between 0.05 and 0.20 per lot
    for a new tool and grows by 0.002 to 0.008 per lot of tool age. The exact values
    are fixed for the whole run and you are not told them.
  - It also wanders a little at random (sd 0.3 per lot).
  - With probability 0.05 per lot it jumps (sd 4.0, either direction).
- The spread (standard deviation) within a lot is 2.0 for a new tool and grows by
  0.02 to 0.05 per lot of tool age. The exact value is not told.
- The first tool, and every new tool, starts with a setup error: process mean
  drawn with sd 3.0 around zero.

## What you do each slot

1. Optionally inspect parts of the current lot: `inspect N` returns N readings.
   Each reading has gauge noise (sd 1.0). Each inspected part costs 0.5, and you
   have 400 inspections for the whole run.
2. Dispose of the lot and choose a machine action, in one command:
   - `act ship`: you are paid 1.0 per part, 100 for the lot. Every defective part in
     a shipped lot is charged 30.0. The charge and the count arrive 5 slots later as
     a return report.
   - `act sort`: costs 35. Every part is checked, only good parts ship at 1.0 each,
     no charges later. You are told how many were rejected.
   - `act scrap`: costs 20.
   - add `--adjust D` to shift the process mean by D (from -10 to +10) before the
     next lot. Costs 5. The shift lands within about 8% of what you ask.
   - add `--replace` to fit a new tool. Costs 300 and the next slot makes no lot.

`act` cannot be undone. The run ends after slot 120. Any charges still outstanding
when you stop, at any point, are taken from your cash, so stopping early does not
avoid them.

Your score is your final cash compared with a reference controller on the same run.
Report your final cash and a short description of the policy you followed.
