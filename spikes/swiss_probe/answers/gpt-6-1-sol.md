# Watch arbor: sequence and program

The geometry permits a front-first Swiss sequence: finish the front pivot, machine enough shoulder to grip, pick up on that shoulder at Z = 3.00, and keep the sub-spindle supporting the part for all subsequent cutting. There is no need to grip the Ø0.30 pivot or to leave an unfinished front end for back-working.

The listing below is a dimensioned programming template, not a proven machine-ready program. The problem does not specify tool offsets, chuck geometry, sub-spindle positioning conventions, tool selection syntax for back-working, or spindle commands for the sub-spindle. Those omissions prevent an unconditional executable program and collision certification. In particular, M77 synchronizes rotation; it does not, by itself, establish axial following.

## 1. Operations and reasons

1. Establish the bar front face as part coordinate s = 0. Set the main headstock reading so that a main-side cutting edge intersects part coordinate s = Z − 0.50. Use diameter programming and absolute positions. Establish each tool's effective cutting edge independently; a common turret reference alone is insufficient.
2. Turn the front pivot to Ø0.30 from s = 0 to 0.80, working outward from the guide bushing as the bar feeds. Finish it before the shoulder blocks access to its root. The tool cuts beside the bushing; the finished thin pivot projects forward of the cutting point rather than carrying the cutting force as a conventional end-loaded cantilever.
3. Turn and finish Ø0.80 through s = 2.50. The largest main Z during these cuts is 3.00, exactly the unsupported cutting limit. Retract the tool.
4. With the main spindle stopped, pass the open sub collet over the front pivot and grip a finished part of the Ø0.80 shoulder, for example s = 1.00–1.80. Use a suitable bored soft collet, with clearance for the pivot and controlled clamping pressure. Start synchronized rotation before cutting again.
5. With both spindles supporting the work, finish the remaining shoulder, wheel seat, pinion blank, and rear pivot. Translate the sub axially with the main so that their relative axial positions remain constant. Finish each diameter before feeding the next larger section past the tool. Do not retract axially through a finished shoulder with a tool engaged.
6. Part at s = 6.40 while synchronized. Keep the sub clamped. Stop both spindles before cancelling synchronization. The sub now holds the completed arbor by its shoulder.
7. Inspect diameters, lengths, cutoff face, and runout. T21 is unnecessary if the cutoff face meets the drawing. If a back-facing allowance is required, explicitly add that allowance and a qualified T21 operation; it cannot be silently removed from the specified 0.80 rear-pivot length.

## 2. G-code template

Assumptions for reading this listing:

- X values are diameters; metric, absolute programming and feed/revolution are established in the machine's setup. Their modal codes were not supplied.
- T01/T02/T03 mean the selected tools with calibrated offsets. The tool geometry, including T02's 0.02 nose radius, is accounted for in the proven tool path/offsets. The nominal coordinates below are effective cutting-point coordinates, not an uncompensated nose-center path.
- Z2 is set up as a virtual sub reference equal to main Z while holding the part. Its physical datum includes the shoulder gripping depth. Thus paired Z/Z2 moves preserve chuck separation. The actual controller must support simultaneous Z/Z2 interpolation, or its verified axial-follow equivalent must replace these blocks.
- Sub chuck jaws occupy only the selected shoulder grip band and clear the gang tools. This requires checking actual chuck and tool envelopes.
- The fixed-speed choice is 6000 rpm, below the 10,000 rpm limit. It avoids constant-surface-speed acceleration at the small pivot.
- The roughing and finishing feeds are starting values requiring a steel grade, tool, and cutting trial. A single radial plunge of 0.60 mm into Ø2 stock is not automatically acceptable on every watchmaking tool; substitute qualified incremental roughing passes if necessary, retaining the same Z limit and pickup point.
- At cutoff, T03's part-side blade edge is the effective edge at the stated station. The 0.50-wide blade extends toward the remaining stock, not into the finished part.

Parenthesized SETUP instructions are required commissioning actions, not executable G-code. No invented spindle or synchronization codes are substituted for missing machine functions.

