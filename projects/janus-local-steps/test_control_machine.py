from dataclasses import replace
import json
import unittest

from control_machine import Machine, Procedure, example
from scope_machine import Local, Program, Update, expression as e


def completed(machine, state):
    return state.following == machine.stops[machine.main] and not state.calls


class ControlTests(unittest.TestCase):
    def test_nested_calls_every_transition_and_checkpoint(self):
        for value in range(-5, 6):
            machine, initial = example(value)
            state = initial
            checkpoints = [state]
            while not completed(machine, state):
                following = machine.step(state)
                self.assertEqual(machine.step(following, backward=True), state)
                state = following
                checkpoints.append(state)
            self.assertEqual(len(checkpoints) - 1, 14)
            self.assertEqual(dict(state.integers), {"g": value + 2})
            self.assertEqual(dict(state.stacks), {"s": (3 * value, 99)})
            for checkpoint in checkpoints:
                recovered = machine.loads(checkpoint.dumps())
                while recovered != initial:
                    before = machine.step(recovered, backward=True)
                    self.assertEqual(machine.step(before), recovered)
                    recovered = before
                self.assertEqual(recovered, initial)

    def test_suspended_locals_survive_without_copying_into_frames(self):
        machine, state = example()
        while state.previous != "leaf:data:1":
            state = machine.step(state)
        self.assertEqual(state.calls, ("main:call:1", "worker:call:1"))
        self.assertEqual(dict(state.integers), {"g": 4, "x": 4, "y": 5, "z": 0})
        self.assertEqual(set(json.loads(state.dumps())), {"control", "integers", "stacks", "calls"})
        while state.previous != "main:call:1":
            state = machine.step(state)
        self.assertEqual(dict(state.integers), {"g": 6, "x": 4})
        self.assertEqual(state.calls, ())
        # Reverse return reconstructs the call site, then y from the final g.
        state = machine.step(state, backward=True)
        self.assertEqual(state.calls, ("main:call:1",))
        state = machine.step(state, backward=True)
        self.assertEqual(dict(state.integers)["y"], 7)

    def test_multiple_calls_to_the_same_procedure(self):
        main = Program.compile((Update("g", 1),), {"g"}, set())
        worker = Program.compile((Update("g", 10),), {"g"}, set())
        machine = Machine({"main": Procedure(main, ((0, "worker"), (1, "worker"))),
                           "worker": Procedure(worker)})
        state = initial = machine.initial({"g": 1}, {})
        while not completed(machine, state):
            state = machine.step(state)
        self.assertEqual(dict(state.integers), {"g": 22})
        while state != initial:
            state = machine.step(state, backward=True)
        self.assertEqual(state, initial)

    def test_empty_callee_and_main_boundary(self):
        kernel = Program.compile((), {"g"}, set())
        machine = Machine({"main": Procedure(kernel, ((0, "worker"),)),
                           "worker": Procedure(kernel)})
        initial = machine.initial({"g": 0}, {})
        with self.assertRaisesRegex(ValueError, "main boundary"):
            machine.step(initial, backward=True)
        end = machine.step(machine.step(initial))
        self.assertTrue(completed(machine, end))
        with self.assertRaisesRegex(ValueError, "main boundary"):
            machine.step(end)
        self.assertEqual(machine.step(machine.step(end, backward=True), backward=True), initial)

    def test_bad_control_frames_and_live_domains(self):
        machine, state = example()
        while state.previous != "leaf:data:1":
            state = machine.step(state)
        bad = (replace(state, previous="missing"),
               replace(state, following="main:data:0"),
               replace(state, calls=()),
               replace(state, calls=("worker:call:1", "main:call:1")),
               replace(state, integers=tuple((k, v) for k, v in state.integers if k != "x")),
               replace(state, integers=state.integers + (("history", 4),)))
        for changed in bad:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                machine.step(changed)
        data = json.loads(state.dumps())
        for changes in ({"history": []}, {"calls": [False]}, {"control": ["main:start"]}):
            with self.assertRaises(ValueError):
                machine.loads(json.dumps(data | changes))

    def test_definition_restrictions(self):
        base = Program.compile((), {"g"}, set())
        with self.assertRaisesRegex(ValueError, "recursive"):
            Machine({"main": Procedure(base, ((0, "worker"),)),
                     "worker": Procedure(base, ((0, "main"),))})
        local = Program.compile((Local("x", 0, 0, ()),), {"g"}, set())
        with self.assertRaisesRegex(ValueError, "distinct across"):
            Machine({"main": Procedure(local), "worker": Procedure(local)})
        for calls in (((False, "main"),), ((3, "main"),), ((0, "missing"),),
                      ((0, "worker"), (0, "worker"))):
            with self.subTest(calls=calls), self.assertRaises(ValueError):
                Machine({"main": Procedure(base, calls), "worker": Procedure(base)})
        # A callee cannot read an unpassed caller local.
        with self.assertRaisesRegex(ValueError, "non-live"):
            Program.compile((Update("g", e("x")),), {"g"}, set())


if __name__ == "__main__":
    unittest.main()
