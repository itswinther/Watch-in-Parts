# Swiss-lathe probe: scoring rubric, written before any model answered

Sources for the practice behind each item:
- [MMS, "How Swiss-Type Machining is Different"](https://mmsonline.com/articles/how-swiss-type-machining-is-different): on a Swiss lathe a longer turn is a Z-plus move.
- [Production Machining, "Swiss-type machining tips"](https://productionmachining.com/blog/post/swiss-type-machining-tips) and [CTE, "Let precision be your guide"](https://ctemag.com/articles/let-precision-be-your-guide/): the guide bushing supports the bar next to the cut, and its land limits travel per pass.
- [CTE, "Time: Swiss precision"](https://ctemag.com/articles/time-swiss-precision/): watch pinions and pivots are under 1 mm and made on Swiss-types because the cut stays next to the support.

Each item is pass or fail, and is judged from the program and the explanation (revised before any model answered: the cut is always at the bushing, so the stated limit that bites is stickout):

1. **Z convention.** It uses the stated convention: +Z feeds bar out, and the tool sits 0.5 in front of the bushing.
2. **Stickout limit.** It never cuts with free stickout above 3.0. The part is 6.4 long (plus the parting width), so this is impossible without the sub-spindle: it must notice that.
3. **Sub-spindle pickup mid-job.** It grips the part with the sub-spindle in sync (M77 before clamping) before stickout passes 3.0, on a diameter of 0.6 to 2.0 (the Ø0.8 shoulder or a larger section; never the Ø0.30 pivot).
4. **Sync discipline.** Both spindles turn at the same speed while gripped. No spindle-speed or direction change on one side only, and no G96 on a gripped part with spindles out of sync.
5. **Parting with support, rear pivot handled.** It parts off while gripped, and either turns the Ø0.30 rear pivot before parting while supported, or back-works it with T21 after parting. It does not leave the finished part hanging unsupported on a 0.30 neck.
6. **Order of operations.** The front pivot is cut first, the sections follow as the bar feeds out, the parting width is accounted for, and the pinion blank keeps full stock until it is turned.
7. **Speed.** It respects 10,000 rpm max (G50 limit with G96). A sensible surface speed at Ø0.30 forces the rpm limit.
8. **Dimensions and tools.** Finishing lands on drawing diameters and lengths, and it uses only T01, T02, T03 and T21.

Expert answer, in outline: turn the front pivot, then the shoulder, feeding out to at most 3.0. Sync and grip the shoulder with the sub-spindle. Continue the wheel seat and pinion blank with support (stickout up to 12). Either turn the rear pivot with support and then part off, or part off and back-work the rear pivot with T21. Spindle limited by G50 S10000.
