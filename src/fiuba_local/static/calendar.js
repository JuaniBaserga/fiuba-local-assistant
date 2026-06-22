const refreshStudyBtn = document.getElementById("refresh-study-btn");
const studyInitBtn = document.getElementById("study-init-btn");
const studyPlanBtn = document.getElementById("study-plan-btn");
const studyReportBtn = document.getElementById("study-report-btn");
const studyIcsBtn = document.getElementById("study-ics-btn");
const studyActionResult = document.getElementById("study-action-result");
const calendarStatusPill = document.getElementById("calendar-status-pill");
const studySessions = document.getElementById("study-sessions");
const studySummary = document.getElementById("study-summary");

function setCalendarStatus(text, mode = "idle") {
  calendarStatusPill.textContent = text;
  calendarStatusPill.dataset.mode = mode;
}

function renderStudyStatus(data) {
  document.getElementById("study-dates-path").textContent = data.dates_path || "-";
  document.getElementById("study-state-path").textContent = data.state_path || "-";
  document.getElementById("study-events-count").textContent = String(data.events_count ?? 0);
  document.getElementById("study-sessions-count").textContent = String(data.planned_sessions_count ?? 0);
  document.getElementById("study-completed-count").textContent = String(data.completed_sessions_count ?? 0);
  const cfg = data.config || {};
  document.getElementById("study-week-count").textContent = `${cfg.weekly_hours ?? 0} h/sem`;

  studySummary.textContent = data.ready ? "Plan disponible" : "Sin estado inicial";
  studySessions.innerHTML = "";
  for (const session of data.planned_sessions || []) {
    const li = document.createElement("li");
    li.className = session.completed ? "done" : "";
    const start = session.start?.replace("T", " ").slice(0, 16) || "";
    const page = session.target_date || "";
    const title = document.createElement("div");
    title.className = "study-session-title";
    title.textContent = `${session.materia || ""} · ${start}`;
    const meta = document.createElement("div");
    meta.className = "study-session-meta";
    meta.textContent = `${session.target_title || ""} · ${session.focus_topic || ""}`;
    const reason = document.createElement("p");
    reason.textContent = session.focus_reason || "";
    const target = document.createElement("small");
    target.textContent = `${page}${session.completed ? " · completada" : ""}`;
    li.append(title, meta, reason, target);
    studySessions.appendChild(li);
  }
}

function downloadIcs(payload) {
  const blob = new Blob([payload], { type: "text/calendar;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "fiuba-study-plan.ics";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function loadStudyStatus() {
  refreshStudyBtn.disabled = true;
  try {
    const resp = await fetch("/api/study/status");
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "fallo estado");
    renderStudyStatus(data);
    setCalendarStatus("Listo");
  } catch (err) {
    setCalendarStatus("Error", "error");
    studySummary.textContent = `Error: ${err.message}`;
  } finally {
    refreshStudyBtn.disabled = false;
  }
}

async function runStudyAction(url, body = {}) {
  studyActionResult.classList.add("hidden");
  studyActionResult.textContent = "";
  setCalendarStatus("Procesando", "loading");
  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "accion fallida");
    if (typeof data.ics === "string") downloadIcs(data.ics);
    studyActionResult.textContent = JSON.stringify(data, null, 2);
    studyActionResult.classList.remove("hidden");
    await loadStudyStatus();
    setCalendarStatus("Listo");
  } catch (err) {
    studyActionResult.textContent = `Error: ${err.message}`;
    studyActionResult.classList.remove("hidden");
    setCalendarStatus("Error", "error");
  }
}

refreshStudyBtn.addEventListener("click", loadStudyStatus);
studyInitBtn.addEventListener("click", () => runStudyAction("/api/study/init", { overwrite: false }));
studyPlanBtn.addEventListener("click", () => runStudyAction("/api/study/plan", {}));
studyReportBtn.addEventListener("click", () => runStudyAction("/api/study/report", {}));
studyIcsBtn.addEventListener("click", () => runStudyAction("/api/study/export-ics", {}));

loadStudyStatus();
