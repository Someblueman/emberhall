"""Literal colour pictures and a conformance runner; no terminal implementation."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
CELLS, FRAME_SIZE = 960, 1924


def expected_frame(stage):
    chars = bytearray(b" " * CELLS)
    attrs = bytearray([stage["blank_attribute"]] * CELLS)
    occupied_rows, occupied_attrs = set(), set()
    for row, text in stage["rows"]:
        if row in occupied_rows or not 0 <= row < 24 or len(text) > 40:
            raise ValueError("invalid or duplicate picture row")
        occupied_rows.add(row)
        chars[row * 40:row * 40 + len(text)] = text.encode("ascii")
    for start, count, value in stage["attribute_spans"]:
        positions = set(range(start, start + count))
        if not 0 <= start < CELLS or count <= 0 or start + count > CELLS:
            raise ValueError("attribute span outside screen")
        if positions & occupied_attrs:
            raise ValueError("overlapping attribute spans")
        if not 0 <= value <= 127:
            raise ValueError("attribute outside byte contract")
        occupied_attrs.update(positions)
        attrs[start:start + count] = bytes([value]) * count
    frame = b"\xff" + chars + attrs + bytes(stage["cursor"]) + b"\xfe"
    validate_frame(frame)
    return frame


def validate_frame(frame):
    if len(frame) != FRAME_SIZE or frame[0] != 255 or frame[-1] != 254:
        raise ValueError("frame length or markers")
    if any(c < 32 or c > 126 for c in frame[1:961]):
        raise ValueError("nonprintable screen character")
    if any(a > 127 for a in frame[961:1921]):
        raise ValueError("attribute outside byte contract")
    if frame[1921] >= 24 or frame[1922] >= 40:
        raise ValueError("cursor outside screen")


def load_cases():
    document = json.loads((HERE / "colour-cases.json").read_text())
    if document["format"] != "terminal-colour-cases-v1":
        raise ValueError("unknown fixture format")
    cases, names = document["cases"], set()
    for case in cases:
        if case["name"] in names:
            raise ValueError("duplicate case")
        names.add(case["name"])
        for chunk in case["chunks"]:
            chunk.encode("ascii")
        stage_names = set()
        for stage in case["checkpoints"]:
            if stage["name"] in stage_names or not 0 <= stage["after_chunks"] <= len(case["chunks"]):
                raise ValueError("invalid checkpoint")
            stage_names.add(stage["name"])
            expected_frame(stage)
    return cases


# The existing VM executes only ><+-.,[]. This runner knows frame boundaries,
# not how any input byte should place, erase, scroll or colour a character.
RUN = r"""
const fs = require('node:fs'), {BrainfuckMachine} = require('./vm.js');
const spec = JSON.parse(fs.readFileSync(0, 'utf8'));
const source = fs.readFileSync(spec.program, 'utf8');
for (const item of spec.cases) {
  const input = item.chunks.flat(), zero = input.indexOf(0);
  const count = zero < 0 ? input.length : zero;
  const schedules = [item.chunks, input.map(b => [b])];
  for (let i = 0; i <= input.length; i++) schedules.push([input.slice(0,i), input.slice(i)]);
  let baseline;
  for (const chunks of schedules) {
    const output = []; let next = 0, loops = 0;
    const vm = new BrainfuckMachine(source, b => output.push(b), spec.tape);
    while (!vm.halted) {
      vm.run(20000);
      if (++loops > 25000) throw Error(item.name + ': operation budget exceeded');
      if (vm.waiting) {
        if (next < chunks.length) vm.feed(chunks[next++]); else vm.end();
      }
    }
    const bytes = Buffer.from(output);
    if (bytes.length !== (count + 1) * 1924) throw Error(item.name + ': wrong output length ' + bytes.length);
    for (let i = 0; i < bytes.length; i += 1924) {
      const f = bytes.subarray(i, i + 1924);
      if (f[0] !== 255 || f[1923] !== 254 || f[1921] >= 24 || f[1922] >= 40 ||
          f.subarray(1,961).some(b => b < 32 || b > 126) ||
          f.subarray(961,1921).some(b => b > 127)) throw Error(item.name + ': invalid frame');
    }
    if (baseline && !bytes.equals(baseline)) throw Error(item.name + ': input split changes frames');
    baseline = bytes;
    for (const stage of item.stages) {
      const actual = bytes.subarray(stage.frame * 1924, (stage.frame + 1) * 1924);
      if (!actual.equals(Buffer.from(stage.expected, 'base64'))) throw Error(item.name + '/' + stage.name + ': picture differs');
    }
  }
  process.stdout.write(item.name + ': ' + schedules.length + ' schedules agree\n');
}
"""


def run_program(program, tape, cases):
    payload = []
    blank = dict(rows=[], attribute_spans=[], cursor=[0, 0], blank_attribute=7)
    for case in cases:
        stages = [dict(name="initial", frame=0, expected=base64.b64encode(expected_frame(blank)).decode())]
        for stage in case["checkpoints"]:
            prefix = "".join(case["chunks"][:stage["after_chunks"]]).encode("ascii")
            frame = len(prefix.split(b"\0", 1)[0])
            stages.append(dict(name=stage["name"], frame=frame,
                               expected=base64.b64encode(expected_frame(stage)).decode()))
        payload.append(dict(name=case["name"], chunks=[list(s.encode("ascii")) for s in case["chunks"]], stages=stages))
    result = subprocess.run(["node", "-e", RUN], cwd=HERE, text=True, capture_output=True,
                            input=json.dumps(dict(program=str(program.resolve()), tape=tape, cases=payload)), timeout=180)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


class ColourCasesTests(unittest.TestCase):
    def test_all_literal_pictures_have_valid_frames(self):
        self.assertEqual(len(load_cases()), 20)

    def test_black_attribute_is_data_and_marker_positions_are_exact(self):
        case = next(c for c in load_cases() if c["name"] == "zero-attribute-is-data")
        frame = expected_frame(case["checkpoints"][-1])
        self.assertEqual(frame[961:1001], bytes(40))
        self.assertEqual(frame[1921:], bytes([0, 1, 254]))

    def test_reject_malformed_frames(self):
        frame = expected_frame(load_cases()[0]["checkpoints"][0])
        for offset, value in [(0, 0), (1, 31), (961, 128), (1921, 24), (1922, 40), (1923, 255)]:
            changed = bytearray(frame)
            changed[offset] = value
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                validate_frame(changed)
        with self.assertRaises(ValueError):
            validate_frame(frame[:-1])

    def test_reject_overlapping_attribute_spans(self):
        stage = dict(rows=[], cursor=[0, 0], blank_attribute=7, attribute_spans=[[0, 2, 1], [1, 1, 2]])
        with self.assertRaises(ValueError):
            expected_frame(stage)

    def test_runner_accepts_a_literal_blank_frame(self):
        # A constant frame tests the verifier/VM boundary, not a colour terminal.
        # It ends at a real comma wait; the driver must explicitly provide EOF.
        frame = b"\xff" + b" " * 960 + bytes([7]) * 960 + b"\0\0\xfe"
        program, previous = [], 0
        for byte in frame:
            program.append("+" * ((byte - previous) % 256) + ".")
            previous = byte
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "blank.bf"
            path.write_text("".join(program) + ",")
            case = dict(name="blank", chunks=[""], checkpoints=[])
            self.assertIn("3 schedules agree", run_program(path, 1, [case]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show", metavar="CASE")
    parser.add_argument("--program", type=Path)
    parser.add_argument("--tape-cells", type=int)
    parser.add_argument("--case", dest="case_name")
    args = parser.parse_args()
    cases = load_cases()
    if args.case_name or args.show:
        cases = [c for c in cases if c["name"] == (args.case_name or args.show)]
        if not cases:
            parser.error("unknown case")
    if args.show:
        for stage in cases[0]["checkpoints"]:
            frame = expected_frame(stage)
            print(stage["name"], "cursor", stage["cursor"], "attribute spans", stage["attribute_spans"])
            print("\n".join(frame[1 + r * 40:41 + r * 40].decode() for r in range(24)))
    elif args.program:
        if args.tape_cells is None or args.tape_cells <= 0:
            parser.error("--program requires a positive --tape-cells")
        print(run_program(args.program, args.tape_cells, cases), end="")
    else:
        unittest.main(argv=[__file__])
