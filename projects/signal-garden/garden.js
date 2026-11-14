"use strict";

(() => {
  const model = SignalGarden;
  const byId = id => document.getElementById(id);
  const seed = [0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0];
  let picture = seed.slice();
  let stage = 0;
  let results = null;
  let prediction = "";
  const titles = ["Encode the rows", "Send the bits", "Flip the burst", "Decode and compare"];
  const descriptions = [
    "Parity positions 1, 2 and 4 protect each row. Order within a block: P1 P2 D1 P4 D2 D3 D4. Both layouts use the same four blocks.",
    "Consecutive sends all seven bits of A, then B, C, D. Interleaved sends A1 B1 C1 D1, then A2 B2 C2 D2, and so on. Read channel chips left to right, top to bottom.",
    "The same channel positions flip in both layouts. Put the received bits back into their own row blocks and count the injected errors.",
    "Each decoder uses its parity syndrome to attempt a flip. Compare recovered pixels to the known original. That comparison belongs to this simulator, not to a real receiver."
  ];

  function node(tag, text, className) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  }

  function paintTile(tile, bit) {
    tile.textContent = String(bit);
    tile.className = `tile${bit ? " ink" : ""}`;
  }

  function restart(message = "Choose a prediction to begin. Nothing advances by itself.") {
    results = null;
    stage = 0;
    byId("prediction").value = "";
    byId("begin").disabled = true;
    byId("walkthrough").hidden = true;
    byId("comparison").replaceChildren();
    byId("trace").textContent = "";
    byId("verdict").textContent = "";
    byId("verdict").hidden = true;
    byId("status").textContent = message;
  }

  const tiles = picture.map((bit, i) => {
    const tile = node("button");
    tile.type = "button";
    paintTile(tile, bit);
    tile.setAttribute("aria-label", `Row ${Math.floor(i / 4) + 1}, column ${i % 4 + 1}`);
    tile.setAttribute("aria-pressed", String(Boolean(bit)));
    tile.addEventListener("click", () => {
      picture[i] ^= 1;
      paintTile(tile, picture[i]);
      tile.setAttribute("aria-pressed", String(Boolean(picture[i])));
      restart("Picture changed. Make a fresh prediction.");
    });
    byId("picture").append(tile);
    return tile;
  });

  byId("reset-picture").addEventListener("click", () => {
    picture = seed.slice();
    tiles.forEach((tile, i) => {
      paintTile(tile, picture[i]);
      tile.setAttribute("aria-pressed", String(Boolean(picture[i])));
    });
    restart("Seed picture restored. Make a fresh prediction.");
  });

  function updateBurst() {
    const length = Number(byId("burst-length").value);
    byId("burst-start").max = String(29 - Math.max(1, length));
    byId("burst-start").value = String(Math.min(Number(byId("burst-start").value), Number(byId("burst-start").max)));
    byId("start-value").textContent = byId("burst-start").value;
    restart("Burst changed. Make a fresh prediction.");
  }
  byId("burst-start").addEventListener("input", updateBurst);
  byId("burst-length").addEventListener("change", updateBurst);
  byId("prediction").addEventListener("change", () => {
    const selected = byId("prediction").value;
    if (results) {
      restart("Prediction changed. Start a fresh run.");
      byId("prediction").value = selected;
    }
    byId("begin").disabled = !byId("prediction").value;
  });

  function render() {
    byId("stage-title").textContent = `${stage + 1} / 4 · ${titles[stage]}`;
    byId("stage-description").textContent = descriptions[stage];
    byId("previous").disabled = stage === 0;
    // Keep this focused control usable at the final step, without disabling it.
    byId("next").textContent = stage === 3 ? "Return to encoding" : "Next step";
    byId("comparison").replaceChildren();
    const traces = [];
    for (const result of results) {
      const panel = node("article", undefined, "layout");
      panel.append(node("h3", result.layout === "consecutive" ? "Consecutive rows" : "Interleaved rows"));
      panel.append(node("p", "16 picture bits · 28 channel bits", "hint"));
      const encodedText = result.encoded.map((word, i) => `${"ABCD"[i]} ${result.rows[i].join("")} → ${word.join("")}`).join("\n");
      panel.append(node("pre", encodedText, "blocks"));
      let currentTrace = `${result.layout.toUpperCase()}\nEncoded rows (P1 P2 D1 P4 D2 D3 D4):\n${encodedText}`;
      if (stage >= 1) {
        panel.append(node("p", stage >= 2 ? "Received channel (× = flipped)" : "Sent channel", "hint"));
        const channel = node("div", undefined, "channel");
        const values = stage >= 2 ? result.received : result.sent;
        const channelTrace = [];
        values.forEach((bit, i) => {
          const row = "ABCD"[result.order[i].row];
          const hit = stage >= 2 && result.sent[i] !== bit;
          const chip = node("span", `${row}${bit}${hit ? "×" : ""}`, `chip${hit ? " hit" : ""}`);
          chip.setAttribute("aria-label", `Channel ${i + 1}, row ${row}, block bit ${result.order[i].column + 1}, value ${bit}${hit ? ", flipped" : ""}`);
          channel.append(chip);
          channelTrace.push(`${i + 1}:${row}${bit}${hit ? "[flipped]" : ""}`);
        });
        panel.append(channel);
        currentTrace += `\n${stage >= 2 ? "Received" : "Sent"} channel:\n${channelTrace.join(" ")}`;
      }
      if (stage >= 2) {
        const blocks = result.blocks.map((word, i) => `${"ABCD"[i]} ${word.join("")} · ${result.errors[i]} injected error(s)`).join("\n");
        panel.append(node("pre", blocks, "blocks"));
        currentTrace += `\nReceived row blocks (simulator error counts):\n${blocks}`;
      }
      if (stage === 3) {
        const recovered = node("div", undefined, "picture recovered");
        recovered.setAttribute("role", "img");
        recovered.setAttribute("aria-label", `Recovered picture, rows: ${result.decoded.map(row => row.data.join("")).join(", ")}`);
        result.recovered.forEach(bit => {
          const tile = node("span");
          paintTile(tile, bit);
          recovered.append(tile);
        });
        panel.append(recovered, node("p", result.matches ? "Matches original · 0 changed pixels" : `${result.changed} changed pixel(s) · recovery failed`));
        panel.append(node("pre", result.decoded.map((row, i) => `${"ABCD"[i]} syndrome ${row.syndrome} → attempted flip ${row.syndrome || "none"}`).join("\n"), "blocks"));
        currentTrace = model.trace(result);
      }
      traces.push(currentTrace);
      byId("comparison").append(panel);
    }
    byId("trace").textContent = traces.join("\n\n");
    byId("verdict").hidden = stage !== 3;
    byId("verdict").textContent = "";
    if (stage === 3) {
      const actual = model.outcome(...results);
      const names = { both: "Both layouts recover the picture", consecutive: "Only consecutive recovers the picture",
        interleaved: "Only interleaved recovers the picture", neither: "Neither layout recovers the picture" };
      byId("verdict").textContent = `${prediction === actual ? "Your prediction matches." : "A surprise to investigate."} ${names[actual]}. Check the errors per block above; the order, not extra redundancy, made the difference.`;
    }
    byId("status").textContent = `Paused at step ${stage + 1} of 4. ${titles[stage]}.`;
  }

  byId("begin").addEventListener("click", () => {
    if (!byId("prediction").value) return;
    prediction = byId("prediction").value;
    const start = Number(byId("burst-start").value) - 1;
    const length = Number(byId("burst-length").value);
    results = ["consecutive", "interleaved"].map(layout => model.run(picture, start, length, layout));
    stage = 0;
    byId("walkthrough").hidden = false;
    render();
    byId("stage-title").focus();
  });
  byId("previous").addEventListener("click", () => { stage = Math.max(0, stage - 1); render(); });
  byId("next").addEventListener("click", () => { stage = (stage + 1) % 4; render(); });
  byId("try-again").addEventListener("click", () => { restart(); byId("prediction").focus(); });
})();
