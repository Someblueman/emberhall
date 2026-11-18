"""An ordinary Brainfuck interpreter, used only by the tests.

Semantics are the plain eight commands on 8-bit wrapping cells with
end-of-input reading as 0.  Runs of the same command are compiled to a
single counted operation; that changes speed, never meaning.
"""

from layout import TAPE_SIZE
_OPS = {">": 0, "<": 1, "+": 2, "-": 3, ".": 4, ",": 5, "[": 6, "]": 7}


def compile_bf(source):
    ops, args = [], []
    for ch in source:
        code = _OPS.get(ch)
        if code is None:
            continue
        if code < 4 and ops and ops[-1] == code:
            args[-1] += 1
        else:
            ops.append(code)
            args.append(1)
    stack = []
    for i, code in enumerate(ops):
        if code == 6:
            stack.append(i)
        elif code == 7:
            j = stack.pop()
            args[i] = j
            args[j] = i
    if stack:
        raise ValueError("unbalanced brackets in Brainfuck source")
    return ops, args


def run_bf(source, data=b"", max_ops=500_000_000):
    ops, args = compile_bf(source)
    tape = bytearray(TAPE_SIZE)
    out = bytearray()
    ptr = ip = inp = steps = 0
    n = len(ops)
    while ip < n:
        steps += 1
        if steps > max_ops:
            raise TimeoutError(f"Brainfuck program exceeded {max_ops} ops")
        code = ops[ip]
        if code == 0:
            ptr += args[ip]
            if ptr >= TAPE_SIZE:
                raise ValueError(f"tape pointer moved beyond cell {TAPE_SIZE - 1}")
        elif code == 1:
            ptr -= args[ip]
            if ptr < 0:
                raise ValueError("tape pointer moved before cell 0")
        elif code == 2:
            tape[ptr] = (tape[ptr] + args[ip]) & 0xFF
        elif code == 3:
            tape[ptr] = (tape[ptr] - args[ip]) & 0xFF
        elif code == 4:
            out.append(tape[ptr])
        elif code == 5:
            tape[ptr] = data[inp] if inp < len(data) else 0
            inp += 1
        elif code == 6:
            if tape[ptr] == 0:
                ip = args[ip]
        else:
            if tape[ptr] != 0:
                ip = args[ip]
        ip += 1
    return bytes(out)
