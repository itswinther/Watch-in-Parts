# How to run Replay

Replay shows, for each AI run on the final task, what the AI delivered, what it said about
its own work, and what the grader found. It is a web page: nothing to install, no account,
no build step. It needs a modern browser (Chrome, Edge, Firefox or Safari) and an internet
connection, because the 3D library (three.js) and the fonts load from the web.

## Option A: open it from a link

If the team has turned on GitHub Pages for this repository, Replay is at:

**https://itswinther.github.io/Watch-in-Parts/visualizer/**

If that link shows a 404 page, Pages is not on; use option B.

## Option B: run it on your computer

### 1. Download

Pick one:

- **Without git (easiest).** Go to https://github.com/itswinther/Watch-in-Parts, click the green
  **Code** button, then **Download ZIP**. The ZIP holds the whole project (about 275 MB unpacked).
- **With git, only the Replay folder** (about 100 MB):

  ```
  git clone --depth 1 --filter=blob:none --sparse https://github.com/itswinther/Watch-in-Parts.git
  cd Watch-in-Parts
  git sparse-checkout set visualizer
  ```

### 2. Unpack (ZIP only)

- **Mac:** double-click the ZIP in Downloads. You get a folder `Watch-in-Parts-main`.
- **Windows:** right-click the ZIP, choose **Extract All…**, then **Extract**. Do not open the
  page from inside the ZIP without extracting it first: Windows then shows only a blank page.

### 3. Open

Open the folder `visualizer` and double-click **`index.html`**. It opens in your default browser.

- **Mac:** `Watch-in-Parts-main/visualizer/index.html`
- **Windows:** `Watch-in-Parts-main\visualizer\index.html`

That is all. If the page opens but the 3D watch stays empty, use step 4.

### 4. Only if the 3D stays empty: start a small local web server

Some browsers limit pages opened straight from a folder. A local web server avoids that.
It needs Python 3, which Macs usually have.

**Mac** (open the Terminal app):

```
cd ~/Downloads/Watch-in-Parts-main/visualizer
python3 -m http.server 8000
```

**Windows** (open PowerShell from the Start menu):

```
cd $HOME\Downloads\Watch-in-Parts-main\visualizer
py -m http.server 8000
```

If Windows says `py` is not found, install Python from https://www.python.org/downloads/
(tick "Add python.exe to PATH" in the installer), open a new PowerShell window, and try again.

Then open **http://localhost:8000** in your browser. Leave the Terminal or PowerShell window
open while you use Replay; close it (or press Ctrl+C in it) when you are done.

If you used git in step 1, the folder is `Watch-in-Parts/visualizer` instead of
`Watch-in-Parts-main/visualizer`.

## Using it

- **Run** (the menu at the top): one of ten runs on the final task: the six by GPT-6.1-sol
  (lowest score first), then the four by Claude Opus 5.5 and Sonnet 5.5.
- **Timeline** (the buttons at the bottom): Parts 1 to 4 are what the grader checked; Part 5
  is the review: where the run failed, what the AI said about its own work, and how the
  final score is calculated, step by step.
- **The 3D watch:** drag to turn, scroll to zoom, right-drag to move. Parts shown in **red**
  are the ones behind a failed check.
- **Log** (right): the AI's own report, line by line. Below it, in red, what the grader found.
- **Play:** replays the run part by part, with each score hidden until that part is graded.
- **X-ray:** the same watch in a detailed viewer (labelled wheels, gear connections, hand
  speeds, a clock you can run). In X-ray mode, **Reference** switches to the reference watch
  that passes every check, for comparison. Click X-ray again to go back.

Every score and failure shown comes from the grader's own output files for that run; the
page computes nothing itself. The runs' files are on the branch `a/final-runs`
(`runs/final_*`).

## Tested

Opened and checked in Chrome on macOS, both straight from the folder and through the local
web server. Not yet tried by us in Safari, Firefox, or on Windows.
