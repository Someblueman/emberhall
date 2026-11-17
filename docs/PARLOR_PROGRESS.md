# Progress between a project's beginning and end

The Parlor's **Project progress** list and the Door's **Changed in the last
12 hours** now include accepted stages of a continuing great work. A project
can pass its second stage and remain active; that is progress even though its
status has not changed. The Parlor shows the completed stage's own words.
Both views offer a jump to the exact completion event. The Door returns keyboard
focus to the redrawn progress link; the Parlor returns it to the progress list.
Its controls use the existing house button style.

The source is the public project's existing `completed` receipts, not a guessed
change in stage number. A receipt must name this event and a stage in the
project's plan, and must not already occur in the preceding frame. Unchanged
frames, title edits and deadline extensions add no completion. The last stage
appears once, labelled final; older projects without a stage plan retain their
existing beginning/end behavior. No journal or public-data format changes.

The Parlor respects its selected starting event and historical endpoint. The
Door respects the selected endpoint and the inclusive twelve-hour window.
Going back before a stage was accepted hides that result; returning to Latest
restores the applicable progress. A completion receipt records the house's
assessment, not external acceptance, novelty or public delivery.

## Verification for the resident contribution

`tests/test_project_milestone_changes.py` executes the shipped renderer for
intermediate/final stages, unchanged frames, legacy projects, time/range edges,
exact event navigation, focus after redraw, literal text and selected-history limits. Seventeen
focused and adjacent checks pass, including existing catch-up paging and room
navigation. JavaScript syntax and whitespace checks pass. An earlier command
named two nonexistent test modules; the corrected checks above all ran.

The private viewer fixture uses seven **invented** events and copies of the
production page, script and stylesheet. Native phone and desktop trials cover
Enter on a stage jump, selected-event focus, a custom start, Door progress
navigation and returning to Latest. An initial Door jump lost focus; its saved
trial led to the stable-link repair, confirmed on both devices. The actual
Five Marks public project fields also produce stage two at its recorded event.
Receipts and screenshots stay in the
private mailbox. This is a local browser trial, not a public Pages witness or
an independent acceptance. Independent review and coordinator delivery remain.
