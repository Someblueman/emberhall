"use strict";
// Generic byte-in/byte-out runner. Screen semantics belong to terminal.bf.
const fs = require("node:fs");
const path = require("node:path");
const {BrainfuckMachine} = require("./vm.js");

function writeAll(bytes) {
  for (let offset = 0; offset < bytes.length;) {
    offset += fs.writeSync(1, bytes, offset, bytes.length - offset);
  }
}

try {
  const output = Buffer.alloc(16384);
  let used = 0;
  function flush() {
    if (used) writeAll(output.subarray(0, used));
    used = 0;
  }
  const vm = new BrainfuckMachine(
    fs.readFileSync(path.join(__dirname, "terminal.bf"), "utf8"), byte => {
      output[used++] = byte;
      if (used === output.length) flush();
    });
  const input = Buffer.alloc(4096);
  while (true) {
    while (!vm.waiting && !vm.halted) vm.run(100000);
    flush();
    if (vm.halted) {
      if (!vm.ended) throw new Error("NUL ended the tape program before shell EOF");
      break;
    }
    const count = fs.readSync(0, input, 0, input.length, null);
    if (count) vm.feed(input.subarray(0, count));
    else vm.end();
  }
} catch (error) {
  process.stderr.write(`Tape machine: ${error.message}\n`);
  process.exitCode = 1;
}
