import itertools
import json
import unittest

from scope_machine import Local, Program, State, Transfer, Update, expression as e


class ScopeTests(unittest.TestCase):
    def test_exit_uses_final_surviving_values(self):
        program = Program.compile((Local("x", e("g"), e("g"), (
            Update("x", 7), Update("g", 7),
        )),), {"g"}, set())
        state = start = State.make(0, {"g": 4}, {})
        while state.pc < len(program.instructions):
            next_state = program.step(state)
            self.assertEqual(program.step(next_state, backward=True), state)
            state = next_state
        self.assertEqual(dict(state.integers), {"g": 11})
        # Recreate 11, not the initial value 4: no saved old local is consulted.
        state = program.step(state, backward=True)
        self.assertEqual(dict(state.integers)["x"], 11)
        while state.pc:
            state = program.step(state, backward=True)
        self.assertEqual(state, start)

    def test_nested_scopes_and_stack_moves(self):
        program = Program.compile((Local("x", e("g + 1"), e("g + 1"), (
            Local("y", e("x * 2"), 0, (Transfer("y", "s"),)),
            Update("x", 3), Update("g", 3),
        )),), {"g"}, {"s"})
        for g, tail in itertools.product(range(-4, 5), ((), (0,), (3, -2))):
            state = start = State.make(0, {"g": g}, {"s": tail})
            while state.pc < len(program.instructions):
                next_state = program.step(state)
                self.assertEqual(program.step(next_state, backward=True), state)
                state = next_state
            self.assertEqual(dict(state.stacks)["s"], (2 * (g + 1),) + tail)
            state = program.loads(state.dumps())
            while state.pc:
                next_state = program.step(state, backward=True)
                self.assertEqual(program.step(next_state), state)
                state = next_state
            self.assertEqual(state, start)

    def test_assertion_failure_preserves_state(self):
        program = Program.compile((Local("x", 2, 2, (Update("x", 1),)),), set(), set())
        state = program.step(program.step(State.make(0, {}, {})))
        before = state.dumps()
        with self.assertRaisesRegex(ValueError, "scope assertion"):
            program.step(state)
        self.assertEqual(state.dumps(), before)
        # Undoing entry also checks, rather than erasing an arbitrary local.
        forged = State.make(1, {"x": 9}, {})
        with self.assertRaisesRegex(ValueError, "scope assertion"):
            program.step(forged, backward=True)

    def test_static_restrictions(self):
        bad = (
            (Local("g", 0, 0, ()),),  # no shadowing
            (Local("x", e("x"), 0, ()),),
            (Local("x", 0, e("x"), ()),),  # tautological deletion is noninjective
            (Local("x", 0, 0, ()), Update("g", e("x"))),
            (Update("g", e("g + 1")),),
            (Transfer("g", "missing"),),
        )
        for body in bad:
            with self.subTest(body=body), self.assertRaises(ValueError):
                Program.compile(body, {"g"}, set())
        with self.assertRaises(ValueError):
            Program.compile((), {"same"}, {"same"})

    def test_transfer_domains(self):
        program = Program.compile((Transfer("x", "s", pop=True),), {"x"}, {"s"})
        for x, values, error in ((0, (), "underflow"), (1, (4,), "zero destination")):
            state = State.make(0, {"x": x}, {"s": values})
            with self.assertRaisesRegex(ValueError, error):
                program.step(state)
            self.assertEqual(dict(state.integers)["x"], x)
            self.assertEqual(dict(state.stacks)["s"], values)
        for v in range(-10, 11):
            state = State.make(0, {"x": 0}, {"s": (v, 8)})
            self.assertEqual(program.step(program.step(state), backward=True), state)

    def test_every_interior_checkpoint_is_sufficient(self):
        program = Program.compile((Local("x", e("g"), 0, (
            Transfer("x", "s"),
        )),), {"g"}, {"s"})
        start = State.make(0, {"g": -123}, {"s": (99,)})
        state = start
        for _ in range(len(program.instructions) + 1):
            restored = program.loads(state.dumps())
            while restored.pc:
                restored = program.step(restored, backward=True)
            self.assertEqual(restored, start)
            if state.pc < len(program.instructions):
                state = program.step(state)

    def test_checkpoint_shape_and_boundaries(self):
        program = Program.compile((Local("x", 0, 0, ()),), {"g"}, {"s"})
        valid = json.loads(State.make(0, {"g": 0}, {"s": ()}).dumps())
        for change in ({"pc": True}, {"pc": -1}, {"pc": 3},
                       {"integers": {"g": False}}, {"integers": {"g": 0, "x": 0}},
                       {"stacks": {"s": [True]}}, {"history": []}, {"stacks": []}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                program.loads(json.dumps(valid | change))
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            program.loads('{"pc":0,"pc":1,"integers":{},"stacks":{}}')
        with self.assertRaisesRegex(ValueError, "no transition"):
            program.step(program.loads(json.dumps(valid)), backward=True)

    def test_expression_parser_is_data_only(self):
        for source in ("f()", "x[0]", "x.y", "True", "x / 3", "2 ** 8"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                e(source)
        program = Program.compile((Update("x", e("-(3 * g) + 2")),), {"x", "g"}, set())
        start = State.make(0, {"x": 10**100, "g": -7}, {})
        end = program.step(start)
        self.assertEqual(dict(end.integers)["x"], 10**100 + 23)
        self.assertEqual(program.step(end, backward=True), start)

    def test_composition_against_closed_form(self):
        # A direct mathematical result, not a second walk over compiled code.
        program = Program.compile((Local("x", e("2 * g + 1"), 0, (
            Update("x", e("d"), subtract=True),
            Transfer("x", "s"),
            Update("g", e("d")),
        )),), {"g", "d"}, {"s"})
        for g, d in itertools.product(range(-12, 13), repeat=2):
            start = State.make(0, {"g": g, "d": d}, {"s": (17,)})
            state = start
            for _ in program.instructions:
                state = program.step(state)
            self.assertEqual(dict(state.integers), {"g": g + d, "d": d})
            self.assertEqual(dict(state.stacks), {"s": (2 * g + 1 - d, 17)})
            for _ in program.instructions:
                state = program.step(state, backward=True)
            self.assertEqual(state, start)


if __name__ == "__main__":
    unittest.main()
