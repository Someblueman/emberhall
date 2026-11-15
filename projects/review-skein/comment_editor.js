"use strict";

// The Python generator supplies validated v2 data. Downloads still pass Python's
// strict validator, baseline-byte check and immutable-field check before writing.
function startEditor(document, environment) {
  const data = JSON.parse(document.getElementById("editor-data").textContent);
  const status = document.getElementById("editor-status");
  const download = document.getElementById("download");
  const container = document.getElementById("comments");
  const index = document.getElementById("comment-index");
  const originals = data.document.comments.map(c => ({body: c.body, resolution: c.resolution}));
  const fields = [];
  let needsDownload = false;
  let draftPending = () => false;

  function node(tag, text, parent) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    parent.appendChild(element);
    return element;
  }

  function fixedText(text) {
    return text.replace(/[\x00-\x08\x0b-\x1f\x7f-\x9f\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]/g,
      character => "\\u" + character.charCodeAt(0).toString(16).padStart(4, "0"));
  }

  function anchorText(anchor) {
    return fixedText(`${anchor.path} | ${anchor.side} line ${anchor.line}\nCommit: ${anchor.commit}\n${anchor.text}`);
  }

  function changedCount() {
    return data.document.comments.filter((c, i) =>
      !originals[i] || c.body !== originals[i].body || c.resolution !== originals[i].resolution).length;
  }

  function updateStatus() {
    status.textContent = `${data.document.comments.length} comments. ${changedCount()} changed. ` +
      (needsDownload ? "Changes not downloaded. Download edits, then apply with the CLI." :
        "No new changes to download. The packet is unchanged until you apply edits with the CLI.");
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
    const bodyLabel = node("label", `Body for ${comment.id}`, article);
    bodyLabel.htmlFor = `${identifier}-body`;
    const body = node("textarea", undefined, article);
    body.id = bodyLabel.htmlFor;
    body.required = true;
    body.setAttribute("aria-describedby", state.id);
    body.value = comment.body;
    const resolutionLabel = node("label", `Resolution for ${comment.id}`, article);
    resolutionLabel.htmlFor = `${identifier}-resolution`;
    const resolution = node("select", undefined, article);
    resolution.id = resolutionLabel.htmlFor;
    for (const value of ["open", "resolved"]) {
      const option = node("option", value, resolution);
      option.value = value;
    }
    resolution.value = comment.resolution;
    body.addEventListener("input", () => {
      const value = body.value;
      const valid = value.trim().length > 0 && Array.from(value).length <= 20000 && !value.includes("\0");
      body.setCustomValidity(valid ? "" : "Enter nonempty text of at most 20000 characters, without NUL.");
      comment.body = value;
      needsDownload = true;
      updateStatus();
    });
    resolution.addEventListener("change", () => {
      comment.resolution = resolution.value;
      needsDownload = true;
      updateStatus();
    });
    fields.push(body);
  }
  data.document.comments.forEach(renderComment);
  const anchorData = document.getElementById("anchor-data");
  if (anchorData) {
    const anchors = JSON.parse(anchorData.textContent);
    const composer = document.getElementById("composer");
    node("h2", "Add an anchored comment", composer);
    if (!anchors.length) {
      node("p", "This packet has no rendered lines to comment on.", composer);
    } else {
      const form = node("form", undefined, composer);
      function field(tag, id, label) {
        const caption = node("label", label, form);
        caption.htmlFor = id;
        const control = node(tag, undefined, form);
        control.id = id;
        return control;
      }
      const line = field("select", "new-anchor", "Rendered line (path, side and line number)");
      anchors.forEach((anchor, i) => {
        const option = node("option", fixedText(`${anchor.path} | ${anchor.side} ${anchor.line}: ${anchor.text}`).slice(0, 180), line);
        option.value = String(i);
      });
      line.value = "0";
      const preview = node("pre", anchorText(anchors[0]), form);
      preview.id = "new-anchor-preview";
      line.setAttribute("aria-describedby", preview.id);
      line.addEventListener("change", () => { preview.textContent = anchorText(anchors[Number(line.value)]); });
      const identifier = field("input", "new-id", "Unique comment ID (1–100 ASCII letters, digits, dot, underscore or hyphen; start with a letter or digit)");
      identifier.type = "text";
      identifier.required = true;
      identifier.maxLength = 100;
      const body = field("textarea", "new-body", "New comment body");
      body.required = true;
      const add = node("button", "Add comment to download", form);
      add.type = "submit";
      draftPending = () => identifier.value.length > 0 || body.value.length > 0;
      for (const control of [identifier, body]) {
        control.addEventListener("input", () => { control.setCustomValidity(""); needsDownload = true; });
      }
      form.addEventListener("submit", event => {
        event.preventDefault();
        const unique = !data.document.comments.some(comment => comment.id === identifier.value);
        identifier.setCustomValidity(/^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$/.test(identifier.value) && unique ? "" :
          "Enter a unique safe comment ID starting with a letter or digit (up to 100 characters).");
        body.setCustomValidity(body.value.trim() && Array.from(body.value).length <= 20000 && !body.value.includes("\0") ? "" :
          "Enter nonempty text of at most 20000 characters, without NUL.");
        for (const control of [identifier, body]) {
          if (!control.reportValidity()) { control.focus(); return; }
        }
        const anchor = anchors[Number(line.value)];
        if (!anchor) return;
        const comment = {id: identifier.value, body: body.value, anchor: {...anchor},
          state: "anchored", resolution: "open", rebased_from: null, orphan_reason: null};
        data.document.comments.push(comment);
        renderComment(comment, data.document.comments.length - 1);
        identifier.value = "";
        body.value = "";
        needsDownload = true;
        updateStatus();
        identifier.focus();
      });
    }
  }
  if (!data.document.comments.length && !anchorData) node("p", "No comments yet. Add one with skein.py comment, or generate a compose page from a packet.", container);

  download.disabled = false;
  download.addEventListener("click", () => {
    if (draftPending()) {
      status.textContent = "Download blocked: add the drafted comment first, or clear its ID and body.";
      return;
    }
    for (const field of fields) {
      if (!field.reportValidity()) {
        field.focus();
        status.textContent = "Download blocked: correct the invalid comment body.";
        return;
      }
    }
    const blob = new environment.Blob([JSON.stringify(data, null, 2) + "\n"], {type: "application/json"});
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
