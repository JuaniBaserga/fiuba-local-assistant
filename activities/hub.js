const activities = {
  assistant: {
    src: "/",
    title: "Preguntar al asistente",
    frameTitle: "Asistente FIUBA",
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
  const targetUrl = new URL(activity.src, window.location.href).toString();

  if (frame.src !== targetUrl) {
    frame.src = targetUrl;
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
