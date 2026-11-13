"""Exercise a delivered ZIP outside the repository; run with network denied."""
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import zipfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    return {str(p.relative_to(root)): (digest(p), p.stat().st_size,
            p.stat().st_mode & 0o777, p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


def main():
    archive, source = (Path(p).resolve(strict=True) for p in sys.argv[1:3])
    product = Path("projects/blackout")
    drill = product / "examples/recovery-drill"
    names = {str(product / n) for n in ("blackout.py", "README.md", "QUICKSTART.md")}
    names |= {str(p.relative_to(source)) for p in (source / drill).rglob("*") if p.is_file()}
    before = {name: digest(source / name) for name in names}
    archive_hash = digest(archive)
    with tempfile.TemporaryDirectory(prefix="blackout-delivered-") as temporary:
        root = Path(temporary).resolve()
        kit = root / "extracted"; kit.mkdir()
        with zipfile.ZipFile(archive) as bundle:
            assert len(bundle.namelist()) == len(names)
            assert set(bundle.namelist()) == names
            for entry in bundle.infolist():
                assert entry.date_time == (1980, 1, 1, 0, 0, 0)
                assert entry.compress_type == zipfile.ZIP_STORED
                assert bundle.read(entry) == (source / entry.filename).read_bytes()
            bundle.extractall(kit)
        untouched = snapshot(kit)

        def cli(*args, expected):
            result = subprocess.run([sys.executable, "-I", str(kit / product / "blackout.py"),
                                     *map(str, args)], cwd=kit, capture_output=True, text=True, timeout=20)
            assert result.returncode == expected, (result.returncode, result.stderr)
            assert not result.stderr, result.stderr
            return json.loads(result.stdout)

        original = cli("verify", drill / "original", drill / "manifest.json", expected=0)
        damaged = cli("verify", drill / "surviving", drill / "manifest.json", expected=1)
        plan = cli("plan", drill / "surviving", drill / "manifest.json", expected=1)
        assert plan == json.loads((kit / drill / "expected-plan.json").read_text())
        guide = (kit / product / "QUICKSTART.md").read_text()
        extract_recipe = next(block for block in re.findall(r"```sh\n(.*?)```", guide, re.S)
                              if block.startswith("KIT=$(mktemp -d "))
        guided = subprocess.run(["/bin/sh", "-c", extract_recipe.replace(
            "/path/to/blackout-kit.zip", shlex.quote(str(archive)))], cwd=root,
            capture_output=True, text=True, timeout=20)
        assert guided.returncode == 1 and not guided.stderr, (guided.returncode, guided.stderr)
        assert [json.loads(line) for line in guided.stdout.splitlines()] == [damaged, plan]
        worksheet = (kit / drill / "recovery-worksheet.md").read_text()
        rehearsal = next(block for block in re.findall(r"```sh\n(.*?)```", worksheet, re.S)
                         if block.startswith("set -eu\nDEST=$(mktemp -d "))
        copied = subprocess.run(["/bin/sh", "-c", rehearsal], cwd=kit,
                                capture_output=True, text=True, timeout=20)
        assert copied.returncode == 1 and not copied.stderr, (copied.returncode, copied.stderr)
        recovered = json.loads(copied.stdout.splitlines()[-1])
        assert recovered == {"changed": [], "extra": [], "matched": 7,
                             "missing": ["family/summer.txt", "letters/lost.txt"], "ok": False}
        sample = root / "new-synthetic-source"; sample.mkdir()
        (sample / "note.txt").write_text("A second invented archive.\n")
        (sample / "empty").write_bytes(b"")
        manifest = root / "new-manifest.json"
        cli("create", sample, manifest, expected=0)
        new_check = cli("verify", sample, manifest, expected=0)
        assert new_check["matched"] == 2 and new_check["ok"]
        assert cli("plan", sample, manifest, expected=0)["matched"] == 2
        assert snapshot(kit) == untouched
        assert before == {name: digest(source / name) for name in names}
        assert digest(archive) == archive_hash
        print(json.dumps({"archive_sha256": archive_hash, "exact_files": len(names),
              "original": original, "damaged": damaged, "recovered": recovered,
              "new_archive": new_check, "expected_plan_equal": True,
              "verbatim_quickstart_and_worksheet_executed": True,
              "extracted_input_bytes_and_metadata_unchanged": True,
              "source_and_zip_bytes_unchanged": True, "python_isolated_mode": True,
              "python": sys.version}, indent=2))


if __name__ == "__main__":
    main()
