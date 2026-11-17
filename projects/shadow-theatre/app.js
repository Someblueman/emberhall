(() => {
  "use strict";

  if (!window.ShadowCore) {
    throw new Error("Shadow Theatre: scene-core.js must load before app.js");
  }
  const core = window.ShadowCore;
  const MAX_PROPS = core.MAX_PROPS;

  function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  let state = {
    mode: "single-gate",
    scene: deepClone(core.CHALLENGES[0]),
    selected: "prop-0",
    notice: "",
    noticeLevel: ""
  };

  const stageEl = document.getElementById("stage");
  const modeTitleEl = document.getElementById("mode-title");
  const modeDescEl = document.getElementById("mode-desc");
  const targetDisplayEl = document.getElementById("target-display");
  const statusBadgeEl = document.getElementById("status-badge");
  const intervalOutputEl = document.getElementById("interval-output");
  const errorOutputEl = document.getElementById("error-output");
  const ioMessageEl = document.getElementById("io-message");
  const selectionControlsEl = document.getElementById("selection-controls");
  const sandboxActionsEl = document.getElementById("sandbox-actions");
  const jsonIoEl = document.getElementById("json-io");

  function setNotice(text, level) {
    state.notice = text;
    state.noticeLevel = level || "";
  }

  function loadMode(modeId) {
    const known = core.CHALLENGES.find((c) => c.id === modeId);
    state.mode = modeId;
    state.scene = deepClone(known || core.SANDBOX_DEFAULT);
    state.selected = state.scene.props.length > 0 ? "prop-0" : "light";
    setNotice("", "");
    render();
  }

  function svgEl(tag, attrs = {}) {
    const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs)) {
      el.setAttribute(k, String(v));
    }
    return el;
  }

  function render() {
    document.querySelectorAll(".mode-buttons button").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.mode === state.mode);
      btn.setAttribute("aria-pressed", String(btn.dataset.mode === state.mode));
    });
    document.querySelectorAll("[data-object]").forEach((btn) => {
      const object = btn.dataset.object;
      btn.hidden = object !== "light" && Number(object.split("-")[1]) >= state.scene.props.length;
      btn.setAttribute("aria-pressed", String(object === state.selected));
    });
    document.getElementById("shrink-prop").disabled = state.selected === "light";
    document.getElementById("grow-prop").disabled = state.selected === "light";
    document.getElementById("moving-object").textContent = `Moving ${state.selected === "light" ? "the light" : `Prop ${Number(state.selected.split("-")[1]) + 1}`}.`;

    const view = core.describeScene(state.scene);

    modeTitleEl.textContent = view.title;
    modeDescEl.textContent = view.description;
    targetDisplayEl.textContent = view.targetText;
    sandboxActionsEl.hidden = state.mode !== "sandbox";

    errorOutputEl.textContent = view.errorText;
    intervalOutputEl.textContent = view.intervalText;
    statusBadgeEl.textContent = view.statusText;
    statusBadgeEl.className = view.statusClass;

    // Import/export diagnostics persist across renders until a mode load or a
    // successful import replaces them; a render must never erase them.
    if (ioMessageEl) {
      ioMessageEl.textContent = state.notice;
      ioMessageEl.className = state.noticeLevel === "error" ? "notice error" : "notice";
    }

    renderStage(view);
    renderSelectionControls();
  }

  function renderStage(view) {
    const { scene } = state;
    stageEl.innerHTML = "";

    // Screen line
    stageEl.appendChild(svgEl("line", {
      x1: scene.screen.x, y1: scene.screen.yMin,
      x2: scene.screen.x, y2: scene.screen.yMax,
      stroke: "#6b7280", "stroke-width": 1.5
    }));

    // Target intervals on screen
    for (const [ta, tb] of scene.target) {
      stageEl.appendChild(svgEl("line", {
        x1: scene.screen.x + 2.5, y1: ta,
        x2: scene.screen.x + 2.5, y2: tb,
        stroke: "#10b981", "stroke-width": 2.2
      }));
    }

    // Rays & cast shadows
    if (view.ok) {
      for (const r of view.rays) {
        stageEl.appendChild(svgEl("line", {
          x1: scene.light.x, y1: scene.light.y,
          x2: scene.screen.x, y2: r.ya,
          stroke: "#fde047", "stroke-opacity": 0.25, "stroke-width": 0.6, "stroke-dasharray": "2,2"
        }));
        stageEl.appendChild(svgEl("line", {
          x1: scene.light.x, y1: scene.light.y,
          x2: scene.screen.x, y2: r.yb,
          stroke: "#fde047", "stroke-opacity": 0.25, "stroke-width": 0.6, "stroke-dasharray": "2,2"
        }));
      }
      for (const [sa, sb] of view.intervals) {
        stageEl.appendChild(svgEl("line", {
          x1: scene.screen.x, y1: sa,
          x2: scene.screen.x, y2: sb,
          stroke: "#f87171", "stroke-width": 2.8
        }));
      }
    }

    // Props
    scene.props.forEach((p, idx) => {
      const isSel = state.selected === `prop-${idx}`;
      const line = svgEl("line", {
        x1: p.x, y1: p.yLow, x2: p.x, y2: p.yHigh,
        stroke: isSel ? "#60a5fa" : "#e5e7eb",
        "stroke-width": isSel ? 2.6 : 2.0,
        cursor: "pointer"
      });
      line.addEventListener("click", () => {
        state.selected = `prop-${idx}`;
        render();
      });
      stageEl.appendChild(line);
    });

    // Light
    const lightSel = state.selected === "light";
    const lightCircle = svgEl("circle", {
      cx: scene.light.x, cy: scene.light.y, r: lightSel ? 3.2 : 2.5,
      fill: "#facc15", stroke: lightSel ? "#60a5fa" : "#713f12", "stroke-width": 0.8,
      cursor: "pointer"
    });
    lightCircle.addEventListener("click", () => {
      state.selected = "light";
      render();
    });
    stageEl.appendChild(lightCircle);
  }

  let controlsForObject = null;
  function renderSelectionControls() {
    const { scene, selected } = state;
    const isLight = selected === "light";
    const object = isLight ? scene.light : scene.props[Number(selected.split("-")[1])];
    const fields = isLight ? [
      ["position-x", "Light across", "x"], ["position-y", "Light down", "y"]
    ] : [
      ["position-x", "Prop across", "x"], ["position-top", "Prop top", "yLow"],
      ["position-bottom", "Prop bottom", "yHigh"]
    ];
    // Keep the actual inputs while moving or editing this object. Replacing
    // a field during its blur/change event breaks the browser's next Tab stop.
    if (controlsForObject === object) {
      for (const [id, , key] of fields) {
        document.getElementById(id).value = String(Number(object[key].toFixed(2)));
      }
      return;
    }
    controlsForObject = object;
    selectionControlsEl.innerHTML = "";

    const selLabel = document.createElement("p");
    selLabel.className = "mono";
    selLabel.textContent = selected === "light" ? "Light" : `Prop ${Number(selected.split("-")[1]) + 1}`;
    selectionControlsEl.appendChild(selLabel);

    for (const [id, label, key] of fields) {
      addNumberField(id, label, object[key], (value) => { object[key] = value; });
    }
  }

  function addNumberField(id, labelText, value, onChange) {
    const row = document.createElement("div");
    row.className = "field-row";
    const label = document.createElement("label");
    label.textContent = labelText;
    label.htmlFor = id;
    const input = document.createElement("input");
    input.id = id;
    input.type = "number";
    input.step = "1";
    input.value = String(Number(value.toFixed(2)));
    input.addEventListener("change", () => {
      const num = Number(input.value);
      onChange(num);
      render();
    });
    row.appendChild(label);
    row.appendChild(input);
    selectionControlsEl.appendChild(row);
  }

  document.querySelectorAll(".mode-buttons button").forEach((btn) => {
    btn.addEventListener("click", () => loadMode(btn.dataset.mode));
  });

  document.querySelectorAll("[data-object]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.selected = btn.dataset.object;
      render();
    });
  });

  document.querySelectorAll("[data-move]").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (moveSelected(btn.dataset.move, 1)) render();
    });
  });

  document.getElementById("reset-btn").addEventListener("click", () => loadMode(state.mode));

  document.getElementById("add-prop-btn").addEventListener("click", () => {
    if (state.scene.props.length >= MAX_PROPS) {
      setNotice(`Out of domain: at most ${MAX_PROPS} props are allowed`, "error");
      render();
      return;
    }
    state.scene.props.push({ x: 55, yLow: 40, yHigh: 60 });
    state.selected = `prop-${state.scene.props.length - 1}`;
    render();
  });

  document.getElementById("remove-prop-btn").addEventListener("click", () => {
    if (state.scene.props.length > 0) {
      state.scene.props.pop();
      state.selected = state.scene.props.length > 0 ? `prop-${state.scene.props.length - 1}` : "light";
      render();
    }
  });

  // Export serializes only the scene that is currently displayed, and only if
  // that scene still validates. An invalid scene never reaches the textarea.
  document.getElementById("export-btn").addEventListener("click", () => {
    try {
      jsonIoEl.value = core.exportChallenge(state.scene);
      setNotice("Exported the displayed scene.", "ok");
    } catch (err) {
      setNotice(`Export refused: ${err.message}. The textarea was left unchanged.`, "error");
    }
    render();
  });

  // Import validates the complete challenge before touching state. On any
  // error the current scene, title, diagram, interval output and target stay
  // exactly as they were, and the diagnostic below persists across renders.
  document.getElementById("import-btn").addEventListener("click", () => {
    const result = core.applyImport(jsonIoEl.value);
    if (result.ok) {
      state.scene = result.scene;
      state.mode = "sandbox";
      state.selected = state.scene.props.length > 0 ? "prop-0" : "light";
      setNotice(`Imported challenge "${result.scene.title}".`, "ok");
    } else {
      setNotice(`Import rejected: ${result.error}. The current scene is unchanged.`, "error");
    }
    render();
  });

  // Touch buttons and keyboard shortcuts use the same one-step geometry.
  function moveSelected(key, step) {
    let targetObj = null;
    if (state.selected === "light") {
      targetObj = state.scene.light;
    } else if (state.selected.startsWith("prop-")) {
      targetObj = state.scene.props[Number(state.selected.split("-")[1])];
    }
    if (!targetObj) return false;

    if (key === "ArrowLeft") {
      targetObj.x -= step;
    } else if (key === "ArrowRight") {
      targetObj.x += step;
    } else if (key === "ArrowUp") {
      if (state.selected === "light") targetObj.y -= step;
      else { targetObj.yLow -= step; targetObj.yHigh -= step; }
    } else if (key === "ArrowDown") {
      if (state.selected === "light") targetObj.y += step;
      else { targetObj.yLow += step; targetObj.yHigh += step; }
    } else if (key === "[" && state.selected.startsWith("prop-")) {
      targetObj.yLow += step;
      targetObj.yHigh -= step;
    } else if (key === "]" && state.selected.startsWith("prop-")) {
      targetObj.yLow -= step;
      targetObj.yHigh += step;
    } else {
      return false;
    }
    return true;
  }

  document.addEventListener("keydown", (e) => {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
    if (e.key === "r" || e.key === "R") {
      loadMode(state.mode);
    } else if (e.key === "0") {
      state.selected = "light";
      render();
    } else if (["1", "2", "3"].includes(e.key)) {
      const idx = Number(e.key) - 1;
      if (idx < state.scene.props.length) {
        state.selected = `prop-${idx}`;
        render();
      }
    } else if (moveSelected(e.key, e.shiftKey ? 5 : 1)) {
      e.preventDefault();
      render();
    }
  });

  loadMode("single-gate");
})();
