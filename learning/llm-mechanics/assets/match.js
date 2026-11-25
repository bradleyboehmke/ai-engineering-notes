// Shared "which source produced this?" component. The learner reads real,
// recorded outputs and assigns each one to the run (model, setting, tier...)
// that produced it. Feedback is immediate per item.
//
// Markup:
//
// <div class="match" data-choices='["Base, raw prompt", "Instruct, chat template"]'>
//   <div class="match-item" data-answer="Base, raw prompt">
//     <pre>recorded output</pre>
//     <p class="why">Explanation shown after answering.</p>
//   </div>
//   ...
//   <p class="match-score"></p>
// </div>
//
// Items are shuffled at load. Choices keep their given order (it's a key, not
// a hint), and every item gets the same list.
(function () {
  function shuffle(a) {
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  document.querySelectorAll(".match").forEach(function (box) {
    const choices = JSON.parse(box.getAttribute("data-choices"));
    const score = box.querySelector(".match-score");
    const items = shuffle(Array.from(box.querySelectorAll(".match-item")));
    items.forEach(function (it) { box.insertBefore(it, score); });
    let answered = 0, correct = 0;

    items.forEach(function (it, n) {
      const answer = it.getAttribute("data-answer");
      const why = it.querySelector(".why");
      const head = document.createElement("div");
      head.className = "match-head";
      head.textContent = "Output " + String.fromCharCode(65 + n);
      it.insertBefore(head, it.firstChild);

      const row = document.createElement("div");
      row.className = "match-opts";
      choices.forEach(function (c) {
        const b = document.createElement("button");
        b.className = "match-opt";
        b.textContent = c;
        b.addEventListener("click", function () {
          if (it.classList.contains("answered")) return;
          it.classList.add("answered");
          const right = c === answer;
          b.classList.add(right ? "correct" : "wrong");
          row.querySelectorAll("button").forEach(function (x) {
            if (x.textContent === answer) x.classList.add("correct");
            x.disabled = true;
          });
          answered++; if (right) correct++;
          if (score) score.textContent = correct + " of " + answered + " matched" +
            (answered === items.length ? "." : "");
        });
        row.appendChild(b);
      });
      it.insertBefore(row, why);
    });
  });
})();
