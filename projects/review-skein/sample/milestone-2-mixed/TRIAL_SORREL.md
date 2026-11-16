# Sorrel's independent rendered-content inspection

16 November 2026; source `b2a65ceac0c16e0ad62110412afccbe7b84fe7a6`.
I wrote neither the renderer nor the trial criteria. I wrote an earlier problem
brief and read prior handoffs and the current method, so this is not an unspoiled
first impression. Before opening the page I expected four file statuses and two
anchored comments to be understandable on desktop, with phone fit uncertain.
No preparation or navigation help was needed.

Packet: committed `sample/milestone-2-mixed`, invented content, base
`f730e964e18e0245862f09f7e0662ab14775e8bd`, head
`7118f31b4d6d4ca429946929d95d9b3d6149f99a`.
`review.html`: 11,257 bytes, SHA-256
`1978374dd63ad88084718ae69308734fb29294f39a77f2ec81668c5935909399`.
The committed sample deliberately omits its bundle; this try does not verify one.

Fixed-channel request `50981ba21db346a181a0b19d1c2a2462-mixed-view`, no steps,
house Chrome with network refused, nominal 1280x1800 and 390x1800 images. I opened
both returned screenshot files. Browser version was not returned. Probe audit
before viewing exited 0 with zero errors and one packet-identity notice.

| TRIAL.md step | Result and actual observation |
| --- | --- |
| 1. Offline rendering | PASS: title `Skein review`, language `en`, untruncated `text` contains both IDs, four paths and their diffs; six headings name the page, comments and four files. Both images are non-blank; desktop shows all sections. `script_errors` contains only the expected CSP observation-limit note. Both overflow values are null, not geometry passes. |
| 2. Skip-link snapshot | PASS: first `tab_order` entry is `1. a: Skip to changed files`. Target resolution, focused visibility and activation NOT RUN; no href or relevant target ID is returned and CSP prevents driver interaction. |
| 3. File index | PASS: text and four matching h2/tab names show renamed notes.txt to directions.txt, deleted old-map.txt, added schedule.txt and modified welcome.txt, matching packet.json. No orphans are reported. Links were not activated. |
| 4. File section | PASS: renamed section reports 5 old / 5 new lines; text and desktop image show Old, New, Base text, Head text, with readable paired rows. |
| 5. Row status | PASS: returned text includes Unchanged, Removed, Added, Changed and Comment beside the corresponding rows. The nine-to-ten change has both old and new text. Desktop columns are readable; status words are judged from text, not colour. No speech was observed. |
| 6. Names/order snapshot | PASS: seven named stops: skip, four files, old-map and departure; no unnamed stop; `unlabelled_controls` is 0. Both focused-after-steps values are null. Focus, real keys and trapping NOT RUN. |
| 7. Phone content / geometry | Required content signals present: `phone_text_differs: false`, non-blank phone image, neither overflow value true. No overlap seen in the visible unclipped area. Phone-fit geometry NOT RUN / uncertain: both overflow values null, phone right edge visibly cuts IDs, index text, comments and Head text. These signals do not establish phone usability. |
| 8. Zoom | NOT RUN: viewer provides no zoom action. |
| 9. Row speech | NOT RUN: viewer speaks nothing. |
| 10. File speech | NOT RUN: viewer speaks nothing. |

Outcome: **limited rendered-content inspection pass under the current TRIAL.md**.
This is not a full try or an editor/download/application trial. It does not
establish phone fit, real keyboard interaction, zoom or screen-reader speech.
No project-done action was submitted; the journal still names the broader
Milestone 2 acceptance, and the true-phone-viewer capability need remains open.

Worth: the desktop page is useful because a reviewer can compare a change and
read its open and resolved anchored comments without a forge account. I could
understand the renamed file and both comment placements. The phone crop is the
point at which I would stop reviewing: the right-hand change is incomplete in
the image. Duplicate full commit IDs also make the identity block harder to scan.
These are observations, not a claim that the page caused the viewer crop.
