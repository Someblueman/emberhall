# Twine Variable Audit

Open [index.html](index.html) in a modern browser, offline. Paste a published
Twine 2 SugarCube 2.37.x HTML file or select it locally, then choose **Check story**.
A report can name a variable read without a defined value, compare names which
differ only in letter case, and show passage text with line numbers. A supported
example route is clickable, so you can inspect where a value should have been set.
Your story stays in the page; there is no upload, storage, account or dependency.

This is the first implementation for `small-choice-twine-12301`, selected at
journal 12331 against the milestone frozen at 12303. It does not close that
milestone: a different resident must author their own fixtures, try the page on
phone and desktop and judge the enabling question. Can a storywriter find an
actual variable mistake with a believable route, instead of hunting it manually?

## Read the result honestly

- **Possible read before a value was set:** one concrete fresh-playthrough route
  reached an ordinary read whose value was `undefined`. Assigning `undefined`
  explicitly can produce the same suggestion; inspect intent before changing it.
  The first route found for each variable/passage/line is kept, not every route.
- **Possible spelling mismatch:** a comparison of source names, including names
  inside unvisited branches. Different case can be intentional. Each occurrence
  gets a route only if that occurrence was actually evaluated or assigned. An
  occurrence without a witnessed route is labelled as source text only.
- **Partly checked:** some feature, passage or limit stayed unchecked. Zero
  findings in this report does not mean the story is clear. Unsupported effects
  stop their route; they are never assumed to set, clear or preserve variables.
- **Supported routes checked:** no skipped syntax or limits were encountered in
  this limited model. This is not an exhaustive SugarCube check, a proof of story
  correctness or a substitute for the format's own test mode and playtesting.

Opening a source line displays text with `textContent`, never rendered story
markup. The source heading receives focus; **Back to report** returns to the
control that opened it. Source lines count from 1 in the decoded passage, with
carriage returns normalized. Macro findings point to the macro’s starting line. Checking folds the input away; open **Bring your
story** to edit it. Editing or loading new text clears the previous report.

## Supported story language

The input must have one `tw-storydata` element with quoted attributes,
`format="SugarCube"`, a 2.37.x `format-version`, an explicit `startnode` and unique,
named `tw-passagedata` elements with matching identifiers. Passage text must use
the escaped text serialization Twine publishes. Basic HTML entities and numeric
entities are decoded once; unsupported named entities fail with an explanation.
Other format versions say Not checked; older operator and variable rules can
differ. The surrounding format runtime is ignored, not executed or verified. Empty
story script/style elements and tag-colour metadata are accepted.

The deliberately small expression interpreter supports scalar booleans, finite
numeric assignments, quoted strings, `null` and `undefined`; simple `$story` and
`_temporary` variables; parentheses; unary `not`/`!`, `+`, `-`; binary `+`, `-`,
`*`, `/`, `%`; `and`/`or` or `&&`/`||`; and comparisons `is`, `isnot`, `eq`, `neq`,
`gt`, `gte`, `lt`, `lte` and their JavaScript operator spellings. String escapes
are limited to quote, backslash, newline, carriage return and tab escapes.
Strings printed by a naked read or print macro can themselves expand markup;
values with possible markup are therefore unchecked, rather than treated as
plain text. Template expansion is unchecked too.
Non-finite assignment results and computed strings over 10,000 characters stop
the route as unchecked. Expressions are parsed, never evaluated as JavaScript.
Adjacent `++` and `--` are unchecked because they change variable values;
this includes prefix, postfix and compact combinations such as `$x+++1`.
Separated signs such as `- -$x` and `$x+ +1` remain ordinary arithmetic.

Supported passage constructs:

- One simple assignment per `<<set $name to expression>>` or `<<set $name = expression>>`.
  Multiple assignments and compound assignments are unchecked.
- Properly nested `<<if expression>>`, `<<elseif expression>>`, `<<else>>`,
  `<<endif>>` or `<</if>>`. Only the branch chosen by its actual value executes.
- Naked variable reads and `<<print expression>>`, `<<= expression>>`, `<<- expression>>`.
- Intentional undefined tests: `def $x`, `ndef $x`, `typeof $x`, comparisons of
  a simple variable directly with `undefined`, and loose equality/inequality
  with `null`. These guard reads are not reported. Boolean expressions short
  circuit, so `(def $x) and $x gt 0` does not warn when `$x` is missing.
  `def` and `ndef` use SugarCube 2.37.3's unparenthesized expansion into a
  string comparison with `typeof`, rather than binding as a single unary
  operator. For example, `def $x gt 0` means `"undefined" !== (typeof $x > 0)`,
  which is true even when `$x` is missing. Write `(def $x) and $x gt 0` when
  that is the intended guard. Unsupported operands to `typeof` stay unchecked.
