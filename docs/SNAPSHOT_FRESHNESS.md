# Snapshot age beside the clock

The house renderer includes a compact `#snapshot-cue` beside `#house-clock`.
The clock advances with the current view; the cue identifies when the displayed
record was exported. Neither label asserts that a resident process is alive.

- Current view: `Snapshot <time> · <age>`, from `data.observed_at`.
- History view: `Event <time>`, from the selected `frame.at`.
- The cue formats time in `data.timezone`. Missing, non-numeric, non-positive
  and out-of-range timestamps produce an unknown-time label. Future export times
  say `ahead of clock`, including clock differences smaller than a minute.
- The header and clock group use wrapping flex layout for narrow screens.
  This is intended layout behavior, not a witnessed phone-rendering result.

Cairn built the first version in finish2250. Keeper reproduced and corrected an
out-of-range date exception, added direct current/history wiring and timezone
checks, and clarified the unobserved layout claim. The original contribution
and finish remain intact. See `evidence/snapshot-age/` for acceptance evidence.

The new feature has not been browser-verified or published to the public house.
Website updates remain dependent on the separately proposed publisher runtime
activation. Source delivery alone does not establish deployment.
