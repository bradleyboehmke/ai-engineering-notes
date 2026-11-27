// Thinking-cost calculator for dictionary pages. Prices one request from its
// token usage, splits the bill into input / thinking / visible answer, scales
// it to a number of requests, and checks recorded runs against the cost the
// script printed.
//
// Usage in a .qmd page (front matter: resources: [widgets/thinking-cost.*]):
//
//   ```{=html}
//   <link rel="stylesheet" href="widgets/thinking-cost.css">
//   <div class="thinking-cost"></div>
//   <script src="widgets/thinking-cost.js"></script>
//   ```
//
// Optional attributes on the div:
//   data-models='[["Label", in $/MTok, out $/MTok, "note on off runs" | null], ...]'
//   data-presets='[["Label", input, thinking, visible, recordedCost, isOff], ...]'
//   data-preset="3" data-volume="100000"   starting state
//
// Default prices: standard per-MTok rates from the Anthropic and OpenAI pricing
// pages, read 2026-11-26. Default presets: thinking_api.py on claude-haiku-5-5,
// two runs recorded 2026-11-25.
(function () {
  var DEFAULT_MODELS = [
    ["Claude Haiku 5.5", 0.10, 0.50, null],
    ["Claude Sonnet 5.5", 2, 10, "Sonnet 5.5 rejects thinking: disabled. Its way to skip up-front thinking is thinking: {type: between_tools} at high effort or below, so this run is only roughly reproducible there."],
    ["Claude Opus 5.5", 4, 20, "Opus 5.5 can't turn thinking off: thinking: disabled returns HTTP 400 at every effort level, so this run can't be reproduced there."],
    ["OpenAI GPT-6.2 Sol", 2, 10, "OpenAI's guide says GPT-6.2 Sol rejects reasoning effort none, so this run can't be reproduced there."],
    ["OpenAI GPT-6.2 Astra", 8, 40, "OpenAI's guide says GPT-6.2 Astra rejects reasoning effort none, so this run can't be reproduced there."]
  ];
  var DEFAULT_PRESETS = [
    ["Run A · 1. off", 119, 0, 284, 0.000154, true],
    ["Run A · 2. low", 121, 206, 191, 0.000211, false],
    ["Run A · 3. medium", 121, 192, 227, 0.000222, false],
    ["Run A · 4. high", 121, 302, 211, 0.000269, false],
    ["Run A · 5. trivial, medium", 19, 0, 5, 0.000004, false],
    ["Run B · 1. off", 119, 0, 231, 0.000127, true],
    ["Run B · 2. low", 121, 174, 258, 0.000228, false],
    ["Run B · 3. medium", 121, 222, 258, 0.000252, false],
    ["Run B · 4. high", 121, 191, 220, 0.000218, false],
    ["Run B · 5. trivial, medium", 19, 0, 5, 0.000004, false]
  ];

  function json(s, fallback) { try { return s ? JSON.parse(s) : fallback; } catch (e) { return fallback; } }
  function num(v) { var n = Number(v); return isFinite(n) && n > 0 ? n : 0; }
  function fmt(n) { return Math.round(n).toLocaleString("en-US"); }
  function money(x) {
    if (x < 0.01) return "$" + x.toFixed(6);
    if (x < 1) return "$" + x.toFixed(4);
    return "$" + x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function build(root, n) {
    var d = root.dataset;
    var MODELS = json(d.models, DEFAULT_MODELS);
    var PRESETS = json(d.presets, DEFAULT_PRESETS);
    var id = function (k) { return "tc" + n + "-" + k; };

    var grid = el("div", "tc-grid");
    function field(key, label, tag) {
      var f = el("div", "tc-field");
      var l = el("label", null, label); l.htmlFor = id(key);
      var c = document.createElement(tag || "input");
      c.id = id(key);
      if (!tag) { c.type = "number"; c.min = "0"; c.step = key === "vol" ? "1000" : "1"; c.inputMode = "numeric"; }
      f.append(l, c); grid.append(f);
      return c;
    }
    var elPreset = field("preset", "Recorded run (Haiku 5.5 token counts)", "select");
    var elModel = field("model", "Price it on", "select");
    var elIn = field("in", "Input tokens");
    var elThink = field("think", "Thinking tokens");
    var elAns = field("ans", "Visible answer tokens");
    var elVol = field("vol", "Requests");

    var elBar = el("div", "tc-bar"); elBar.setAttribute("role", "img");
    elBar.setAttribute("aria-label", "Share of the cost that is input, thinking and visible answer");
    var elLegend = el("div", "tc-legend");
    var elTotal = el("div", "tc-status"); elTotal.setAttribute("role", "status"); elTotal.setAttribute("aria-live", "polite");
    var elRec = el("div", "tc-extra");
    var elNote = el("div", "tc-extra tc-warn"); elNote.hidden = true;
    root.append(grid, elBar, elLegend, elTotal, elRec, elNote);

    PRESETS.forEach(function (p, i) { var o = el("option", null, p[0]); o.value = i; elPreset.append(o); });
    MODELS.forEach(function (m, i) { var o = el("option", null, m[0]); o.value = i; elModel.append(o); });
    var dirty = false;

    function loadPreset() {
      var p = PRESETS[Number(elPreset.value)];
      elIn.value = p[1]; elThink.value = p[2]; elAns.value = p[3];
      dirty = false;
      render();
    }

    function render() {
      var m = MODELS[Number(elModel.value)], p = PRESETS[Number(elPreset.value)];
      var tin = num(elIn.value), tth = num(elThink.value), tans = num(elAns.value), vol = num(elVol.value);
      var cIn = tin * m[1] / 1e6, cTh = tth * m[2] / 1e6, cAns = tans * m[2] / 1e6;
      var one = cIn + cTh + cAns;
      var pct = function (x) { return one ? (100 * x / one) + "%" : "0%"; };

      elBar.innerHTML = "";
      [["tc-in", cIn], ["tc-think", cTh], ["tc-ans", cAns]].forEach(function (s) {
        var seg = el("div", "tc-seg " + s[0]); seg.style.width = pct(s[1]); elBar.append(seg);
      });
      elLegend.innerHTML =
        '<span><i class="tc-in"></i>input ' + money(cIn) + '</span>' +
        '<span><i class="tc-think"></i>thinking ' + money(cTh) + '</span>' +
        '<span><i class="tc-ans"></i>visible answer ' + money(cAns) + '</span>' +
        '<span>$' + m[1] + ' in / $' + m[2] + ' out per MTok</span>';

      var share = one ? Math.round(100 * cTh / one) : 0;
      elTotal.innerHTML =
        '<strong>' + money(one) + '</strong> per request · <strong>' + money(one * vol) + '</strong> for ' + fmt(vol) +
        ' requests<br>output_tokens = ' + fmt(tth + tans) + ' (' + fmt(tth) + ' thinking + ' + fmt(tans) +
        ' visible) · thinking is <strong>' + share + '%</strong> of the bill';

      if (!dirty && Number(elModel.value) === 0) {
        var ok = Math.abs(one - p[4]) < 0.0000005;
        elRec.textContent = "The script printed " + money(p[4]) + " for this run. The calculator " +
          (ok ? "matches it." : "gives " + money(one) + ", which doesn't match.");
      } else if (dirty) {
        elRec.textContent = "You've edited the numbers, so this is a what-if, not a recorded run.";
      } else {
        elRec.textContent = "Recorded token counts are from Haiku 5.5. Other models will use different counts.";
      }

      if (!dirty && p[5] && m[3]) { elNote.hidden = false; elNote.textContent = m[3]; }
      else { elNote.hidden = true; elNote.textContent = ""; }
    }

    elPreset.addEventListener("change", loadPreset);
    elModel.addEventListener("change", render);
    [elIn, elThink, elAns].forEach(function (e) { e.addEventListener("input", function () { dirty = true; render(); }); });
    elVol.addEventListener("input", render);

    elVol.value = d.volume || 100000;
    elPreset.value = d.preset || 3;   // Run A · 4. high
    loadPreset();
  }

  document.querySelectorAll(".thinking-cost").forEach(build);
})();
