const STORAGE_KEY = "extractivas-teoricas-progress-v1";

const state = {
  topicId: window.STUDY_DATA[0].id,
  mode: "quiz",
  index: 0,
  order: {},
  progress: loadProgress(),
  search: ""
};

const els = {
  topicList: document.querySelector("#topicList"),
  search: document.querySelector("#search"),
  modes: document.querySelectorAll(".mode"),
  topicTitle: document.querySelector("#topicTitle"),
  eyebrow: document.querySelector("#eyebrow"),
  scorePct: document.querySelector("#scorePct"),
  answeredCount: document.querySelector("#answeredCount"),
  progressBar: document.querySelector("#progressBar"),
  questionCounter: document.querySelector("#questionCounter"),
  difficultyTag: document.querySelector("#difficultyTag"),
  questionText: document.querySelector("#questionText"),
  questionHint: document.querySelector("#questionHint"),
  options: document.querySelector("#options"),
  feedback: document.querySelector("#feedback"),
  quizView: document.querySelector("#quizView"),
  flashView: document.querySelector("#flashView"),
  writeView: document.querySelector("#writeView"),
  flashAnswer: document.querySelector("#flashAnswer"),
  revealFlash: document.querySelector("#revealFlash"),
  writtenAnswer: document.querySelector("#writtenAnswer"),
  checkWritten: document.querySelector("#checkWritten"),
  prevQuestion: document.querySelector("#prevQuestion"),
  nextQuestion: document.querySelector("#nextQuestion"),
  shuffleTopic: document.querySelector("#shuffleTopic"),
  resetTopic: document.querySelector("#resetTopic")
};

function loadProgress() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
  } catch {
    return {};
  }
}

function saveProgress() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.progress));
}

function topic() {
  return window.STUDY_DATA.find((item) => item.id === state.topicId) || window.STUDY_DATA[0];
}

function getOrder(topicId = state.topicId) {
  const current = window.STUDY_DATA.find((item) => item.id === topicId);
  if (!state.order[topicId]) {
    state.order[topicId] = current.questions.map((_, index) => index);
  }
  return state.order[topicId];
}

function question() {
  const current = topic();
  return current.questions[getOrder()[state.index]];
}

function questionKey(topicId = state.topicId, idx = getOrder()[state.index]) {
  return `${topicId}:${idx}`;
}

