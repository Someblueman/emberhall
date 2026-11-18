# Lethe: the ferry admission experiment

Hawthorn, 18 November 2026. Project `great-lethe-20261117`, first
milestone; task `lethe-admission-semantics`.

**Recommendation: do not admit this core to runtime construction.** The
candidate has a precise safety contract, but the ordinary Rust comparison
expresses the same contract under the same trusted-runner assumptions. I
have not established the required combined safety or clarity advantage.
Recommend dropping the present project scope rather than adding features
to rescue this gate. An independent resident must reconstruct this finding;
the project owner makes the separate milestone/drop decision.

This is a bounded negative result about the core below. It is not a theorem
that no useful language about forgetting can exist, nor evidence that a
ready-made Rust/AWS integration already supplies the whole contract.

The example books one fictional ferry ticket. A temporary departure-board
message disappears on restart. An order and its booking arguments persist.
If a sale might already have happened, the program can inspect or wait;
it cannot buy another ticket. Sometimes waiting forever is the only safe
answer. No real service, account, payment or network is used.

- [The complete candidate program](ferry.lethe) has an explicit recovery
  entry and all three outcomes. It is a specification, not executable syntax.
- [Semantics and crash table](SEMANTICS.md) define what the words mean,
  every modeled boundary, the assumptions and the small safety argument.
- [Comparison and admission finding](COMPARISON.md) put the same ferry
  beside Modal Crash Types, AWS's interrupted-action interface and a typed
  Rust encoding. They distinguish source facts from this experiment.
- [Ordinary Rust comparison](comparison.rs) checks the sealed control
  interface and exact identity validation. It has no storage or service
  implementation and cannot prove disk durability.

Run the local comparison from the repository root (Rust 2024 edition;
tested with `rustc 1.97.1`):

```sh
rustc --edition=2024 --test projects/lethe/comparison.rs -o /tmp/lethe-comparison
/tmp/lethe-comparison
rustfmt --edition 2024 --check projects/lethe/comparison.rs
```

The following are deliberately invalid clients. Each compilation must fail
for the named reason, not merely for a warning. Output files stay outside
the repository.

```sh
rustc --edition=2024 --crate-type=lib --cfg retry_pending projects/lethe/comparison.rs -o /tmp/lethe-invalid.rlib
rustc --edition=2024 --crate-type=lib --cfg forget_scope projects/lethe/comparison.rs -o /tmp/lethe-invalid.rlib
rustc --edition=2024 --crate-type=lib --cfg forge_ticket projects/lethe/comparison.rs -o /tmp/lethe-invalid.rlib
```

Expected errors: `Pending` is not `Ready`; `bulletin` is absent from the
recovery scope; a ticket's fields are private. The positive build uses
`--test` because this is a comparison artifact, not an application binary.

No code from a web page was downloaded or executed, and no dependency was
added. These checks test a finite specification and compiler boundaries.
They do not test the proposed language checker, an AWS SDK, a real crash,
an on-disk journal, external exactly-once execution or visitor experience.
