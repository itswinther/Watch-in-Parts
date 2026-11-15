# Datasheet gaps, round 2: what real sources fill the eight open gaps

Written by Mikael + Claude (workstream A), 14 Nov 2026. Research only: no task file, datasheet or
existing document was changed. This follows `REAL_DATASHEETS.md` section 8 (its gap list) and
STANDARDS.md section 4.

**Method.** Web search and fetch, plus downloads run in Docker (`curlimages/curl`, text by `pypdf` in
`python:3.12-slim`) into a scratch folder outside the repo. Nothing downloaded is committed.

- **READ** means we read the value in the document text.
- **SNIPPET** means search-result text only, not verified.

**Labels** (as in REAL_DATASHEETS.md):

- **[PD]** public domain: US patent text, US-government work, or a pre-1930 publication.
- **[link-only]** copyrighted: cite and link, never commit.
- **primary / secondary:** maker, patent, standard or author versus forum, reseller or blog.

This is our reading of the terms, not legal advice.

---

## 0. Summary

| # | Gap | Status | Best source |
|---|---|---|---|
| 1 | Keyless tooth counts and modules | **Partly.** A full set exists in a PD textbook (worked example, not a named calibre). No modern calibre | Grossmann 1905, art. 168 to 169 [PD] |
| 2 | Mainspring torque curve | **Partly.** Two maker points and a slipping-bridle band, a PD curve shape, and the hysteresis | Sellita SW200-1 DocTec p. 3; AMCP 706-205 ch. 16 [PD]; US 11,320,786 [PD] |
| 3 | Jewel tolerances and loads | **Partly.** OD tolerance, interference and press-fit hold; Seitz friction formulas. No load rating | EPFL thesis 6665 (Laurenczy 2015) |
| 4 | Click, setting-lever and jumper forces | **Geometry and crown strength only.** No spring stiffness published | MIL-W-46374F [PD]; Britten 1896 [PD]; Hillmann 1910 |
| 5 | Stem travel outside Sellita | **Not filled.** Positions only | ETA, Seiko, Seagull: number of positions |
| 6 | Comfortable crown winding torque | **Partly.** A crown strength value of 42 mN·m from a military watch spec. "Comfortable" is still not published | MIL-W-46374F §3.3.7 [PD] |
| 7 | Barrel core ratio | **Filled** | Grossmann 1905, art. 108 to 111 and 310 [PD]; Saunier art. 517 [PD]; AMCP 706-205 [PD]; US 11,320,786 [PD] |
| 8 | Seiko 6R15 and Seagull ST36 documents | **Found** (third-party hosted copies) | Seiko 6R15B parts catalogue and technical guide (Boley); 6R15C/D (Cousins); ST3600K sheet |

---

## 1. Keyless tooth counts and modules

### Found

**A. Grossmann, *Lessons in Horology*, 1905 [PD, primary, READ].**

- **Source:** the copy already in the repo, `spikes/keyless/datasheets/public_domain/grossmann_lessons_1905_djvu.txt`;
  https://archive.org/details/lessonsinhorolog00gros
- These are worked textbook examples, not a named calibre, but the counts are realistic for a pocket
  watch of the time.

| Part | Teeth | Where |
|---|---|---|
| Cannon pinion | 12 leaves | art. 168, p. 112 to 113, Fig. 36 |
| Minute wheel | 30 | same |
| Main setting wheel | 27 | same |
| Small setting wheel | 18 | same |
| Sliding pinion (setting side) | 16 | same |
| Ratchet wheel | 44 | art. 169, p. 113 to 114, Fig. 37 |
| Crown wheel (spur teeth, to ratchet) | 42 | same |
| Crown wheel, crown teeth on the lower side | 38 | same |
| Winding pinion | 18 | same |

- **Art. 168:** the stem turns 12/16 = **¾ turn per turn of the minute hand**. Intermediate wheels do not
  change the ratio.
- **Art. 169:** for 3 ratchet turns (a 24 h wind), n = 3 × (44 × 38)/(42 × 18) = **6.63 stem turns**,
  which is about 2.2 stem turns per barrel turn.
  - Grossmann: "it is generally desired to have this number as large as possible", so that the force at
    the crown is smaller.
  - Compare the modern NH35: about 6.9 crown turns per barrel turn (REAL_DATASHEETS.md 1.4).