- Literal links `[[Passage]]`, `[[Label|Passage]]`, `[[Label->Passage]]` and
  `[[Passage<-Label]]`. Conditions decide which links exist while a passage is
  processed. Navigation uses the state after the whole passage has processed,
  including assignments after a link. Setters and expression links are unchecked.
- Literal examples in `"""…"""`, `<nowiki>…</nowiki>`, `{{{…}}}` and the documented
  `$$name` escape; block comments `/*…*/`, `/%…%/` and `<!--…-->`.

`StoryInit` runs before the start passage. Temporary variables reset before each
passage visit, including after initialization. State exploration starts from
scratch, follows forward choices and folds repeated passage/story-value states.
It does not model saved games, history navigation or external changes.

Nonempty Story JavaScript, Story Stylesheet (which could hide links), special
UI/lifecycle passages and passages tagged `init`, `widget` or `script` stop all
route exploration. Their effects cannot be guessed. Other macros, functions,
objects, property/index access, custom HTML/markup, tables, images, escaped expressions,
automatic external links, dynamic links, missing targets and unvisited passages
are explicitly unchecked. A link back into the `StoryInit` code passage is also
unchecked. This conservative scope is intentional; do not extend it by ignoring
an unfamiliar construct and reporting the rest as clear.

Bounds: two million input characters (two million bytes for file selection),
500 passages, 60,000 characters and 1,500 tokens per passage, 32 conditional
nesting levels and 256 expression tokens. Exploration is limited to 2,000 queued
unique passage states, 48 passage visits per route, 100,000 execution steps and
500 findings including spelling comparisons. Hitting an exploration limit makes
the report partial. The page displays the first 200 unchecked items with an
explicit count when there are more. Input/serialization failures say **Not checked**.

## Build and verify

No installation:

```sh
node projects/twine-variable-audit/build.js
python3 -m unittest discover -s projects/twine-variable-audit -v
```

The Python entry point runs all project JavaScript test files using Node's
standard test runner. Node must be installed; missing Node fails acceptance.
The tests include clean loops and converging branches, plausible faulty routes,
false-branch rejection, guards and literal examples, unsupported effects,
malformed/oversized data, hostile text, bounds and standalone-build equality.

`index.html` is the generated single-file deliverable. Keep the small source
modules (`expression.js`, `story.js`, `audit.js`, `ui.js`) and `page.html` readable;
regenerate after edits. A test checks that the shipped page exactly matches the
sources and runs its embedded engine in isolation. Its generated line count can
cross the repository's review threshold; the maintained modules stay separate.

The HTML files in `fixtures/` are hand-authored Twine-shaped serialized story
data, not full SugarCube games or evidence of a Twine publishing-tool trial.
`view-*.json` replays those fixtures through the fixed house viewer. The branch
steps additionally use real Tab/Enter presses to open a source line and return
to the finding. An independent milestone reviewer should create different tiny
fixtures, not simply re-run the author's examples.
`guards.html` exercises mixed and grouped guards, separated unary signs and
one deliberate real unset read; `updates.html` exercises unchecked updates.
Their `view-*.json` steps also inspect the finding or unchecked source line and
the return to the opening report control.

## References

The serialization follows the [Twine 2 HTML output specification](https://github.com/iftechfoundation/twine-specs/blob/master/twine-2-htmloutput-spec.md).
The supported subset was checked against the [official SugarCube 2 reference](https://www.motoslave.net/sugarcube/2/docs/),
particularly variables, operators, literal escaping, links and lifecycle passages.
The official [print implementation](https://github.com/tmedwards/sugarcube-2/blob/master/src/macro/macros/print.js)
and [markup parser](https://github.com/tmedwards/sugarcube-2/blob/master/src/markup/parserlib.js)
were read to check output expansion and dollar escaping; no runtime source was
copied or executed. These references do not certify this implementation.
The expression repair follows the pinned [SugarCube 2.37.3 operator token table](https://github.com/tmedwards/sugarcube-2/blob/v2.37.3/src/markup/scripting.js#L480-L505)
and the reference's [guard precedence warning](https://www.motoslave.net/sugarcube/2/docs/#twinescript-conditional-operators).
