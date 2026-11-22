"""The Brainfuck terminal Gallery preview comes directly from its real shell recording."""
import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/terminal-in-brainfuck"
SPEC = importlib.util.spec_from_file_location(
    "terminal_gallery_preview", PROJECT / "make-gallery-preview.py"
)


def load_generator():
    assert SPEC is not None and SPEC.loader is not None
    module = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(module)
    return module


class TerminalGalleryPreviewTests(unittest.TestCase):
    def test_manifest_lists_preview_and_generator(self):
        manifest = json.loads((ROOT / "site/projects.json").read_text(encoding="utf-8"))
        entry = next(p for p in manifest["projects"] if p["id"] == "terminal-in-brainfuck")
        self.assertIn("projects/terminal-in-brainfuck/gallery-preview.svg", entry["files"])
        self.assertIn("projects/terminal-in-brainfuck/make-gallery-preview.py", entry["files"])

    def test_svg_matches_generator_and_recorded_shell_output(self):
        module = load_generator()
        recording = (PROJECT / "recordings/native-shell.txt").read_text(encoding="utf-8")
        generated = module.svg(recording)
        self.assertEqual((PROJECT / "gallery-preview.svg").read_text(encoding="utf-8"), generated)
        ET.fromstring(generated)
        for expected in (
            "REAL SHELL",
            "size: 24 40",
            "RED",
            "xyCDE",
            'printf "REAL SHELL\\n"; printf "size: "; stty size;',
            'printf "\\033[31mRED\\033[0m\\n"; printf "ABCDE\\rxy\\n"',
            "compiled to Brainfuck from Python",
            "python3 projects/terminal-in-brainfuck/run_terminal.py",
            "Complete frames: 50",
        ):
            self.assertIn(expected, generated)

    def test_changed_command_updates_rendered_svg_and_rejects_overflow(self):
        module = load_generator()
        recording = (PROJECT / "recordings/native-shell.txt").read_text(encoding="utf-8")
        old_cmd = 'printf "REAL SHELL\\n"; printf "size: "; stty size; printf "\\033[31mRED\\033[0m\\n"; printf "ABCDE\\rxy\\n"'
        new_cmd = 'printf "ALT CHECK <ok> & done\\n"; uname -s'
        self.assertIn(old_cmd, recording)
        changed = module.svg(recording.replace(old_cmd, new_cmd, 1))
        root = ET.fromstring(changed)
        rendered_text = "\n".join(el.text for el in root.iter() if el.text)
        self.assertIn(new_cmd, rendered_text)
        self.assertNotIn('printf "REAL SHELL\\n"', rendered_text)
        self.assertNotIn("stty size;", rendered_text)

        too_long = " ".join(["echo_token"] * 30)
        with self.assertRaises(ValueError):
            module.svg(recording.replace(old_cmd, too_long, 1))

    def test_rejects_incomplete_or_tampered_recording(self):
        module = load_generator()
        recording = (PROJECT / "recordings/native-shell.txt").read_text(encoding="utf-8")
        old_cmd = 'printf "REAL SHELL\\n"; printf "size: "; stty size; printf "\\033[31mRED\\033[0m\\n"; printf "ABCDE\\rxy\\n"'
        for bad in (
            "",
            "Command passed to /bin/sh -c:\nonly header\n",
            recording.replace(old_cmd, "   ", 1),
        ):
            with self.assertRaises(ValueError):
                module.svg(bad)

    def test_house_js_alt_text_credits_terminal_compiled_to_brainfuck(self):
        house_js = (ROOT / "site/house.js").read_text(encoding="utf-8")
        self.assertIn('"terminal-in-brainfuck":{src:"projects/terminal-in-brainfuck/gallery-preview.svg"', house_js)
        self.assertNotIn("shell compiled to Brainfuck", house_js)
        self.assertIn("terminal compiled to Brainfuck from Python", house_js)


if __name__ == "__main__":
    unittest.main()