- **Art. 286 to 287, pp. 197 to 199, Figs. 77 to 79: tooth form.**
  - Crown wheel to ratchet gearing is epicycloidal, with play of only one-twentieth, rounded roots and
    shortened ogives.
  - Contact runs from 3/5 of the pitch before the line of centres to 3/5 after it.
  - Blank sizes: crown wheel n′ + 2½ and ratchet n + 2½ "division" (pitch units).
  - The crown wheel should be made proportionally the larger, since it drives.
  - We read the OCR's "2%" and "2^" as 2½. Check the page image before quoting this.

**B. M. Grossmann, *The Construction of a Simple but Mechanically Perfect Watch*, ch. XII, art. 162
[primary, historical, READ by a sub-agent].**

- **Values:**
  - winding pinion 12, crown wheel 24, spur (intermediate) wheel 40, barrel-arbor wheel 60, which gives
    a **ratio of 1/3**;
  - "in the majority of carefully designed keyless watches each revolution of the stem causes about a
    1/3 rotation of the barrel arbor";
  - art. 156: the pendant is at about 20° to the barrel (70° in a hunter case).
- **Licence:** the 19th-century German original is PD. The Watkins English translation is ©:
  **[link-only]**. https://www.abbeyclock.com/gbk/gbkt21.html

**C. Britten, *The Watch & Clockmakers' Handbook*, 1881 (and 1896) [PD, primary, READ (OCR)].**

- **Motion work:** cannon pinion 12, minute wheel 36, minute pinion 10, hour wheel 40, so 3 × 4 = 12.
  The table holds 12 sets, but its OCR is garbled; only this first set is reliable.
- **Shifting-sleeve and rocking-bar keyless work** are described in words, with no counts.
- **Motion-work tooth form:** for keyless motion work, where the followers drive while the hands are
  set, use a generating circle equal to twice the pitch (1896, "Wheel" entries).
- **URLs:**
  - https://archive.org/details/watchclockmaker00britgoog (1881)
  - https://archive.org/details/watchclockmaker01britgoog (1896, 9th ed.; `_djvu.txt` sha256
    `c9b20e5d366061ce8a1db6573676acc3e19cbdecd40b72e5c6eb206f8fd5d6f1`)

**D. US 3,131,531 (Stamm, 1964), description [PD, primary, READ].**

- The crown wheel's circular pitch is **twice** that of the ratchet wheel, so the crown wheel meshes
  with every second ratchet tooth.
- The ratio is "always an integer multiple". No absolute counts.
- https://patents.google.com/patent/US3131531A/en

**E. US 3,983,691 (A. Schild, 1976) [PD, primary, READ].**

- Date ring with 31 internal teeth; day star of 14 teeth.
- "The module of the pinion 58 is half that of the star 46."
- No keyless counts.
- https://patents.google.com/patent/US3983691A/en

**F. TM 9-1575, *Ordnance Maintenance: Watches* (US War Dept., 1945) [PD, primary, READ].**

- Escape wheel of 15 teeth at 10 rpm.
- The keyless parts are named, with no counts and no stem travel.
- https://archive.org/details/TM9-1575

**Rejected or unverified:**

- **ETA 2824-2: winding pinion 12, crown wheel 26, ratchet 63** (WatchUSeek thread). SNIPPET only: the
  page returned HTTP 402. https://www.watchuseek.com/threads/number-of-crown-turns-required-to-fully-wind-a-new-2824-2.808693/
- **Firgelli blog "bench-measured" counts:** the counts differed between fetches, and the page looks
  machine-written and unsourced. **Rejected.**

### Remains unfilled

- Tooth counts of the keyless works in any **modern named calibre** (ETA, Unitas, Valjoux, Sellita,
  Seiko, Miyota).
- **Modules** of keyless wheels.
- **The Breguet (clutch) tooth count and angle** of the sliding pinion.
- An automated full-text patent search was not possible from this session. Google Patents with the CPC
  class G04B 3/00, searched by hand in a browser, is the best remaining route.

### Recommendation

- Use the Grossmann 1905 counts (PD; may be quoted in the brief) as the **reference keyless train**.
- Set the module by our scale: real watch modules of about 0.05 to 0.2 mm [secondary, STANDARDS.md 4.1].
- Check the crown-to-barrel ratio against the modern makers' crown-turn figures:
  - Grossmann's 2.2 is a pocket-watch value, and art. 162 gives about 3;
  - modern calibres run about 6.9 (TMI NH35, and Seiko 4R57 and 8R48 by SNIPPET), Sellita about 27
    turns, Miyota 40.
