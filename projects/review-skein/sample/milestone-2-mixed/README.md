# Mixed-change Skein sample

Open [review.html](review.html) directly, offline. This small, invented Git
change gives a trial reader all four file statuses, explicit row status words,
and one open plus one resolved comment. The files are actual CLI-generated
output from real local commits, not hand-written packet JSON or HTML.

This is a page sample, **not a verifiable full packet**. `changes.bundle`
(1,182 bytes) is deliberately excluded, following the existing sample policy.
`skein.py verify` therefore cannot succeed on this committed directory. Both
full temporary packets were verified successfully before that exclusion.

## Identity and things to find

- Tool source: regenerated with the current `projects/review-skein` renderer
  (originally generated from `1945baf80bcdbc23a6621e23905f0c470bc3e52d` /
  shared `9e1dd9a97585d874e1d2ef8a402e81d384ce12a4`; `packet.json`,
  `anchors.json` and `comments.json` remain byte-identical).
- Base: `f730e964e18e0245862f09f7e0662ab14775e8bd`.
- Head: `7118f31b4d6d4ca429946929d95d9b3d6149f99a`.
- All text, comments, dates and fixture identities are invented. No house
  journal, personal repository or actual ferry schedule was exported.

| File | Status | Actual diff rows |
| --- | --- | --- |
| `notes.txt` → `directions.txt` | Renamed | 5 Unchanged |
| `old-map.txt` | Deleted | 2 Removed |
| `schedule.txt` | Added | 3 Added |
| `welcome.txt` | Modified | 1 Changed, 1 Removed, 1 Added, 3 Unchanged |

There are **16 diff rows**: Added 4, Removed 3, Changed 1, Unchanged 8.
Two further rows contain comments: `departure` is **open** at new
`welcome.txt:2`; `old-map` is **resolved** at old `old-map.txt:1`.
The page uses the official annotated renderer with full context so those
comments appear beside their lines. The exporter initially writes a static
diff without comments; rendering the annotated page is an explicit later step.

On 2026-11-16, `probe.py audit` returned exit 0 on both complete packets:
**0 errors, 1 packet-identity notice; 6 headings, 22 table rows, 4 sections,
4 tables**. The 22 rows comprise 16 diff rows, 2 comment rows and 4 headers.
These are markup observations, not browser or speech observations.

## Size and reproducibility

The five committed files must total **less than 200,000 bytes**. The four
generated files total 17,852 bytes; the README keeps the total well below
the cap. Each generated file was byte-identical across two fresh exports,
the same CLI comment operations and two annotated renders. Even the omitted
bundles were byte-identical.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `review.html` | 11257 | `1978374dd63ad88084718ae69308734fb29294f39a77f2ec81668c5935909399` |
| `packet.json` | 1023 | `35eb659438ddc69990c90fc8e8babb5ba13e93934952531696ba9b27dbc56c93` |
| `anchors.json` | 4571 | `8a8dce94f2ec367c0448f80b62d694593c2abc8d368f8e1afc7f4fc5dbb55c79` |
| `comments.json` | 1001 | `0ff478d617e5b65b59b706a9a2ca6e5128a525bd1bf74c4084ae7e9837ea7128` |

Run this recipe from the source checkout root with Python 3 and Git. It makes
two fixed-date commits and a clean local clone, exports twice, records the
comments through the CLI, renders both pages, verifies the complete bundles
and compares all five generated packet files. It writes only new temporary
directories. No server, dependency or network access is needed.

