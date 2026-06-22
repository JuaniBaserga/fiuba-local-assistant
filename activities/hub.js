const activities = {
  assistant: {
    src: "http://127.0.0.1:8787/",
    title: "Preguntar al asistente",
    frameTitle: "FIUBA Assistant",
  },
  extractivas: {
    src: "ind-extractivas-teoricas/",
    title: "Industrias Extractivas",
    frameTitle: "Actividad de Industrias Extractivas",
  },
  auto: {
    src: "auto-verdadero-falso/",
    title: "Automatización",
    frameTitle: "Actividad de Automatización Industrial",
  },
};

const frame = document.querySelector("#activityFrame");
const cards = document.querySelectorAll(".activity-card");
const select = document.querySelector("#activitySelect");
const mobileTitle = document.querySelector("#mobileTitle");

function showActivity(activityId, updateHash = true) {
  const activity = activities[activityId] || activities.assistant;

  if (!frame.src.endsWith(activity.src)) {
    frame.src = activity.src;
  }
  frame.title = activity.frameTitle;
  mobileTitle.textContent = activity.title;
  select.value = activityId;

  cards.forEach((card) => {
    const isActive = card.dataset.activity === activityId;
    card.classList.toggle("active", isActive);
    if (isActive) {
      card.setAttribute("aria-current", "page");
    } else {
      card.removeAttribute("aria-current");
    }
  });

  if (updateHash) {
    history.replaceState(null, "", `#${activityId}`);
  }
}

cards.forEach((card) => {
  card.addEventListener("click", () => showActivity(card.dataset.activity));
});

select.addEventListener("change", () => showActivity(select.value));
window.addEventListener("hashchange", () => showActivity(location.hash.slice(1), false));

showActivity(location.hash.slice(1), false);
