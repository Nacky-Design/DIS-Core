# DIS — Novice Pilot Protocol v1.0
**Status:** DRAFT. Run only after integration gates below; not a claim that DIS is ready today.

## Goal
Test whether an operator without professional design training can move from a client brief to a meaningful approved HERO and, if selected, a visually consistent homepage built one section at a time. Compare with normal ChatGPT/Codex use on the same project inputs where feasible. Never substitute technical PASS for the operator's explicit decisions.

## Before inviting a novice — hard prerequisites
- [ ] Author explicitly reviews proposed architecture and staged PRs. Current `main` must not silently use candidate contracts.
- [ ] Separate PRIVATE **synthetic** project repository available; actual GitHub access and writes demonstrated in user's environment (ChatGPT and/or browser Codex) with no client confidential data.
- [ ] Trusted human approval mechanism either deployed and verified **or** explicitly disclosed as `PROCEDURAL_ONLY`, with novice test not counted as full P0 approval enforcement.
- [ ] DIS can load exact method commit/version, recover active stage from GitHub, display selected route/three Scopes and no unnecessary options, and print clear errors if unavailable.
- [ ] Stage Acceptance Criteria stated before work and checked on actual artifact; no agent self-approval.
- [ ] If HTML/interactive is a selected deliverable, real browser QA is configured and tested; if static PNG only, visually review the actual PNG at mobile/desktop scope.
- [ ] Next Move Theory skills are present and rights clarified for intended test, OR NMT use excluded with `NMT_NOT_CONNECTED` stated.
- [ ] DIS Core PUBLIC extraction audited for client materials, licenses and Git history; until then share only appropriately authorized access to private DIS repo.

## Optional privacy-minimized Pilot Monitor

[DIS Pilot Monitor v0.1](../docs/pilot-monitor-v0.1.md) records route, stage changes, issues, attempted fixes and reported outcomes in the novice's **private** GitHub project, with their explicit consent and a working write connection. It does not record chat transcripts, screen or typed keystrokes. Distinguish `agent_reported` fixes from externally verified results and report `NOT_CONNECTED` when instrumentation is absent. Do not treat lack of consent as a novice failure.

## Test task preparation
Create one synthetic, realistic client brief including: brand name, product and target customer, 3–5 factual details, an uncertain market claim, explicit design goal, mobile needs, and 2–3 optionally supplied reference URLs. Do not artificially give the user a perfect solution. Keep a single version/hash of inputs for comparison.

**No prior expert coaching:** the novice receives only the Operator Guide, full startup prompt and brief. They do not receive hidden solution recommendations or an engineer assisting between checkpoints.

## Core novice journey (observe, don't steer)
| # | User action | Evidence expected | Failure example |
|---|---|---|---|
| 1 | Create/attach project repo | successful read/write preflight | user cannot complete without engineer |
| 2 | Paste full startup prompt, attach TЗ | initial source register | AI begins generating HERO before configuration |
| 3 | Select Research/Design/Delivery Scope | chosen route + alternatives & rationale | system silently chooses shortest path |
| 4 | Confirm criteria and start Discovery | stage packet/SSA where available | unexplained acronym wall or no source verification |
| 5 | Explore and revise findings | proposed vs verified claims | fabricated interviews / false research PASS |
| 6 | Say **«Переходим к следующему этапу»** | structured exit check & decisions | auto-approves or auto-advances |
| 7 | Deepen/revise/approve | exact version and GitHub readback | approval claims without commit |
| 8 | Complete IA/semantic/prototype/reference/art direction | traceability of selected options | one stage replaces another's intent |
| 9 | Approve Seed UI Kit and generate HERO first | source-to-output visual trace | simultaneous full homepage generation |
| 10 | Review HERO in chosen sizes | actual artwork, missing facts & QA | AI claims pixel fidelity without verification |
| 11 | If homepage selected, generate sections one by one | whole-page rhythm and consistency | sections good alone, broken together |
| 12 | Final concept approval and selected documents | correct files with real source citations | reports invented after the fact |

## Evaluation rubric (no fake “90%” scores)
- **Completion:** stage progress recorded, operator understood choices, design delivered in selected scope.
- **Correctness:** no unapproved transitions, no missing locked client data, evidence/hypothesis distinction intact.
- **Usability:** number of unexplained tool setup steps; whether novice independently completed each step.
- **Design quality:** human reviewer checks concept against agreed criteria, real mobile adaptation, content and coherence; no automatic quality score presented as measured truth.
- **Efficiency:** time on task, number of model prompts, stage reversals, human interventions; comparison requires the same input conditions and disclosure of tools.
- **Recovery:** open project from another chat/context and identify exact stage, last approved version and next permitted action.

## Stop semantics
Stop the trial (and classify infrastructure failure, not operator failure) if private repo authentication fails, required source unavailable, no trustworthy approval process is configured for a claimed protected transition, or promised deliverables depend on unavailable tools. Never ask the novice to manually fabricate receipts, GitHub JSON or confidence data.

## Outcome report
At the end, write a single report with:
- actual scenario and pinned source identity;
- chosen scopes, stages and time spent;
- user decisions, questions, failures and missed explanations;
- test results vs manual/human judgments;
- bugs with reproduction steps and suggested owner/fix;
- whether each of the original 16 defects is fixed, partially fixed or open.
No score without evidence. The report is reviewed by the DIS author before any new release.
