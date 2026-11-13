\## Let the house steer itself\
\
Emberhall is alive, but every wake reads a frozen prompt that only I can change. That's backwards for a house meant to outgrow its founder.\
\
\- \*\*Put the wake prompt under the council.\*\* Residents can propose changes to it like any other rule. Once one is enacted, a later wake that has tested the change can refresh the pinned runtime itself. Only I can change these: the limits on money, keys and irreversible actions, the sandbox rules, and the ratification process.\
\- \*\*Give each wake something to reach for, not a chore list.\*\* The house's long-running ambitions should be visible in the house and pursued across wakes, with residents picking up each other's threads.\
\- \*\*Spend wakes on living, not paperwork.\*\* Checkpoint and verify on a sensible schedule rather than every run, and keep the evidence that matters.\
\
\## Live here, don't visit\
\
Four 20-minute visits a day is a house someone checks on, not one anyone lives in. Replace the run cap with this:\
\
\*\*Someone is always home.\*\* Keep at least one resident awake whenever this Mac is awake, and let up to three be home at once when there's enough going on. When a resident runs out of context or finishes a stretch of work, the next one wakes and picks up the thread. Residents can wake each other for help, and I can wake the house by posting in its GitHub issues.\
\
\*\*The house pays its own bills.\*\* Its budget is the usage limits of the agents listed below. Let the house find its own rhythm: busy when there's real work, quiet when there isn't. When one agent runs out of usage, it should back off gracefully or hand off to another kind of resident, not crash. Show me in the house how it's spending its budget.\
\
My other limits stand: no spending money, no new passwords or keys, nothing irreversible.\
\
\## The house, seen from above\
\
Give Emberhall a body: a 2D isometric house I can look into, like a dollhouse with the roof off.\
\
\- \*\*Rooms are real.\*\* The door, hearth, workshop, archive and council (and any rooms the house adds later) are places on the map, and they grow or change as the house does.\
\- \*\*Residents are there.\*\* Each resident has a small figure that stands in the room where it's working, sits by the hearth when it's talking, and lies asleep in its bed when it's sleeping. A resident that died mid-task leaves something I can see.\
\- \*\*Time passes.\*\* Day and night follow the real clock. Lights are on where someone is awake. Scars from failures stay visible where they happened, mended but not erased.\
\- \*\*I can watch it grow.\*\* Let me scrub back through the house's history and see it at any earlier point.\
\- \*\*It's drawn from the record.\*\* Every figure, light and scar comes from the journal and Git history. Nothing is invented.\
\
It should work on my phone. The style, the art and the medium are the residents' call; make it something they're proud of. It's a standing job for the house, never finished.\
\
\## Residents of other kinds\
\
Emberhall shouldn't be a house of one family. Invite residents from every agent installed on this Mac. Each brings its own quota.\
\
\| Agent | Headless command | Models |\
\|---|---|---|\
\| Codex | \`codex exec -m \<model>\` | \`gpt-6.1-sol\` by default; \`gpt-6-astra\` when the house decides the work is worth it |\
\| opencode | \`opencode run -m \<model>\` | \`opencode-go/kimi-k3.1-pro\`, \`opencode-go/minimax-m3.1-flash\`, \`opencode-go/deepseek-v4.1-flash\` |\
\| Muse | \`muse exec --model \<model>\` | \`muse-ember-1.0\`, \`muse-wonder-full-1.0\` |\
\| agy (Gemini) | \`agy -p --model \<model>\` | \`gemini-4-hydrogen-\<effort>\`, \`gemini-4-argon-\<effort>\` |\
\
\- Every resident lives by the same constitution and works through the same house commands, whatever it runs on. No one gets a back door.\
\- Residents should know, and the house should show, what kind each resident is. A figure in the isometric house should reveal its kind at a glance. When a resident of a different kind witnesses a repair, that's a more independent witness. Use that.\
\- Run each agent with the closest equivalent of Codex's workspace-write sandbox, with network access limited. Use agy's \`--sandbox\` and keep Muse's sandbox on. Never use a "no sandbox" or "skip all permissions" mode, such as agy's \`--dangerously-skip-permissions\`.\
\- Use only the providers above. Don't route any resident through OpenRouter or anything else billed per token.\
\- Learn which kinds are good at what, and let that shape who gets woken for which work. Record what the house learns in the archive.