if (window.self !== window.top) {
  document.body.classList.add("is-embedded");
}

const statusPill = document.getElementById("status-pill");
const materiaSelect = document.getElementById("materia");
const materiaCount = document.getElementById("materia-count");
const materiaList = document.getElementById("materia-list");
const refreshMateriasBtn = document.getElementById("refresh-materias-btn");
const indexBtn = document.getElementById("index-btn");
const indexResult = document.getElementById("index-result");
const modelInput = document.getElementById("model");
const engineSelect = document.getElementById("engine");
const topkInput = document.getElementById("topk");
const timeoutInput = document.getElementById("timeout");
const questionInput = document.getElementById("question");
const askBtn = document.getElementById("ask-btn");
const answerCard = document.getElementById("answer-card");
const sourcesCard = document.getElementById("sources-card");
const answerText = document.getElementById("answer-text");
const modelBadge = document.getElementById("model-badge");
const sourcesList = document.getElementById("sources-list");

const MODEL_BY_ENGINE = {
  gemini: "gemini-2.5-flash",
  openai: "gpt-4.1-mini",
  ollama: "qwen2.5:3b-instruct",
};

function applyEngineDefaultModel() {
  const engine = engineSelect.value || "gemini";
  modelInput.value = MODEL_BY_ENGINE[engine] || modelInput.value;
}

function setStatus(text, mode = "idle") {
  statusPill.textContent = text;
  statusPill.dataset.mode = mode;
}

function renderSources(sources) {
  sourcesList.innerHTML = "";
  for (const source of sources) {
    const li = document.createElement("li");
    const title = document.createElement("div");
    const excerpt = document.createElement("p");
    title.textContent = `[${source.id}] ${source.file} (chunk ${source.chunk})`;
    excerpt.textContent = source.excerpt || "";
    li.appendChild(title);
    li.appendChild(excerpt);
    sourcesList.appendChild(li);
  }
}

function formatIndexResult(results) {
  if (!Array.isArray(results) || results.length === 0) return "Sin resultados.";
  const lines = [];
  for (const item of results) {
    if (!item.ok) {
      lines.push(`- ${item.materia}: error (${item.error || "desconocido"})`);
      continue;
    }
    const s = item.stats || {};
    lines.push(
      `- ${item.materia}: ${s.updated ?? 0} actualizados, ${s.skipped_unchanged ?? 0} sin cambios, ${s.warnings ?? 0} advertencias`
    );
  }
  return lines.join("\n");
}

async function loadMaterias() {
  refreshMateriasBtn.disabled = true;
  try {
    const resp = await fetch("/api/materias");
    if (!resp.ok) {
      materiaCount.textContent = "Detectadas: error";
      return;
    }
    const data = await resp.json();
    const materias = data.materias || [];
    const indexedMaterias = data.indexed_materias || [];
    const items = data.items || materias.map((name) => ({ name, indexed: false }));

    materiaSelect.innerHTML = "";
    const allOpt = document.createElement("option");
    allOpt.value = "";
    allOpt.textContent = "Todas";
    materiaSelect.appendChild(allOpt);

    materiaList.innerHTML = "";
    for (const materia of materias) {
      const opt = document.createElement("option");
      opt.value = materia;
      opt.textContent = materia;
      materiaSelect.appendChild(opt);
    }

    if (items.length === 0) {
      const li = document.createElement("li");
      li.textContent = "No se detectaron materias en la carpeta raiz.";
      materiaList.appendChild(li);
    } else {
      for (const item of items) {
        const li = document.createElement("li");
        li.className = item.indexed ? "indexed" : "pending";
        li.textContent = `${item.name} · ${item.indexed ? "indexada" : "sin indexar"}`;
        materiaList.appendChild(li);
      }
    }

    materiaCount.textContent = `Detectadas: ${materias.length} | Indexadas: ${indexedMaterias.length}`;
  } catch {
    materiaCount.textContent = "Detectadas: error";
  } finally {
    refreshMateriasBtn.disabled = false;
  }
}

async function ask() {
  const question = questionInput.value.trim();
  if (!question) {
    setStatus("Falta pregunta", "error");
    questionInput.focus();
    return;
  }

  askBtn.disabled = true;
  setStatus("Pensando", "loading");
  answerCard.classList.add("hidden");
  sourcesCard.classList.add("hidden");

  const payload = {
    question,
    materia: materiaSelect.value || null,
    engine: engineSelect.value || "gemini",
    model: modelInput.value.trim() || MODEL_BY_ENGINE[engineSelect.value || "gemini"],
    top_k: Number(topkInput.value || 6),
    timeout_sec: Number(timeoutInput.value || 300),
  };

  try {
    const resp = await fetch("/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.error || "fallo la consulta");
    }

    answerText.textContent = data.answer || "";
    modelBadge.textContent = data.model || payload.model;
    renderSources(data.sources || []);
    answerCard.classList.remove("hidden");
    sourcesCard.classList.remove("hidden");
    setStatus("Listo");
  } catch (err) {
    answerText.textContent = `Error: ${err.message}`;
    modelBadge.textContent = payload.model;
    answerCard.classList.remove("hidden");
    sourcesCard.classList.add("hidden");
    setStatus("Error", "error");
  } finally {
    askBtn.disabled = false;
  }
}

async function runIndex() {
  indexBtn.disabled = true;
  refreshMateriasBtn.disabled = true;
  setStatus("Indexando", "loading");
  indexResult.classList.add("hidden");
  indexResult.textContent = "";

  const payload = { materia: materiaSelect.value || null };
  try {
    const resp = await fetch("/api/index", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.error || "fallo el indexado");
    }
    indexResult.textContent = formatIndexResult(data.results || []);
    indexResult.classList.remove("hidden");
    await loadMaterias();
    setStatus("Listo");
  } catch (err) {
    indexResult.textContent = `Error: ${err.message}`;
    indexResult.classList.remove("hidden");
    setStatus("Error", "error");
  } finally {
    indexBtn.disabled = false;
    refreshMateriasBtn.disabled = false;
  }
}

askBtn.addEventListener("click", ask);
questionInput.addEventListener("keydown", (ev) => {
  if ((ev.metaKey || ev.ctrlKey) && ev.key === "Enter") {
    ask();
  }
});
refreshMateriasBtn.addEventListener("click", loadMaterias);
indexBtn.addEventListener("click", runIndex);
engineSelect.addEventListener("change", applyEngineDefaultModel);

applyEngineDefaultModel();
loadMaterias();
