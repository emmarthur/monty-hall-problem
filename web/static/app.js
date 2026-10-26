const doorsRoot = document.getElementById("doors");
const choiceRow = document.getElementById("choice-row");
const pickPrompt = document.getElementById("pick-prompt");
const roundResult = document.getElementById("round-result");
const errorEl = document.getElementById("error-text");
const btnStay = document.getElementById("btn-stay");
const btnSwitch = document.getElementById("btn-switch");
const btnResetRound = document.getElementById("btn-reset-round");
const monteBtn = document.getElementById("monte-btn");
const monteStatus = document.getElementById("monte-status");
const progressBar = document.getElementById("progress-bar");
const monteStats = document.getElementById("monte-stats");
const stayStat = document.getElementById("stay-stat");
const switchStat = document.getElementById("switch-stat");

let gameId = null;
let monteSource = null;

function showError(msg) {
  if (!msg) {
    errorEl.hidden = true;
    errorEl.textContent = "";
    return;
  }
  errorEl.hidden = false;
  errorEl.textContent = msg;
}

function resetRoundUi() {
  gameId = null;
  choiceRow.hidden = true;
  btnResetRound.hidden = true;
  roundResult.textContent = "";
  pickPrompt.textContent = "Pick a door to start.";
  doorsRoot.querySelectorAll(".door").forEach((btn) => {
    btn.disabled = false;
    btn.classList.remove("opened", "picked", "winner");
  });
}

doorsRoot.addEventListener("click", async (event) => {
  const btn = event.target.closest(".door");
  if (!btn || btn.disabled) return;
  showError("");
  const door = Number(btn.dataset.door);
  try {
    const res = await fetch("/api/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ door }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not start round.");
    gameId = data.game_id;
    pickPrompt.textContent = `You picked door ${door}. Host opens door ${data.host_opens} (goat). Stay or switch?`;
    doorsRoot.querySelectorAll(".door").forEach((d) => {
      const n = Number(d.dataset.door);
      d.disabled = true;
      if (n === door) d.classList.add("picked");
      if (n === data.host_opens) d.classList.add("opened");
    });
    choiceRow.hidden = false;
  } catch (err) {
    showError(err.message);
  }
});

async function finishRound(switchDoor) {
  if (!gameId) return;
  showError("");
  try {
    const res = await fetch("/api/finish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ game_id: gameId, switch: switchDoor }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not finish round.");
    choiceRow.hidden = true;
    btnResetRound.hidden = false;
    doorsRoot.querySelectorAll(".door").forEach((d) => {
      if (Number(d.dataset.door) === data.car_door) d.classList.add("winner");
    });
    const action = data.switched ? "Switched" : "Stayed";
    roundResult.textContent = `${action} on door ${data.final_door}. Car was on door ${data.car_door}. ${
      data.won ? "You win!" : "Goat — try again."
    }`;
    gameId = null;
  } catch (err) {
    showError(err.message);
  }
}

btnStay.addEventListener("click", () => finishRound(false));
btnSwitch.addEventListener("click", () => finishRound(true));
btnResetRound.addEventListener("click", resetRoundUi);

function closeMonte() {
  if (monteSource) {
    monteSource.close();
    monteSource = null;
  }
}

monteBtn.addEventListener("click", () => {
  closeMonte();
  monteStats.hidden = true;
  progressBar.style.width = "0%";
  monteStatus.textContent = "Running…";
  monteBtn.disabled = true;
  const total = window.MONTY_CONFIG.simulationCount;
  monteSource = new EventSource("/stream/monte-carlo");
  monteSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "progress") {
      const pct = Math.round((data.completed / total) * 100);
      progressBar.style.width = `${pct}%`;
      monteStatus.textContent = `${data.completed.toLocaleString()} / ${total.toLocaleString()} trials`;
    } else if (data.type === "done") {
      progressBar.style.width = "100%";
      monteStatus.textContent = "Simulation complete.";
      stayStat.textContent = `${data.stay_percent}% (${data.stay_wins.toLocaleString()} wins)`;
      switchStat.textContent = `${data.switch_percent}% (${data.switch_wins.toLocaleString()} wins)`;
      monteStats.hidden = false;
      monteBtn.disabled = false;
      closeMonte();
    }
  };
  monteSource.onerror = () => {
    monteStatus.textContent = "Connection lost.";
    monteBtn.disabled = false;
    closeMonte();
  };
});

document.querySelectorAll("[data-help-jump]").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.getElementById("help-heading")?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

resetRoundUi();