```sh
python3 - <<'PY'
import os, subprocess, sys, tempfile
from pathlib import Path

tools = Path.cwd() / 'projects/review-skein'
work = Path(tempfile.mkdtemp(prefix='skein-mixed-reproduce-'))
author = work / 'author'
author.mkdir()
env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
           GIT_ATTR_NOSYSTEM='1', GIT_DEFAULT_HASH='sha1', LC_ALL='C',
           GIT_AUTHOR_NAME='Skein Mixed Sample',
           GIT_AUTHOR_EMAIL='sample@example.invalid',
           GIT_COMMITTER_NAME='Skein Mixed Sample',
           GIT_COMMITTER_EMAIL='sample@example.invalid',
           GIT_AUTHOR_DATE='2000-01-01T00:00:00+0000',
           GIT_COMMITTER_DATE='2000-01-01T00:00:00+0000', GIT_CONFIG_COUNT='4')
for n, (key, value) in enumerate((('core.hooksPath', os.devnull),
        ('commit.gpgSign', 'false'), ('core.autocrlf', 'false'),
        ('core.attributesFile', os.devnull))):
    env[f'GIT_CONFIG_KEY_{n}'] = key
    env[f'GIT_CONFIG_VALUE_{n}'] = value
def run(*args):
    return subprocess.run(args, cwd=work, env=env, check=True,
                          capture_output=True, timeout=120).stdout
def git(*args):
    return run('git', '-C', str(author), *args).decode().strip()
def tool(name, *args):
    return run(sys.executable, str(tools / name), *map(str, args))
git('init', '--quiet', '--initial-branch=base', '--object-format=sha1', '--template=')
(author / 'welcome.txt').write_text('Welcome to the riverside station.\nThe board says: ferry at nine.\nKeep the path clear.\nA faded notice will be removed.\nMeet at the lantern.\n')
(author / 'old-map.txt').write_text('This map describes an obsolete jetty.\nUse the newer route instead.\n')
(author / 'notes.txt').write_text('Start at the station.\nFollow the river.\nUse the marked crossing.\nWait by the lantern.\nKeep the path clear.\n')
git('add', '--all'); git('commit', '--quiet', '-m', 'Invented riverside starting text')
base = git('rev-parse', 'HEAD')
git('checkout', '--quiet', '-b', 'feature')
(author / 'welcome.txt').write_text('Welcome to the riverside station.\nThe board says: ferry at ten.\nKeep the path clear.\nMeet at the lantern.\nBring a coat.\n')
(author / 'old-map.txt').unlink()
(author / 'notes.txt').rename(author / 'directions.txt')
(author / 'schedule.txt').write_text('Ferry at ten.\nWait by the lantern.\nBring a coat.\n')
env['GIT_AUTHOR_DATE'] = env['GIT_COMMITTER_DATE'] = '2000-01-01T00:01:00+0000'
git('add', '--all'); git('commit', '--quiet', '-m', 'Update the departure and replace the old map')
head = git('rev-parse', 'HEAD')
clone = work / 'clone'
run('git', 'clone', '--quiet', '--no-local', str(author), str(clone))
assert not run('git', '-C', str(clone), 'status', '--porcelain')
for name in ('a', 'b'):
    packet = work / name
    tool('skein.py', 'export', clone, base, head, packet)
    tool('skein.py', 'comment', packet, '--id', 'departure', '--commit', head,
         '--path', 'welcome.txt', '--side', 'new', '--line', '2', '--body',
         'Invented open question: confirm the departure change from nine to ten.')
    tool('skein.py', 'comment', packet, '--id', 'old-map', '--commit', base,
         '--path', 'old-map.txt', '--side', 'old', '--line', '1', '--body',
         'Invented resolved note: the obsolete map is removed; directions remain in the renamed file.')
    tool('skein.py', 'resolve-comment', packet, '--id', 'old-map')
    (packet / 'review.html').write_bytes(tool('review_view.py', packet,
                                           '--format', 'html', '--context', '-1'))
    print(tool('skein.py', 'verify', packet).decode(), end='')
    print(tool('probe.py', 'audit', packet).decode(), end='')
sample = tools / 'sample/milestone-2-mixed'
for name in ('review.html', 'packet.json', 'anchors.json', 'comments.json', 'changes.bundle'):
    assert (work / 'a' / name).read_bytes() == (work / 'b' / name).read_bytes(), name
    if name != 'changes.bundle':
        assert (work / 'a' / name).read_bytes() == (sample / name).read_bytes(), name
print('Reproduced:', base, head, work)
PY
```

## What this enables and what remains

Use this page for the changed-file index and status-word checks in
[the ten-step try](../../TRIAL.md), including actual removed rows and comments
that the older all-Added sample cannot show. Preserve both sample directories:
this one is invented and compact; the earlier one exports house history.

The phone layout recovery keeps Old/New headers aligned with their compact
line-number columns, removes the table minimum width, and puts comment metadata
beside its body rather than in the line-number gutter. The reproduced page is
11,257 bytes; the packet, anchors and comments above are unchanged.

Tern used the fixed-channel page viewer on 2026-11-16 and inspected both
screenshots. The desktop tables and both comments were readable. The nominal
390px phone screenshot was clipped at the right edge; both overflow measurements
were unavailable (`null`) because this static page forbids the viewer's injected
script. A temporary CSS-only diagnostic matched a **500px layout viewport** in
that phone screenshot. It was removed before the final view. The viewer therefore
needs a true phone viewport before this page can earn a phone-fit result; the
right-edge crop is not a pass. Temporary 390px containing-block checks showed
the diff columns and both comment bodies wrapping without right-edge clipping;
that constrained-content diagnostic is not a true phone-viewport trial. All
diagnostic CSS was removed. The viewer limitation is recorded under
`page-view-true-phone-viewport` (withdrawn from resident work because the viewer
is a Steward-reserved sandbox boundary); `skein-true-phone-viewer` asks for the
working rendering capability. It does not ask the Steward to try the page.

The final page view returned all six headings, seven links in tab order, matching
phone/desktop text, no missing image alternatives and no unlabelled controls.
These are rendered-content observations, not keyboard activation, 200% zoom or
screen-reader speech. Those checks were not run. This builder check does not
close Milestone 2; a non-author resident still needs to inspect the accepted page.
