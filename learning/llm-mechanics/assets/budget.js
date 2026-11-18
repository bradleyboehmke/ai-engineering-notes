// Shared context-budget bar. Draws one request against a model's context
// window: input tokens, the output room max_tokens asks for, and any part of
// that ask that doesn't fit. Gives a plain-language verdict.
//
// Markup (static):
//   <div class="budget" data-window="1024" data-max-output="1024"
//        data-input="1000" data-max-tokens="100"></div>
//
// Add data-interactive to get number inputs the learner can change, and
// data-presets='[["GPT-2", 1024, 1024], ["Claude Opus 5.5", 1000000, 128000]]'
// for a model picker (name, window, max output). Numbers are tokens.
//
// Verdict rules follow current Claude models (from the Anthropic "Context
// windows" docs, read 2026-11-16): input alone over the window is rejected;
// input + max_tokens over the window is accepted but output can stop early at
// the window (stop_reason "model_context_window_exceeded").
(function () {
  function fmt(n) { return Math.round(n).toLocaleString("en-US"); }
  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function verdict(s) {
    const room = s.window - s.input;
    if (s.input > s.window)
      return ["bad", "Rejected before generation: the prompt alone is " + fmt(s.input - s.window) +
        " tokens over the window (Claude returns HTTP 400, “prompt is too long”)."];
    if (s.maxTokens > s.maxOutput)
      return ["bad", "Not allowed: max_tokens is above this model's max output of " + fmt(s.maxOutput) + "."];
    if (s.input + s.maxTokens > s.window)
      return ["warn", "Only " + fmt(room) + " of the " + fmt(s.maxTokens) +
        " output tokens you asked for fit. Current Claude models accept this and stop at the window " +
        "(model_context_window_exceeded); earlier models reject it."];
    return ["ok", "Fits. Output ends at end of turn, or is cut off at max_tokens = " + fmt(s.maxTokens) +
      ". " + fmt(room - s.maxTokens) + " tokens of the window stay unused."];
  }

  function draw(root, s) {
    const total = Math.max(s.window, s.input + s.maxTokens);
    const pct = function (n) { return (100 * n / total) + "%"; };
    const inFit = Math.min(s.input, s.window);
    const outFit = Math.max(0, Math.min(s.maxTokens, s.window - s.input));
    const over = s.input + s.maxTokens - s.window;

    const bar = root.querySelector(".budget-bar");
    bar.innerHTML = "";
    const segIn = el("div", "budget-seg budget-in"); segIn.style.width = pct(inFit);
    const segOut = el("div", "budget-seg budget-out"); segOut.style.width = pct(outFit);
    bar.append(segIn, segOut);
    if (over > 0) {
      const segOver = el("div", "budget-seg budget-over"); segOver.style.width = pct(over);
      bar.append(segOver);
    }
    const mark = el("div", "budget-mark"); mark.style.left = pct(s.window);
    mark.title = "context window"; bar.append(mark);

    root.querySelector(".budget-legend").innerHTML =
      '<span><i class="budget-in"></i>input ' + fmt(s.input) + '</span>' +
      '<span><i class="budget-out"></i>output room ' + fmt(outFit) + '</span>' +
      (over > 0 ? '<span><i class="budget-over"></i>doesn’t fit ' + fmt(over) + '</span>' : '') +
      '<span>window ' + fmt(s.window) + ' · max output ' + fmt(s.maxOutput) + '</span>';

    const v = verdict(s);
    const out = root.querySelector(".budget-verdict");
    out.className = "budget-verdict " + v[0];
    out.textContent = v[1];
  }

  function numInput(label, value, onChange) {
    const wrap = el("label", "budget-field");
    wrap.append(el("span", null, label));
    const i = document.createElement("input");
    i.type = "number"; i.min = "0"; i.step = "any"; i.value = value;
    i.addEventListener("input", function () { onChange(Number(i.value) || 0); });
    wrap.append(i);
    return [wrap, i];
  }

  document.querySelectorAll(".budget").forEach(function (root) {
    const d = root.dataset;
    const s = {
      window: Number(d.window), maxOutput: Number(d.maxOutput || d.window),
      input: Number(d.input), maxTokens: Number(d.maxTokens)
    };

    if (d.interactive !== undefined) {
      const controls = el("div", "budget-controls");
      const fields = {};
      if (d.presets) {
        const presets = JSON.parse(d.presets);
        const pick = el("label", "budget-field");
        pick.append(el("span", null, "Model"));
        const sel = document.createElement("select");
        presets.forEach(function (p, k) { const o = el("option", null, p[0]); o.value = k; sel.append(o); });
        sel.addEventListener("change", function () {
          const p = presets[sel.value]; s.window = p[1]; s.maxOutput = p[2]; draw(root, s);
        });
        pick.append(sel); controls.append(pick);
        s.window = presets[0][1]; s.maxOutput = presets[0][2];
      }
      [["Input tokens", "input"], ["max_tokens", "maxTokens"]].forEach(function (f) {
        const pair = numInput(f[0], s[f[1]], function (v) { s[f[1]] = v; draw(root, s); });
        fields[f[1]] = pair[1]; controls.append(pair[0]);
      });
      root.append(controls);
    }
    root.append(el("div", "budget-bar"), el("div", "budget-legend"), el("p", "budget-verdict"));
    draw(root, s);
  });
})();
