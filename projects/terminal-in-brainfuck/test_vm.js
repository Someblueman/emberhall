"use strict";
const {test} = require("node:test");
const assert = require("node:assert/strict");
const {BrainfuckMachine} = require("./vm.js");
const {encodeStream} = require("./input.js");

test("literal steps, including inside counted runs, execute exactly one command", () => {
  const vm = new BrainfuckMachine("+++>>--<");
  for (const [ptr, value, pc] of [[0,1,1],[0,2,2],[0,3,3],[1,0,4],[2,0,5],[2,255,6],[2,254,7],[1,0,null]]) {
    assert.equal(vm.step(), true);
    assert.deepEqual([vm.ptr, vm.tape[vm.ptr], vm.pc], [ptr,value,pc]);
  }
  assert.equal(vm.instructions, 8);
  assert.equal(vm.step(), false);
});

test("counted execution resumes from a partially stepped instruction run", () => {
  const vm = new BrainfuckMachine("++++[>++<-]>.", n => output.push(n));
  const output = [];
  vm.step();
  vm.run(100);
  assert.deepEqual(output, [8]);
  assert.equal(vm.halted, true);
});

test("input wait is not EOF, and feeding and explicit EOF resume the same comma", () => {
  const output = [];
  const vm = new BrainfuckMachine(",[.,]", b => output.push(b));
  vm.run();
  assert.equal(vm.waiting, true);
  assert.equal(vm.pc, 0);
  assert.equal(vm.instructions, 0);
  for (const b of [65, 255, 66]) { vm.feed([b]); vm.run(); assert.equal(vm.waiting, true); }
  vm.end(); vm.run();
  assert.deepEqual(output, [65, 255, 66]);
  assert.equal(vm.halted, true);
  assert.throws(() => vm.feed([67]), /Reset/);
});

test("output may stop execution at an exact byte, without running ahead", () => {
  const output = [];
  const vm = new BrainfuckMachine("+.+.+.", b => output.push(b));
  vm.run(100, () => output.length === 1);
  assert.deepEqual(output, [1]);
  assert.equal(vm.tape[0], 1);
  assert.equal(vm.pc, 2);
  vm.step();
  assert.equal(vm.tape[0], 2);
});

test("one terminal frame consumes only A from a queued AB", () => {
  const code = require("node:fs").readFileSync(require("node:path").join(__dirname, "terminal.bf"), "utf8");
  let output = [], frames = 0;
  const vm = new BrainfuckMachine(code, b => {
    output.push(b);
    if (output.length === 1924) { frames++; output = []; }
  }, 6000);
  while (frames < 1) vm.run(20000, () => frames === 1);
  vm.feed([65, 66]);
  while (frames < 2) vm.run(20000, () => frames === 2);
  assert.equal(vm.consumed, 1);
  assert.equal(vm.queued, 1);
  assert.equal(vm.tape[2], 1);
  assert.equal(vm.tape[72], 65);
  assert.equal(vm.tape[75], 8);
  assert.equal(vm.tape[78], 32);
  assert.equal(vm.ptr, 6);
});

test("bounds, byte validation and bracket errors fail explicitly", () => {
  for (const code of ["[", "]", "[]]"]) assert.throws(() => new BrainfuckMachine(code), /bracket/);
  for (const code of ["<", ">>>"]) assert.throws(() => new BrainfuckMachine(code, () => {}, 3).run(), /bounds/);
  const vm = new BrainfuckMachine(",");
  for (const input of [[-1], [256], [0.5], [NaN]]) assert.throws(() => vm.feed(input), /bytes/);
});

test("ASCII and escape notation encode exact bytes and reject accidental aliases", () => {
  assert.deepEqual(encodeStream("A\\r\\n\\t\\\\\\x00\\xFF\n"), [65,13,10,9,92,0,255,10]);
  for (const s of ["Ā", "🙂", "\\xQ0", "\\", "\\q"]) assert.throws(() => encodeStream(s));
});
