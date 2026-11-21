"""Run the scope-kernel tests and a real checkpoint/restart demonstration."""
from pathlib import Path
import subprocess
import sys
import unittest

from scope_machine import Local, Program, State, Transfer, Update, expression as e


def example() -> tuple[Program, State]:
    program = Program.compile((Local("x", e("g + 1"), e("g + 1"), (
        Local("y", e("2 * x"), 0, (Transfer("y", "s"),)),
        Update("x", 3), Update("g", 3),
    )),), {"g"}, {"s"})
    return program, State.make(0, {"g": 4}, {"s": (99,)})


def main() -> int:
    program, initial = example()
    if sys.argv[1:] == ["--resume"]:
        state = program.loads(sys.stdin.read())
        count = 0
        while state.pc:
            state = program.step(state, backward=True)
            count += 1
        if state != initial:
            raise ValueError("reverse execution did not recover the initial state")
        print(f"fresh process: reversed {count} steps; recovered {state.dumps()}")
        return 0
    if sys.argv[1:]:
        raise ValueError("usage: check.py [--resume]")
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), "test_scope_machine.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        return 1
    state = initial
    # Stop inside both scopes, just after moving y onto the data stack.
    for _ in range(3):
        state = program.step(state)
    snapshot = state.dumps()
    print(f"checkpoint inside two scopes: {snapshot}", flush=True)
    subprocess.run([sys.executable, str(Path(__file__).resolve()), "--resume"],
                   input=snapshot, text=True, check=True)
    print("Scope kernel only: full Janus control flow and novelty review remain open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
