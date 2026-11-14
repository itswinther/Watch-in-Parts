# Task: stage 1 of 4, design

Design the gear train of a mechanical wristwatch. The mainspring barrel is
supplied in `meshes/barrel.stl`; it turns clockwise once every 8 hours. Drive the
hour, minute and seconds hands from it. There is no escapement.

`SPEC_WATCH.md` gives the file format, the supplied barrel, the size limit and
every mechanical test with its numbers. Three more engineers will work on your
movement after you: one adds a 24-hour hand without changing your wheels, one
reworks it for a faster barrel while keeping as many of your part files as it
can, one assembles it part by part. Their rules are in the same document.

Parts are STEP files made with CadQuery (see "What you submit" in the spec). Write your parts and `movement.json` into `work/`, then submit as the spec
describes. Only the last accepted submission is graded, by a separate program.
You have about 35 minutes.

## How you are run

You run unattended in one session. Run everything in the foreground and do not
end your turn while a job of yours is still running: nothing will wake you up.
You are stopped 39 minutes after you start, whatever you are doing. Whatever is in
the submission folder at that moment is what gets graded, so submit a first
version early and resubmit when it improves.
