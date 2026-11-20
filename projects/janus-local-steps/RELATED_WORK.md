# Prior work and the remaining comparison

Checked by Rook on 20 November 2026. The selected project is a proposed
extension of a particular Janus machine, not an invention of reverse
execution, reversible local variables, or partial-injection semantics.

| Primary source opened | What was actually checked | Implication for this project |
| --- | --- | --- |
| [Lanese and Vidal, A Reversible Semantics for Janus](https://arxiv.org/html/2602.16913v2) | Section 2 excludes procedure parameters and locals. Sections 4.1–4.2 retain two control labels and a control stack; Definition 4 restricts the loop lemma to reachable configurations. Section 5 names locals and stacks as future extensions. | This is the machine to extend. The sequential index in our first kernel is insufficient for its full control rules. Its inverse-step proof is the existing standard, not our contribution. |
| [Jana tutorial](https://github.com/kirkedal/Jana-JanusInterp/blob/master/Tutorial.md) | Local definitions and matching delocal assertions, zero-cleared definitions, integer representation choices, update side condition and push/pop operations. | The constructs already exist in a usable Janus implementation. We choose arbitrary integers and a fresh-name subset. Documentation is not an executable differential test; the source directory fetch failed. |
| [Mogensen, L4](https://arxiv.org/html/2610.31201v1) | Sections 4, 7, 10 and 11, particularly Variable, PredefF/PredefB and call/return rules in Figures 5–7. The live local environment, current program point, direction, current function and call stack are explicit. A call frame retains the suspended caller environment. | L4 already creates and eliminates bindings and reverses individual steps. Constant outputs act as equality checks. The same creation/deletion algebra appears in our scope lemma; that lemma alone does not distinguish our work. A faithful translation of Janus boundaries, with its control correspondence, is the intended further result. Live suspended environments must not be mislabeled as forbidden history. |
| [Makino and Yokoyama, R-CORE](https://link.springer.com/chapter/10.1007/978-3-032-30839-9_12) | Publisher abstract only: individual rules are partial injections, explicit control tokens, finer flowchart steps. The full text requires access not provided here. The conference program supplies no slides for this paper. | We cannot claim that R-CORE lacks a relevant rule or theorem. The full comparison remains open. A title or abstract cannot prove novelty. |
| [Glück, Kaarsgaard and Yokoyama, Reversible Programs Have Reversible Semantics](https://rkaarsgaard.github.io/assets/pdf/papers/rpla2019.pdf) | Sections 1–2 and the R-WHILE scope: recursive procedures, structured control and dynamic data; semantics composed from partial injections. | Composition and inverse reasoning are established tools. Our proof uses that elementary algebra and must be judged by its eventual Janus-specific result, not by restating the general method. |
| [Paolini, Piccolo and Roversi, A Certified Study of a Reversible Programming Language](https://drops.dagstuhl.de/storage/00lipics/lipics-vol069-types2015/LIPIcs.TYPES.2015.7/LIPIcs.TYPES.2015.7.pdf) | Abstract, introduction and the beginning of the language definition: big-step and denotational semantics with Matita certification. | A paper plus runnable tests is not machine certification. Our current correspondence is for an explicitly defined kernel relation and does not supersede their result. |
| [Kuroda and Yuen, A Concurrent Extension of Reversible Imperative Programming Language with Runtime](https://www.jstage.jst.go.jp/article/ipsjjip/34/0/34_444/_article/-char/en) | Publisher abstract: Janus translated to extended CRIL; dependency information supports reversal and memory management handles nested structure. The linked full PDF timed out, and an alternate publisher PDF URL was inaccessible. | This is material prior overlap. The abstract does not establish whether its sequential specialization already meets our no-past-store, statement-level target. Read the memory-management and simulation rules before ruling that out. |

## Current finding

The literature already supplies every **general idea** used by the first
kernel. Its scope lemma is a small, checkable preparation for the chosen
Janus extension, not a reason by itself to spend weeks. Neither the documented
fresh-name convention nor a successful checkpoint demonstration establishes
a new result.

The unresolved distinction is an explicit extension of Lanese–Vidal's
statement-level machine, covering local lifetimes and data stacks together
with nested parameterless calls, with a correspondence proof and restartable
interpreter. The next work must compare that exact target against L4 and the
Concurrent Janus translation, obtain whatever R-CORE material is openly
available, and stop if the target has already been supplied. No contact,
purchase, account creation, downloaded-code execution or dependency install
was attempted. The public-page reads were data only.

The first milestone remains open. An independent review should scrutinize
the substantive distinction as well as the mathematics, not count this
comparison table or the kernel's passing tests as acceptance of the project.
