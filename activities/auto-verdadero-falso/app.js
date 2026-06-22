const categoryLabels = {
  all: "Todo",
  motores: "Motores",
  plc: "PLC",
  sensores: "Sensores",
  encoders: "Encoders",
  neumatica: "Neumática",
};

const state = {
  category: "all",
  order: [],
  currentIndex: 0,
  answered: new Map(),
  correct: 0,
  totalAnswered: 0,
  streak: 0,
};

const els = {
  tabs: document.querySelectorAll(".tab"),
  shuffle: document.querySelector("#shuffleToggle"),
  reset: document.querySelector("#resetBtn"),
  question: document.querySelector("#questionText"),
  progress: document.querySelector("#progressText"),
  category: document.querySelector("#categoryPill"),
  trueBtn: document.querySelector("#trueBtn"),
  falseBtn: document.querySelector("#falseBtn"),
  feedback: document.querySelector("#feedback"),
  feedbackTitle: document.querySelector("#feedbackTitle"),
  feedbackText: document.querySelector("#feedbackText"),
  source: document.querySelector("#sourceText"),
  prev: document.querySelector("#prevBtn"),
  next: document.querySelector("#nextBtn"),
  score: document.querySelector("#scoreText"),
  streak: document.querySelector("#streakText"),
  available: document.querySelector("#availableCount"),
  answered: document.querySelector("#answeredCount"),
  accuracy: document.querySelector("#accuracyText"),
};

function filteredQuestions() {
  if (state.category === "all") return window.QUESTIONS;
  return window.QUESTIONS.filter((question) =>
    question.categories.includes(state.category),
  );
}

function shuffledIndexes(length) {
  const indexes = Array.from({ length }, (_, index) => index);
  for (let i = indexes.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [indexes[i], indexes[j]] = [indexes[j], indexes[i]];
  }
  return indexes;
}

function rebuildOrder(keepPosition = false) {
  const questions = filteredQuestions();
  const previousQuestion = currentQuestion();
  state.order = els.shuffle.checked
    ? shuffledIndexes(questions.length)
    : Array.from({ length: questions.length }, (_, index) => index);

  if (keepPosition && previousQuestion) {
    const newIndex = state.order.findIndex(
      (questionIndex) => questions[questionIndex]?.id === previousQuestion.id,
    );
    state.currentIndex = newIndex >= 0 ? newIndex : 0;
  } else {
    state.currentIndex = 0;
  }
}

function currentQuestion() {
  const questions = filteredQuestions();
  const questionIndex = state.order[state.currentIndex];
  return questions[questionIndex];
}

function setCategory(category) {
  state.category = category;
  els.tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.category === category);
  });
  rebuildOrder();
  render();
}

function resetStats() {
  state.answered.clear();
  state.correct = 0;
  state.totalAnswered = 0;
  state.streak = 0;
  rebuildOrder();
  render();
}

function answer(value) {
  const question = currentQuestion();
  if (!question || state.answered.has(question.id)) return;

  const isCorrect = value === question.answer;
  state.answered.set(question.id, { value, isCorrect });
  state.totalAnswered += 1;
  if (isCorrect) {
    state.correct += 1;
    state.streak += 1;
  } else {
    state.streak = 0;
  }
  render();
}

function move(delta) {
  const lastIndex = state.order.length - 1;
  state.currentIndex = Math.min(Math.max(state.currentIndex + delta, 0), lastIndex);
  render();
}

function renderFeedback(question, savedAnswer) {
  els.feedback.className = "feedback hidden";
  els.trueBtn.classList.remove("selected");
  els.falseBtn.classList.remove("selected");
  els.trueBtn.disabled = false;
  els.falseBtn.disabled = false;

  if (!savedAnswer) return;

  const selectedButton = savedAnswer.value === "V" ? els.trueBtn : els.falseBtn;
  selectedButton.classList.add("selected");
  els.trueBtn.disabled = true;
  els.falseBtn.disabled = true;

  els.feedback.className = `feedback ${savedAnswer.isCorrect ? "correct" : "incorrect"}`;
  els.feedbackTitle.textContent = savedAnswer.isCorrect
    ? "Bien"
    : `No: era ${question.answer === "V" ? "Verdadero" : "Falso"}`;
  els.feedbackText.textContent = question.explanation;
  els.source.textContent = `${question.source} · ítem ${question.numberInSource}`;
}

function renderStats() {
  const questions = filteredQuestions();
  const accuracy = state.totalAnswered
    ? Math.round((state.correct / state.totalAnswered) * 100)
    : 0;

  els.score.textContent = `${state.correct} / ${state.totalAnswered}`;
  els.streak.textContent = `racha ${state.streak}`;
  els.available.textContent = questions.length;
  els.answered.textContent = state.totalAnswered;
  els.accuracy.textContent = `${accuracy}%`;
}

function render() {
  const questions = filteredQuestions();
  const question = currentQuestion();

  els.category.textContent = categoryLabels[state.category];
  els.available.textContent = questions.length;

  if (!question) {
    els.question.textContent = "No hay preguntas para este filtro.";
    els.progress.textContent = "0 de 0";
    els.trueBtn.disabled = true;
    els.falseBtn.disabled = true;
    els.prev.disabled = true;
    els.next.disabled = true;
    els.feedback.className = "feedback hidden";
    renderStats();
    return;
  }

  const savedAnswer = state.answered.get(question.id);
  els.question.textContent = question.statement;
  els.progress.textContent = `Pregunta ${state.currentIndex + 1} de ${state.order.length}`;
  els.prev.disabled = state.currentIndex === 0;
  els.next.disabled = state.currentIndex === state.order.length - 1;

  renderFeedback(question, savedAnswer);
  renderStats();
}

els.tabs.forEach((tab) => {
  tab.addEventListener("click", () => setCategory(tab.dataset.category));
});

els.shuffle.addEventListener("change", () => {
  rebuildOrder(true);
  render();
});

els.reset.addEventListener("click", resetStats);
els.trueBtn.addEventListener("click", () => answer("V"));
els.falseBtn.addEventListener("click", () => answer("F"));
els.prev.addEventListener("click", () => move(-1));
els.next.addEventListener("click", () => move(1));

document.addEventListener("keydown", (event) => {
  if (event.key.toLowerCase() === "v") answer("V");
  if (event.key.toLowerCase() === "f") answer("F");
  if (event.key === "ArrowRight") move(1);
  if (event.key === "ArrowLeft") move(-1);
});

rebuildOrder();
render();
