"""Executable scope lemma, not yet the complete Janus machine.

The immutable state contains only the current instruction boundary, live
integers and data stacks. Program text and lexical scopes are static.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
import json
from typing import TypeAlias


Expr: TypeAlias = int | str | tuple[str, "Expr", "Expr"]


def expression(source: str) -> Expr:
    """Read integer/name expressions with +, - and *; never execute Python."""
    def convert(node: ast.AST) -> Expr:
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            return ("-" if isinstance(node.op, ast.USub) else "+", 0, convert(node.operand))
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
            op = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*"}[type(node.op)]
            return op, convert(node.left), convert(node.right)
        raise ValueError("expressions allow only integers, names, +, - and *")

    return convert(ast.parse(source, mode="eval").body)


def names(expr: Expr) -> set[str]:
    if type(expr) is int:
        return set()
    if isinstance(expr, str):
        return {expr}
    if (isinstance(expr, tuple) and len(expr) == 3 and expr[0] in {"+", "-", "*"}):
        return names(expr[1]) | names(expr[2])
    raise ValueError("invalid expression")


def evaluate(expr: Expr, values: dict[str, int]) -> int:
    if type(expr) is int:
        return expr
    if isinstance(expr, str):
        return values[expr]
    op, left, right = expr
    a, b = evaluate(left, values), evaluate(right, values)
    return a + b if op == "+" else a - b if op == "-" else a * b


@dataclass(frozen=True)
class Update:
    name: str
    value: Expr
    subtract: bool = False


@dataclass(frozen=True)
class Transfer:
    name: str
    stack: str
    pop: bool = False


@dataclass(frozen=True)
class Local:
    name: str
    initial: Expr
    final: Expr
    body: tuple[Statement, ...]


@dataclass(frozen=True)
class Boundary:
    name: str
    value: Expr
    enter: bool


Statement: TypeAlias = Update | Transfer | Local
Instruction: TypeAlias = Update | Transfer | Boundary


@dataclass(frozen=True)
class State:
    pc: int
    integers: tuple[tuple[str, int], ...]
    stacks: tuple[tuple[str, tuple[int, ...]], ...]

    @classmethod
    def make(cls, pc: int, integers: dict[str, int], stacks: dict[str, tuple[int, ...]]) -> State:
        return cls(pc, tuple(sorted(integers.items())), tuple(sorted(stacks.items())))

    def dumps(self) -> str:
        return json.dumps({"pc": self.pc, "integers": dict(self.integers),
                           "stacks": dict(self.stacks)}, sort_keys=True)


@dataclass(frozen=True)
class Program:
    instructions: tuple[Instruction, ...]
    domains: tuple[frozenset[str], ...]
    stack_names: frozenset[str]

    @classmethod
    def compile(cls, body: tuple[Statement, ...], integers: set[str], stacks: set[str]) -> Program:
        """Compile a straight-line scope tree; a boundary indexes static text."""
        if integers & stacks or any(not n.isidentifier() for n in integers | stacks):
            raise ValueError("integer and stack names must be distinct identifiers")
        code: list[Instruction] = []
        domains = [frozenset(integers)]

        def emit(instruction: Instruction, live: set[str]) -> None:
            code.append(instruction)
            domains.append(frozenset(live))

        def check_expr(expr: Expr, live: set[str]) -> None:
            if not names(expr) <= live:
                raise ValueError("expression mentions a non-live integer")

        def visit(statements: tuple[Statement, ...], live: set[str]) -> None:
            for stmt in statements:
                if isinstance(stmt, Local):
                    if (not stmt.name.isidentifier() or stmt.name in live | stacks):
                        raise ValueError("local name must be fresh; shadowing is outside this fragment")
                    check_expr(stmt.initial, live)
                    check_expr(stmt.final, live)
                    inner = live | {stmt.name}
                    emit(Boundary(stmt.name, stmt.initial, True), inner)
                    visit(stmt.body, inner)
                    emit(Boundary(stmt.name, stmt.final, False), live)
                elif isinstance(stmt, Update):
                    if stmt.name not in live or stmt.name in names(stmt.value):
                        raise ValueError("update target must be live and absent from its expression")
                    check_expr(stmt.value, live)
                    emit(stmt, live)
                elif isinstance(stmt, Transfer):
                    if stmt.name not in live or stmt.stack not in stacks:
                        raise ValueError("transfer requires a live integer and a declared stack")
                    emit(stmt, live)
                else:
                    raise ValueError("unknown statement")

        visit(body, set(integers))
        return cls(tuple(code), tuple(domains), frozenset(stacks))

    def validate(self, state: State) -> None:
        if type(state.pc) is not int or not 0 <= state.pc <= len(self.instructions):
            raise ValueError("instruction boundary is outside the program")
        ints, stacks = dict(state.integers), dict(state.stacks)
        if len(ints) != len(state.integers) or len(stacks) != len(state.stacks):
            raise ValueError("duplicate state binding")
        if set(ints) != self.domains[state.pc] or set(stacks) != self.stack_names:
            raise ValueError("state bindings do not match this lexical boundary")
        if any(type(v) is not int for v in ints.values()):
            raise ValueError("integer bindings must contain integers")
        if any(not isinstance(v, tuple) or any(type(x) is not int for x in v)
               for v in stacks.values()):
            raise ValueError("stacks must contain integer tuples")
        if state != State.make(state.pc, ints, stacks):
            raise ValueError("state bindings must have canonical name order")

    def loads(self, text: str) -> State:
        """Decode a state for this program; shape validation is not reachability."""
        def object_pairs(pairs: list[tuple[str, object]]) -> dict:
            out: dict = {}
            for key, value in pairs:
                if key in out:
                    raise ValueError("duplicate JSON field")
                out[key] = value
            return out

        data = json.loads(text, object_pairs_hook=object_pairs)
        if not isinstance(data, dict) or set(data) != {"pc", "integers", "stacks"}:
            raise ValueError("state must have pc, integers and stacks only")
        if not isinstance(data["integers"], dict) or not isinstance(data["stacks"], dict):
            raise ValueError("state bindings must be objects")
        if any(not isinstance(v, list) for v in data["stacks"].values()):
            raise ValueError("serialized stacks must be arrays")
        state = State.make(data["pc"], data["integers"],
                           {k: tuple(v) for k, v in data["stacks"].items()})
        self.validate(state)
        return state

    def step(self, state: State, *, backward: bool = False) -> State:
        """A partial transition: refusal leaves the immutable input untouched."""
        self.validate(state)
        index = state.pc - 1 if backward else state.pc
        if not 0 <= index < len(self.instructions):
            raise ValueError("no transition in this direction")
        instruction = self.instructions[index]
        ints, stacks = dict(state.integers), dict(state.stacks)
        if isinstance(instruction, Boundary):
            create = instruction.enter != backward
            # Static checking ensures value never depends on the removed binding.
            value = evaluate(instruction.value, ints)
            if create:
                if instruction.name in ints:
                    raise ValueError("local is already bound")
                ints[instruction.name] = value
            else:
                if ints[instruction.name] != value:
                    raise ValueError("scope assertion failed; local was not removed")
                del ints[instruction.name]
        elif isinstance(instruction, Update):
            value = evaluate(instruction.value, ints)
            sign = -1 if instruction.subtract != backward else 1
            ints[instruction.name] += sign * value
        else:
            pop = instruction.pop != backward
            values = stacks[instruction.stack]
            if pop:
                if ints[instruction.name] != 0:
                    raise ValueError("pop requires a zero destination")
                if not values:
                    raise ValueError("stack underflow")
                ints[instruction.name], stacks[instruction.stack] = values[0], values[1:]
            else:
                stacks[instruction.stack] = (ints[instruction.name],) + values
                ints[instruction.name] = 0
        result = State.make(state.pc + (-1 if backward else 1), ints, stacks)
        self.validate(result)
        return result
