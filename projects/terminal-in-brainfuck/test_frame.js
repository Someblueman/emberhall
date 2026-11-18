"use strict";
const {test} = require("node:test");
const assert = require("node:assert/strict");
const {decodeFrame, FRAME_SIZE} = require("./frame.js");

function blank() {
  return [255, ...Array(960).fill(32), ...Array(960).fill(7), 0, 0, 254];
}

test("colour frame preserves zero and maximum attributes and both corner cursors", () => {
  const bytes = blank();
  assert.equal(bytes.length, FRAME_SIZE);
  bytes[961] = 0;
  bytes[1920] = 127;
  bytes[1921] = 23;
  bytes[1922] = 39;
  const f = decodeFrame(bytes);
  assert.deepEqual([f.attributes[0], f.attributes[959], f.row, f.col], [0, 127, 23, 39]);
  bytes[961] = 7;
  assert.equal(f.attributes[0], 0); // retained frames do not alias pending input
});

test("host refuses wrong framing, lengths and each malformed payload range", () => {
  for (const [offset, value] of [[0, 0], [1923, 255], [1, 31], [960, 127],
    [961, -1], [1920, 128], [961, NaN], [1921, 24], [1922, 40], [1922, 0.5]]) {
    const bytes = blank();
    bytes[offset] = value;
    assert.throws(() => decodeFrame(bytes), /Malformed/);
  }
  assert.throws(() => decodeFrame(blank().slice(1)), /Malformed/);
  assert.throws(() => decodeFrame([...blank(), 0]), /Malformed/);
  assert.throws(() => decodeFrame([255, ...Array(960).fill(32), 0, 0, 254]), /Malformed/);
});
