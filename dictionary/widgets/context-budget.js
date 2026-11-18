// Context-budget calculator for dictionary pages. Draws one request against a
// model's context window (input + max_tokens) and says which outcome you land
// in: fits, tight (input fits but input + max_tokens doesn't), or too long.
//
// Usage in a .qmd page (front matter: resources: [widgets/context-budget.*]):
//
//   ```{=html}
//   <link rel="stylesheet" href="widgets/context-budget.css">
//   <div class="context-budget"></div>
//   <script src="widgets/context-budget.js"></script>
//   ```
//
// Optional attributes on the div (all numbers are tokens):
//   data-models='[["Label", window, maxOutput], ...]'   defaults below
//   data-model="0" data-input="120000" data-max="8000"  starting state
//   data-presets='[["Name", modelIndex, input, max], ...]'
//
// Outcome rules follow current Claude models (Anthropic "Context windows"
// docs, read 2026-11-18): input alone over the window is rejected with HTTP
// 400; input + max_tokens over the window is accepted on Claude 4.5 and newer,
// and output can stop early with stop_reason "model_context_window_exceeded".
(function () {
  var DEFAULT_MODELS = [
    ["Claude Opus 5.5 (1M / 128K)", 1000000, 128000],
    ["Claude Sonnet 5.5 (1M / 128K)", 1000000, 128000],
    ["Claude Haiku 5.5 (1M / 128K)", 1000000, 128000],
    ["Claude Haiku 4.5 (200K / 64K)", 200000, 64000]
  ];
  var DEFAULT_PRESETS = [
    ["Comfortable", 1, 120000, 8000],
    ["Squeezed", 0, 990000, 64000],
    ["Too long", 3, 210000, 1024]
  ];

  function fmt(n) { return Math.round(n).toLocaleString("en-US"); }
  function num(v) { var n = Math.floor(Number(v)); return isFinite(n) && n > 0 ? n : 0; }
  function json(s, fallback) { try { return s ? JSON.parse(s) : fallback; } catch (e) { return fallback; } }

  // Pure fit logic: state is ok | tight | over.
  function evaluate(W, O, input, max) {
    var r = { total: input + max, maxTooBig: max > O };
    if (input > W) { r.state = "over"; r.over = input - W; }
    else if (r.total > W) { r.state = "tight"; r.over = r.total - W; r.room = W - input; }
    else { r.state = "ok"; r.unused = W - r.total; }
    return r;
  }

  function field(label, control) {
    var wrap = document.createElement("label");
    wrap.className = "cb-field";
    var span = document.createElement("span");
    span.textContent = label;
    wrap.appendChild(span);
    for (var i = 1; i < arguments.length; i++) wrap.appendChild(arguments[i]);
    return wrap;
  }
  function input(type, attrs) {
    var e = document.createElement(type === "select" ? "select" : "input");
    if (type !== "select") e.type = type;
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  function seg(cls, v, scale) {
    return v > 0 ? '<div class="cb-seg ' + cls + '" style="flex-basis:' + (v / scale * 100) + '%"></div>' : "";
  }

  function build(root) {
    var d = root.dataset;
    var models = json(d.models, DEFAULT_MODELS);
    var presets = json(d.presets, DEFAULT_PRESETS);

    var sel = input("select", { "aria-label": "Model" });
    models.forEach(function (m, i) {
      var o = document.createElement("option"); o.value = i; o.textContent = m[0]; sel.appendChild(o);
    });
    var inN = input("number", { min: 0, step: 1000, inputmode: "numeric" });
    var inR = input("range", { min: 0, step: 1000, "aria-label": "Input tokens slider" });
    var mxN = input("number", { min: 1, step: 1000, inputmode: "numeric" });
    var mxR = input("range", { min: 1, step: 1000, "aria-label": "max_tokens slider" });

    var grid = document.createElement("div");
    grid.className = "cb-grid";
    grid.append(field("Model", sel), field("Input tokens", inN, inR), field("max_tokens", mxN, mxR));
    root.appendChild(grid);

    var pre = document.createElement("div");
    pre.className = "cb-presets";
    pre.innerHTML = "<span>Try:</span>";
    presets.forEach(function (p) {
      var b = document.createElement("button");
      b.type = "button"; b.textContent = p[0];
      b.addEventListener("click", function () { sel.value = p[1]; inN.value = p[2]; mxN.value = p[3]; render(); });
      pre.appendChild(b);
    });
    root.appendChild(pre);

    var barWrap = document.createElement("div"); barWrap.className = "cb-bar-wrap";
    var bar = document.createElement("div"); bar.className = "cb-bar";
    var end = document.createElement("div"); end.className = "cb-end";
    barWrap.append(bar, end);
    var legend = document.createElement("div"); legend.className = "cb-legend";
    var status = document.createElement("div"); status.className = "cb-status";
    status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
    var rot = document.createElement("p"); rot.className = "cb-rot";
    root.append(barWrap, legend, status, rot);

    function render(from) {
      var m = models[sel.value], W = m[1], O = m[2];
      inR.max = Math.round(W * 1.25); mxR.max = O;
      var inp = num(inN.value), max = Math.max(1, num(mxN.value));
      if (from !== "inR") inR.value = Math.min(inp, inR.max);
      if (from !== "mxR") mxR.value = Math.min(max, O);

      var e = evaluate(W, O, inp, max);
      var scale = Math.max(W, e.total);
      var inIn = Math.min(inp, W), inPast = Math.max(0, inp - W);
      var outIn = Math.max(0, Math.min(max, W - inp)), outPast = max - outIn;
      bar.innerHTML = seg("in", inIn, scale) + seg("in past", inPast, scale) +
        seg("out", outIn, scale) + seg("out past", outPast, scale) +
        seg("free", Math.max(0, W - e.total), scale);
      var w = W / scale * 100;
      end.style.left = w + "%";
      end.className = "cb-end" + (w > 90 ? " edge" : "");

      legend.innerHTML = '<span><i class="in"></i>input ' + fmt(inp) + "</span>" +
        '<span><i class="out"></i>output room ' + fmt(max) + "</span>" +
        "<span>window " + fmt(W) + " · max output " + fmt(O) + "</span>" +
        (inPast + outPast > 0 ? '<span><i class="past"></i>past the window</span>' : "");

      var html, cls;
      if (e.state === "ok") {
        cls = "ok";
        html = "<b>Fits.</b> Output ends at end of turn, or is cut off at max_tokens = " + fmt(max) +
          ". " + fmt(e.unused) + " tokens of the window stay unused.";
      } else if (e.state === "tight") {
        cls = "warn";
        html = "<b>Tight.</b> The input fits, but input + max_tokens is " + fmt(e.total) + ", " + fmt(e.over) +
          " over the window. Claude 4.5 and newer models accept this, but only " + fmt(e.room) +
          " tokens are left for output, and the reply can stop with stop_reason model_context_window_exceeded.";
      } else {
        cls = "bad";
        html = "<b>Too long.</b> The input alone is " + fmt(e.over) + " tokens over the " + fmt(W) +
          "-token window. The API returns HTTP 400 invalid_request_error (“prompt is too long”) and nothing is generated.";
      }
      if (e.maxTooBig) html += '<span class="cb-extra">max_tokens is above this model’s max output of ' + fmt(O) + ". Lower it.</span>";
      status.className = "cb-status " + cls;
      status.innerHTML = html;

      var pct = e.total / W * 100;
      rot.textContent = "Input + max_tokens is " + (pct >= 100 ? fmt(pct) : pct.toFixed(1)) +
        "% of the window. Fitting is the minimum bar: accuracy and recall tend to degrade as context grows, so test your own task at different sizes.";
    }

    sel.addEventListener("change", function () { render(); });
    inN.addEventListener("input", function () { render("inN"); });
    mxN.addEventListener("input", function () { render("mxN"); });
    inR.addEventListener("input", function () { inN.value = inR.value; render("inR"); });
    mxR.addEventListener("input", function () { mxN.value = mxR.value; render("mxR"); });

    var start = presets[0] || ["", 0, 0, 1000];
    sel.value = d.model !== undefined ? d.model : start[1];
    inN.value = d.input !== undefined ? d.input : start[2];
    mxN.value = d.max !== undefined ? d.max : start[3];
    render();
  }

  document.querySelectorAll(".context-budget").forEach(build);
})();
