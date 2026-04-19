const endpoints = {
  nowPlaying: "/nowplaying",
  stations: "/radiostations",
  nowPlayingSocket: "/ws/nowplaying",
  playStation: (stationId) => `/radiostations/${stationId}/play`
};

const elements = {
  title: document.getElementById("track-title"),
  name: document.getElementById("track-name"),
  list: document.getElementById("stations-list"),
  emptyState: document.getElementById("empty-state"),
  refreshButton: document.getElementById("refresh-button"),
  addButton: document.getElementById("add-button"),
  stationDialog: document.getElementById("station-dialog"),
  stationForm: document.getElementById("station-form"),
  stationDialogTitle: document.getElementById("station-dialog-title"),
  stationSubmitButton: document.getElementById("station-submit-button"),
  stationTitle: document.getElementById("station-title"),
  stationUrl: document.getElementById("station-url"),
  cancelStation: document.getElementById("cancel-station"),
  toast: document.getElementById("toast")
};

let stations = [];
let stationDialogMode = "add";
let editingStationId = null;
let toastTimer = null;
let nowPlayingSocket = null;

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 2200);
}

async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string" ? payload.detail : "Unbekannter Fehler";
    throw new Error(detail);
  }
  return payload;
}

function setNowPlaying(data) {
  const hasTitle = Boolean(data.title && data.title.trim());
  const hasName = Boolean(data.name && data.name.trim());
  elements.title.textContent = hasTitle ? data.title : "Keine Wiedergabe";
  elements.name.textContent = hasName ? data.name : "";
}

function createIcon(iconId) {
  const svgNamespace = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNamespace, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS(svgNamespace, "use");
  use.setAttribute("href", `#${iconId}`);
  svg.append(use);
  return svg;
}

function createActionButton(iconId, label, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "ui-button icon-action-button";
  button.setAttribute("aria-label", label);
  button.setAttribute("title", label);
  button.append(createIcon(iconId));
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    onClick();
  });
  return button;
}

function renderStations() {
  elements.list.innerHTML = "";

  if (stations.length === 0) {
    elements.emptyState.hidden = false;
    return;
  }

  elements.emptyState.hidden = true;

  stations.forEach((station) => {
    const item = document.createElement("li");
    item.className = "station-item";
    item.tabIndex = 0;

    const main = document.createElement("div");
    main.className = "station-main";

    const title = document.createElement("p");
    title.className = "station-title";
    title.textContent = station.title;
    main.append(title);

    const actions = document.createElement("div");
    actions.className = "station-actions";

    const editButton = createActionButton("icon-edit", "Bearbeiten", () => {
      openStationDialog("edit", station);
    });

    const deleteButton = createActionButton("icon-trash", "Löschen", async () => {
      await onDeleteStation(station);
    });

    actions.append(editButton, deleteButton);
    item.append(main, actions);
    item.addEventListener("click", async () => {
      await onPlayStation(station);
    });
    item.addEventListener("keydown", async (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        await onPlayStation(station);
      }
    });
    elements.list.append(item);
  });
}

async function loadNowPlaying() {
  const nowPlaying = await fetch(endpoints.nowPlaying).then(parseResponse);
  setNowPlaying(nowPlaying);
}

async function loadStations() {
  stations = await fetch(endpoints.stations).then(parseResponse);
  renderStations();
}

async function refreshStations(showSuccess = false) {
  try {
    await loadStations();
    if (showSuccess) {
      showToast("Daten aktualisiert");
    }
  } catch (error) {
    showToast(`Fehler: ${error.message}`);
  }
}

function closeStationDialog() {
  elements.stationDialog.close();
  editingStationId = null;
}

function openStationDialog(mode, station = null) {
  stationDialogMode = mode;

  if (mode === "edit" && station !== null) {
    editingStationId = station.id;
    elements.stationDialogTitle.textContent = "Radiosender bearbeiten";
    elements.stationSubmitButton.textContent = "Speichern";
    elements.stationTitle.value = station.title;
    elements.stationUrl.value = station.url;
  } else {
    editingStationId = null;
    elements.stationDialogTitle.textContent = "Radiosender hinzufügen";
    elements.stationSubmitButton.textContent = "Hinzufügen";
    elements.stationForm.reset();
  }

  elements.stationDialog.showModal();
}

function connectNowPlayingSocket() {
  if (nowPlayingSocket !== null) {
    nowPlayingSocket.close();
  }

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  nowPlayingSocket = new WebSocket(`${protocol}://${window.location.host}${endpoints.nowPlayingSocket}`);

  nowPlayingSocket.addEventListener("message", (event) => {
    try {
      const data = JSON.parse(event.data);
      setNowPlaying(data);
    } catch (_error) {
      showToast("Now Playing Daten konnten nicht gelesen werden");
    }
  });

  nowPlayingSocket.addEventListener("close", () => {
    window.setTimeout(connectNowPlayingSocket, 1500);
  });

  nowPlayingSocket.addEventListener("error", () => {
    nowPlayingSocket.close();
  });
}

async function onDeleteStation(station) {
  const confirmed = window.confirm(`Sender \"${station.title}\" wirklich löschen?`);
  if (!confirmed) {
    return;
  }

  try {
    await fetch(`${endpoints.stations}/${station.id}`, { method: "DELETE" }).then(parseResponse);
    showToast("Sender gelöscht");
    await loadStations();
  } catch (error) {
    showToast(`Löschen fehlgeschlagen: ${error.message}`);
  }
}

async function onPlayStation(station) {
  try {
    await fetch(endpoints.playStation(station.id), { method: "POST" }).then(parseResponse);
    showToast(`Spiele: ${station.title}`);
  } catch (error) {
    showToast(`Start fehlgeschlagen: ${error.message}`);
  }
}

elements.refreshButton.addEventListener("click", () => {
  refreshStations(true);
});

elements.addButton.addEventListener("click", () => {
  openStationDialog("add");
});

elements.stationForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    title: elements.stationTitle.value.trim(),
    url: elements.stationUrl.value.trim()
  };

  if (!payload.title || !payload.url) {
    showToast("Titel und URL sind erforderlich");
    return;
  }

  try {
    if (stationDialogMode === "edit") {
      if (editingStationId === null) {
        return;
      }

      await fetch(`${endpoints.stations}/${editingStationId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).then(parseResponse);
      showToast("Sender gespeichert");
    } else {
      await fetch(endpoints.stations, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).then(parseResponse);
      showToast("Sender hinzugefügt");
    }

    closeStationDialog();
    await loadStations();
  } catch (error) {
    showToast(`Speichern fehlgeschlagen: ${error.message}`);
  }
});

elements.cancelStation.addEventListener("click", () => {
  closeStationDialog();
});

elements.stationDialog.addEventListener("cancel", () => {
  elements.stationForm.reset();
  editingStationId = null;
});

loadNowPlaying();
connectNowPlayingSocket();
refreshStations();
