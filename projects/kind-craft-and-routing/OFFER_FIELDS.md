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
