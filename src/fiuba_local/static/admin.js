const refreshStatusBtn = document.getElementById("refresh-status-btn");
const semanticIndexBtn = document.getElementById("semantic-index-btn");
const semanticSearchBtn = document.getElementById("semantic-search-btn");
const adminStatusPill = document.getElementById("admin-status-pill");
const semanticIndexResult = document.getElementById("semantic-index-result");
const semanticResults = document.getElementById("semantic-results");

function setAdminStatus(text, mode = "idle") {
  adminStatusPill.textContent = text;
  adminStatusPill.dataset.mode = mode;
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

async function loadAdminStatus() {
  refreshStatusBtn.disabled = true;
  try {
    const resp = await fetch("/api/admin/status");
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "fallo estado");
    setText("root-path", data.root_path || "-");
    setText("db-path", data.db_path || "-");
    setText("semantic-db-path", data.semantic_db_path || "-");
    setText("semantic-model", data.semantic_model || "-");
    setText("fts-docs", data.fts?.documents ?? 0);
    setText("fts-chunks", data.fts?.chunks ?? 0);
    setText("semantic-docs", data.semantic?.documents ?? 0);
    setText("semantic-embeddings", data.semantic?.embeddings ?? 0);
  } catch (err) {
    setAdminStatus(`Error: ${err.message}`, "error");
  } finally {
    refreshStatusBtn.disabled = false;
  }
}

function formatSemanticIndex(stats) {
  return [
    `Archivos escaneados: ${stats.scanned ?? 0}`,
    `Actualizados: ${stats.updated ?? 0}`,
    `Sin cambios: ${stats.skipped_unchanged ?? 0}`,
    `Fragmentos: ${stats.fragments ?? 0}`,
    `Vectores creados: ${stats.embeddings_created ?? 0}`,
    `Vectores reutilizados: ${stats.embeddings_reused ?? 0}`,
    `Advertencias: ${stats.warnings ?? 0}`,
  ].join("\n");
}

async function runSemanticIndex() {
  semanticIndexBtn.disabled = true;
  semanticIndexResult.classList.add("hidden");
  semanticIndexResult.textContent = "";
  setAdminStatus("Indexando", "loading");
  const payload = {
    materia: document.getElementById("semantic-materia").value.trim() || "Ind Extractivas",
    limit_files: Number(document.getElementById("semantic-limit").value || 10),
  };
  try {
    const resp = await fetch("/api/admin/semantic-index", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "fallo indexado semantico");
    semanticIndexResult.textContent = formatSemanticIndex(data.stats || {});
    semanticIndexResult.classList.remove("hidden");
    await loadAdminStatus();
    setAdminStatus("Listo");
  } catch (err) {
    semanticIndexResult.textContent = `Error: ${err.message}`;
    semanticIndexResult.classList.remove("hidden");
    setAdminStatus("Error", "error");
  } finally {
    semanticIndexBtn.disabled = false;
  }
}

function renderSemanticResults(results) {
  semanticResults.innerHTML = "";
  if (!results.length) {
    const li = document.createElement("li");
    li.textContent = "Sin resultados semanticos para esa consulta. Proba indexar mas archivos o ajustar la materia.";
    semanticResults.appendChild(li);
    return;
  }
  for (const item of results) {
    const li = document.createElement("li");
    const page = item.page_start === item.page_end ? item.page_start : `${item.page_start}-${item.page_end}`;
    const title = document.createElement("div");
    title.className = "semantic-result-title";
    title.textContent = `${item.file} · p.${page} · ${item.document_type} · score ${Number(item.score).toFixed(3)}`;
    const path = document.createElement("div");
    path.className = "semantic-result-path";
    path.textContent = item.path || "";
    const excerpt = document.createElement("p");
    excerpt.textContent = item.excerpt || "";
    li.appendChild(title);
    li.appendChild(path);
    li.appendChild(excerpt);
    semanticResults.appendChild(li);
  }
}

async function runSemanticSearch() {
  const query = document.getElementById("semantic-query").value.trim();
  if (!query) {
    setAdminStatus("Falta consulta", "error");
    return;
  }
  semanticSearchBtn.disabled = true;
  semanticResults.innerHTML = "";
  setAdminStatus("Buscando", "loading");
  const payload = {
    query,
    materia: document.getElementById("semantic-filter").value.trim() || null,
    top_k: Number(document.getElementById("semantic-topk").value || 10),
  };
  try {
    const resp = await fetch("/api/admin/semantic-search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "falló la búsqueda semántica");
    const results = data.results || [];
    renderSemanticResults(results);
    setAdminStatus(`${results.length} resultado${results.length === 1 ? "" : "s"}`);
  } catch (err) {
    const li = document.createElement("li");
    li.textContent = `Error: ${err.message}`;
    semanticResults.appendChild(li);
    setAdminStatus("Error", "error");
  } finally {
    semanticSearchBtn.disabled = false;
  }
}

refreshStatusBtn.addEventListener("click", loadAdminStatus);
semanticIndexBtn.addEventListener("click", runSemanticIndex);
semanticSearchBtn.addEventListener("click", runSemanticSearch);

loadAdminStatus();
