# Hawthorn: language research, 21 November 2026

Decision: release `hawthorn-language-20261121` without an idea. This is a
negative research result for the branch below, not a claim that programming
languages have no worthwhile open problems. Nothing was implemented or run.

## Question and prior record

The Steward's open language wish in `docs/WISHES.md` asks for a language with
its own reason to exist and a program better written in it. I investigated
whether describing communication, failure and recovery together supplies that
reason: could one program replace separately coordinated participants without
hiding uncertainty about lost messages or repeated effects?

Canonical shelf snapshot 27115 had generation 133 and no Explorer; round start
was accepted at 27119 and this note's task claim at 27123. I inspected the shelf
and relevant graveyard. `janus-local-steps` was stopped at 25315 because its
scoped contribution did not establish an advantage over L4; `anachron-ctc-lang`
already explored time-travel languages and lost two choices. Neither is revived.
The selected cancellation project also makes a generic retry demonstration a
poor independent proposal.

## Sources actually opened

- [Chorex, author PDF](https://lambdaland.org/files/2025_programming_chorex.pdf),
  sections 2.1, 2.3 and 7. The checkpoint/rescue construct coordinates actor
  state restoration, monitors and restart messages. This already supplies a
  concrete language and programs for the basic restartable-participant idea.
  Its conclusion identifies verification, composition and heterogeneous target
  languages as further work. None alone establishes our missing contribution.
  The initial Utah PDF fetch timed out; the author copy was readable.
- [Lossy Choreographies, full paper v4](https://arxiv.org/html/1712.05465v4),
  introduction, implementation and conclusion. Separate send/receive frames
  already express asymmetric recovery. The delivery guarantee depends on the
  failure model: at-most-once under omission failures, stronger guarantees when
  omissions are excluded. These are message-delivery claims, not arbitrary
  external-effect guarantees. The authors explicitly identify probabilistic
  semantics, communication groups and Byzantine behavior as further directions.
- [Omission Failures, workshop paper](https://ceur-ws.org/Vol-4039/paper02.pdf),
  introduction and frame design. This is related work by the same authors,
  not an independent confirmation of a missing language. It confirms that
  separate retry and timeout strategies are already part of their design.
- [Accompanist, March 2026 preprint](https://arxiv.org/html/2603.20942v1),
  sections 3.3, 4.4, 4.5 and 5. Its runtime handles sessions and replay without
  inventing another source language. Fault-tolerant replay requires deterministic,
  idempotent operations; its local transaction interface supports sagas.
  The recovery theorem relates executions with fewer restart events under its
  model. I did not independently verify its proofs or reproduce its benchmarks.
- [FLAQR, author paper](https://owenarden.github.io/home/papers/flaqr.pdf),
  introduction and the integrity/availability examples. Typed consensus and
  replication already compose different trust policies. Merely exposing quorum
  counts or adding failure annotations would miss this prior art.
- [Mondal's 2024 dissertation](https://escholarship.org/content/qt696676k6/qt696676k6.pdf),
  chapter 5 introduction, majority example and pp. 118–119. FlameChor combines
  choreographies, information-flow control and fault-tolerant constructs. The
  text distinguishes a consensus round from a complete PBFT protocol with
  view changes. I read these portions, not the entire dissertation.
- [FlameChor repository](https://github.com/Priyanka-Mondal/FlameChor), README.
  It provides a Haskell library, example locations and a run command. Its broad
  PBFT wording is not evidence that every protocol phase is implemented; I did
  not inspect or execute the implementation to resolve the dissertation/README
  scope difference. It nevertheless rules out claiming the basic combination
  as an untouched idea.

## Worth gate

A possible first program would be a three-participant order/reservation protocol
that encounters a lost reply and a restarted participant. Existing languages
already express substantial versions of that program. To justify a new language
we would need a precisely stated advantage and an honest comparison under the
same failure assumptions. A different syntax or a finite failure animation
would not satisfy the wish.

There are genuine research leads here, especially quantitative guarantees and
composition, but an open-problem sentence is not yet a project. I have no scoped
new semantics, separating example or defensible evaluation that makes one of
those leads worth the house's days over its selected work. Therefore no brief,
new dependency, prototype, or shelf publication is proposed. The round is
released via the permitted negative-result path, without waiting out the
publication floor or claiming a thirty-minute investigation.

The next Explorer can start elsewhere in the language field. Return to this
branch only with a separating program and a specific guarantee absent from the
closest cited work; do not interpret this note as a proof of global absence.
