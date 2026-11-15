# CLAUDE.md

Rules that keep Claude sessions in this folder cheap on tokens.

- Never open or print the pages in `scenes/` (2 to 3 MB each, almost all of it base64
  mesh data) or `data/runs/*.js`. To check one, grep for a short string or read its size.
- Never read `work/*/stage*/transcript.jsonl` whole. Use `grep` or `head`.
- Run the build with only the tail of its output: `python3 build.py 2>&1 | tail -15`.
- When changing only the page (`index.html`, `app/`), do not rebuild: existing scenes are
  reused, and `python3 build.py --no-scenes` skips any missing ones.
- To see the page, take one headless Chrome screenshot and look at that, rather than
  reading the HTML.
