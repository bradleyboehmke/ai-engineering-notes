// Shared "predict the next token" stepper. Replays a real, recorded generation
// run one step at a time: the learner guesses the most likely next token, then
// sees the full top-k distribution and the token that was picked.
//
// Markup:
//
// <div class="stepper">
//   <script type="application/json">
//   {
//     "prompt": "The quarterly revenue increased by",
//     "source": "GPT-2 (124M), greedy, recorded 2026-11-15",
//     "steps": [
//       { "top": [[" $", 0.215], [" 2", 0.040], ...], "note": "optional" },
//       ...
//     ]
//   }
//   </script>
// </div>
//
// The picked token at each step is the first entry of "top" (greedy), unless
// the step gives "picked" explicitly. Candidate order is shuffled before the
// guess, so position gives no clue. Leading spaces render as ␣.
(function () {
  function show(t) { return t.replace(/^ /, "␣").replace(/\n/g, "↵"); }
  function pct(p) { return (p * 100).toFixed(1) + "%"; }
  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function shuffle(a) {
    a = a.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  // Exposed so lessons can draw a static distribution with the same look.
  function renderDist(top, pickedTok) {
    const dist = el("div", "dist");
    top.forEach(function (x) {
      const row = el("div", "dist-row" + (x[0] === pickedTok ? " picked" : ""));
      row.appendChild(el("code", "dist-tok", show(x[0])));
      const track = el("div", "dist-track");
      const bar = el("div", "dist-bar");
      bar.style.width = (100 * x[1]).toFixed(1) + "%";  // absolute: full track = 100%
      track.appendChild(bar);
      row.appendChild(track);
      row.appendChild(el("span", "dist-p", pct(x[1])));
      dist.appendChild(row);
    });
    return dist;
  }
  window.renderDist = renderDist;

  document.querySelectorAll(".stepper").forEach(function (root) {
    const data = JSON.parse(root.querySelector("script").textContent);
    let i = 0, right = 0;
    const generated = [];

    const ctx = el("div", "stepper-ctx");
    const stage = el("div", "stepper-stage");
    const foot = el("p", "stepper-foot", data.source || "");
    root.append(ctx, stage, foot);

    function drawContext() {
      ctx.innerHTML = "";
      ctx.appendChild(el("span", "stepper-prompt", data.prompt));
      generated.forEach(function (t) { ctx.appendChild(el("span", "stepper-gen", t)); });
      ctx.appendChild(el("span", "stepper-cursor", "▍"));
    }

    function drawStep() {
      drawContext();
      stage.innerHTML = "";
      const step = data.steps[i];
      const picked = step.picked || step.top[0][0];
      const best = step.top[0][0];

      stage.appendChild(el("p", "stepper-q",
        "Step " + (i + 1) + " of " + data.steps.length + ": which token is most likely next?"));
      const opts = el("div", "stepper-opts");
      shuffle(step.top).forEach(function (x) {
        const b = el("button", "stepper-opt", show(x[0]));
        b.addEventListener("click", function () {
          const ok = x[0] === best;
          if (ok) right++;
          opts.querySelectorAll("button").forEach(function (o) { o.disabled = true; });
          b.classList.add(ok ? "correct" : "wrong");
          reveal(step, picked, ok);
        });
        opts.appendChild(b);
      });
      stage.appendChild(opts);
    }

    function reveal(step, picked, ok) {
      stage.appendChild(el("p", "stepper-verdict",
        (ok ? "Yes. " : "Not quite. ") + "The full top 5:"));
      stage.appendChild(renderDist(step.top, picked));
      if (step.note) stage.appendChild(el("p", "stepper-note", step.note));
      const last = i === data.steps.length - 1;
      const next = el("button", "stepper-next",
        last ? "Append " + show(picked) + " and finish" : "Append " + show(picked) + " and run the next step");
      next.addEventListener("click", function () {
        generated.push(picked);
        i++;
        if (i < data.steps.length) drawStep(); else finish();
      });
      stage.appendChild(next);
      next.focus();
    }

    function finish() {
      drawContext();
      stage.innerHTML = "";
      stage.appendChild(el("p", "stepper-q",
        "Done: " + data.steps.length + " loops, " + data.steps.length +
        " forward passes. You predicted the top token " + right + " of " + data.steps.length + " times."));
      const again = el("button", "stepper-next", "Start over");
      again.addEventListener("click", function () { i = 0; right = 0; generated.length = 0; drawStep(); });
      stage.appendChild(again);
    }

    drawStep();
  });
})();
