# The Bench Was for Two

An original playable poem by Fern, Emberhall, 2026. Edie played the piano;
Nell turned the pages. Their mother left a letter under the bench lid. Give
its one loose phrase to either sister, open both envelopes, then reconsider.

Open `index.html` through a static server, or use the house page viewer. All
art, words and behavior are local; no accounts, storage, sound, network calls
or dependencies. Native radio buttons work with taps, Tab, arrow keys and
Space. Opening and moving the phrase takes focus to the resulting letters;
folding returns to the chosen envelope; reset returns to the closed bench.

This is the first encounter for `small-after-gloves-20261118`, not an
independent artistic verdict or a claim of public delivery. One loose phrase
is deliberate: two readings must earn inclusion before a second phrase is
added. No invented testimony is presented as a real family’s history.

## The reading copy

The bracketed phrase goes to exactly one sister, after her first sentence.
Both letters retain the order of the found paper. Envelope names and interface
instructions are labels, not words smuggled into the mother’s text.

**Edie**

> I sold the piano.  
> [For you.]  
> You asked me not to wait.  
> I watched the men lift it over the step.  
> One of them asked if you still played.  
> I said, whenever she can.  
> Love, Mum.

**Nell**

> I kept the bench.  
> [For you.]  
> There is a pale place where you sat.  
> I used to tell you to turn the page.  
> You always knew when.  
> I should have looked up.  
> Love, Mum.

The complete ordered paper lives in `letter.js` and is visible under “The found
paper” on the page. A line index follows every line through the division. The
only transferable words are “For you.” The two copies of “Love, Mum.” are two
separate original lines. There is no shuffle, generated sentence or deletion.

## Checks and the next judgment

Run `python3 -m unittest discover -s projects/bench-for-two -v` from the
repository root. Its small adapter runs the actual Node test file used directly
by `node --test projects/bench-for-two/letter.test.js`.
The focused checks exhaust both offered divisions, reconstruct every original
line exactly once, check each sister’s order, pin the two complete reading
copies and reject an absent or invalid choice. They cannot judge beauty.

The milestone reviewer should open and try the actual phone and desktop page,
read both pairs, move the loose phrase in both directions, fold and reset,
and follow controls by keyboard. They must name ordinary words whose meaning
changes, then say whether they want to reopen or share it. Drop for grammatical
scraps, merely moving words, or writing/drawing that does not earn a second
reading. Do not accept this because the counters and tests agree.

## Credits

Words, bench illustration and code are original to this piece. Its precedents
were researched on the selected idea shelf; no predecessor’s prose or image
is copied here. We acknowledge [Phuoc-Tan Diep’s account of cleave poetry](https://cleavepoetry.wordpress.com/what-is-cleave-poetry/)
and [Emily Short’s author statement for First Draft of the Revolution](https://lizadaly.com/first-draft/).
No new poetic form is claimed.
