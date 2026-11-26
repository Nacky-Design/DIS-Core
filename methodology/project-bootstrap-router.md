# DIS Project Bootstrap & Stage Packet Router — pilot v1.0

Date: 2026-11-16. Status: controlled Python CLI, NOT an interceptor of native ChatGPT replies, image generation, browser Codex or Figma writes.

## Author result decision / critical review

Every Stage Result Packet is an **authorial decision checkpoint**: offer exact SRA approval, **critical review of the stage output**, and freeform corrections. No button is required: explicit natural-language author decisions are recorded to the exact source version and scope. A separate privileged issuer is still needed for the controller's cryptographic verification; do not fabricate one. Unapproved or critiqued results remain current-stage NEEDS_WORK until explicitly accepted; then a new SSA for the next stage is required. For Discovery the [DBR-001 baseline](discovery-baseline-research-standard.md) is mandatory even with zero client interviews and pre-launch offerings.

## Architectural contract

One permanent bootstrap prompt per new project. Every subsequent stage uses the existing versioned DIS prompt assembled automatically by the router with the precise original sources and all previously approved stage results.

New project with client brief is **Intake only**. Do NOT require nonexistent future artifacts at intake. DO NOT start Discovery just because the user said "make a concept" or "use DIS".

[Connect the DIS skills in the working checkout](../docs/codex-agent-skills-impeccable.md#connect-dis-at-project-start) as part of intake when the project will use Codex. Start the local instructions with the brief and the main user journey. Link the accepted baseline, UI Kit and verification commands as they become available. Stage preflight, execution and approvals follow the route below.

An existing project uses RECOVERY instead of a clean reboot: retain original input, observed research, hypotheses, previously explicitly approved decisions, missing evidence, and current stage. Earlier assistant-generated reports without SRA remain PROPOSED, not approved.

Stage Start Packet must disclose:
- current stage, scope and goal; original pinned source paths and SHA256
- all previously approved stage result snapshots, verified SRA receipts
- exact prompt path and content hash, prompt full text
- author choices REQUIRED for this stage and recorded choices
- declared route and documented scope adaptations (no silent omission)
- separate SSA-001 for this exact packet; execution DEC-001 and stage QA; separate result approval SRA-001

The router only compiles the proposed packet. Unknown or missing required choice produces STOP_AUTHOR_SELECTION_REQUIRED. Missing proof/attachment or prior user confirmation produces STOP_PROJECT_PREFLIGHT. No automatic stage production.

## Commands

    python -m tools.enforcement.project_router --project /project/project.json --root /project --dis-root /checkout/DIS

Current CLI prints the complete proposed stage snapshot including the full universal prompt. The project manifest points to original sources and prior pinned result documents. The tests exercise signed SSA/SRA API functions using a mock fixture key. In production, signing keys must reside in a separate privileged issuer, NEVER with the agent.

First universal prompt: prompts/dis-project-bootstrap-v1.md.

## Distinction between checks

- The router verifies source file identity, fixed prompt, declared route, required author choices and signed prior result receipts on a trusted key supplied by a separate issuer.
- Stage Guard / RQC-001: checks structural Discovery evidence where the controlled route actually calls it.
- DEC-001: maps each applicable approved requirement to a verifiable execution plan and actual result review.
- SSA-001: user authorizes exact proposed stage packet.
- SRA-001: user separately approves the checked output.

**Known integration gap:** the prototype router does not yet run DEC-001 or RQC-001 automatically within its stage-result function. The function's READY_FOR_SRA status means its own limited file/QA checks passed; it explicitly does NOT authorize promotion without separate DEC and stage-specific checks. Until such invocation is enforced, route status is PARTIAL, not enforcement complete. No native ChatGPT interception or true two-factor identity-auth is claimed.

## Regression

tests/test_project_router.py covers cold start, missing original brief, source tampering, prompt change, skipped stages, missing SRA, no SSA, untrusted issuer, fabricated receipt, stage choices and stale author additions.

## AUTO recovery

Project scope remains HERO visual concept for Moscow rental site. Original client DOCX remains authoritative. R0 v0.1 and v0.2 are research evidence/PROPOSED drafts, not accepted SRA-001. The early two art directions remain UNAPPROVED. Reopen at Intake/source recovery, preserve originals and existing findings, then run an RQC-001-tested **Discovery revision** after explicit SSA. No blank-slate restart; no automatic promotion to Art Direction.
