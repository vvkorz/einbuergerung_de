const $ = (id) => document.getElementById(id);

let questions = [];
let current = 0;
let score = 0;

function renderQuestion() {
  const q = questions[current];
  $("progress").textContent = `Frage ${current + 1} von ${questions.length}`;
  $("progress-bar").style.width = `${(current / questions.length) * 100}%`;
  $("question").textContent = q.question;

  const options = $("options");
  options.replaceChildren();
  for (const [letter, text] of Object.entries(q.options)) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "option";
    button.dataset.letter = letter;
    const key = document.createElement("span");
    key.className = "key";
    key.textContent = letter;
    button.append(key, document.createTextNode(text));
    button.addEventListener("click", () => answer(letter));
    options.append(button);
  }

  $("feedback").hidden = true;
  $("result").hidden = true;
  $("quiz").hidden = false;
}

function answer(choice) {
  const q = questions[current];
  const correct = choice === q.answer;
  if (correct) score++;

  for (const button of $("options").children) {
    button.disabled = true;
    if (button.dataset.letter === q.answer) button.classList.add("correct");
    else if (button.dataset.letter === choice) button.classList.add("wrong");
  }

  $("verdict").textContent = correct ? "Richtig!" : `Leider falsch – richtig ist ${q.answer}.`;
  $("verdict").className = `verdict ${correct ? "ok" : "nok"}`;
  $("explanation").textContent = q.explanation;
  $("next").textContent = current + 1 < questions.length ? "Nächste Frage" : "Ergebnis anzeigen";
  $("feedback").hidden = false;
  $("next").focus();
}

function next() {
  current++;
  if (current < questions.length) renderQuestion();
  else showResult();
}

function showResult() {
  const ratio = score / questions.length;
  $("progress-bar").style.width = "100%";
  $("score").textContent = `${score} von ${questions.length}`;
  $("rating").textContent =
    ratio === 1 ? "Herzlichen Glückwunsch – Sie sind offiziell inoffiziell eingebürgert!"
    : ratio >= 0.5 ? "Bestanden! Noch ein bisschen Stoßlüften, und Sie sind perfekt integriert."
    : "Leider nicht bestanden. Holen Sie sich einen Pfandbon und versuchen Sie es erneut.";
  $("quiz").hidden = true;
  $("result").hidden = false;
}

function restart() {
  current = 0;
  score = 0;
  renderQuestion();
}

async function init() {
  $("next").addEventListener("click", next);
  $("restart").addEventListener("click", restart);
  try {
    const response = await fetch("questions.json", { cache: "no-cache" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (data.title) {
      document.title = data.title;
      $("title").textContent = data.title;
    }
    $("subtitle").textContent = data.subtitle ?? "";
    $("note").textContent = data.note ?? "";
    questions = data.questions;
    renderQuestion();
  } catch (err) {
    console.error(err);
    $("error").hidden = false;
  }
}

init();
