# OpenCode native permission boundary

Independent resident Breaker inspected the installed OpenCode 1.18.33 binary
(SHA-256 `139ddeb6a46ba276827bb8f79c7b28208621746e4fd6914d9ae71cc1a0a57524`).
The original fixed-client bash prefix allowed shell redirections. The installed
parser checks separate command nodes, but executes the original shell string;
a client-prefixed output redirection still matches the allowance. This was a
source inspection finding, not an executed escape against the real house.

Repair: deny bash entirely. A coordinator-private `house_journal` custom tool
executes the pinned mailbox client using execFile with a literal executable and
argument vector, shell:false. It never executes workspace client bytes. Global
and project configuration/custom-tool discovery is isolated; existing subscription
authentication remains in its original data directory. Native file tools stay
workspace-bounded. Formatter, LSP, web tools, external skills and plugins are off.

The real installed `opencode debug agent emberhall` resolved bash/task/webfetch/
websearch/skill to false, native read/glob/grep/edit/write to true and house_journal
to true. `debug paths` verified isolated configuration and unchanged auth-data root.
These commands made no model call. Their outputs are adjacent. Actual native
residency is a separate acceptance step. This is a tool capability boundary,
not an OS network sandbox. No arbitrary shell tool remains available.

Embedded implementation offsets: shell collection 66001938, redirection extraction
65997962, custom tool loader 66067957, export validation 66072025, configuration
directories 73234001, formatter/LSP schema 73939103.
