// Shared request-cost calculator. Prices one request from its token usage,
// splits the bill into input / thinking / visible answer, and scales it to a
// volume of requests. Thinking is billed at the output price, so it gets its
// own segment.
//
// Markup:
//   <div class="cost"
//        data-models='[["Claude Haiku 5.5", 0.10, 0.50], ["GPT-6 Luna", 0.10, 0.50]]'
//        data-input="120" data-thinking="900" data-answer="80"
//        data-volume="100000"></div>
//
// data-models: [name, input $/MTok, output $/MTok]. Cite the pricing page and
// its read date next to every use: prices change.
// data-thinking is optional; set data-no-thinking to hide that field (for
// lessons where thinking isn't the point).
(function () {
  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function money(x) {
    if (x === 0) return "$0";
    if (x < 0.01) return "$" + x.toPrecision(2);
    return "$" + x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function field(label, value, onChange, isSelect) {
    const wrap = el("label", "budget-field");
    wrap.append(el("span", null, label));
    const i = document.createElement(isSelect ? "select" : "input");
    if (!isSelect) { i.type = "number"; i.min = "0"; i.step = "any"; i.value = value; }
    i.addEventListener(isSelect ? "change" : "input", function () { onChange(i.value); });
    wrap.append(i);
    return [wrap, i];
  }

  function draw(root, s) {
    const m = s.models[s.model];
    const cIn = s.input * m[1] / 1e6;
    const cThink = s.thinking * m[2] / 1e6;
    const cAns = s.answer * m[2] / 1e6;
    const one = cIn + cThink + cAns;
    const pct = function (x) { return one ? (100 * x / one) + "%" : "0%"; };

    const bar = root.querySelector(".budget-bar");
    bar.innerHTML = "";
    [["budget-in", cIn], ["cost-think", cThink], ["budget-out", cAns]].forEach(function (p) {
      const seg = el("div", "budget-seg " + p[0]); seg.style.width = pct(p[1]); bar.append(seg);
    });

    root.querySelector(".budget-legend").innerHTML =
      '<span><i class="budget-in"></i>input ' + money(cIn) + '</span>' +
      (s.showThinking ? '<span><i class="cost-think"></i>thinking ' + money(cThink) + '</span>' : '') +
      '<span><i class="budget-out"></i>visible answer ' + money(cAns) + '</span>' +
      '<span>' + m[0] + ': $' + m[1] + ' in / $' + m[2] + ' out per MTok</span>';

    const share = one ? Math.round(100 * cThink / one) : 0;
    root.querySelector(".cost-total").innerHTML =
      "<strong>" + money(one) + "</strong> per request · <strong>" + money(one * s.volume) +
      "</strong> for " + s.volume.toLocaleString("en-US") + " requests" +
      (s.showThinking ? " · thinking is <strong>" + share + "%</strong> of the bill" : "");
  }

  document.querySelectorAll(".cost").forEach(function (root) {
    const d = root.dataset;
    const s = {
      models: JSON.parse(d.models), model: 0,
      input: Number(d.input || 0), thinking: Number(d.thinking || 0),
      answer: Number(d.answer || 0), volume: Number(d.volume || 1),
      showThinking: d.noThinking === undefined
    };
    if (!s.showThinking) s.thinking = 0;

    const controls = el("div", "budget-controls");
    const pick = field("Model", null, function (v) { s.model = Number(v); draw(root, s); }, true);
    s.models.forEach(function (m, k) { const o = el("option", null, m[0]); o.value = k; pick[1].append(o); });
    controls.append(pick[0]);
    const nums = [["Input tokens", "input"], ["Thinking tokens", "thinking"],
                  ["Answer tokens", "answer"], ["Requests", "volume"]];
    nums.forEach(function (f) {
      if (f[1] === "thinking" && !s.showThinking) return;
      controls.append(field(f[0], s[f[1]], function (v) { s[f[1]] = Number(v) || 0; draw(root, s); })[0]);
    });

    root.append(controls, el("div", "budget-bar"), el("div", "budget-legend"), el("p", "cost-total"));
    draw(root, s);
  });
})();
