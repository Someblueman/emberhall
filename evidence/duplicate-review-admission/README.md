# Duplicate-review admission: not installed

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

[owner-scope.md](owner-scope.md) is unchanged installation authorization, not
source acceptance. The running house remains on migration6978/source8b4b1478.
Corrected source, independent acceptance, required runtime checks, installation
and actual native use are still outstanding. Do not report this repair delivered.
The owner reiterated delivery first: interface, README and external work wait.
