import json, os, pathlib, subprocess, sys, tempfile
cli = pathlib.Path('projects/blackout/blackout.py').resolve()
with tempfile.TemporaryDirectory() as temporary:
    home = pathlib.Path(temporary).resolve()
    source = home / 'source'
    source.mkdir()
    (source / 'evidence').write_text('expected bytes')
    manifest = home / 'manifest.fifo'
    os.mkfifo(manifest)
    try:
        result = subprocess.run(
            [sys.executable, str(cli), 'verify', str(source), str(manifest)],
            capture_output=True, text=True, timeout=2)
        print('FIFO manifest:', result.returncode, result.stderr.strip())
    except subprocess.TimeoutExpired:
        print('FIFO manifest: TIMEOUT after 2 seconds; killed by harness')
    alias = home / 'alias'
    alias.symlink_to(source, target_is_directory=True)
    for label, root in (
        ('symlink-component', str(alias) + '/../source'),
        ('missing-component', str(home / 'missing') + '/../source'),
    ):
        result = subprocess.run(
            [sys.executable, str(cli), 'create', root, str(home / (label + '.json'))],
            capture_output=True, text=True, timeout=2)
        print(label, result.returncode, result.stdout.strip(), result.stderr.strip())
