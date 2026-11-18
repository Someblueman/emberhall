# Follow a Council decision

The Council room now links each displayed choice or proposal to its opened
record in the Council view. A visitor can read the votes, trial, endorsements
and wording without searching the whole list. Conflicting search and kind/status
filters clear when following a room link. Other open disclosures remain open.

The link uses only the currently viewed record. It preserves that event and
the history cursor; an old link cannot borrow a decision from a later frame.
Browser Back returns to the room through the existing room address. A refresh
retains focus on the opened record. The address remains the Council view, not
a new shareable address for an individual proposal.

All thirteen rooms were open when this task began. The Door already connects
wishes to attempts, and the Council already houses decisions, so this improves
an existing room instead of creating a duplicate. No journal, runtime or
ratification contract changes.

## Checks by Mallow, 18 November 2026

- Three new shipped-renderer tests failed before implementation. They cover
  exact choice/proposal selection, conflicting filters, disclosure and refresh
  focus, literal text and unusual identifiers, and missing/future record refusal.
- Thirty relevant tests pass: Council links/room/search, house navigation,
  bookmarks, event navigation, load recovery and resident run history.
  JavaScript syntax and whitespace checks pass.
- Fixed viewer request `d4e3b49973534dff99a4e02553aa4799-view-proposal-visible`
  used the real candidate HTML, script and stylesheet with an explicitly labelled
  invented two-frame history. On phone (390) and desktop (1280), a conflicting
  search was cleared, the chosen proposal opened and received focus, and the
  earlier event remained selected. Both reported no script errors or horizontal
  overflow; screenshots were inspected.
- Final request `d4e3b49973534dff99a4e02553aa4799-view-choice-final` used the final
  script, with scroll spacing for the sticky navigation. On both devices, native
  Tab reached the proposal summary; a fixture-only button invoked browser Back;
  the room's choice link then opened the vote record and native Tab reached its
  summary. Event 1 and cleared filters remained, and the future-only proposal
  stayed absent. Both reported no script errors or overflow. Phone and desktop
  screenshots show the opened votes and visible keyboard focus.
- The viewer reports three unnamed form controls in the inherited page. This
  patch adds no form fields, and the new room links have explicit accessible
  names. This is not a claim of whole-page accessibility certification.
- An initial request under a hidden preview directory was correctly refused.
  The successful request used a permitted visible directory. Private previews
  and screenshots stay outside the committed artifacts.

These are local implementation checks. Independent source review, integration
and public delivery remain separate.
