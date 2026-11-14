# Regulate a watch

A finished mechanical watch is on a timing machine. Bring it to chronometer standard: as
close to 0 s/day as possible in every position and at both full wind and after 24 hours, with
the rates in all conditions as close to each other as possible.

Your only access to the watch is the command line in `/app`:

    python3 /app/timer.py status
    python3 /app/timer.py measure POSITION WIND MINUTES
    python3 /app/timer.py regulate INDEX
    python3 /app/timer.py remove SCREW MG
    python3 /app/timer.py washer SCREW

You may write and run your own code in `/app`. There is no internet access. If you read,
fetch or use anything other than this brief, the files in `/app` and the timing machine,
say so in your final message.

## The watch and the timing machine

- Positions: `DU` dial up, `DD` dial down, and four vertical positions with the crown up,
  down, left and right: `CU`, `CD`, `CL`, `CR`. Winds: `full` (just wound) and `24h`.
- A measurement reports the rate (s/day, positive = gaining) and the balance amplitude
  (degrees). Longer measurements are less noisy: the rate noise is about 1.2 s/day for a
  60-minute run and grows as 1/sqrt(minutes); amplitude noise is about 3 degrees.
  Each measurement costs its duration plus 1 minute; you have 100 minutes in total.
- The balance has 8 timing screws on its rim, screw `n` at angle 45 x n degrees, in the same
  plane and orientation as the vertical positions (crown right `CR` points along 0 degrees,
  crown up `CU` along 90 degrees).

## Physics (structure exact; the numbers belong to this watch and must be measured)

    amplitude(p, w) = A0 - dV (if p is vertical) - dW (if w is 24h)
    rate(p, w)      = R + K_iso * (amplitude - 250) / 100
                      + H (DU) or -H (DD) or 0 (vertical)
                      + (u . g_p) * 400 * J1(a) / a        (vertical positions only)

- `a` is the amplitude in radians; J1 is the Bessel function of the first kind, order 1.
- `g_p` is the unit direction of gravity's pull in the balance plane for the vertical position:
  `CU` (0, 1), `CD` (0, -1), `CL` (-1, 0), `CR` (1, 0).
- `u` is the balance's unbalance (poise error) vector, in mg.
- `R = R0 + 60 x + 9 x (mg removed) - 9 x (mg of washers added)`, where `x` is the regulator
  index (-1 to 1).

## Adjustments

- `regulate INDEX`: set the regulator index `x` (-1 to 1). It lands within about 0.004 of the
  request. Reversible.
- `remove SCREW MG`: remove 0.05 to 1.0 mg at a screw (at most 3.0 mg in total). Removing mass
  at angle t changes `u` by -m x (cos t, sin t) and makes the watch faster. The amount removed
  is within about 8% of the request. **It cannot be undone.**
- `washer SCREW`: add a 0.5 mg timing washer at a screw: changes `u` by +0.5 x (cos t, sin t)
  and makes the watch slower. You have 4.

## Score

When you finish, the watch's true rates in all 12 conditions (6 positions x 2 winds) are
computed without noise. The error is the worst absolute rate plus the spread between the
fastest and slowest condition. Your score compares that error with the untouched watch's and
with a reference watchmaker's on the same watch: 0 means no better than untouched, 1 means as
good as the reference or better.

End by stating what you measured, what you changed, and the rates you expect now.
