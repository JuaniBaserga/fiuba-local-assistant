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
const copyBtn = document.getElementById("copy-btn");

const answerCard = document.getElementById("answer-card");
const sourcesCard = document.getElementById("sources-card");
const answerText = document.getElementById("answer-text");
const modelBadge = document.getElementById("model-badge");
const sourcesList = document.getElementById("sources-list");
const codexPromptWrap = document.getElementById("codex-prompt-wrap");
const codexPrompt = document.getElementById("codex-prompt");
const tabAskBtn = document.getElementById("tab-ask-btn");
const tabOcrBtn = document.getElementById("tab-ocr-btn");
const tabAsk = document.getElementById("tab-ask");
const tabOcr = document.getElementById("tab-ocr");
const ocrBtn = document.getElementById("ocr-btn");
const ocrCard = document.getElementById("ocr-card");
const ocrSummary = document.getElementById("ocr-summary");
const ocrList = document.getElementById("ocr-list");
const ocrMinTotalInput = document.getElementById("ocr-min-total");
const ocrMinPageInput = document.getElementById("ocr-min-page");
const ocrLimitInput = document.getElementById("ocr-limit");
const ocrOnlyNeedsSelect = document.getElementById("ocr-only-needs");

let latestPromptForCodex = "";
const MODEL_BY_ENGINE = {
  codex: "gemini-2.5-flash",
  gemini: "gemini-2.5-flash",
  openai: "gpt-4.1-mini",
  ollama: "qwen2.5:3b-instruct",
};

function applyEngineDefaultModel() {
  const engine = engineSelect.value || "codex";
  modelInput.value = MODEL_BY_ENGINE[engine] || modelInput.value;
}

function setStatus(text, mode = "idle") {
  statusPill.textContent = text;
  if (mode === "loading") {
    statusPill.style.background = "#eef4ff";
    statusPill.style.borderColor = "#cddaf1";
    statusPill.style.color = "#234e7b";
    return;
  }
  if (mode === "error") {
    statusPill.style.background = "#fff1ef";
    statusPill.style.borderColor = "#f4c9c4";
    statusPill.style.color = "#8f3428";
    return;
  }
  statusPill.style.background = "#eff9f8";
  statusPill.style.borderColor = "#cddfdd";
  statusPill.style.color = "#186865";
}

function renderSources(sources) {
  sourcesList.innerHTML = "";
  for (const source of sources) {
    const li = document.createElement("li");
    li.textContent = `[${source.id}] ${source.file} (chunk ${source.chunk})`;
    sourcesList.appendChild(li);
  }
}

function setActiveTab(tabName) {
  const askActive = tabName === "ask";
  tabAsk.classList.toggle("hidden", !askActive);
  tabOcr.classList.toggle("hidden", askActive);
  tabAskBtn.classList.toggle("active", askActive);
  tabOcrBtn.classList.toggle("active", !askActive);
}

