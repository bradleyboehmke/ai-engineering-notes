// Shared quiz component. Markup:
//
// <div class="quiz">
//   <div class="quiz-q">
//     <p class="stem">Question?</p>
//     <button class="opt" data-correct>Right answer</button>
//     <button class="opt">Wrong answer</button>
//     <p class="why">Explanation shown after answering.</p>
//   </div>
//   <p class="quiz-score"></p>
// </div>
//
// Options are shuffled at load, so the correct answer's position gives no clue.
(function () {
  function shuffle(nodes) {
    for (let i = nodes.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [nodes[i], nodes[j]] = [nodes[j], nodes[i]];
    }
    return nodes;
  }

  document.querySelectorAll(".quiz").forEach(function (quiz) {
    const questions = quiz.querySelectorAll(".quiz-q");
    const score = quiz.querySelector(".quiz-score");
    let answered = 0, correct = 0;

    questions.forEach(function (q) {
      const opts = Array.from(q.querySelectorAll("button.opt"));
      const why = q.querySelector(".why");
      shuffle(opts).forEach(function (o) { q.insertBefore(o, why); });

      opts.forEach(function (o) {
        o.addEventListener("click", function () {
          if (q.classList.contains("answered")) return;
          q.classList.add("answered");
          const right = o.hasAttribute("data-correct");
          o.classList.add(right ? "correct" : "wrong");
          opts.forEach(function (x) {
            if (x.hasAttribute("data-correct")) x.classList.add("correct");
            x.disabled = true;
          });
          answered++; if (right) correct++;
          if (score) score.textContent = correct + " of " + answered + " correct" +
            (answered === questions.length ? ". Missed ones are worth revisiting tomorrow." : "");
        });
      });
    });
  });
})();
