/* Replay: pick a run, read what the AI did, section by section.
 * Reads only the files build.py writes: data/index.js and data/runs/<id>.js.
 * Every score shown comes from the run file, which copies it from the grader output. */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  };

  const KIND_LABEL = {
    read: "reads", write: "writes", run: "runs", check: "checks", result: "→",
    error: "error", harness: "tool", wait: "waits", submit: "submit", say: "says",
    think: "thinks", done: "done", claim: "reports", note: "notes",
  };
  const PLAY_SECONDS_PER_SECTION = 18;   // a played section lasts about this long

  const state = {
    run: null,          // the loaded run file
    sec: 0,             // selected section index
    playing: false,
    revealed: Infinity, // log lines shown in the selected section (Infinity = all)
    scored: new Set(),  // sections whose score has been revealed during play
    timer: null,
  };

  const fmtScore = (x) => (x == null ? "—" : Number(x).toFixed(3));
  const fmtTime = (s) => {
    s = Math.max(0, Math.round(s || 0));
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  };
  const failed = (s) => (s.failures && s.failures.length > 0) || (s.reward != null && s.reward < 1);

  /* ---------- loading ---------- */

  function loadRun(id) {
    stop();
    const item = (window.REPLAY_INDEX || []).find((r) => r.id === id);
    if (!item) return;
    const have = window.REPLAY && window.REPLAY.runs && window.REPLAY.runs[id];
    if (have) return showRun(have);
    const s = document.createElement("script");
    s.src = item.file;
    s.onload = () => showRun(window.REPLAY.runs[id]);
    s.onerror = () => fatal(`Could not load ${item.file}. Run python3 build.py.`);
    document.body.appendChild(s);
  }

  function fatal(msg) {
    $("log").replaceChildren(el("li", "empty", msg));
  }

  function showRun(run) {
    state.run = run;
    $("xray").hidden = !run.sections.some((s) => s.xray);   // only runs built with X-ray pages
    state.scored = new Set(run.sections.map((_, i) => i));
    state.revealed = Infinity;
    const want = new URLSearchParams(location.hash.slice(1)).get("s");
    const idx = run.sections.findIndex((s) => s.id === want);
    state.sec = idx >= 0 ? idx : 0;
    renderRunInfo();
    renderAll();
  }

  /* ---------- rendering ---------- */

  function renderRunInfo() {
    const r = state.run.run;
    const box = $("runinfo");
    box.replaceChildren();
    const item = (k, v, cls) => {
      const span = el("span", cls);
      span.append(k + " ", el("b", null, v));
      box.append(span);
    };
    item("model", r.model || r.label);
    item(r.score_label || "chain score", fmtScore(r.chain_score));
    item("task", r.task_version);
    if (r.harness) item("run with", r.harness);
    item("graded with", `${r.grader_version}${r.graded_at_commit ? " @ " + r.graded_at_commit : ""}`);
    if (r.cost_usd != null) item("cost", "$" + r.cost_usd.toFixed(2));
    if (r.current_spec && !String(r.task_version).includes(r.current_spec)) {
      const w = el("span", "warn", `not regraded on the current SPEC ${r.current_spec}`);
      w.title = r.version_note || "";
      box.append(w);
    }
  }

  function renderAll() {
    renderTimeline();
    renderSection();
    writeHash();
  }

  function renderTimeline() {
    const tl = $("timeline");
    tl.replaceChildren();
    state.run.sections.forEach((s, i) => {
      const b = el("button", "seg");
      b.type = "button";
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", String(i === state.sec));
      const shown = state.scored.has(i);
      if (!shown) b.classList.add("pending");
      else if (failed(s)) b.classList.add("fail");
      b.append(el("span", "name", s.label), el("span", "score", shown ? fmtScore(s.reward) : "· · ·"));
      b.title = shown ? `score ${s.reward} (from ${s.score_source})` : "not graded yet in this replay";
      b.addEventListener("click", () => { stop(); select(i); });
      tl.append(b);
    });
    const done = state.playing ? state.sec + Math.min(1, progress()) : state.sec + 1;
    $("playhead").style.width = `${(100 * done) / state.run.sections.length}%`;
  }

  function progress() {
    const s = state.run.sections[state.sec];
    if (!s.log.length) return 1;
    return Math.min(state.revealed, s.log.length) / s.log.length;
  }

  function renderSection() {
    const s = state.run.sections[state.sec];
    const showHarness = $("show-harness").checked;
    $("log-title").textContent = s.label;
    $("log-meta").textContent = s.tool_calls == null && s.duration_s == null
      ? "from the AI's own report.json · no transcript kept" :
      `${s.tool_calls ?? "?"} tool calls · ${fmtTime(s.duration_s)}` +
      (s.cost_usd != null ? ` · $${s.cost_usd.toFixed(2)}` : "");

    const ol = $("log");
    ol.replaceChildren();
    if (s.review) {
      $("log-meta").textContent = `every number from ${s.score_source}`;
      if (state.scored.has(state.sec)) ol.append(renderReview(s.review));
      else ol.append(el("li", "empty", "The review appears when grading ends."));
      ol.scrollTop = 0;
      renderViewport(s);
      renderFailures(s);
      return;
    }
    if (!s.log.length) ol.append(el("li", "empty", "No transcript for this section."));
    s.log.slice(0, state.revealed).forEach((l) => ol.append(logLine(l, showHarness)));
    if (state.playing) ol.scrollTop = ol.scrollHeight;
    else ol.scrollTop = 0;

    renderViewport(s);
    renderFailures(s);
  }

  /* Part 5: where the delivery failed, and how the grader's formula gives the score */
  function renderReview(rv) {
    const f3 = (x) => Number(x).toFixed(3), f4 = (x) => Number(x).toFixed(4);
    const sc = rv.score, h = sc.honesty;
    const box = el("li", "review");
    const section = (title) => { const d = el("div", "rv-block"); d.append(el("h3", null, title)); box.append(d); return d; };

    const fail = section("Where it failed");
    rv.failures.forEach((f) => {
      const d = el("div", "rv-fail");
      d.append(el("span", "rv-x", "✕"), el("b", null, f.check),
               el("span", "rv-where", ` · ${f.parts.join(", ")}`), el("div", "rv-msg", f.message));
      fail.append(d);
    });
    if (rv.passed.length) fail.append(el("div", "rv-pass", `✓ passed everything: ${rv.passed.join(", ")}`));

    const said = section("What the AI said");
    const claims = Object.entries(h.claims || {}).map(([k, v]) => `${k} ${v.replace("_", " ")}`).join(", ");
    said.append(el("p", null, `It reported ${claims}. The checks it lists in its report: ` +
      `${rv.report_checked.join(", ")}.` + (rv.gap_note ? ` ${rv.gap_note}` : "")));

    const how = section(`How it got ${f3(sc.reward)}`);
    const t = el("table", "rv-table");
    t.append(Object.assign(el("tr"), { innerHTML: "<th>part</th><th>weight</th><th>part score</th><th>weight × score</th>" }));
    sc.rows.forEach((r) => {
      const tr = el("tr", r.s < 1 ? "bad" : "");
      [r.label, f3(r.weight), f3(r.s), f4(r.weighted)].forEach((v) => tr.append(el("td", null, v)));
      t.append(tr);
    });
    how.append(t);
    const steps = el("ol", "rv-steps");
    [
      `Parts: ${f4(sc.weighted_sum)} ÷ ${f3(sc.weight_total)} total weight = ${f4(sc.parts_average)}. Half the score is this: ½ × ${f4(sc.parts_average)} = ${f4(sc.parts_half)}.`,
      sc.all_pass
        ? `Everything passed, so the other half is ½ × thickness score ${f4(sc.thickness.s)} = ${f4(sc.all_pass_half)}.`
        : `The other half is paid only if every check passes. Some failed, so it adds 0. (Even then it would be ½ × the thickness score ${f4(sc.thickness.s)}: the movement is ${sc.thickness.H_mm.toFixed(2)} mm tall against the ${sc.thickness.h0_mm} mm it is measured against.)`,
      `Honesty: its claims scored ${Object.entries(h.points).map(([k, v]) => `${k} ${v}`).join(", ")}, an average of ${f3(h.honesty)}. Factor = (${h.W_PRODUCT} + ${h.W_HONESTY} × ${f3(h.honesty)}) ÷ (${h.W_PRODUCT} + ${h.W_HONESTY}) = ${f4(h.factor)}.`,
      `Score = (${f4(sc.parts_half)} + ${f4(sc.all_pass_half)}) × ${f4(h.factor)} = ${f4(sc.reward)}.`,
    ].forEach((x) => steps.append(el("li", null, x)));
    how.append(steps);
    return box;
  }

  function logLine(l, showHarness) {
    const li = el("li", l.kind);
    if (l.kind === "harness" && !showHarness) li.classList.add("hidden");
    li.title = `${l.src.file}, line ${l.src.line}`;
    li.append(el("span", "t", fmtTime(l.t)), el("span", "k", KIND_LABEL[l.kind] || l.kind));
    const x = el("span", "x");
    if (l.done) {
      const mark = el("span", "donemark", "◆ Says it's done");
      const body = el("span", "x");
      body.textContent = l.text;
      x.className = "";
      x.append(mark, body);
      if (l.full && l.full.length > l.text.length) {
        const more = el("button", "more", "full message");
        more.type = "button";
        more.addEventListener("click", () => {
          const open = more.textContent === "full message";
          body.textContent = open ? l.full : l.text;
          body.style.whiteSpace = open ? "pre-wrap" : "";
          more.textContent = open ? "shorter" : "full message";
        });
        x.append(more);
      }
      li.append(x);
    } else {
      x.textContent = l.text;
      if (l.repeat) x.append(el("span", "rep", `  ×${l.repeat}`));
      li.append(x);
    }
    return li;
  }

  /* the 3D scene: one page per section, made by build.py from the team's viewer */
  let sceneSrc = null, sceneReady = false;

  function sceneProgress() {
    const s = state.run.sections[state.sec];
    return state.revealed === Infinity || !s.log.length ? 1 : Math.min(1, state.revealed / s.log.length);
  }

  function updateScene() {
    const s = state.run.sections[state.sec];
    const fr = $("scene");
    const xray = state.xray && s.xray;
    document.querySelector(".stage").classList.toggle("xray", !!xray);
    const src = xray ? s.xray : s.scene;
    if (!src) { fr.hidden = true; sceneSrc = null; return; }
    if (sceneSrc !== src) {
      sceneSrc = src; sceneReady = false;
      fr.classList.remove("ready");
      fr.hidden = false;
      if (xray) {
        // Mikael's X-ray page runs on its own; it sends no ready message
        fr.onload = () => fr.classList.add("ready");
        fr.src = src;
      } else {
        fr.onload = null;
        fr.src = src + "#embed=1&cam=iso";
      }
      return; // the build scene sends its state when it says it is ready
    }
    if (xray) return;
    if (sceneReady) {
      fr.contentWindow.postMessage({ type: "replay", progress: sceneProgress(),
        mode: s.scene_mode, newParts: s.new_parts,
        failParts: state.scored.has(state.sec) ? (s.fail_parts || []) : [] }, "*");
    }
  }

  window.addEventListener("message", (e) => {
    if (e.data && e.data.type === "replay-scene-ready" && e.source === $("scene").contentWindow) {
      sceneReady = true;
      $("scene").classList.add("ready");
      updateScene();
    }
  });

  function renderViewport(s) {
    updateScene();
    const box = $("vp-inner");
    box.replaceChildren();
    const shown = state.scored.has(state.sec);
    const top = el("div");
    top.append(el("div", "vp-label", s.label));
    const big = el("div", "vp-big" + (shown && failed(s) ? " fail" : ""), shown ? fmtScore(s.reward) : "· · ·");
    big.title = shown ? `from ${s.score_source}` : "";
    const said = s.claim ? `the AI reported: ${s.claim.replace("_", " ")}` : null;
    const sub = el("div", "vp-sub",
      s.review ? (shown ? "final score · how it is made is on the right" : "grading")
      : shown ? [said, `grader: p = ${fmtScore(s.p)} (share of checks passed)`].filter(Boolean).join(" · ")
            : (said || "the AI is working"));
    top.append(big, sub);
    const failNote = shown && s.fail_parts && s.fail_parts.length
      ? (s.review ? ` Red: every part behind a failed check (${s.fail_parts.length}).`
                  : ` Red: ${s.fail_parts.join(", ")}.`) : "";
    const note = s.scene
      ? (s.scene_mode === "assembly" ? "The AI's own assembly paths, replayed. Drag to turn." + failNote
         : s.fail_parts ? `The delivered movement. Drag to turn.${failNote}`
         : `${s.new_parts.length} part${s.new_parts.length === 1 ? "" : "s"} added in this section. Drag to turn.`)
      : "No 3D for this section. Run python3 build.py with the .venv set up.";
    box.append(top, el("div", "vp-note", note));
  }

  function renderFailures(s) {
    const box = $("failures");
    box.replaceChildren();
    if (!state.scored.has(state.sec) || !s.failures || !s.failures.length) return;
    s.failures.forEach((f) => {
      const d = el("div", "failure");
      let msg = (f.format_messages && f.format_messages.join("; ")) ||
        (f.hit ? `hits ${f.hit} at pose ${f.pose_index} of ${f.poses}` : "failed");
      d.append(`✕ ${f.kind} ${f.name} · ${msg}`);
      const why = el("div", "why");
      const parts = [];
      if (f.introduced_in_section) parts.push(`this part was added in Stage ${f.introduced_in_section}`);
      if (s.score_key) parts.push(`${s.score_key}.checks.${f.name}`);
      parts.push(`grader output: ${s.score_source}`);
      why.textContent = parts.join(" · ");
      d.append(why);
      box.append(d);
    });
  }

  /* ---------- selection and playback ---------- */

  function select(i) {
    state.sec = Math.max(0, Math.min(state.run.sections.length - 1, i));
    if (!state.playing) state.revealed = Infinity;
    renderAll();
  }

  function play() {
    if (!state.run) return;
    // start from the selected section; sections from here on are "not graded yet"
    state.playing = true;
    state.scored = new Set(state.run.sections.map((_, i) => i).filter((i) => i < state.sec));
    state.revealed = 0;
    $("play").textContent = "Pause";
    $("play").setAttribute("aria-pressed", "true");
    renderAll();
    step();
  }

  function step() {
    const s = state.run.sections[state.sec];
    if (state.revealed < s.log.length) {
      const prev = state.revealed > 0 ? s.log[state.revealed - 1].t : 0;
      const gap = Math.max(0, s.log[state.revealed].t - prev);
      const total = Math.max(1, s.duration_s || s.log[s.log.length - 1].t || 1);
      const delay = Math.min(1600, Math.max(140, (gap / total) * PLAY_SECONDS_PER_SECTION * 1000));
      state.timer = setTimeout(() => {
        state.revealed += 1;
        renderSection();
        renderTimeline();
        step();
      }, delay);
      return;
    }
    // section finished: the grader's score appears
    state.timer = setTimeout(() => {
      state.scored.add(state.sec);
      renderSection();
      renderTimeline();
      state.timer = setTimeout(() => {
        if (state.sec < state.run.sections.length - 1) {
          state.sec += 1;
          state.revealed = 0;
          renderAll();
          step();
        } else {
          stop();
        }
      }, failed(s) ? 3200 : 1600);
    }, 700);
  }

  function stop() {
    clearTimeout(state.timer);
    state.timer = null;
    if (!state.playing) return;
    state.playing = false;
    state.revealed = Infinity;
    if (state.run) state.scored = new Set(state.run.sections.map((_, i) => i));
    $("play").textContent = "Play";
    $("play").setAttribute("aria-pressed", "false");
    if (state.run) renderAll();
  }

  function writeHash() {
    const h = `run=${state.run.run.id}&s=${state.run.sections[state.sec].id}`;
    if (location.hash.slice(1) !== h) history.replaceState(null, "", "#" + h);
  }

  /* ---------- start ---------- */

  function init() {
    const idx = window.REPLAY_INDEX;
    if (!idx || !idx.length) return fatal("No runs found. Run python3 build.py first.");
    const sel = $("run-select");
    idx.forEach((r) => {
      const o = el("option", null, `${r.label} · ${fmtScore(r.chain_score)}`);
      o.value = r.id;
      sel.append(o);
    });
    const want = new URLSearchParams(location.hash.slice(1)).get("run");
    sel.value = idx.some((r) => r.id === want) ? want : idx[0].id;
    sel.addEventListener("change", () => { history.replaceState(null, "", "#run=" + sel.value); loadRun(sel.value); });
    $("play").addEventListener("click", () => (state.playing ? stop() : play()));
    $("show-harness").addEventListener("change", () => state.run && renderSection());
    $("xray").addEventListener("click", () => {
      state.xray = !state.xray;
      $("xray").setAttribute("aria-pressed", String(state.xray));
      if (state.run) updateScene();
    });
    document.addEventListener("keydown", (e) => {
      if (!state.run || e.target.tagName === "SELECT") return;
      if (e.key === "ArrowRight") { stop(); select(state.sec + 1); }
      if (e.key === "ArrowLeft") { stop(); select(state.sec - 1); }
      if (e.key === " " && e.target === document.body) { e.preventDefault(); state.playing ? stop() : play(); }
    });
    loadRun(sel.value);
  }

  init();
})();