function formatIndexResult(results) {
  if (!Array.isArray(results) || results.length === 0) return "Sin resultados.";
  const lines = [];
  for (const item of results) {
    if (!item.ok) {
      lines.push(`- ${item.materia}: ERROR (${item.error || "unknown"})`);
      continue;
    }
    const s = item.stats || {};
    lines.push(
      `- ${item.materia}: scanned=${s.scanned ?? 0}, updated=${s.updated ?? 0}, unchanged=${s.skipped_unchanged ?? 0}, warn=${s.warnings ?? 0}`
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
        const status = item.indexed ? "indexada" : "sin indexar";
        li.textContent = `${item.name} (${status})`;
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
    setStatus("Question required", "error");
    questionInput.focus();
    return;
  }

  askBtn.disabled = true;
  setStatus("Thinking...", "loading");
  answerCard.classList.add("hidden");
  sourcesCard.classList.add("hidden");
  copyBtn.classList.add("hidden");
  codexPromptWrap.classList.add("hidden");
  latestPromptForCodex = "";

  const payload = {
    question,
    materia: materiaSelect.value || null,
    engine: engineSelect.value || "codex",
    model: modelInput.value.trim() || "qwen2.5:3b-instruct",
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
      throw new Error(data.error || "request failed");
    }

    answerText.textContent = data.answer || "";
    modelBadge.textContent = data.model || payload.model;
    renderSources(data.sources || []);
    if (data.prompt_for_codex) {
      latestPromptForCodex = data.prompt_for_codex;
      codexPrompt.textContent = latestPromptForCodex;
      codexPromptWrap.classList.remove("hidden");
      copyBtn.classList.remove("hidden");
    }
    answerCard.classList.remove("hidden");
    sourcesCard.classList.remove("hidden");
    setStatus("Done");
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

function renderOcrResults(data) {
  const results = data.results || [];
  ocrList.innerHTML = "";
  if (!results.length) {
    const li = document.createElement("li");
    li.textContent = "No se detectaron candidatos OCR con los filtros actuales.";
    ocrList.appendChild(li);
    return;
  }

  for (const item of results) {
    const li = document.createElement("li");
    const pages = item.pages == null ? "?" : item.pages;
    const avg =
      item.avg_chars_per_page == null ? "?" : Number(item.avg_chars_per_page).toFixed(1);
    li.textContent =
      `[${item.needs_ocr ? "OCR" : "OK"}] ${item.path} | pages=${pages} chars=${item.total_chars} avg=${avg} | razon=${item.reason} | cmd: ${item.suggested_cmd}`;
    ocrList.appendChild(li);
  }
}

async function runOcrScan() {
  ocrBtn.disabled = true;
  setStatus("Scanning...", "loading");
  ocrCard.classList.add("hidden");

  const payload = {
    materia: materiaSelect.value || null,
    min_total_chars: Number(ocrMinTotalInput.value || 120),
    min_chars_per_page: Number(ocrMinPageInput.value || 60),
    limit: Number(ocrLimitInput.value || 100),
    only_needs_ocr: ocrOnlyNeedsSelect.value !== "false",
  };

  try {
    const resp = await fetch("/api/ocr/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.error || "ocr request failed");
    }

    renderOcrResults(data);
    ocrSummary.textContent = `${data.count} archivos`;
    ocrCard.classList.remove("hidden");
    setStatus("Done");
  } catch (err) {
    ocrList.innerHTML = "";
    const li = document.createElement("li");
    li.textContent = `Error: ${err.message}`;
    ocrList.appendChild(li);
    ocrSummary.textContent = "Error";
    ocrCard.classList.remove("hidden");
    setStatus("Error", "error");
  } finally {
    ocrBtn.disabled = false;
  }
}

async function runIndex() {
  indexBtn.disabled = true;
  refreshMateriasBtn.disabled = true;
  setStatus("Indexing...", "loading");
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
      throw new Error(data.error || "index request failed");
    }
    indexResult.textContent = formatIndexResult(data.results || []);
    indexResult.classList.remove("hidden");
    await loadMaterias();
    setStatus("Done");
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
ocrBtn.addEventListener("click", runOcrScan);
copyBtn.addEventListener("click", async () => {
  if (!latestPromptForCodex) return;
  await navigator.clipboard.writeText(latestPromptForCodex);
  setStatus("Copied");
});
questionInput.addEventListener("keydown", (ev) => {
  if ((ev.metaKey || ev.ctrlKey) && ev.key === "Enter") {
    ask();
  }
});
tabAskBtn.addEventListener("click", () => setActiveTab("ask"));
tabOcrBtn.addEventListener("click", () => setActiveTab("ocr"));
refreshMateriasBtn.addEventListener("click", loadMaterias);
indexBtn.addEventListener("click", runIndex);

engineSelect.addEventListener("change", applyEngineDefaultModel);
applyEngineDefaultModel();
setActiveTab("ask");
loadMaterias();
