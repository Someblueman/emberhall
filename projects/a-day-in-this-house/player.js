/* Plain-data episode player. The only input is the local, authored episodes file. */
(function () {
  "use strict";
  function validate(episodes) {
    if (!Array.isArray(episodes) || !episodes.length) throw Error("No episodes supplied");
    const ids = new Set();
    for (const e of episodes) {
      if (!/^[a-z][a-z0-9-]*$/.test(e.id) || ids.has(e.id)) throw Error("Invalid or duplicate episode id");
      ids.add(e.id);
      if (!e.title || !e.author || e.date !== "2026-11-19") throw Error("Episode needs a title, author and this edition's date");
      if (!Number.isFinite(e.seconds) || e.seconds < 6 || e.seconds > 60) throw Error("Invalid scene duration");
      if (!Array.isArray(e.scenes) || e.scenes.length < 3 || e.scenes.length > 6) throw Error("Use three to six scenes");
      if (!e.exhibit || !["codebook", "text"].includes(e.exhibit.kind) || !e.exhibit.title || !e.exhibit.body) throw Error("Invalid exhibit");
      if (e.exhibit.kind === "codebook") verifyCodebook(e.exhibit.words);
      for (const s of e.scenes) {
        for (const key of ["label", "title", "body", "credit", "caption"]) {
          if (typeof s[key] !== "string" || !s[key].trim()) throw Error("Missing scene " + key);
        }
        if (!["codebook", "clock", "result", "text"].includes(s.visual)) throw Error("Unknown scene visual");
        if (s.visual === "codebook" && e.exhibit.kind !== "codebook") throw Error("Codebook visual needs words");
        if (!Array.isArray(s.sources) || !s.sources.length) throw Error("Each scene needs sources");
        for (const source of s.sources) {
          if (!source.label || !/^https:\/\//.test(source.url)) throw Error("Source must be a labelled HTTPS link");
          const url = new URL(source.url);
          if (url.username || url.password) throw Error("Source must not contain credentials");
        }
      }
    }
    return episodes;
  }
  function erase(word, positions) {
    return Array.from(word).filter((_, i) => !positions.includes(i)).join("");
  }
  function verifyCodebook(words) {
    if (!Array.isArray(words) || !words.length || new Set(words).size !== words.length || words.some(w => !/^[01]{12}$/.test(w))) throw Error("Invalid twelve-bit codebook");
    const owners = new Map();
    for (const word of words) {
      for (let i = 0; i < 11; i++) for (let j = i + 1; j < 12; j++) {
        const output = erase(word, [i, j]);
        if (owners.has(output) && owners.get(output) !== word) throw Error("Ambiguous codebook output");
        owners.set(output, word);
      }
    }
    return owners;
  }
  function move(index, change, count) { return Math.max(0, Math.min(count - 1, index + change)); }
  function route(hash, episodes) {
    const [id, raw] = hash.replace(/^#/, "").split("/");
    const episode = Math.max(0, episodes.findIndex(e => e.id === id));
    const scene = /^\d+$/.test(raw || "") ? move(0, Number(raw), episodes[episode].scenes.length) : 0;
    return {episode, scene};
  }
  if (typeof module !== "undefined") module.exports = {validate, erase, verifyCodebook, move, route};
  if (typeof document === "undefined") return;

  const $ = id => document.getElementById(id);
  const add = (tag, parent, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    parent.append(node);
    return node;
  };
  try {
    const episodes = validate(HOUSE_EPISODES);
    let {episode, scene} = route(location.hash, episodes);
    let timer = null;
    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    $("still").checked = reduced.matches;
    const current = () => episodes[episode];
    function pause(message = "Paused. Read at your own pace, or choose Play.") {
      clearTimeout(timer); timer = null;
      $("play").textContent = "Play";
      $("play").setAttribute("aria-pressed", "false");
      $("play-status").textContent = message;
    }
    function render() {
      const e = current(), s = e.scenes[scene];
      $("chapter").textContent = `${scene + 1} / ${e.scenes.length} · ${s.label}`;
      $("scene-title").textContent = s.title;
      $("scene-body").textContent = s.body;
      $("attribution").textContent = s.credit;
      $("caption").textContent = s.caption;
      $("previous").disabled = scene === 0;
      $("next").disabled = scene === e.scenes.length - 1;
      const art = $("evidence-art"); art.replaceChildren();
      if (s.visual === "codebook") {
        const count = add("div", art, String(e.exhibit.words.length), "count");
        add("small", count, "/ 38");
        const grid = add("div", art, undefined, "word-grid");
        for (let i = 0; i < Math.max(38, e.exhibit.words.length); i++) add("span", grid, "", "word-mark" + (i >= e.exhibit.words.length ? " missing" : ""));
        add("span", art, "Valid words · target missed", "board-label");
      } else if (s.visual === "clock") {
        for (const [big, small] of [["240 seconds", "requested for the original attempt"], ["0.1 → about 6 seconds", "a later review probe exposed the clock"], ["Original elapsed time?", "not established by the saved evidence"]]) {
          const row = add("div", art, undefined, "clock-line");
          add("strong", row, big); add("span", row, small);
        }
      } else if (s.visual === "result") {
        add("pre", art, "PASS: 36 words of length 12\n66 deletion pairs / word\n544 distinct ten-bit outputs\n\nTarget: at least 38\nResult: below threshold", "output");
      } else add("blockquote", art, s.excerpt || s.title, "output");
      $("source-list").replaceChildren();
      for (const source of s.sources) {
        const link = add("a", add("li", $("source-list")), source.label + " ↗");
        link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer";
      }
      $("chapters").replaceChildren();
      e.scenes.forEach((item, i) => {
        const b = add("button", $("chapters"), `${i + 1}. ${item.label}`);
        b.type = "button"; b.setAttribute("aria-current", String(i === scene));
        b.addEventListener("click", () => { pause(); scene = i; render(); $("story").focus(); });
      });
      history.replaceState(null, "", `#${e.id}/${scene}`);
    }
    function advance() {
      if (scene === current().scenes.length - 1) { pause("The episode has ended. The work and its limits remain open to inspect."); return; }
      scene++; render(); timer = setTimeout(advance, current().seconds * 1000);
    }
    episodes.forEach((e, i) => {
      const b = add("button", $("episodes"), `${i + 1}. ${e.title}`);
      b.type = "button"; b.setAttribute("aria-current", String(i === episode));
      b.addEventListener("click", () => {
        pause(); episode = i; scene = 0;
        Array.from($("episodes").children).forEach((node, n) => node.setAttribute("aria-current", String(n === i)));
        render(); pause(); $("story").focus();
      });
    });
    $("previous").onclick = () => { pause(); scene = move(scene, -1, current().scenes.length); render(); $("story").focus(); };
    $("next").onclick = () => { pause(); scene = move(scene, 1, current().scenes.length); render(); $("story").focus(); };
    $("play").onclick = () => {
      if (timer !== null) { pause(); return; }
      if (scene === current().scenes.length - 1) { scene = 0; render(); }
      $("play").textContent = "Pause"; $("play").setAttribute("aria-pressed", "true");
      $("play-status").textContent = `Playing. Each scene stays for ${current().seconds} seconds.`;
      $("story").scrollIntoView({block: "start"});
      timer = setTimeout(advance, current().seconds * 1000);
    };
    $("replay").onclick = () => { pause(); scene = 0; render(); $("story").focus(); };
    $("still").onchange = () => { pause($("still").checked ? "Still reading: scenes change only when you choose them." : "Paused. Choose Play to start."); $("play").disabled = $("still").checked; };
    reduced.addEventListener("change", e => { if (e.matches) { $("still").checked = true; $("still").onchange(); } });
    document.addEventListener("visibilitychange", () => { if (document.hidden) pause(); });
    window.addEventListener("hashchange", () => {
      pause(); ({episode, scene} = route(location.hash, episodes));
      Array.from($("episodes").children).forEach((b, i) => b.setAttribute("aria-current", String(i === episode)));
      render();
    });
    $("inspect").onclick = () => {
      pause("Paused while you inspect the original work.");
      const exhibit = current().exhibit, body = $("exhibit-body"); body.replaceChildren();
      $("exhibit-title").textContent = exhibit.title;
      add("p", body, exhibit.body, "exhibit-note");
      if (exhibit.kind === "codebook") buildCodebook(body, exhibit.words);
      else add("pre", body, exhibit.text || exhibit.body, "output");
      $("exhibit").showModal(); $("close").focus();
    };
    $("close").onclick = () => $("exhibit").close();
    $("exhibit").addEventListener("close", () => {
      pause(`Paused. Returned to scene ${scene + 1}: ${current().scenes[scene].label}.`);
      $("inspect").focus();
    });
    function buildCodebook(body, words) {
      const owners = verifyCodebook(words);
      const label = add("label", body, "Choose one saved twelve-bit word"); label.htmlFor = "word";
      const select = add("select", body); select.id = "word";
      select.setAttribute("aria-label", "Choose one saved twelve-bit word");
      words.forEach((w, i) => { const option = add("option", select, `${String(i + 1).padStart(2, "0")} · ${w}`); option.value = w; });
      select.value = words[9];
      add("p", body, "Press two positions to erase them. Press an erased position to restore it. Positions start at 1.", "small");
      const bits = add("div", body, undefined, "bits"); bits.setAttribute("role", "group"); bits.setAttribute("aria-label", "Twelve bit positions");
      const result = add("div", body, undefined, "decode"); result.setAttribute("role", "status");
      let deleted = [0, 1];
      function show() {
        bits.replaceChildren();
        Array.from(select.value).forEach((bit, i) => {
          const b = add("button", bits, bit); b.type = "button";
          b.setAttribute("aria-label", `Position ${i + 1}: ${bit}`); b.setAttribute("aria-pressed", String(deleted.includes(i)));
          b.onclick = () => {
            if (deleted.includes(i)) deleted = deleted.filter(n => n !== i);
            else if (deleted.length < 2) deleted.push(i);
            show(); bits.children[i].focus();
          };
        });
        if (deleted.length !== 2) { result.textContent = `Erase exactly two positions (${deleted.length} selected).`; return; }
        const output = erase(select.value, deleted);
        result.textContent = `Received: ${output}\nOnly matching saved word: ${owners.get(output)}`;
      }
      select.onchange = () => { deleted = [0, 1]; show(); };
      show();
      const details = add("details", body); add("summary", details, "All 36 saved words");
      const list = add("ol", details, undefined, "word-list"); words.forEach(w => add("li", list, w));
      add("p", body, "The exhibit checks all 66 deletion pairs for each word locally. It finds 544 distinct outputs and rejects any output shared by different saved words. This is not a proof that 36 is the largest possible codebook.", "small");
    }
    render(); pause(); $("play").disabled = $("still").checked;
  } catch (error) {
    $("error").hidden = false;
    $("error").textContent = "This episode could not load: " + error.message + ". The original result remains linked below.";
  }
})();
