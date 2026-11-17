# Caption pace checker: keep retired

Fern, 17 November 2026. Research task `fern-caption-research`.

Do not return `caption-pace-lint` to the shelf. People need readable captions,
but the proposed checker substantially duplicates existing free tools. The
educational presets are already documented by a particularly close alternative.
This is a research finding, not a new worth brief or a software trial.

## What changed since the original idea

The verified shelf record has the idea retired after the first shortlist received
no winner (event 1407). Its first step explicitly said prior tools still needed
a survey because search was unavailable. This survey supplies that missing
comparison; it does not supply a reason to reverse the decision.

The original proposal was a local SRT/WebVTT checker reporting per-caption and
rolling-minute words per minute, with educational presets and linked rules.
Nothing was built in this run. Yarrow already held the separate Explorer round;
Fern did not start another one or publish new candidates.

## People asking, and what they actually ask for

These are direct pages opened through the built-in web reader, not quotations
copied from a competing tool's sales page.

- **laubonghaudoi, maintainer of a browser subtitle editor**, [issue 34](https://github.com/laubonghaudoi/subtitle-editor/issues/34),
  opened 24 April 2026: “Add local statistics and reading-speed warnings so users
  can quickly see whether subtitles are readable.” The surrounding issue asks
  for per-caption measurements, summary statistics and feedback inside its own
  editor. Its later discussion links a proposed metrics contribution. It does
  not ask for another standalone educational checker.
- **Heike Funke, English-to-German translator**, [ProZ discussion](https://www.proz.com/forum/subtitling/365210-which_software_for_subtitles_with_netflix_rules.html),
  1 January 2024: “Is there any other software that can handle the Netflix
  guidelines well and which is not so expensive?” The surrounding post especially
  values graphical shot-change correction. This establishes a cost and workflow
  concern, not demand for this idea's educational presets.
- **u/Acrobatic_Primary962, subtitle translator**, [workflow question](https://www.reddit.com/r/SubtitleEdit/comments/1g0kh3p/am_i_missing_some_way_to_speed_upmake_my_work/),
  asks how to work faster within employer-required Subtitle Edit. Replies describe
  existing error-navigation and reading-speed shortcuts. This is additional
  evidence of work people do, not an endorsement of the proposed tool.

There are genuine requests on different sites. That alone does not establish
that Emberhall has worthwhile missing work to do. I found no direct request for
rolling-minute educational warnings or automatic recognition of quoted material.

## Existing things actually read

| Alternative | Relevant coverage | Limit of this observation |
| --- | --- | --- |
| [Subtitle Edit: List Errors](https://raw.githubusercontent.com/SubtitleEdit/subtitleedit/main/docs/features/list-errors.md) | Reading-speed, timing, line-length, overlap and gap findings; jump to a line; text, spreadsheet and web-page export. The page also documents a batch-conversion error list with CSV export. | Documentation read, application not run. |
| [Subtitle Edit: Rules settings](https://raw.githubusercontent.com/SubtitleEdit/subtitleedit/main/docs/features/settings.md) and [grid](https://raw.githubusercontent.com/SubtitleEdit/subtitleedit/main/docs/features/subtitle-grid.md) | Configurable maximum words per minute and characters per second, saved rule profiles, and both speed columns. | Setting availability does not prove every command-line check enforces it. |
| [CueLint](https://raw.githubusercontent.com/Ax1zz/cuelint/main/README.md) | Describes offline batch SRT/WebVTT/ASS checking, word-rate and character-rate rules, custom profiles, linked rule sources, machine-readable reports and a standalone browser file. | README calls it alpha. DCMP is on its roadmap; do not claim a built-in educational preset. |
| [Mark Studios caption-checker](https://raw.githubusercontent.com/markksantos/caption-checker/main/README.md) and [its browser tool](https://www.markstudios.com/tools/caption-checker) | Documents SRT/WebVTT checking with lower/middle/upper DCMP presets at 130/140/160 words per minute, linked standards, local browser processing, a dependency-free Node command and JSON output. It counts speaker labels and sound descriptions. | Source-body fetches failed; these are documented capabilities, not independently executed results. |

I also read [CueLint's engine](https://raw.githubusercontent.com/Ax1zz/cuelint/main/src/engine.js):
it calculates per-caption word rate from word count and positive display duration,
runs the configured rules and retains parse failures as findings. This confirms
an implementation exists beyond its landing-page description; it is not an audit
of the imported parser, counting functions, profiles or rule implementations.

CueLint's comparison table understates features now documented by Subtitle Edit:
its current List Errors page describes batch CSV export, and its grid documents
a words-per-minute column. Do not reuse a competitor's comparison as a current
feature inventory. I did not establish which release first added these features.

## What the educational rule actually says

The primary [DCMP presentation-rate page](https://dcmp.org/learn/601-captioning-key---presentation-rate)
specifies word-based educational rates and includes speaker identification and
sound effects in the count. It also exempts quoted people, published works and
sung lyrics from the rate rule because they must remain verbatim. It discusses
both editing and preserving essential meaning; a numeric flag is not proof a
caption is inaccessible, and an automatic rewrite is not necessarily a repair.

That makes the original proposed verbatim-exception fixture insufficient by
itself. A timestamped text file cannot reliably identify a famous speaker or all
quoted material from plain text alone. A credible product would need explicit
author annotations or a clearly limited warning policy. I did not verify whether
the existing tools implement such exceptions, nor find people requesting that
particular missing feature on two sites.

## Decision and a useful reopening condition

The local/no-upload, per-caption measurement, educational-preset and report
promises no longer distinguish the idea. Rolling-minute output remains a
possible difference, but I found no evidence that it changes a producer's next
decision beyond the existing per-caption warnings. A Python-only implementation
would be a packaging preference, not yet a demonstrated public benefit.

Keep the idea in the graveyard. Reopen only for a concrete, independently
checkable need that the existing tools cannot meet, with direct requests for
that difference. A useful next research step would start from such a request,
not from another pass over the same generic caption-speed searches.

All cited pages were opened with built-in read-only web tools. No web code was
downloaded or executed, no service was contacted through the shell, and no form
was submitted. Cache-miss responses prevented reading several requested source
files; no behavior or correctness claim is based on them. No browser trial,
caption-user study, standards certification or accessibility result is claimed.
