"""Two-label call control over the existing scoped data kernel.

Procedures are kernel programs with calls inserted at instruction boundaries.
There are no branches, loops, recursion or source-level uncall yet.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import subprocess
import sys

from scope_machine import Local, Program, State, Transfer, Update, expression as e


@dataclass(frozen=True)
class Procedure:
    kernel: Program
    calls: tuple[tuple[int, str], ...] = ()


@dataclass(frozen=True)
class Node:
    procedure: str
    kind: str
    boundary: int
    target: str = ""


@dataclass(frozen=True)
class ControlState:
    previous: str
    following: str
    integers: tuple[tuple[str, int], ...]
    stacks: tuple[tuple[str, tuple[int, ...]], ...]
    calls: tuple[str, ...] = ()

    def dumps(self) -> str:
        return json.dumps({"control": [self.previous, self.following],
                           "integers": dict(self.integers), "stacks": dict(self.stacks),
                           "calls": self.calls}, sort_keys=True)


class Machine:
    def __init__(self, procedures: dict[str, Procedure], main: str = "main"):
        if main not in procedures or any(not name.isidentifier() for name in procedures):
            raise ValueError("procedures need identifier names and a main procedure")
        self.procedures = dict(procedures)
        self.main = main
        self.globals = procedures[main].kernel.domains[0]
        self.stack_names = procedures[main].kernel.stack_names
        self.nodes: dict[str, Node] = {}
        self.successor: dict[str, str] = {}
        self.predecessor: dict[str, str] = {}
        self.starts: dict[str, str] = {}
        self.stops: dict[str, str] = {}
        local_names: set[str] = set()
        graph: dict[str, set[str]] = {}
        for name, procedure in procedures.items():
            kernel = procedure.kernel
            if kernel.domains[0] != self.globals or kernel.stack_names != self.stack_names:
                raise ValueError("all procedures must declare the same globals and stacks")
            locals_here = set().union(*kernel.domains) - self.globals
            if local_names & locals_here:
                raise ValueError("local names must be distinct across procedures")
            local_names |= locals_here
            call_map = dict(procedure.calls)
            if len(call_map) != len(procedure.calls):
                raise ValueError("at most one call may occupy an instruction boundary")
            if any(type(i) is not int or not 0 <= i <= len(kernel.instructions)
                   or target not in procedures for i, target in call_map.items()):
                raise ValueError("invalid call boundary or target")
            graph[name] = set(call_map.values())
            start, stop = f"{name}:start", f"{name}:stop"
            self.starts[name], self.stops[name] = start, stop
            self.nodes[start] = Node(name, "start", 0)
            labels = [start]
            for i in range(len(kernel.instructions) + 1):
                if i in call_map:
                    label = f"{name}:call:{i}"
                    self.nodes[label] = Node(name, "call", i, call_map[i])
                    labels.append(label)
                if i < len(kernel.instructions):
                    label = f"{name}:data:{i}"
                    self.nodes[label] = Node(name, "data", i)
                    labels.append(label)
            self.nodes[stop] = Node(name, "stop", len(kernel.instructions))
            labels.append(stop)
            for previous, following in zip(labels, labels[1:]):
                self.successor[previous] = following
                self.predecessor[following] = previous

        active, done = set(), set()

        def visit(name: str) -> None:
            if name in active:
                raise ValueError("recursive calls are outside this fragment")
            if name not in done:
                active.add(name)
                for target in graph[name]:
                    visit(target)
                active.remove(name)
                done.add(name)

        for name in procedures:
            visit(name)

    def initial(self, integers: dict[str, int], stacks: dict[str, tuple[int, ...]]) -> ControlState:
        data = State.make(0, integers, stacks)
        start = self.starts[self.main]
        state = ControlState(start, self.successor[start], data.integers, data.stacks)
        self.validate(state)
        return state

    def validate(self, state: ControlState) -> None:
        if (state.previous not in self.nodes or state.following not in self.nodes
                or self.successor.get(state.previous) != state.following):
            raise ValueError("control labels must form an intraprocedural edge")
        current = self.nodes[state.following]
        expected = set(self.globals)
        owner = self.main
        for label in state.calls:
            call = self.nodes.get(label)
            if call is None or call.kind != "call" or call.procedure != owner:
                raise ValueError("call stack does not describe a nested call chain")
            expected |= self.procedures[owner].kernel.domains[call.boundary]
            owner = call.target
        if current.procedure != owner:
            raise ValueError("active procedure disagrees with the call stack")
        kernel = self.procedures[owner].kernel
        expected |= kernel.domains[current.boundary]
        integers, stacks = dict(state.integers), dict(state.stacks)
        if (len(integers) != len(state.integers) or set(integers) != expected
                or len(stacks) != len(state.stacks) or set(stacks) != self.stack_names):
            raise ValueError("live bindings do not match active and suspended scopes")
        if any(type(value) is not int for value in integers.values()):
            raise ValueError("integer bindings must contain integers")
        if any(not isinstance(values, tuple) or any(type(v) is not int for v in values)
               for values in stacks.values()):
            raise ValueError("data stacks must be integer tuples")
        data = State.make(0, integers, stacks)
        if (data.integers, data.stacks) != (state.integers, state.stacks):
            raise ValueError("state bindings must have canonical name order")

    def loads(self, text: str) -> ControlState:
        def unique(pairs: list[tuple[str, object]]) -> dict:
            result: dict = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate checkpoint field")
                result[key] = value
            return result

        data = json.loads(text, object_pairs_hook=unique)
        if not isinstance(data, dict) or set(data) != {"control", "integers", "stacks", "calls"}:
            raise ValueError("checkpoint has unexpected fields")
        control, calls = data["control"], data["calls"]
        if (not isinstance(control, list) or len(control) != 2
                or any(not isinstance(label, str) for label in control)
                or not isinstance(calls, list) or any(not isinstance(c, str) for c in calls)
                or not isinstance(data["integers"], dict) or not isinstance(data["stacks"], dict)
                or any(not isinstance(v, list) for v in data["stacks"].values())):
            raise ValueError("invalid checkpoint structure")
        values = State.make(0, data["integers"], {k: tuple(v) for k, v in data["stacks"].items()})
        state = ControlState(*control, values.integers, values.stacks, tuple(calls))
        self.validate(state)
        return state

    def step(self, state: ControlState, *, backward: bool = False) -> ControlState:
        self.validate(state)
        label = state.previous if backward else state.following
        node = self.nodes[label]
        if node.kind == "call":
            if backward:
                stop = self.stops[node.target]
                result = replace(state, previous=self.predecessor[stop], following=stop,
                                 calls=state.calls + (label,))
            else:
                start = self.starts[node.target]
                result = replace(state, previous=start, following=self.successor[start],
                                 calls=state.calls + (label,))
        elif node.kind == ("start" if backward else "stop"):
            if not state.calls:
                raise ValueError("no transition beyond the main boundary")
            call = state.calls[-1]
            previous, following = ((self.predecessor[call], call) if backward
                                   else (call, self.successor[call]))
            result = replace(state, previous=previous, following=following, calls=state.calls[:-1])
        elif node.kind == "data":
            kernel = self.procedures[node.procedure].kernel
            boundary = node.boundary + int(backward)
            live = kernel.domains[boundary]
            integers = dict(state.integers)
            # Suspended caller locals are retained, but invisible to the callee.
            current = State.make(boundary, {n: integers[n] for n in live}, dict(state.stacks))
            updated = kernel.step(current, backward=backward)
            retained = {n: v for n, v in integers.items() if n not in live}
            retained.update(updated.integers)
            packed = State.make(0, retained, dict(updated.stacks))
            previous, following = ((self.predecessor[label], label) if backward
                                   else (label, self.successor[label]))
            result = ControlState(previous, following, packed.integers, packed.stacks, state.calls)
        else:
            raise ValueError("invalid direction at this boundary")
        self.validate(result)
        return result


def example(value: int = 4) -> tuple[Machine, ControlState]:
    main = Program.compile((Local("x", e("g"), e("g"), (Update("x", 2),)),), {"g"}, {"s"})
    worker = Program.compile((Local("y", e("g + 1"), e("g + 1"), (Update("y", 2),)),), {"g"}, {"s"})
    leaf = Program.compile((Local("z", e("3 * g"), 0, (Transfer("z", "s"),)),
                            Update("g", 2)), {"g"}, {"s"})
    machine = Machine({"main": Procedure(main, ((1, "worker"),)),
                       "worker": Procedure(worker, ((1, "leaf"),)), "leaf": Procedure(leaf)})
    return machine, machine.initial({"g": value}, {"s": (99,)})


def main() -> int:
    machine, initial = example()
    if sys.argv[1:] == ["--resume"]:
        state = machine.loads(sys.stdin.read())
        count = 0
        while state != initial:
            state = machine.step(state, backward=True)
            count += 1
        print(f"fresh process: reversed {count} transitions; recovered {state.dumps()}")
        return 0
    if sys.argv[1:]:
        raise ValueError("usage: control_machine.py [--resume]")
    state = initial
    while not (state.previous == "leaf:data:1"):
        state = machine.step(state)
    print(f"checkpoint in nested call: {state.dumps()}", flush=True)
    subprocess.run([sys.executable, str(Path(__file__).resolve()), "--resume"],
                   input=state.dumps(), text=True, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
