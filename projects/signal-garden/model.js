/* Original teaching model. Hamming(7,4), even parity at positions 1, 2, 4. */
"use strict";

const SignalGarden = (() => {
  function bits(value, size) {
    if (!Array.isArray(value) || value.length !== size ||
        !Array.from(value).every(bit => bit === 0 || bit === 1)) {
      throw new TypeError(`Expected ${size} binary digits`);
    }
  }

  function encode(data) {
    bits(data, 4);
    const [a, b, c, d] = data;
    return [a ^ b ^ d, a ^ c ^ d, a, b ^ c ^ d, b, c, d];
  }

  function decode(word) {
    bits(word, 7);
    let syndrome = 0;
    word.forEach((bit, index) => { if (bit) syndrome ^= index + 1; });
    const corrected = word.slice();
    if (syndrome) corrected[syndrome - 1] ^= 1;
    // This is an attempted correction, never a certificate of correct recovery.
    return { syndrome, corrected, data: [2, 4, 5, 6].map(i => corrected[i]) };
  }

  function mapping(layout) {
    if (layout !== "consecutive" && layout !== "interleaved") {
      throw new TypeError("Unknown layout");
    }
    return Array.from({ length: 28 }, (_, i) => layout === "consecutive"
      ? { row: Math.floor(i / 7), column: i % 7 }
      : { row: i % 4, column: Math.floor(i / 4) });
  }

  function run(picture, start, length, layout) {
    bits(picture, 16);
    if (!Number.isInteger(start) || !Number.isInteger(length) || start < 0 ||
        start >= 28 || length < 0 || start + length > 28) {
      throw new RangeError("Burst must fit inside 28 positions without wrapping");
    }
    const rows = Array.from({ length: 4 }, (_, row) => picture.slice(row * 4, row * 4 + 4));
    const encoded = rows.map(encode);
    const order = mapping(layout);
    const sent = order.map(({ row, column }) => encoded[row][column]);
    const received = sent.map((bit, i) => bit ^ Number(i >= start && i < start + length));
    const blocks = encoded.map(word => word.slice());
    const errors = [0, 0, 0, 0];
    order.forEach(({ row, column }, i) => {
      blocks[row][column] = received[i];
      errors[row] += Number(sent[i] !== received[i]);
    });
    const decoded = blocks.map(decode);
    const recovered = decoded.flatMap(result => result.data);
    const changed = recovered.reduce((count, bit, i) => count + Number(bit !== picture[i]), 0);
    return { layout, start, length, rows, encoded, order, sent, received, blocks,
      errors, decoded, recovered, changed, matches: changed === 0 };
  }

  function outcome(consecutive, interleaved) {
    if (consecutive.matches && interleaved.matches) return "both";
    if (consecutive.matches) return "consecutive";
    if (interleaved.matches) return "interleaved";
    return "neither";
  }

  function trace(result) {
    const burst = result.length ? `${result.start + 1}..${result.start + result.length}` : "none";
    const lines = [`${result.layout.toUpperCase()}: 16 payload bits / 28 transmitted bits`,
      `Flipped channel positions (1-based): ${burst}`,
      `Sent:     ${result.sent.join("")}`, `Received: ${result.received.join("")}`];
    result.rows.forEach((row, i) => {
      const decoded = result.decoded[i];
      lines.push(`Row ${i + 1}: ${row.join("")} -> ${result.encoded[i].join("")} -> ${result.blocks[i].join("")}`,
        `  ${result.errors[i]} injected error(s); syndrome ${decoded.syndrome}; attempted flip ${decoded.syndrome || "none"}; recovered ${decoded.data.join("")}`);
    });
    lines.push(`Simulator comparison to original: ${result.changed} changed pixel(s).`,
      "The decoder sees only received bits. Error counts and original-match verdict use simulator knowledge.",
      "One error per block is correctable. Two or more can silently decode to the wrong data.");
    return lines.join("\n");
  }

  return { encode, decode, mapping, run, outcome, trace };
})();
if (typeof module !== "undefined" && module.exports) module.exports = SignalGarden;
