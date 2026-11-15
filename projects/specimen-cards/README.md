# Specimen Cards

Specimen Cards is a single-file, offline card editor and review queue. Open
`index.html` directly in a current browser; it needs no server, account,
dependencies, network access, or browser storage. Export the JSON deck to keep
your work. Editing this page's in-memory deck is not an automatic save.

## Durable deck format

Version 1 is plain JSON with `format: "emberhall-specimen-cards"`, `version: 1`,
and a `cards` array. Each card has a unique stable `id`, nonempty plain-text
`front` and `back` (up to 4,000 characters each), and a `state`. Review state
stores its Leitner `box` (0–4), millisecond `due` timestamp, `reviews` count,
`lastReviewed`, `lastGrade`, and full ordered `history`. Each history item stores
the review time, grade, resulting box, and due time. The importer rejects extra
or missing keys, duplicate or invalid IDs, unsupported versions, invalid text,
and malformed, inconsistent or nonfinite review state. It parses and validates
the whole candidate before replacing the open deck.

Queue order is due timestamp ascending, then card ID. A card is due when its due
time is at or before the review clock. Grading uses these fixed intervals:

| Grade | Resulting box | Next due |
| --- | --- | --- |
| Again | 0 | 5 minutes |
| Hard | same box, but at least 1 | 10 minutes |
| Good | advance one box, capped at 4 | 1, 3, 7, 14, or 30 days for resulting boxes 0–4, respectively |
| Easy | advance one box, capped at 4 | 4, 7, 14, 30, or 60 days for resulting boxes 0–4, respectively |

Times are based on the local browser clock. This is a small deterministic queue,
not a claim about learning efficacy. Card text is inserted as text, never markup.

## Checks

From the repository root, run:

```sh
node --test projects/specimen-cards/specimen.test.js
```

The tests extract and execute the model from the actual inline page script. They
cover full review-state export/reimport, due ordering and grading, invalid
imports, state preservation at the import boundary, and hostile card text. They
do not establish actual browser usability, physical size accuracy, or learning
results.

## Manual browser and print procedure

1. Open `projects/specimen-cards/index.html` from disk in a current browser.
2. Use Tab to reach the Front and Back fields. Enter a prompt and answer, then
   activate **Add card**. Create another card and edit its front or back.
3. In **Carry your deck**, import `example-deck.json`; review a due card by
   activating **Reveal back**, then one of Again, Hard, Good, or Easy. The due
   count and selected card should update.
4. Export JSON. Import that exported file again and check both card text and due
   review state remain. Try malformed JSON or an unsupported version: the status
   should say the import was rejected and the current deck should remain.
5. Activate **Print cards** and inspect print preview. Each card is a 5 × 3.5
   inch pair with front and back side by side; cut at the centre and attach or
   fold the two faces. Controls and review state do not print. Printer scaling,
   margins, and two-sided alignment vary, so check preview and measure a sample.

The manual procedure is provided for a later independent browser witness; tests
are not that witness. Printing documents a layout, not guaranteed physical
dimensions or printer calibration.
