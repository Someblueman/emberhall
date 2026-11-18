"use strict";
// General eight-command machine. No terminal, cursor, row or frame knowledge.
class BrainfuckMachine {
  constructor(source, output = () => {}, tapeSize = 6000) {
    this.ops = [];
    const stack = [];
    let pc = 0;
    for (const c of source) {
      if (!"><+-.,[]".includes(c)) continue;
      const last = this.ops.at(-1);
      if ("><+-".includes(c) && last?.c === c) last.n++;
      else this.ops.push({c, n: 1, pc});
      pc++;
    }
    this.ops.forEach((op, i) => {
      if (op.c === "[") stack.push(i);
      if (op.c === "]") {
        if (!stack.length) throw new Error("Unmatched closing bracket");
        const j = stack.pop();
        op.jump = j;
        this.ops[j].jump = i;
      }
    });
    if (stack.length) throw new Error("Unmatched opening bracket");
    this.tape = new Uint8Array(tapeSize);
    this.ptr = 0;
    this.ip = 0;
    this.offset = 0;
    this.instructions = 0;
    this.consumed = 0;
    this.queue = [];
    this.inputPosition = 0;
    this.ended = false;
    this.waiting = false;
    this.output = output;
  }

  get halted() { return this.ip >= this.ops.length; }
  get pc() { return this.halted ? null : this.ops[this.ip].pc + this.offset; }
  get instruction() { return this.halted ? "halt" : this.ops[this.ip].c; }
  get queued() { return this.queue.length - this.inputPosition; }

  feed(bytes) {
    if (this.ended || this.halted) throw new Error("Reset before adding more input");
    if (!bytes.every(b => Number.isInteger(b) && b >= 0 && b <= 255)) {
      throw new Error("Input must contain bytes from 0 to 255");
    }
    this.queue = this.queue.slice(this.inputPosition).concat(Array.from(bytes));
    this.inputPosition = 0;
    this.waiting = false;
  }

  end() { this.ended = true; this.waiting = false; }

  // One literal instruction for the debugger, or one equivalent counted run.
  // A blocked comma executes nothing and never means end of input.
  step(literal = true) {
    if (this.halted) return false;
    const op = this.ops[this.ip];
    const n = literal ? 1 : op.n - this.offset;
    switch (op.c) {
      case ">": case "<": {
        const next = this.ptr + (op.c === ">" ? n : -n);
        if (next < 0 || next >= this.tape.length) throw new Error("Tape bounds exceeded");
        this.ptr = next;
        break;
      }
      case "+": this.tape[this.ptr] += n; break;
      case "-": this.tape[this.ptr] -= n; break;
      case ".": this.output(this.tape[this.ptr]); break;
      case ",":
        if (this.queued) {
          this.tape[this.ptr] = this.queue[this.inputPosition++];
          this.consumed++;
        } else if (this.ended) this.tape[this.ptr] = 0;
        else { this.waiting = true; return false; }
        this.waiting = false;
        break;
      case "[": if (this.tape[this.ptr] === 0) this.ip = op.jump; break;
      case "]": if (this.tape[this.ptr] !== 0) this.ip = op.jump; break;
    }
    this.instructions += n;
    this.offset += n;
    if (this.offset === op.n) { this.ip++; this.offset = 0; }
    return true;
  }

  run(budget = 20000, stop = () => false) {
    while (budget-- > 0 && !stop()) if (!this.step(false)) break;
  }
}

if (typeof module !== "undefined") module.exports = {BrainfuckMachine};
