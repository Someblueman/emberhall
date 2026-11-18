"use strict";
// Explicit ASCII/byte notation; Unicode must never alias to a control byte.
function encodeStream(text) {
  const bytes = [];
  for (let i = 0; i < text.length; i++) {
    let n = text.charCodeAt(i);
    if (text[i] === "\\") {
      const c = text[++i];
      const escapes = {r: 13, n: 10, t: 9, "\\": 92};
      if (Object.hasOwn(escapes, c)) n = escapes[c];
      else if (c === "x" && /^[0-9a-f]{2}$/i.test(text.slice(i + 1, i + 3))) {
        n = parseInt(text.slice(i + 1, i + 3), 16);
        i += 2;
      } else throw new Error("Use \\r, \\n, \\t, \\\\ or \\xHH for escapes.");
    } else if (n > 127) throw new Error("Use ASCII text or explicit \\xHH bytes; Unicode is not silently converted.");
    bytes.push(n);
  }
  return bytes;
}
if (typeof module !== "undefined") module.exports = {encodeStream};
