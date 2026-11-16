"use strict";

// The Python generator supplies validated v2 data. Downloads still pass Python's
// strict validator, baseline-byte check and immutable-field check before writing.
function startEditor(document, environment) {
  const data = JSON.parse(document.getElementById("editor-data").textContent);
  const status = document.getElementById("editor-status");
  const download = document.getElementById("download");
  const showJSON = document.getElementById("export-json");
  const exportPanel = document.getElementById("edits-export");
  const exportText = document.getElementById("edits-json");
  const container = document.getElementById("comments");
  const index = document.getElementById("comment-index");
  const originals = data.document.comments.map(c => ({body: c.body, resolution: c.resolution}));
  const fields = [];
  const renderedComments = [];
  let needsDownload = false;
  let draftPending = () => false;
  let refreshPreview = () => {};
  let applyCommentFilters = () => {};
  let resetCommentFilters = () => {};
  let jumpToAnchor = null;

  function node(tag, text, parent) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    parent.appendChild(element);
    return element;
  }

  function clearChildren(element) {
    if (typeof element.replaceChildren === "function") element.replaceChildren();
    else while (element.children.length) element.children[0].remove();
  }

  function fixedText(text) {
    return text.replace(/[\x00-\x08\x0b-\x1f\x7f-\x9f\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]/g,
      character => "\\u" + character.charCodeAt(0).toString(16).padStart(4, "0"));
  }

  function anchorText(anchor) {
    return fixedText(`${anchor.path} | ${anchor.side} line ${anchor.line}\nCommit: ${anchor.commit}\n${anchor.text}`);
  }

  function sameAnchor(a, b) {
    return a.commit === b.commit && a.path === b.path && a.side === b.side && a.line === b.line && a.text === b.text;
  }

  function labeledControl(tag, id, labelText, parent, className) {
    const wrapper = className ? node("div", undefined, parent) : parent;
    if (className) wrapper.className = className;
    const caption = node("label", labelText, wrapper);
    caption.htmlFor = id;
    const control = node(tag, undefined, wrapper);
    control.id = id;
    control.setAttribute("aria-label", labelText);
    return control;
  }

  function addOptions(select, items) {
    for (const [value, label] of items) {
      const option = node("option", label, select);
      option.value = value;
    }
  }

  function changedCount() {
    return data.document.comments.filter((c, i) =>
      !originals[i] || c.body !== originals[i].body || c.resolution !== originals[i].resolution).length;
  }

  function updateStatus() {
    status.textContent = `${data.document.comments.length} comments. ${changedCount()} changed. ` +
      (needsDownload ? "Changes need saving. Download edits or show edits JSON to save a copy, then apply with the CLI." :
        "No new changes to export. The packet is unchanged until you apply edits with the CLI.");
  }

  function editsChanged() {
    exportText.textContent = "";
    exportPanel.hidden = true;
    needsDownload = true;
    updateStatus();
  }

  const anchorData = document.getElementById("anchor-data");
  const anchors = anchorData ? JSON.parse(anchorData.textContent) : null;

  if (data.document.comments.length || anchors) {
    const filterBox = node("div", undefined, container);
    filterBox.id = "comment-filters";
    filterBox.hidden = !data.document.comments.length;
    const filterRow = node("div", undefined, filterBox);
    filterRow.className = "filter-row";
    const filterResolution = labeledControl("select", "filter-resolution", "Filter comments by resolution", filterRow, "filter-field");
    addOptions(filterResolution, [["all", "All resolutions"], ["open", "open"], ["resolved", "resolved"]]);
    filterResolution.value = "all";
    const filterState = labeledControl("select", "filter-state", "Filter comments by anchor state", filterRow, "filter-field");
    addOptions(filterState, [["all", "All anchor states"], ["anchored", "anchored"], ["orphan", "orphan"]]);
    filterState.value = "all";
    const filterQuery = labeledControl("input", "filter-comment-query", "Search comments (ID, file, line, or body)", filterRow, "filter-field");
    filterQuery.type = "search";
    const filterStatus = node("p", "", filterBox);
    filterStatus.id = "comment-filter-status";
    filterStatus.setAttribute("role", "status");
    filterStatus.setAttribute("aria-live", "polite");

    applyCommentFilters = () => {
      const total = renderedComments.length;
      filterBox.hidden = total === 0;
      if (!total) { filterStatus.textContent = "0 comments."; return; }
      const resVal = filterResolution.value;
      const stateVal = filterState.value;
      const queryVal = filterQuery.value.trim().toLowerCase();
      let shown = 0;
      for (const entry of renderedComments) {
        const c = entry.comment;
        const fields = [c.id, c.anchor.path, c.anchor.text || "", c.body, c.orphan_reason || ""];
        if (c.rebased_from) fields.push(c.rebased_from.path || "", c.rebased_from.text || "");
        const matches = (resVal === "all" || c.resolution === resVal) &&
          (stateVal === "all" || c.state === stateVal) &&
          (!queryVal || fields.some(value => value.toLowerCase().includes(queryVal)));
        entry.article.hidden = !matches;
        entry.indexItem.hidden = !matches;
        if (matches) shown += 1;
      }
      filterStatus.textContent = (resVal === "all" && stateVal === "all" && !queryVal)
        ? `Showing all ${total} comments.`
        : `Showing ${shown} of ${total} comments.`;
    };

    resetCommentFilters = () => {
      filterResolution.value = "all";
      filterState.value = "all";
      filterQuery.value = "";
      applyCommentFilters();
    };

    filterResolution.addEventListener("change", applyCommentFilters);
    filterState.addEventListener("change", applyCommentFilters);
    filterQuery.addEventListener("input", applyCommentFilters);
  }

  function renderComment(comment, i) {
    const identifier = `comment-${i}`;
    const item = node("li", undefined, index);
    const link = node("a", comment.id, item);
    link.href = `#${identifier}`;
    const article = node("article", undefined, container);
    article.id = identifier;
    article.setAttribute("aria-labelledby", `${identifier}-title`);
    const heading = node("h2", comment.id, article);
    heading.id = `${identifier}-title`;
    const state = node("p", `Anchor state: ${comment.state}.`, article);
    state.id = `${identifier}-state`;
    node("pre", anchorText(comment.anchor), article);
    if (comment.orphan_reason !== null) node("p", `Orphan reason: ${fixedText(comment.orphan_reason)}`, article);
    if (comment.rebased_from !== null) {
      node("h3", "Rebased from", article);
      node("pre", anchorText(comment.rebased_from), article);
    }
    if (anchors && comment.state === "anchored") {
      const anchorIndex = anchors.findIndex(a => sameAnchor(a, comment.anchor));
      if (anchorIndex !== -1) {
        const reply = node("button", "Comment on same line", article);
        reply.type = "button";
        reply.setAttribute("aria-label", `Comment on same line as ${comment.id}`);
        reply.addEventListener("click", () => { if (jumpToAnchor) jumpToAnchor(anchorIndex, comment.anchor); });
      }
    }
    const body = labeledControl("textarea", `${identifier}-body`, `Body for ${comment.id}`, article);
    body.required = true;
    body.setAttribute("aria-describedby", state.id);
    body.value = comment.body;
    const resolution = labeledControl("select", `${identifier}-resolution`, `Resolution for ${comment.id}`, article);
    addOptions(resolution, [["open", "open"], ["resolved", "resolved"]]);
    resolution.value = comment.resolution;
    body.addEventListener("input", () => {
      const value = body.value;
      const valid = value.trim().length > 0 && Array.from(value).length <= 20000 && !value.includes("\0");
      body.setCustomValidity(valid ? "" : "Enter nonempty text of at most 20000 characters, without NUL.");
      comment.body = value;
      editsChanged();
      refreshPreview();
    });
    // Defer body filtering until the edit is committed or focus leaves: a
    // textarea must not disappear when its text stops matching during typing.
    body.addEventListener("change", applyCommentFilters);
    body.addEventListener("blur", applyCommentFilters);
    resolution.addEventListener("change", () => {
      comment.resolution = resolution.value;
      editsChanged();
      refreshPreview();
      applyCommentFilters();
    });
    fields.push(body);
    renderedComments.push({comment, article, indexItem: item});
  }

  if (anchors) {
    const composer = document.getElementById("composer");
    node("h2", "Add an anchored comment", composer);
    if (!anchors.length) {
      node("p", "This packet has no rendered lines to comment on.", composer);
    } else {
      const sideGroups = new Map();
      const fileCounts = new Map();
      anchors.forEach((anchor, i) => {
        fileCounts.set(anchor.path, (fileCounts.get(anchor.path) || 0) + 1);
        const key = `${anchor.path}\0${anchor.side}`;
        if (!sideGroups.has(key)) sideGroups.set(key, []);
        sideGroups.get(key).push({index: i, anchor});
      });
      for (const group of sideGroups.values()) group.sort((a, b) => a.anchor.line - b.anchor.line);

      const form = node("form", undefined, composer);
      const filterRow = node("div", undefined, form);
      filterRow.className = "filter-row";
      const filterFile = labeledControl("select", "filter-file", "Filter by file", filterRow, "filter-field");
      addOptions(filterFile, [["", `All files (${anchors.length} lines)`],
        ...[...fileCounts.entries()].map(([path, count]) => [path, fixedText(`${path} (${count})`)])]);
      filterFile.value = "";
      const filterSide = labeledControl("select", "filter-side", "Filter by side", filterRow, "filter-field");
      addOptions(filterSide, [["", "All sides"], ["new", "new (head)"], ["old", "old (base)"]]);
      filterSide.value = "";
      const filterText = labeledControl("input", "filter-text", "Search line text or number", filterRow, "filter-field");
      filterText.type = "search";

      const anchorStatus = node("p", "", form);
      anchorStatus.id = "anchor-filter-status";
      anchorStatus.setAttribute("role", "status");
      anchorStatus.setAttribute("aria-live", "polite");

      const line = labeledControl("select", "new-anchor", "Rendered line (path, side and line number)", form);
      const preview = node("pre", "", form);
      preview.id = "new-anchor-preview";
      line.setAttribute("aria-describedby", preview.id);

      function renderAnchorPreview(anchorIndex) {
        const selected = anchors[anchorIndex];
        if (!selected) {
          preview.textContent = "No rendered line matches the current filter.";
          return;
        }
        const group = sideGroups.get(`${selected.path}\0${selected.side}`) || [];
        const contextLines = group.filter(item => Math.abs(item.anchor.line - selected.line) <= 3).map(item =>
          fixedText(`${item.index === anchorIndex ? ">" : " "} ${item.anchor.line}: ${item.anchor.text}`));
        const parts = [
          fixedText(`${selected.path} | ${selected.side} line ${selected.line}`),
          `Commit: ${selected.commit}`,
          "",
          ...contextLines,
        ];
        const onLine = data.document.comments.filter(c => c.state === "anchored" && sameAnchor(c.anchor, selected));
        if (onLine.length) {
          parts.push("", `Comments on this line (${onLine.length}):`);
          for (const item of onLine) {
            const snippet = fixedText(item.body.replace(/\s+/g, " ").trim()).slice(0, 120);
            parts.push(`- ${item.id} [${item.resolution}]: ${snippet}`);
          }
        }
        preview.textContent = parts.join("\n");
      }

      refreshPreview = () => {
        if (line.value === "" || !anchors[Number(line.value)]) renderAnchorPreview(-1);
        else renderAnchorPreview(Number(line.value));
      };

      function refreshAnchorOptions(preferredIndex, announcement) {
        const current = line.value !== "" ? Number(line.value) : -1;
        const fileVal = filterFile.value;
        const sideVal = filterSide.value;
        const textVal = filterText.value.trim().toLowerCase();
        const matches = [];
        anchors.forEach((anchor, i) => {
          if (fileVal && anchor.path !== fileVal) return;
          if (sideVal && anchor.side !== sideVal) return;
          if (textVal && !anchor.path.toLowerCase().includes(textVal) &&
              !anchor.text.toLowerCase().includes(textVal) && !String(anchor.line).includes(textVal)) return;
          matches.push({anchor, index: i});
        });
        clearChildren(line);
        for (const {anchor, index: i} of matches) {
          const option = node("option", fixedText(`${anchor.path} | ${anchor.side} ${anchor.line}: ${anchor.text}`).slice(0, 180), line);
          option.value = String(i);
        }
        if (!matches.length) {
          line.value = "";
          line.setCustomValidity("No rendered line matches the current filter.");
          preview.textContent = "No rendered line matches the current filter.";
          anchorStatus.textContent = `0 of ${anchors.length} rendered lines match. Adjust the filters above.`;
          return;
        }
        const chosen = (preferredIndex !== undefined && matches.some(m => m.index === preferredIndex)) ? preferredIndex :
          (matches.some(m => m.index === current) ? current : matches[0].index);
        line.value = String(chosen);
        line.setCustomValidity("");
        renderAnchorPreview(chosen);
        anchorStatus.textContent = announcement || `Showing ${matches.length} of ${anchors.length} rendered lines.`;
      }

      filterFile.addEventListener("change", () => refreshAnchorOptions());
      filterSide.addEventListener("change", () => refreshAnchorOptions());
      filterText.addEventListener("input", () => refreshAnchorOptions());
      line.addEventListener("change", () => {
        line.setCustomValidity("");
        refreshPreview();
      });

      const identifier = labeledControl("input", "new-id",
        "Unique comment ID (1–100 ASCII letters, digits, dot, underscore or hyphen; start with a letter or digit)", form);
      identifier.type = "text";
      identifier.required = true;
      identifier.maxLength = 100;
      const body = labeledControl("textarea", "new-body", "New comment body", form);
      body.required = true;
      const add = node("button", "Add comment to download", form);
      add.type = "submit";
      draftPending = () => identifier.value.length > 0 || body.value.length > 0;
      for (const control of [identifier, body]) {
        control.addEventListener("input", () => { control.setCustomValidity(""); editsChanged(); });
      }
      jumpToAnchor = (anchorIndex, anchor) => {
        filterFile.value = anchor.path;
        filterSide.value = anchor.side;
        filterText.value = "";
        refreshAnchorOptions(anchorIndex,
          `Selected ${fixedText(anchor.path)} ${anchor.side} line ${anchor.line} in composer.`);
        identifier.focus();
      };
      form.addEventListener("submit", event => {
        event.preventDefault();
        const selectedIndex = line.value === "" ? -1 : Number(line.value);
        const anchor = Number.isInteger(selectedIndex) ? anchors[selectedIndex] : undefined;
        line.setCustomValidity(anchor ? "" : "Select a matching rendered line before adding a comment.");
        const unique = !data.document.comments.some(comment => comment.id === identifier.value);
        identifier.setCustomValidity(/^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$/.test(identifier.value) && unique ? "" :
          "Enter a unique safe comment ID starting with a letter or digit (up to 100 characters).");
        body.setCustomValidity(body.value.trim() && Array.from(body.value).length <= 20000 && !body.value.includes("\0") ? "" :
          "Enter nonempty text of at most 20000 characters, without NUL.");
        for (const control of [line, identifier, body]) {
          if (!control.reportValidity()) { control.focus(); return; }
        }
        const comment = {id: identifier.value, body: body.value, anchor: {...anchor},
          state: "anchored", resolution: "open", rebased_from: null, orphan_reason: null};
        data.document.comments.push(comment);
        renderComment(comment, data.document.comments.length - 1);
        identifier.value = "";
        body.value = "";
        editsChanged();
        applyCommentFilters();
        refreshPreview();
        identifier.focus();
      });

      refreshAnchorOptions();
    }
  }

  data.document.comments.forEach(renderComment);
  applyCommentFilters();
  refreshPreview();
  if (!data.document.comments.length && !anchorData) node("p", "No comments yet. Add one with skein.py comment, or generate a compose page from a packet.", container);

  function validatedJSON(action) {
    if (draftPending()) {
      status.textContent = `${action} blocked: add the drafted comment first, or clear its ID and body.`;
      return null;
    }
    for (const field of fields) {
      if (!field.reportValidity()) {
        resetCommentFilters();
        field.focus();
        status.textContent = `${action} blocked: correct the invalid comment body.`;
        return null;
      }
    }
    return JSON.stringify(data, null, 2) + "\n";
  }
  showJSON.disabled = false;
  showJSON.addEventListener("click", () => {
    const text = validatedJSON("Export");
    if (text === null) return;
    exportText.textContent = text;
    exportPanel.hidden = false;
    status.textContent = `${changedCount()} changed comments. Edits JSON ready to copy. ` +
      "Save the complete text as UTF-8 JSON, then check and apply it with the CLI. Showing it does not save it.";
    exportText.focus();
  });
  document.getElementById("select-json").addEventListener("click", () => {
    exportText.focus();
    const range = document.createRange();
    range.selectNodeContents(exportText);
    const selection = environment.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = "Edits JSON selected. Use your browser's Copy command, then save the complete text as UTF-8 JSON. Copying does not apply it to the packet.";
  });
  download.disabled = false;
  download.addEventListener("click", () => {
    const text = validatedJSON("Download");
    if (text === null) return;
    const blob = new environment.Blob([text], {type: "application/json"});
    const url = environment.URL.createObjectURL(blob);
    const link = node("a", "", document.body);
    link.href = url;
    link.download = "skein-comment-edits.json";
    link.click();
    link.remove();
    environment.setTimeout(() => environment.URL.revokeObjectURL(url), 1000);
    needsDownload = false;
    status.textContent = `${changedCount()} changed comments. Download requested. ` +
      "Check that the file was saved, then apply it with comment_editor.py apply. The packet is still unchanged.";
  });
  environment.addEventListener("beforeunload", event => {
    if (needsDownload) {
      event.preventDefault();
      event.returnValue = "";
    }
  });
  updateStatus();
}

if (typeof module !== "undefined" && module.exports) module.exports = {startEditor};
if (typeof document !== "undefined") startEditor(document, window);