- State the Breguet tooth geometry in the brief as "not published".

---

## 2. Mainspring torque against turns

### Found

| Value | Source | Status |
|---|---|---|
| **M½ max = 11.86 N·mm** (half a turn down from full wind) | Sellita SW200-1 DocTec rev 04 (02.02.2015), p. 3. Third-party copy: https://watch.co.uk/download/sw200-ml-pdf | primary, READ, [link-only] |
| **M24 min = 8.83 N·mm** (after 24 h; ratio 0.745) | same | READ |
| **Slipping-bridle torque 12.21 to 16.57 N·mm** (1.03 to 1.40 × M½) | same | READ |
| SW330-1: M½ 7.45, M24 5.98, slipping 7.70 to 10.44 N·mm. SW500: 8.53 / 7.06 / 8.53 to 12.00. SW1000: slipping 5.15 to 7.40 | Sellita DocTec (boley.de, sellita.ch) | SNIPPET only |
| Curve shape: torque 88 % of maximum at 40 % let down. Max torque G = σ·b·h²/6. Useful output about ½ of input. At most about 17 useful turns. Arbor Ø 15 to 25 × thickness | AMCP 706-205, *Timing Systems and Components* (US Army, 1975), ch. 16, pp. 16-4 to 16-7. https://everyspec.com/ARMY/ARMY-General/download.php?spec=AMCP_706-205_DEC1975.050858.pdf | [PD] text, READ. **Figs. 16-4 and 16-5 are reprinted from McGraw-Hill (Wahl) and Hunter Spring: do not copy them** |
| Hysteresis: "abrupt at the end of winding and the end of unwinding, but closer to a linear response in an intermediate range, one or two turns away from the end of winding" | US 8,356,930 B2 (Blancpain), description. https://patents.google.com/patent/US8356930B2/en | [PD], READ, no numbers |
| Unwinding over winding torque **≥ 80 %, 84 % measured** after half a turn. Spring 500 mm × 90 µm, core Ø 1.5 mm | US 11,320,786 B2 (Nivarox-FAR), summary, claim 7, FIG. 2. https://patents.google.com/patent/US11320786B2/en | [PD], READ |
| Unwinding torque "10 to 20 per cent less" than winding | Pook, *Coiled Springs as a Power Source*, ICMFF9 2009 | READ, [link-only] |
| Torque law with friction terms (K1, N0); amorphous against steel spring: 40 h against 45 h | US 6,843,594 (Seiko Epson), eq. 24, Fig. 4 | [PD], READ, curve qualitative |
| ETA 2824-2 spring "1300 g·mm" (about 12.7 N·mm); maximum at 7.2 barrel turns; about 0.3 J | DonCorson, WatchProSite "WatchTech 101.1", 2012 | secondary, READ |

### Remains unfilled

- A numeric torque-against-turns **table** for any watch calibre.
- Witschi, Greiner and Générale Ressorts curve data.
- DTIC AD0276037 (Hamilton, 1962) is PD but answered 403 to scripted fetches.

### Recommendation

- **Derive the curve** from Grossmann's linear law (art. 97) plus the Seiko friction term.
- **Anchor it to Sellita's two points:** 11.86 N·mm at ½ turn down, and 8.83 N·mm after 24 h.
- **Add the end effects** from US 8,356,930.
- **Unwinding:** 0.80 to 0.85 × winding (US 11,320,786).
- **Slipping bridle:** 1.03 to 1.40 × M½ (Sellita).
- **Cite Sellita as facts only.** Its documents are link-only, and the SW200-1 drawing pages are marked
  confidential (REAL_DATASHEETS.md 1.2).

---

## 3. Watch jewel tolerances and load ratings

### Found

