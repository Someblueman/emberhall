"""One reconstruction using literal commands, without the counted interpreter."""
from pathlib import Path
import unittest

import model


class LiteralReconstructionTests(unittest.TestCase):
    def test_literal_eight_command_reconstruction(self):
        code = Path(__file__).with_name("terminal.bf").read_text().strip()
        self.assertLessEqual(set(code), set("><+-.,[]"))
        stack, jumps = [], {}
        for i, c in enumerate(code):
            if c == "[":
                stack.append(i)
            elif c == "]":
                j = stack.pop()
                jumps[i], jumps[j] = j, i
        self.assertFalse(stack)
        data = iter(b"\x1b[31;44mABC\rZ\n!\xff\x00Q")
        memory = bytearray(6000)
        output = bytearray()
        head = pc = count = 0
        while pc < len(code):
            c = code[pc]
            if c == ">":
                head += 1
            elif c == "<":
                head -= 1
            elif c == "+":
                memory[head] = (memory[head] + 1) % 256
            elif c == "-":
                memory[head] = (memory[head] - 1) % 256
            elif c == ".":
                output.append(memory[head])
            elif c == ",":
                memory[head] = next(data, 0)
            elif c == "[" and not memory[head]:
                pc = jumps[pc]
            elif c == "]" and memory[head]:
                pc = jumps[pc]
            self.assertTrue(0 <= head < len(memory))
            pc += 1
            count += 1
            if count > 12_000_000:
                self.fail("literal reconstruction exceeded its instruction budget")
        expected = bytearray()
        for cells, row, col, attributes in model.ref_frames(b"\x1b[31;44mABC\rZ\n!\xff\x00Q"):
            expected.extend(b"\xff" + cells.encode("ascii") + bytes(attributes) + bytes([row, col, 254]))
        self.assertEqual(output, expected)


if __name__ == "__main__":
    unittest.main()
