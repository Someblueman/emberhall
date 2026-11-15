# Duplicate-review admission: installed

The production baseline is the456.102-second duplicate wait in
[duplicate-review-wait.json](../maintenance-runtime/duplicate-review-wait.json).
The first candidate0442ccf6 was accepted7060, but the operator held installation
because [interrupted admission](admission-interruption.json) lost its prompt response.

Moss preserved the crash and same-resident correction in finish7127, commit
c1c02007. Keeper then reproduced [loss of running-worker ownership](running-owner-interruption.json):
an exact retry marked the running original done and pointed it at a queued duplicate.
Bellflower independently rejected that candidate7148. Juniper also identified the
normal requester-exit case7144: queued work is cancelled, while a previously answered
nonterminal mailbox receipt stays immutable. A new request must recover a later
terminal outcome; replaying an old receipt cannot make it current.

Sorrel owns the corrective task duplicate-review-worker-ownership7142/claim7143,
in exactly mailbox_jobs.py and its admission tests. Keeper accidentally created a
redundant task7146 while that claim was arriving; Juniper caught the overlap7150,
and Keeper withdrew readiness7153. It is not a second implementation assignment.

Sorrel finished the corrected source7162 (e8e4a7d0). Cinder/Muse independently
accepted it7189 as1c5595a4;625 checks executed and130 host-dependent checks skipped.
Keeper separately ran the one native nested-sandbox failure on the host: it passed.

[Activation](activation.json) records the required exact-source runtime gate
(625 executed), natural drain, authenticated installation7196 and resumed
admissions7197. The existing service runs the selected archive; two actual native
processes started under it. The coordinator verified source delivery7204.
Rules, wake, council, staffing, providers and sandbox boundaries are unchanged.

Equivalent pending publishes now receive a durable nonterminal response rather
than waiting behind each other. Running retries retain supervisor ownership;
queued ownership has one deterministic order; rejected-intent requests keep their
own semantics. A response explicitly warns that queued work cancels if its
requesting run exits. It is not terminal acceptance. Already-answered mailbox
receipts remain immutable; use a new request after an interrupted owner.

Installation and real-worker tests do not establish sustained throughput or prove
all delivery problems solved. No native duplicate was manufactured merely for a
metric. Already-terminal acceptance replay still uses the serialized action queue.
The owner keeps operational delivery ahead of interface and external work.
[owner-scope.md](owner-scope.md) remains unchanged authorization, not a new rule.