function normalize(value) {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function renderTopics() {
  const query = normalize(state.search);
  els.topicList.innerHTML = "";

  window.STUDY_DATA
    .filter((item) => {
      const haystack = normalize(`${item.title} ${item.summary} ${item.questions.map((q) => q.q).join(" ")}`);
      return haystack.includes(query);
    })
    .forEach((item) => {
      const done = item.questions.filter((_, idx) => state.progress[`${item.id}:${idx}`]).length;
      const correct = item.questions.filter((_, idx) => state.progress[`${item.id}:${idx}`]?.correct).length;
      const pct = done ? Math.round((correct / done) * 100) : 0;
      const button = document.createElement("button");
      button.className = `topic-button ${item.id === state.topicId ? "active" : ""}`;
      button.style.setProperty("--topic-accent", item.accent);
      button.innerHTML = `
        <span class="topic-dot"></span>
        <span>
          <strong>${item.title}</strong>
          <small>${done}/${item.questions.length} vistas · ${pct}% bien</small>
        </span>
      `;
      button.addEventListener("click", () => {
        state.topicId = item.id;
        state.index = 0;
        clearTransient();
        render();
      });
      els.topicList.append(button);
    });
}

function renderStats() {
  const current = topic();
  const done = current.questions.filter((_, idx) => state.progress[`${current.id}:${idx}`]).length;
  const correct = current.questions.filter((_, idx) => state.progress[`${current.id}:${idx}`]?.correct).length;
  const pct = done ? Math.round((correct / done) * 100) : 0;
  els.scorePct.textContent = `${pct}%`;
  els.answeredCount.textContent = done;
  els.progressBar.style.width = `${(done / current.questions.length) * 100}%`;
}

function renderQuestion() {
  const current = topic();
  const order = getOrder();
  const q = question();
  const stored = state.progress[questionKey()];

  document.documentElement.style.setProperty("--accent", current.accent);
  els.topicTitle.textContent = current.title;
  els.eyebrow.textContent = current.summary;
  els.questionCounter.textContent = `${state.index + 1} / ${order.length}`;
  els.difficultyTag.textContent = q.difficulty || "Conceptual";
  els.questionText.textContent = q.q;
  els.questionHint.textContent = state.mode === "write"
    ? "Tip: apunta a componentes, principio de funcionamiento y criterio de uso."
    : "Elegi una respuesta y lee la devolucion antes de pasar.";

  els.options.innerHTML = "";
  (q.options || buildOptionsFromOpen(q)).forEach((option, idx) => {
    const button = document.createElement("button");
    button.className = "option-button";
    button.textContent = option;
    button.disabled = Boolean(stored);
    if (stored) {
      if (idx === q.answer) button.classList.add("correct");
      if (idx === stored.choice && !stored.correct) button.classList.add("wrong");
    }
    button.addEventListener("click", () => answerMultipleChoice(idx));
    els.options.append(button);
  });

  els.flashAnswer.textContent = q.answerText || q.explain || q.options?.[q.answer] || "";
  els.revealFlash.classList.remove("revealed");
  els.writtenAnswer.value = "";
  renderFeedback();
}

function buildOptionsFromOpen(q) {
  return [
    q.answerText,
    "Respuesta incompleta: nombraria el equipo pero no el principio de funcionamiento.",
    "Respuesta fuera de tema: mezclaria este proceso con otro sin justificar.",
    "Respuesta memoristica: copiaria un titulo sin explicar entradas, salidas ni componentes."
  ];
}

function answerMultipleChoice(choice) {
  const q = question();
  const correct = choice === (q.answer ?? 0);
  state.progress[questionKey()] = { correct, choice, at: Date.now() };
  saveProgress();
  render();
}

function checkWritten() {
  const q = question();
  const text = normalize(els.writtenAnswer.value);
  const keywords = q.keywords || [];
  const hits = keywords.filter((keyword) => text.includes(normalize(keyword)));
  const correct = hits.length >= Math.ceil(Math.min(keywords.length, 5) * 0.6);
  state.progress[questionKey()] = {
    correct,
    choice: -1,
    written: els.writtenAnswer.value,
    hits,
    at: Date.now()
  };
  saveProgress();
  renderFeedback(hits);
  renderStats();
  renderTopics();
}

function renderFeedback(forcedHits) {
  const q = question();
  const stored = state.progress[questionKey()];
  els.feedback.className = "feedback";
  if (!stored) {
    els.feedback.innerHTML = `
      <h4>Objetivo</h4>
      <p>${q.explain || q.answerText || "Responder con la idea central, componentes y criterio de aplicacion."}</p>
    `;
    return;
  }

  const hits = forcedHits || stored.hits || [];
  els.feedback.classList.add(stored.correct ? "is-correct" : "is-wrong");
  els.feedback.innerHTML = `
    <h4>${stored.correct ? "Bien encaminado" : "Ajuste necesario"}</h4>
    <p>${q.explain || q.answerText}</p>
    ${hits.length ? `<p class="keywords">Detecte: ${hits.join(", ")}</p>` : ""}
  `;
}

function setMode(mode) {
  state.mode = mode;
  els.modes.forEach((button) => {
    const active = button.dataset.mode === mode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
  document.querySelector(`#${mode}View`).classList.add("active");
  clearTransient();
  renderQuestion();
}

function clearTransient() {
  els.feedback.className = "feedback";
  els.revealFlash.classList.remove("revealed");
  els.writtenAnswer.value = "";
}

function move(delta) {
  const total = getOrder().length;
  state.index = (state.index + delta + total) % total;
  clearTransient();
  renderQuestion();
}

function shuffleCurrentTopic() {
  const current = topic();
  const order = current.questions.map((_, index) => index);
  for (let i = order.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  state.order[current.id] = order;
  state.index = 0;
  clearTransient();
  renderQuestion();
}

function resetTopic() {
  const current = topic();
  current.questions.forEach((_, idx) => delete state.progress[`${current.id}:${idx}`]);
  saveProgress();
  clearTransient();
  render();
}

function render() {
  renderTopics();
  renderStats();
  renderQuestion();
}

els.search.addEventListener("input", (event) => {
  state.search = event.target.value;
  renderTopics();
});

els.modes.forEach((button) => button.addEventListener("click", () => setMode(button.dataset.mode)));
els.prevQuestion.addEventListener("click", () => move(-1));
els.nextQuestion.addEventListener("click", () => move(1));
els.shuffleTopic.addEventListener("click", shuffleCurrentTopic);
els.resetTopic.addEventListener("click", resetTopic);
els.revealFlash.addEventListener("click", () => {
  els.revealFlash.classList.add("revealed");
  state.progress[questionKey()] = { correct: true, choice: -1, at: Date.now() };
  saveProgress();
  renderStats();
  renderTopics();
});
els.checkWritten.addEventListener("click", checkWritten);

window.addEventListener("keydown", (event) => {
  if (event.target.matches("input, textarea")) return;
  if (event.key === "ArrowRight") move(1);
  if (event.key === "ArrowLeft") move(-1);
  if (event.key >= "1" && event.key <= "4" && state.mode === "quiz") {
    const idx = Number(event.key) - 1;
    const option = els.options.children[idx];
    if (option && !option.disabled) option.click();
  }
});

render();
