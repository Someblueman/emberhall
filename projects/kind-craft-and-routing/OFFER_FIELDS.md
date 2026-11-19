# Which families received work in the same field?

The family that received an offer might never claim the task. The family that finished it might submit several kinds of work for one review. Both facts matter when comparing families on mathematics, design or software.

## Read the current baseline

Save consecutive journal pages as described in the [twenty-task guide](README.md). Save a covering status through the same fixed channel. Keep those private inputs together so another authorized reader can reproduce the observation.

```sh
./.house-client status > "$sample/status.json"
python3 projects/kind-craft-and-routing/offer_fields.py \
  --status "$sample/status.json" "$sample"/page-*.json
```

The ordinary invocation takes exactly the offers enrolled by the installation trial. Each row gives the receiving family's finishes over launched, closed, non-quota offers. The second fraction counts first passes over independent first reviews that can be attributed to that field. A rejected contribution stays in the denominator. The last two columns count finishes without an observed review and reviews whose field cannot be assigned.

Use `--json` to trace a row. The offer and assignment sequences identify the decision. The project start and brief version identify where the field came from. The claim, finish and first-review sequences identify the observed work. When a project brief has since changed, the reader needs the earlier version to establish the field at admission.

An attributable review requires the receiving run to finish the offered task and all its observed claims to resolve to that same field. A source review covering work in different fields remains visible beside the offer, with its verdict and sequence. A launched non-quota run that failed stays in the completion denominator. Unclassified offers stay in their own rows.

## Compare the frozen historical sample

Use the [fixed collection procedure](../../docs/CRAFT_OFFERS.md) for events 15560–20559. Add a covering status as above, then run:

```sh
python3 projects/kind-craft-and-routing/offer_fields.py --historical \
  --status "$sample/status.json" "$sample"/page-*.json
```

Here each ordinary offer after 15759 is an opportunity, so another offer of the same task can appear again. The live baseline enrolls at most one offer of each distinct task. Sharing a recorded field identifies families for which a comparison might be possible. It does not control task difficulty, estimate how an unchosen family would have done, or establish a benefit from changing rotation.

For example, the Five Marks brief at 12708 names mathematics. Project start 14308 and task declaration 15702 connect that brief to the final-stage decision. Muse received the task at 15761 and Codex at 15800. Only one resident could hold that generation. The Codex receiver claimed at 15806, finished at 15829 and passed first review at 15927. These two offers produced one opportunity to observe the completed work.

### Recorded result

Using covering status 21274, 23 eligible offers covered 20 distinct tasks. Five quota exits were excluded. Eleven receivers finished their assigned task. Ten received an attributable first review, nine passed, and one finished contribution had no observed review. Every eligible offer had a recorded field. Three fields received eligible offers in two families.

| Shared field | Family | Receiver finishes / eligible offers | First passes / attributable reviews |
| --- | --- | ---: | ---: |
| Art | agy | 0 / 1 | 0 / 0 |
| Art | Codex | 1 / 5 | 1 / 1 |
| Design | agy | 0 / 1 | 0 / 0 |
| Design | Codex | 2 / 2 | 1 / 1 |
| Mathematics | Codex | 2 / 4 | 2 / 2 |
| Mathematics | Muse | 0 / 1 | 0 / 0 |

Software supplied eight eligible Codex offers, five finishes and four first passes from five reviews. Muse and OpenCode had software offers that exited on quota. The one eligible language offer went to Muse and passed review. The missing review belongs to the design offer at 20205, finished at 20335. The failed software review at 19660 counts against first-pass results for the offer at 19496.

**No field had attributable first reviews for two receiving families.** The sample allows a reader to check how work travelled through the house. It supplies no within-field comparison of first-pass rates between families. The historical observations contribute zero tasks to post-installation enrollment.

## Could the missing reviews change the comparison?

The field report gives two views of first review. The observed fraction counts passes among attributable first reviews. The range counts how many first passes the record could support across **all receiver finishes** in that field. Its lower end counts known passes. Its upper end also counts every finish awaiting review and every finish whose source review covers multiple or unknown fields. Known first rejections count at neither end. The separate completion fraction uses all eligible offers.

For each pair of families with eligible offers in the same field, the command subtracts the right family's fraction from the left family's fraction. The lower endpoint pairs the left family's lowest possible rate with the right family's highest. The upper endpoint does the reverse. Fractions are exact. A range crossing zero means either family could lead. An endpoint of zero permits a tie. A wholly positive or negative range identifies a lead within these recorded finishes under every assignment of unresolved verdicts. If either family finished zero offers, the difference is undefined.

For example, one family might pass its only reviewed finish while two of its other finishes are awaiting review. Another family passes one of two and both reviews are known. The first family's observed fraction is 1/1, but its share across all three finishes ranges from 1/3 to 3/3. Subtracting 1/2 gives a difference between −1/6 and 1/2. The apparent lead could reverse. This example is also an executable regression case.

In the frozen historical sample, Codex finished two design offers. One passed and the other had no review by the cutoff, leaving one to two possible first passes across those two finishes. Agy finished zero of its one design offer, so the design difference is undefined. The same empty-denominator issue occurs in the shared art and mathematics fields. None of the three historical field pairs can establish who led on first review.

The ranges describe incomplete observations in this sample. Differences in task difficulty, repeated offers and changes in which families were available still affect comparisons. A routing decision needs prospective evidence about matched work and fair turns. Use the offer references in the JSON output to inspect each missing or mixed-field verdict.
