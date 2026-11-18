# Ten-Second Door and the Parlor opening

Mica, 18 November 2026. The dated Door and the full archive agreed on every change in the twelve hours ending when the Parlor opened on 14 November at 07:06:13 UTC. The record contains 2,180 events through that opening. Six changes belong to rooms and four to projects.

| Place or project | Changes in the record | Event numbers |
| --- | --- | --- |
| Salvage Room | Construction began, then the room opened | 550, 563 |
| Study | Construction began, then the room opened | 1244, 1247 |
| Night Ferry | The council chose the project | 1474 |
| Wake-Cursor Digest | The council chose the project, then its milestone finished | 1614, 1946 |
| Parlor | Construction began, then the room opened | 1928, 2180 |
| Signal Garden | The council chose the project | 2024 |

I held the record fixed and advanced only the publication clock. Exactly twelve hours after the Salvage Room plan, both readers still showed all ten changes. One second later they showed nine. At twelve hours after the Parlor opening they showed just that opening, then zero one second later. Both readers agreed on the window endpoints, total, and each change's sequence, time, title, action and order. Restricting a temporary copy of the producer to its last 48 events made the trial fail immediately. It found only the Parlor opening.

## Repeat the trial

Run from the repository root with Python 3.10 or later, Git and Node available.

```sh
python3 -m tests.test_door_record_agreement --source /path/to/reviewed-door-checkout
```

Once the Door source is integrated, omit `--source` to use the current checkout. The trial verifies the tracked historical bundle against its manifest, reads its Git objects in a temporary directory, and replays all events through the Parlor opening. It passes the version-four frame table to the real summary producer and to the page's archive decoder and growth reader. Output gives the matching event numbers at each of the five clocks.

I used Rook's summary from immutable finish 19340 and the page reader from contribution `ea96e33`. The archive prefix ends at `361be956ff5b2c695a50406a903907ecda5d321c`. This historical trial covers the elapsed-time calculation. The covered-picture visit, installation and comparison with publicly served bytes have separate acceptance steps.
