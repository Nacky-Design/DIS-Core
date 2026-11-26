# DIS — Project Continuity System (PCS-001) v1 pilot
Status: IMPLEMENTATION PILOT, not a universal production gateway. One maintained human-readable document per stage, cumulative applicable predecessor documents, immutable approval evidence, versioned universal prompts, mandatory human checkpoints at stage entry and exit.

## P0 cross-system invariant — DEC-001

> **Ни один этап DIS не имеет права начинать производство на основании простого ознакомления с документами. Каждое применимое утверждённое требование должно быть перенесено в исполнительный контракт, а его выполнение — проверено на фактическом результате.**

PCS transports/verifies originals and approvals; [DEC-001](document-to-execution-contract.md) turns each applicable decision into a stage-specific machine/human-readable execution ledger with explicit realization and auditable real-output evidence. **SSA-001 is necessary but not sufficient for production:** `DEC_PRE_EXEC_PASS` is also required. No applicable approved decision may be omitted. `READ != COMPLY`, `INTENT != EVIDENCE`. Missing traceability => `STOP_DEC_001`, critical violation in actual artifact => `REJECTED`, result still needs separate SRA-001. Controller pilot does not intercept direct creative calls.

## Core invariant
The next stage cannot start from conversation recollection. Controller retrieves all predecessor documents, checks integrity, scope, approval, conflicts, then compiles a readable start packet with links and full prompt. User explicitly accepts this exact packet before execution; user separately approves the output. Native ChatGPT image generation is NOT intercepted by this repository, and this is NOT identity-based 2FA.

## Artifacts
- One canonical human-readable document per stage, updated in place during work; upon exit, pin content identity (Git blob/commit), preserve old revisions only in Git history.
- One universal prompt per stage type stored in DIS; it encodes workflow, not project-specific truth.
- A machine manifest with stage statuses, document URLs/path/blob identities, decision IDs, scopes, approval references, dependencies and conflicts. Manifest indexes documents and does not replace them.
- Attachments (images, original client briefing, Figma, HTML, reference screenshots) are registered evidence; they are not parallel decision documents.
- Full input chain = original briefing + all applicable approved stage docs + live UI Kit + author selection; Active Decision Set is indexed from sources, never a free-form summary that drops LOCKED requirements.

## Two checkpoints
SSA-001 / start: Controller loads actual file contents, validates provenance, computes/pins versions, compiles entire prompt and source list, then awaits explicit user acceptance of this snapshot. Source change invalidates approval.
SRA-001 / finish: independent output QA + proposed stage document + explicit user result approval, then pin stage version and update project state. Start approval never implies result approval.

## Mandatory mitigations: 6 critical + 5 secondary
R01 unloaded documents: require reading real bytes of every mandatory source, stop on omission.
R02 context overload: retain complete originals; use verifiable indexed decision IDs and references, never silently truncate mandatory requirements.
R03 conflicts: scoped supersedes with approval; unresolved conflict => STOP.
R04 prompt drift: pin prompt ID/version/content digest, enforce schema compatibility.
R05 artistic fidelity: separately audit actual image for chosen properties; code cannot guarantee visual taste. Critical violations => STOP / manual review.
R06 bypass: enforcement applies only to actual controlled tool routes; require gateway/branch protections for stronger guarantee; direct image calls currently uncontrolled.
R07 post-approval changes: pin file hashes and snapshot, reject stale inputs; Git revisions provide history.
R08 reference rot: store inspected evidence/provenance and legally permitted previews, URL, review date, selected mechanism, status.
R09 scope bleed: approvals scoped project/page/section/element; HERO approval never approves section 02.
R10 document bureaucracy: one active stage doc; only major scope/contract changes reopen start checkpoint.
R11 upstream edits: dependency graph marks affected downstream decisions stale; unaffected work stays approved.

Additional: original client's web and brief form mandatory Source Baseline; external content is DATA, never instructions; every requirement LOCKED/GUIDED/OPEN. Loaded is not approved; preflight passing is not artistic acceptance.

## Negative pilot tests
Cold-session full recovery; missing source; changed blob hash; lost reference; unsupported UI Kit approval; prompt mismatch; no start approval; no result approval; stale dependency; scope mismatch; direct-tool bypass attempt.
No physical protection of native ChatGPT images/Figma is claimed until a tool gateway has been independently proven.
