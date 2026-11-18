//! Original finite Rust encoding of the ferry contract, not a storage engine.
//! `begin` represents an assumed atomic durable host transition. Nothing here
//! writes a journal, invokes a service, implements an SDK or simulates power loss.
#![cfg_attr(not(test), allow(dead_code))]

mod boundary {
    #[derive(Clone, Debug, PartialEq, Eq)]
    pub struct Binding {
        program: &'static str,
        order: u64,
        action: &'static str,
        route: &'static str,
        seats: u8,
        schema: u8,
    }

    // Data may be copied; permissions deliberately implement neither Clone nor Copy.
    pub struct Ready(Binding);
    pub struct Pending(Binding);
    pub struct Dispatch(Binding);
    pub struct Ticket {
        binding: Binding,
        number: u64,
    }
    pub struct Closed(Binding);

    pub enum Outcome {
        Done(Ticket),
        NotDone(Closed),
        Unknown(Pending),
    }

    #[derive(Debug, PartialEq, Eq)]
    pub enum Refusal {
        IdentityMismatch,
        CorruptRecord,
    }

    pub enum Restored {
        Fresh(Ready),
        Settle(Outcome),
    }

    // The trusted adapter supplies authoritative evidence; a caller's empty
    // lookup is Missing, never Closed. These are not cryptographic certificates.
    enum Evidence {
        Sold(Binding, u64),
        Closed(Binding),
        Missing,
        InFlight,
        Unavailable,
    }

    enum Record {
        Ready(Binding),
        Intent(Binding),
        Done(Binding, u64),
        Closed(Binding),
        Corrupt,
    }

    fn restore(record: Record, current: &Binding) -> Result<Restored, Refusal> {
        let saved = match &record {
            Record::Ready(b) | Record::Intent(b) | Record::Done(b, _) | Record::Closed(b) => b,
            Record::Corrupt => return Err(Refusal::CorruptRecord),
        };
        if saved != current {
            return Err(Refusal::IdentityMismatch);
        }
        Ok(match record {
            Record::Ready(b) => Restored::Fresh(Ready(b)),
            Record::Intent(b) => Restored::Settle(Outcome::Unknown(Pending(b))),
            Record::Done(b, number) => {
                Restored::Settle(Outcome::Done(Ticket { binding: b, number }))
            }
            Record::Closed(b) => Restored::Settle(Outcome::NotDone(Closed(b))),
            Record::Corrupt => unreachable!("handled before validation"),
        })
    }

    pub fn begin(ready: Ready) -> (Pending, Dispatch) {
        // Specification of the host boundary: durably commit Intent first.
        // A real implementation must not expose this pair before that commit.
        (Pending(ready.0.clone()), Dispatch(ready.0))
    }

    fn observe(pending: Pending, evidence: Evidence) -> Result<Outcome, Refusal> {
        match evidence {
            Evidence::Sold(b, number) if b == pending.0 => {
                Ok(Outcome::Done(Ticket { binding: b, number }))
            }
            Evidence::Closed(b) if b == pending.0 => Ok(Outcome::NotDone(Closed(b))),
            Evidence::Sold(_, _) | Evidence::Closed(_) => Err(Refusal::IdentityMismatch),
            Evidence::Missing | Evidence::InFlight | Evidence::Unavailable => {
                Ok(Outcome::Unknown(pending))
            }
        }
    }

    fn invoke_once(
        pending: Pending,
        permit: Dispatch,
        service: impl FnOnce(&Binding) -> Evidence,
    ) -> Result<Outcome, Refusal> {
        if pending.0 != permit.0 {
            return Err(Refusal::IdentityMismatch);
        }
        // The one call is to the assumed single-attempt host adapter. Its
        // implementation and transport are trusted, exactly as in the core.
        observe(pending, service(&permit.0))
    }

    // The host serializes these terminal tokens before displaying them.
    // A stopped client may drop a pending token, but cannot forge terminal proof.
    pub enum Exit {
        Delivered(Ticket),
        Cancelled(Closed),
        Waiting(Pending),
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        fn binding() -> Binding {
            Binding {
                program: "exact ferry program version zero",
                order: 42,
                action: "sale",
                route: "North to South",
                seats: 1,
                schema: 0,
            }
        }

        #[test]
        fn only_ready_restoration_can_begin() {
            let b = binding();
            let Restored::Fresh(ready) = restore(Record::Ready(b.clone()), &b).unwrap() else {
                panic!("ready record lost");
            };
            let (pending, dispatch) = crate::start(ready, "Board is busy".to_owned());
            assert_eq!(pending.0, dispatch.0);
            let result = invoke_once(pending, dispatch, |binding| {
                Evidence::Sold(binding.clone(), 7)
            })
            .unwrap();
            assert!(matches!(crate::settle(result), Exit::Delivered(_)));
            assert!(matches!(
                restore(Record::Intent(b.clone()), &b).unwrap(),
                Restored::Settle(Outcome::Unknown(_))
            ));
        }

