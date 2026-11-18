"use strict";
// The one wire format from COLOUR_CONTRACT.md. No input or terminal rules here.
const FRAME_SIZE = 1924;
function decodeFrame(bytes) {
  if (bytes.length !== FRAME_SIZE || bytes[0] !== 255 || bytes[1923] !== 254 ||
      bytes.slice(1, 961).some(n => !Number.isInteger(n) || n < 32 || n > 126) ||
      bytes.slice(961, 1921).some(n => !Number.isInteger(n) || n < 0 || n > 127) ||
      !Number.isInteger(bytes[1921]) || bytes[1921] < 0 || bytes[1921] >= 24 ||
      !Number.isInteger(bytes[1922]) || bytes[1922] < 0 || bytes[1922] >= 40) {
    throw new Error("Malformed screen frame");
  }
  return {cells: bytes.slice(1, 961), attributes: bytes.slice(961, 1921),
    row: bytes[1921], col: bytes[1922]};
}
if (typeof module !== "undefined") module.exports = {FRAME_SIZE, decodeFrame};