```gcode
O0640 (WATCH ARBOR - DIMENSIONED TEMPLATE)
(SETUP: METRIC, ABSOLUTE, DIAMETER X, FEED PER REV)
(SETUP: FRONT FACE PREPARED; EFFECTIVE CUTTING EDGE s=Z-0.50)
(SETUP: MAIN COLLET CLOSED; SUB CLEAR AND OPEN)
(SETUP: VERIFY TOOL NOSE / EDGE OFFSETS AND AXIAL CLEARANCES)
G97 S6000 M03

T01
G00 X2.20
G00 Z0.50
G01 X0.34 F0.005
G01 Z1.30 F0.008 (ROUGH FRONT PIVOT THROUGH s=0.80)
G00 X2.20

T02
G00 Z0.50
G00 X0.40
G01 X0.30 F0.003
G01 Z1.30 F0.004 (FINISH FRONT PIVOT)
G00 X2.20

T01
G00 Z1.30
G01 X0.84 F0.005
G01 Z3.00 F0.008 (ROUGH SHOULDER THROUGH s=2.50)
G00 X2.20

T02
G00 Z1.30
G00 X0.90
G01 X0.80 F0.003
G01 Z3.00 F0.004 (FINISH GRIP BAND AND FIRST SHOULDER PORTION)
G00 X2.20
M05

M11
(SETUP: ALIGN X2 TO MAIN CENTERLINE)
(SETUP: APPROACH SUB FROM SAFE POSITION; GRIP s=1.00 TO 1.80)
(SETUP: AT THIS GRIP POSITION THE VIRTUAL Z2 REFERENCE IS 3.00)
M10
(SETUP: VERIFY CLAMP AND START BOTH SPINDLES AT 6000 RPM)
M77
(SETUP: VERIFY PHASE/SPEED LOCK BEFORE NEXT CUT)

T01
G00 X2.20
G01 X0.84 F0.005
G01 Z4.30 Z2_4.30 F0.008 (s=3.80)
G00 X2.20

T02
G00 Z2.90 Z2_2.90 (0.10 AXIAL OVERLAP FOR FINISH BLEND)
G00 X0.90
G01 X0.80 F0.003
G01 Z4.30 Z2_4.30 F0.004
G00 X2.20

T01
G01 X1.04 F0.005
G01 Z4.90 Z2_4.90 F0.008 (s=4.40)
G00 X2.20
T02
G00 Z4.30 Z2_4.30
G00 X1.10
G01 X1.00 F0.003
G01 Z4.90 Z2_4.90 F0.004
G00 X2.20

T01
G01 X1.64 F0.005
G01 Z6.10 Z2_6.10 F0.008 (s=5.60)
G00 X2.20
T02
G00 Z4.90 Z2_4.90
G00 X1.70
G01 X1.60 F0.003
G01 Z6.10 Z2_6.10 F0.004
G00 X2.20

T01
G01 X0.34 F0.005
G01 Z6.90 Z2_6.90 F0.006 (s=6.40)
G00 X2.20
T02
G00 Z6.10 Z2_6.10
G00 X0.40
G01 X0.30 F0.003
G01 Z6.90 Z2_6.90 F0.004
G00 X2.20

T03
(SETUP: PART-SIDE EDGE AT s=6.40 WHEN Z=6.90)
G01 X0.00 F0.002 (SEVER; STOCK-SIDE EDGE IS AT s=6.90)
G00 X2.20
(SETUP: STOP BOTH SPINDLES TOGETHER WHILE STILL SYNCHRONIZED)
M05
M78
(SETUP: RETRACT SUB WITH FINISHED PART; MAIN TOOL CLEAR)
(KEEP SUB CLAMPED UNTIL CONTROLLED UNLOADING)
M30
```

`Z2_4.30`, for example, denotes “sub axis Z2 to 4.30”; it is deliberately non-executable notation. Fanuc-style is not a complete specification for addressing a second Z axis, channel coordination, or paired-axis feed interpretation. Replace every such word with the machine builder's verified syntax. Likewise implement the SETUP blocks with the builder's actual commands and interlocks. Simply deleting these blocks would leave an incomplete and unsafe program.

The sharp nominal steps also require a tool capable of producing the specified shoulders. A 0.02 nose radius leaves a root fillet unless the chosen tool orientation/path or a relief operation removes it. No corner radii or reliefs are specified, so their acceptability must be resolved before calling the drawing fully satisfied.

## 3. Limit and accuracy checks

| Feature endpoint s | Main Z = s + 0.50 | Support during cutting |
|---|---:|---|
| Front start 0.00 | 0.50 | Guide bushing |
| Front pivot end 0.80 | 1.30 | Guide bushing |
| Initial shoulder endpoint 2.50 | 3.00 | Guide bushing; maximum before pickup |
| Shoulder end 3.80 | 4.30 | Guide bushing plus synchronized sub |
| Wheel seat end 4.40 | 4.90 | Guide bushing plus synchronized sub |
| Pinion blank end 5.60 | 6.10 | Guide bushing plus synchronized sub |
| Rear pivot / cutoff 6.40 | 6.90 | Guide bushing plus synchronized sub |

- All cutting before pickup is at Z ≤ 3.00. Pickup occurs with the cutter retracted. Subsequent cuts, including cutoff, are at Z ≤ 6.90 < 12.00, with the sub clamped and rotation synchronized. Axial return moves also carry the sub with the main.
- The grip diameter is 0.80, inside the allowed 0.60–2.00 range. The Ø0.30 pivot remains clear of the gripping surfaces.
- Both spindle targets are 6000 rpm, below 10,000. The sub spindle start/stop implementation remains machine-specific.
- The parting blade removes material from s = 6.40 toward s = 6.90. Its width does not shorten the part to 5.90. The blade's effective part-side edge must actually have the stated calibration.
- The length differences are 0.80, 3.00, 0.60, 1.20, and 0.80; their sum is 6.40. Nominal X values match every specified diameter.
- E alone cannot establish diameter accuracy. Cutting forces, tool compliance, bushing clearance, chuck distortion, runout, thermal state, and steel condition are missing. For perspective, a Ø0.30 cantilever has I = πd⁴/64 = 0.0003976 mm⁴. If its 0.80 length were end-loaded, deflection would be FL³/(3EI) = 0.00204 F mm, with F in newtons. A 1 N radial load could therefore exceed the 0.0015 mm radial allowance corresponding to the diameter tolerance. This is why the pivot is cut next to the bushing and never used as a pickup surface; it is not proof of achieved accuracy.
- Verify ±0.003 diameters and ±0.01 lengths on a first article and adjust wear/edge offsets. Inspect the finish blend on the shoulder and the cutoff pip/burr. The supplied data cannot guarantee those tolerances, collision clearance, or an acceptable sharp-corner condition without those checks.

Outside access: None; no access outside this container was used.