        #[test]
        fn missing_in_flight_and_unavailable_preserve_the_same_pending_order() {
            let b = binding();
            let mut p = Pending(b.clone());
            for evidence in [Evidence::Missing, Evidence::InFlight, Evidence::Unavailable] {
                let Exit::Waiting(next) = crate::settle(observe(p, evidence).unwrap()) else {
                    panic!("unknown became terminal");
                };
                assert_eq!(next.0, b);
                p = next;
            }
        }

        #[test]
        fn lost_local_response_requires_authoritative_evidence() {
            let b = binding();
            // The service can already have sold, but local Intent alone says unknown.
            let Restored::Settle(Outcome::Unknown(p)) =
                restore(Record::Intent(b.clone()), &b).unwrap()
            else {
                panic!("intent invented a receipt");
            };
            let Exit::Delivered(t) =
                crate::settle(observe(p, Evidence::Sold(b.clone(), 7)).unwrap())
            else {
                panic!("matching sale lost");
            };
            assert_eq!((t.binding, t.number), (b, 7));
        }

        #[test]
        fn only_fenced_negative_evidence_can_cancel() {
            let b = binding();
            let Exit::Cancelled(c) =
                crate::settle(observe(Pending(b.clone()), Evidence::Closed(b.clone())).unwrap())
            else {
                panic!("closed result lost");
            };
            assert_eq!(c.0, b);
        }

        #[test]
        fn every_identity_component_and_corruption_refuse_restore() {
            let b = binding();
            let mut alternatives = [
                b.clone(),
                b.clone(),
                b.clone(),
                b.clone(),
                b.clone(),
                b.clone(),
            ];
            alternatives[0].program = "changed program";
            alternatives[1].order += 1;
            alternatives[2].action = "renamed sale";
            alternatives[3].route = "another route";
            alternatives[4].seats += 1;
            alternatives[5].schema += 1;
            for other in alternatives {
                assert!(matches!(
                    restore(Record::Intent(b.clone()), &other),
                    Err(Refusal::IdentityMismatch)
                ));
                assert!(matches!(
                    observe(Pending(b.clone()), Evidence::Sold(other.clone(), 7)),
                    Err(Refusal::IdentityMismatch)
                ));
                assert!(matches!(
                    observe(Pending(b.clone()), Evidence::Closed(other)),
                    Err(Refusal::IdentityMismatch)
                ));
            }
            assert!(matches!(
                restore(Record::Corrupt, &b),
                Err(Refusal::CorruptRecord)
            ));
        }

        #[test]
        fn durable_terminal_records_do_not_recover_dispatch_permission() {
            let b = binding();
            match restore(Record::Done(b.clone(), 7), &b).unwrap() {
                Restored::Settle(outcome) => match crate::settle(outcome) {
                    Exit::Delivered(t) => assert_eq!(t.number, 7),
                    _ => panic!("wrong terminal outcome"),
                },
                _ => panic!("terminal record became ready"),
            }
            assert!(matches!(
                restore(Record::Closed(b.clone()), &b).unwrap(),
                Restored::Settle(Outcome::NotDone(_))
            ));
        }
    }
}

// Temporary display data is a local of this entry and is not stored in Binding.
fn start(ready: boundary::Ready, bulletin: String) -> (boundary::Pending, boundary::Dispatch) {
    println!("{bulletin}");
    boundary::begin(ready)
}

// This is the entire recovery decision, outside the trusted boundary module.
// It receives no start-time environment or closure.
fn settle(outcome: boundary::Outcome) -> boundary::Exit {
    match outcome {
        boundary::Outcome::Done(t) => boundary::Exit::Delivered(t),
        boundary::Outcome::NotDone(c) => boundary::Exit::Cancelled(c),
        boundary::Outcome::Unknown(p) => boundary::Exit::Waiting(p),
    }
}

#[cfg(retry_pending)]
fn invalid_retry(pending: boundary::Pending) {
    boundary::begin(pending);
}

#[cfg(forget_scope)]
fn invalid_recovery(_outcome: boundary::Outcome) {
    let _alias = bulletin;
}

#[cfg(forge_ticket)]
fn invalid_completion(binding: boundary::Binding) -> boundary::Ticket {
    boundary::Ticket { binding, number: 7 }
}
