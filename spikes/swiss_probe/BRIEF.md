# Program a Swiss-type lathe to make a watch arbor

You are a CNC programmer. Write the part program for the arbor below, for the machine described
here, and explain your sequence of operations. Answer in text only: you have no files and no tools,
and there is no simulator. Reason it out as you would for a real job.

## The part (steel, all diameters ±0.003 mm, lengths ±0.01 mm; dimensions in mm, from the front end)

| Section | From z | To z | Diameter |
|---|---|---|---|
| Front pivot | 0.00 | 0.80 | 0.30 |
| Shoulder | 0.80 | 3.80 | 0.80 |
| Wheel seat | 3.80 | 4.40 | 1.00 |
| Pinion blank | 4.40 | 5.60 | 1.60 |
| Rear pivot | 5.60 | 6.40 | 0.30 |

Bar stock: Ø2.00 round steel, E = 210,000 N/mm². Total part length 6.40.

## The machine (sliding-headstock Swiss-type, Fanuc-style G-code)

- **Main spindle and guide bushing.** The bar is clamped in the main spindle, which slides along Z
  behind a fixed guide bushing. The bushing supports the bar at its face (z of the bushing face =
  0 in machine coordinates). **+Z moves the headstock so that more bar comes out of the bushing.**
  Tools on the gang slide move only in X (diameter) and stay just in front of the bushing face.
  The free length of bar in front of the bushing is the current Z position.
- **Tools cut 0.5 mm in front of the bushing face.** So when the headstock is at Z, the tool is at
  distance Z − 0.5 from the front end of the bar.
- **Maximum free stickout while cutting: 3.0 mm** from the bushing face, because longer free
  lengths chatter. The only exception: while the sub-spindle is gripping the part and turning in
  synchronisation with the main spindle, stickout may go up to 12.0 mm.
- **Gang tools (X axis, main side):** T01 turning tool, T02 finishing tool (nose radius 0.02),
  T03 parting tool, width 0.5.
- **Sub-spindle:** on the other side, moves in Z2 and X2, can grip a diameter of 0.6 to 2.0 and
  synchronise with the main spindle (M-code M77 sync on, M78 off; M10/M11 sub chuck clamp/unclamp).
  After parting, the sub-spindle can present the part to **T21**, a back-working turning tool
  that can finish diameters on the part held in the sub-spindle.
- **Spindle speed:** max 10,000 rpm on both spindles. G96 constant surface speed is available with
  a G50 S limit.
- Codes: G00/G01 moves, X is diameter, F in mm/rev, G96/G97, M03 spindle on, M05 off, M30 end.

## What to return

1. The ordered list of operations, with the reason for the order.
2. The program (G-code, comments allowed).
3. Any check you make that every limit above is respected at every step.