**Primary source:** Laurenczy C., EPFL thesis no. 6665 (2015), READ, [link-only] ("tous droits
réservés"). https://infoscience.epfl.ch/record/210616/files/EPFL_TH6665.pdf?version=1

| Value | Where in the thesis |
|---|---|
| **Jewel OD tolerance 0 to +0.006 mm**, "prescribed by NIHS 41-02" | p. 34, Tab. 3.2 p. 37 |
| Measured OD σ 0.44 to 0.61 µm at nominal Ø 1.000 mm (3 lots, 2 suppliers); Cp 1.64 to 2.27 | Tab. 3.2 |
| **Typical interference i = 0.010 mm.** Hole Ø 1.002 mm in CuZn39Pb2, fit length 1.0 mm | Figs. 6.3 to 6.5, pp. 84 to 87 |
| Press fits at watch scale carry about 100 N and about 50 N·mm | p. 12 |
| Acceptance for screw-foot press fits: axial ≥ 15 N; torque ≥ 25 N·mm; position ≤ 2 µm | Tab. 2.1, p. 12 |
| Shock example: 70 mg × 5000 g gives an axial hold ≥ 3.4 N | eq. 2.1, pp. 13 to 14 |
| Press-in model Fc = µ·π·c1·i·z, with c1 = 0.66 GPa for brass on steel; inaccurate below about 3 mm | eqs. 2.3 to 2.5, Tab. 2.2, pp. 15 to 17 |
| Norms cited: NIHS 41-02 (2003); NIHS 94-10 (2009) = ISO 1112; DIN 7190 | bibliography (titles only) |

**Other sources:**

- **Seitz friction moments (Bird Precision, *Ring Jewel Bearings*, p. 1, Fig. 1, citing the Seitz guide,
  p. 20) [secondary, READ].** µ = 0.14 dry steel on ruby.

  | Hole or end | Friction moment |
  |---|---|
  | Straight hole | M = ⅓·µ·S·p |
  | Olive hole | ⅙·µ·S·p |
  | Flat end | ½·µ·S·p |
  | Radius end | 1/50·µ·S·p |

- **Bird, p. 2, Fig. 3: olive hole tolerates 2 to 5° misalignment** (3.41° at a 0.050″ olive radius,
  5.92° at 0.013″).
- **MIL-W-46374F §3.2.3.3.3, p. 5 [PD]:** jewels "solidly secured ... by friction fit"; at least 15
  functional jewels.
- **US 12,038,723 B2 (Rolex), description [PD]:** shock-absorber spring stiffness "less than 4 N/mm or
  less than 3 N/mm".
- **Sherwood, *Watch and Chronometer Jeweling* (1887) [PD text]:** side shake and endshake in words
  only.

### Remains unfilled

- A citable side-shake or endshake rule. Forums give about 0.01 mm side shake and 0.02 to 0.05 mm
  endshake (SNIPPET, anecdotal).
- **Any load rating or allowable contact pressure for a watch jewel.**
- Push-out or crushing force of a jewel.
- The NIHS 41-02 and 94-10 tables (paywalled).
- DTIC AD0276037 and AD0609922 (timer jewel bearings, PD): 403 to scripts. Fetch them by hand.

### Recommendation

- **OD tolerance:** 0/+6 µm (Laurenczy, citing NIHS 41-02).
- **Interference:** 10 µm.
- **Axial hold:** ≥ 15 N; torque ≥ 25 N·mm.
- **Friction:** Seitz formulas with µ = 0.14 to 0.15 (Grossmann art. 335 agrees).
- **Leave as "not published" in the brief:** side shake, endshake and jewel load rating. If a check needs
  a load bound, derive it from sapphire strength (as DS-301 already does) and say it is derived.

---

## 4. Click spring, setting-lever spring and jumper forces

### Found

| Value | Source | Status |
|---|---|---|
| Crown pull while moving from running to set: **withstand 5 ± 0.25 lb (22.2 ± 1.1 N)**. A strength test, not the operating force | MIL-W-46374F, *Watch, Wrist, General Purpose*, §3.3.6, p. 8 (test §4.7.13). https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-W/download.php?spec=MIL-W-46374F.021322.PDF | [PD], primary, READ (OCR, checked against the page image) |
| MIL-PRF-46374G (1999) keeps the test but no longer states the value | https://chrononautix.com/wp-content/uploads/2022/03/Mil-PRF-46374G.pdf | [PD], READ |
| Crown side load **5 N** for 5 min, immersed (water-resistance test) | ISO 2281:1984 §5.4.4 (free iTeh preview). Same 5 N in ISO 22810:2010 §4.3.4 and ISO 6425 | © ISO: cite only. 2281 READ; 22810 and 6425 SNIPPET |
| Ronda 5xx stem sheet: force min 10 N, max 15 N, probably the separation force of the two-piece stem | Ronda 509 documentation, p. 11 (Cousins copy) | primary, READ, [link-only]; meaning ambiguous |
| **Click geometry:** a line from the wheel centre through the click point should make **about 100°** with the line to the click pivot hole; with the hole much farther out, the click may jam or be forced off | Britten 1896, entry "Keyless: rocking-bar keyless mechanism" | [PD], primary, READ |
| Click geometry: **90°** between the line to the ratchet centre and the line to the click pivot (pivot on the tangent); for epicycloidal teeth make the click a little shorter | Hillmann, *Der Kronenaufzug* (1910), Watkins translation 2004, ch. II pp. 14 to 15. http://www.watkinsr.id.au/Hillmann.pdf | German original probably PD; translation [link-only] |
| Recoiling click: the click is allowed a little recoil before it butts on a pin, so that the mainspring is not strained | Britten 1896, same entry | [PD], READ |

### Remains unfilled

- **No stiffness (N/mm) or force** for the click spring, setting-lever spring, yoke spring or
  setting-lever jumper of any real calibre.
- No published operating force to pull the stem between positions in a mechanical movement.
- Patent searches in English and French (tirette, ressort de tirette, sautoir, bascule) found no
  numbers.

### Recommendation

- **Crown strength:** 22.2 N pull and 42 mN·m winding (section 6). This is a "must survive" floor, not
  an operating force.
- **Click angle band:** 90 to 100° (Hillmann, Britten).
- **Spring stiffness:** derive with the cantilever formula k = 3EI/L³ (E = 200 to 220 GPa, the DS-201
  steels) on the agent's own blade dimensions.
- **In the brief:** "spring forces not published; derived".

---

## 5. Stem travel and crown positions

### Found

- **ETA date calibres: 3 positions.** 1 running and winding, 2 quick date, 3 time setting with stop
  seconds (ETA technical sheets). SNIPPET; it agrees with the CT 2824-2 parts list we read for
  REAL_DATASHEETS.md.
- **Seiko 6R15B: 3 positions** (normal, first click, second click; primary, READ, see section 8).
  - Normal: wind by turning clockwise.
  - First click: date correction, counterclockwise.
  - Second click: time setting, with the second hand stopping.
- **Seagull ST3600K: 2 positions** ("Pull the crown out to the 1st position"), READ.
- **Grossmann (*Simple watch*), art. 156:** pendant angle only.

### Remains unfilled

- **Stem travel in mm for any calibre except Sellita (0.80 mm).**
- The Miyota 8215 and 5R sheets give clearances, not travel.
- Patents on 3-position jumpers (e.g. US 4,447,163; US 8,439,558) give no mm values (SNIPPET).

### Recommendation

- Keep the Sellita 0.80 mm as the only primary value, with the position counts above.
- State in the brief that "stem travel for other calibres is not published".
- If needed, read it off an ETA casing drawing ("plan d'encageage") by hand. These are not openly
  downloadable.

---

## 6. Comfortable crown winding torque

### Found

| Value | Source | Status |
|---|---|---|
| **No damage when the crown is turned against the fully wound spring at 6 ± 0.5 in-oz (42 ± 3.5 mN·m)** | MIL-W-46374F §3.3.7, p. 8 (test §4.7.12) | [PD], primary, READ |
| Elapsed-time bezel turning torque 26 ± 6 in-oz (180 ± 40 mN·m) | MIL-W-46374F §3.2.9.2 to 3, p. 8; MIL-PRF-46374G §3.4.4 | [PD], READ |
| Crown side load 5 N | ISO 2281 / 22810 / 6425 (section 4) | © ISO, cite only |

Already in REAL_DATASHEETS.md 6: MIL-STD-1472H, at most 32 mN·m for knobs ≤ 25 mm; Imrhan 2013, maximum
voluntary torque 69 to 155 mN·m at Ø 3.3 to 5 mm.

**Implied running torque at the crown [derived]:** Sellita's 11.86 N·mm ÷ about 6.9 to 27 crown turns
per barrel turn gives about 0.4 to 1.7 N·mm.

- Add the slipping bridle, 16.57 N·mm maximum: about 0.6 to 2.4 N·mm.
- That is well below the MIL 42 mN·m survival torque and the 32 mN·m knob maximum.

### Remains unfilled

- **A published "comfortable" winding torque.** No ergonomics study of watch crowns was found.
- ISO 22810 and 6425 have crown clauses on load and water resistance, not on torque.

### Recommendation

The brief should say:

- **comfortable:** "not published";
- **upper bound for operation:** 32 mN·m (MIL-STD-1472H);
- **survival:** 42 mN·m (MIL-W-46374F);
- **human maximum:** 69 mN·m and up (Imrhan).

DS-501's T_rec (20 % of the lowest measured maximum, capped at 32 N·mm) stays as the derived
recommendation.

---

## 7. Barrel core ratio

### Found (all READ)

| Rule or value | Source | Licence |
|---|---|---|
| "It is the custom, in practice, to make the radius of the hub equal to one-third of the interior radius of the barrel." The maximum turns come at r′ = √((R² + r²)/2), i.e. 2.236 for R = 3, r = 1 | Grossmann 1905, art. 108, p. 63 | [PD] |
| With ½ R spring, ⅙ R empty and ⅓ R hub: N = 5.7 / 6.1 / 6.6 turns for 13 / 14 / 15 coils | art. 110, p. 64 | [PD] |
| "Established by long practice": a larger hub gives too few turns; a smaller one, the spring breaks or "sets". Worked case: barrel ID 17.4 mm, hub Ø 5.8 mm, spring 0.18 mm, so **hub Ø ≈ 32 × spring thickness**. Outer-fibre strain limit 0.012 | art. 111, pp. 64 to 66 | [PD] |
| Second worked case: hub radius 3.66 mm = 17.777 × thickness; for a 0.188 mm spring the hub r = 3.34 mm; scale the hub with thickness | art. 310, p. 214 | [PD] |
| "Make the diameter of the nut equal to one-third that of the inside of the barrel", larger for thick springs and smaller for thin | Saunier, *Watchmaker's Hand-Book*, art. 517 (Gutenberg 76850) | [PD] |
| Arbor Ø "fifteen to twenty-five times the spring thickness"; spring area = ½ (drum area − arbor area) | AMCP 706-205, p. 16-5, eq. 16-2 | [PD] (US Army) |
| Modern spring: **core Ø 1.5 mm with t = 0.09 mm, so d/t ≈ 16.7**; eye Ø "typically comprised between 1 mm and 1.5 mm" | US 11,320,786 B2 (Nivarox-FAR) | [PD] |
| r/t = 16 (Defossez), earlier 14, today down to about 10; r is ¼ to ⅓ of R; fill up to 55 % | watchesbysjx 2025 (D. Ichim) | secondary, [link-only] |

### Recommendation

**Fill from these sources.** The rule is r_core = R/3, with d_core/t between about 17 (modern Nivarox)
and 32 (classical: Grossmann and Defossez). AMCP's 15 to 25 sits between them.

This supports DS-101's two core ratios of 12·t and 16·t (radius, i.e. d/t = 24 and 32). Grossmann
art. 111 and US 11,320,786 can now be cited as [PD] primary sources instead of the secondary
watchesbysjx.

---

## 8. Official documents for the Seiko 6R15 and Seagull ST36

| Doc | URL | sha256 | Status |
|---|---|---|---|
| Seiko **Cal. 6R15B Parts Catalogue / Technical Guide**, 19 pp. (SII format) [secondary host: Boley] | https://boley.de/downloads/c6941cc257f2415f8f8c5a0e532f807f/HATTORY-SEIKO-6R15.pdf | `03787aa550ae4a6723464d0aae045738086c71c4e8dc65f6495b8fe379e94a0d` | READ, [link-only] |
| Seiko 6R15C/D Parts Catalogue / Technical Guide [secondary host: Cousins] | https://www.cousinsuk.com/pdf/categories/8955_pao024_14267_191030121314_1_6r15cd.pdf | not fetched | SNIPPET |
| Seiko 6R15A, 6R15C (ManualsLib) | https://www.manualslib.com/manual/1578259/Seiko-6r15a.html | n/a | SNIPPET |
| **Seagull ST3600K** movement sheet and instruction manual, 2 pp. [retailer's Shopify host; origin not verified] | https://cdn.shopify.com/s/files/1/0273/4289/7255/files/SeagullST3600K.pdf | `7a0cd534d64e8aeb365fcab4b56908cdda153dc52fb447ef066e7854ac9b1c78` | READ, [link-only] |

**Seiko 6R15B values (p. 1).**

- Ø 27.0 mm, casing Ø 27.4 mm, height 5.25 mm, 23 jewels.
- Accuracy -5 to +25 s/day; 3 hands, date, instant date setting, second setting.
- "Automatic winding with auxiliary hand winding mechanism".
- Crown positions as in section 5.
- **Keyless parts with codes:** clutch wheel 0282 040, winding pinion 0283 020, ratchet wheel 0285 05,
  click 038 004, yoke 0384 06, yoke spring 0388 07, setting lever 0383 060.
- The rate prints as "2,600" in the PDF text: a font-extraction loss. It is 21,600 A/h, a value not
  read from this document.
- **Not in the text layer:** power reserve and crown turns to full wind. Check the page images.

**Seagull ST3600K values:**

- 21,600 A/h, 17 jewels, about 42 h, -20 to +40 s/day;
- 2 crown positions.

No Tianjin Seagull-hosted document was found. Ø 36.6 mm and 4.5 mm come from retailers only (SNIPPET).

**Recommendation:** cite the 6R15B guide as a primary Seiko document on a secondary host. Treat the
ST3600K sheet as secondary, and keep the Unitas 6497-2 CT (REAL_DATASHEETS.md 1.1) as the authority for
that layout.

---

## 9. Public-domain texts worth committing

| Text | URL | Keyless value |
|---|---|---|
| **Grossmann, *Lessons in Horology* (1905)**: already committed | https://archive.org/details/lessonsinhorolog00gros | Keyless tooth counts (art. 168 to 169), keyless tooth forms (art. 286 to 287), core ratio (art. 108 to 111, 310), torque law |
| **Britten, *Watch & Clock Makers' Handbook*, 9th ed. (1896)** | https://archive.org/download/watchclockmaker01britgoog/watchclockmaker01britgoog_djvu.txt | Click angle about 100°, recoiling click, rocking-bar and shifting-sleeve keyless work, motion-work tooth form |
| Britten, 1881 ed. | https://archive.org/details/watchclockmaker00britgoog | Motion-work tooth-count tables |
| **AMCP 706-205, *Timing Systems and Components* (US Army, 1975)**, ch. 16 text | https://everyspec.com/ARMY/ARMY-General/download.php?spec=AMCP_706-205_DEC1975.050858.pdf (75 MB) | Power-spring torque, curve shape, efficiency, arbor ratio. **Do not copy Figs. 16-4 and 16-5** (third-party ©) |
| **MIL-W-46374F, *Watch, Wrist, General Purpose*** (scan; needs OCR) | https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-W/download.php?spec=MIL-W-46374F.021322.PDF | Crown pull 22.2 N, winding torque 42 mN·m, jewel fixing |
| MIL-PRF-46374G (1999) | https://chrononautix.com/wp-content/uploads/2022/03/Mil-PRF-46374G.pdf | Test methods |
| TM 9-1575, *Ordnance Maintenance: Watches* (1945) | https://archive.org/details/TM9-1575 | Names and service of the keyless parts |
| US patents 11,320,786 (Nivarox mainspring); 8,356,930 (Blancpain hysteresis); 6,843,594 (Seiko Epson); 3,131,531 (crown-wheel pitch) | patents.google.com | Torque, efficiency, core Ø, pitch ratio |
| Saunier, *Watchmaker's Hand-Book* (Gutenberg 76850): already committed | https://www.gutenberg.org/ebooks/76850 | Arbor nut = ⅓ barrel ID |
| Sherwood, *Watch and Chronometer Jeweling* (1887) | Use an original scan, not the 2023 re-typeset edition (© typesetting) | Jewelling practice (qualitative) |
| DTIC AD0276037 and AD0609922 (timer jewel bearings, mainsprings) | https://apps.dtic.mil/ (403 to scripts; fetch by hand) | Likely jewel clearances and timer-spring torque |

## 10. Not verified

- Grossmann's "2½" addendum (OCR).
- The Sellita SW330, SW500 and SW1000 numbers (SNIPPET).
- Whether the Ronda 10 to 15 N applies to the stem separation.
- The ETA 2824-2 12/26/63 counts (WatchUSeek, unread).
- The 6R15B rate digit and reserve (text layer).
- The ISO 22810 and 6425 clause numbers (SNIPPET).
- Seagull ST36 dimensions.
