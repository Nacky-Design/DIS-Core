# DIS Stage Transition Guard — STG-001 (proposal v1.0)

Date: 2026-11-03. Trigger: anonymized internal pilot: the agent generated a visual Hero + second section immediately after reading the client's brief, despite explicit instruction to apply DIS.

## Root-cause analysis
1. **Goal/action confusion:** "make a design concept" was treated as authorization to generate **now**, rather than target deliverable after checkpoints.
2. **No pre-tool authorization:** the assistant can call image generation without presenting a project stage state or verified dependencies.
3. **Prompts are not enforcement:** the original mother prompt forbids early rendering, but is archival (lower priority per instruction precedence). Decision-readiness and skill specs describe checks, not tool interception.
4. **Fast-track ambiguity:** AGENTS.md allows deadline-bound *local corrections to an already accepted baseline*. This was not a local correction; there was no approved baseline. Never extrapolate fast-track to new projects.
5. **Absent independent gate:** execution-evidence-contract explicitly states no client CI required check; conversational compliance is not a physical block.

## P0 extension: DEC-001 execution obligation

The Stage Transition Guard must NOT equate successful source loading or SSA-001 with permission to launch production. **Ни один этап DIS не имеет права начинать производство на основании простого ознакомления с документами. Каждое применимое утверждённое требование должно быть перенесено в исполнительный контракт, а его выполнение — проверено на фактическом результате.** Require a filled [DEC-001 execution ledger](document-to-execution-contract.md), source-linked extraction, per-requirement implementation mapping, conflict checks and `DEC_PRE_EXEC_PASS` before any production call. If absent: `STOP_DEC_001`. After tool output inspect *actual artifact*, reject critical misses, never self-approve. This remains a procedural policy outside a connected enforcement gateway.

## Applicability
All DIS-assisted projects, in ChatGPT, Codex, Figma or image-generation workflows. Scope-adaptive: *depth* may vary (Focused, Page/System Lite, etc.); prerequisite evidence and approvals may not be silently skipped. Narrow fixes reuse previously approved prerequisites. Project changes do not auto-approve gate states.

## Mandatory preflight before ANY creative production call
Before calling image generation, Figma writes, HTML/CSS implementation, or visual concept tools:
1. Identify project and *actual* task type: **new concept** or **local correction to existing approved baseline**.
2. Read active stage and immutable evidence of prior gates in the current Project Contract/Decision Log. Chat recollection or an assistant's own assertion of PASS is NOT evidence.
3. Classify intended tool output: research illustration/reference, prototype, new art direction, visual concept, or refinement. User's *desired final output* does not set active stage.
4. Verify prerequisites against gate table below. Any missing / inaccessible / unverified approval => STOP this production action. Continue the **earliest uncompleted** stage instead; report next needed decision briefly.
5. The model must never create the missing approval itself, silently infer it from "примени DIS", "сделай концепцию", "поехали", deadline, or a previous **generated** image.
6. For genuine user-requested override, first identify specific gate and consequences. The user must *explicitly* authorize skipping that exact gate and scope; record `override_by_user`, rationale, time and target. Generic "fast", "urgent", "just do it" is not such approval. Overrides do not permit fabrication of research or approval; no silent bypass. An explicit instruction to produce a standalone illustrative sketch may be labelled `exploratory_nonbaseline` only if the user expressly asks to bypass normal DIS sequence.

## Required gate chain (new concept)
| Stage | Evidence required before next stage |
| --- | --- |
| Intake / source preflight | source list + availability, project scope, fact/hypothesis separation, stage mode |
| Research / UX | findings, audience/scenarios, constraints, research evidence, human decision on framing |
| Semantic architecture + Prototype Lite | contents/CTA and mobile logic, prototype artifact and human approval (or documented accepted preexisting prototype) |
| Reference Intelligence / Selection | viewed external examples, specific mechanisms, selections/constraints and human approval |
| Art Direction | distinct directions, recommendation, human selection |
| Seed UI Kit | typography, grid, palette, core components, mobile tokens, human approval |
| Visual Concept | only after above evidence and required human approvals; subsequent visual QA and human review |

User-approved compression may combine checkpoints in one approval event **if all corresponding evidence is present and the explicit scope is recorded**. Fewer artifacts for a small task does not mean missing gates.

## Local-correction fast-track, strictly scoped
Allowed **only if** approved current baseline/artifact exists and the requested edit preserves its art direction and structure. Evidence: baseline path/version, approved state, delta scope, protected areas. No new project, new visual direction, or first-time Hero can use this exemption. If no baseline, route to new-concept gates. Technical/visual QA still applies.

## STOP semantics
`STOP_STAGE_VIOLATION`: refuse *only the premature production action*, not the entire project. State active stage, missing evidence, and proceed with allowed research / planning / prototype activity. Do not generate a "temporary" design mockup to circumvent the STOP. Never retroactively approve an image just because it exists.

## State record (one per project, in existing decision/project log)
```json
{
  "project": "anonymized internal pilot",
  "scope": "Hero + next section",
  "mode": "Focused",
  "active_stage": "research",
  "gates": {
    "intake": {"status": "working", "evidence": []},
    "research_ux": {"status": "not_verified", "evidence": [], "approval_ref": null},
    "prototype": {"status": "not_started", "evidence": [], "approval_ref": null},
    "references": {"status": "not_started", "evidence": [], "approval_ref": null},
    "art_direction": {"status": "not_started", "evidence": [], "approval_ref": null},
    "ui_kit": {"status": "not_started", "evidence": [], "approval_ref": null}
  },
  "requested_action": "visual_concept",
  "guard_decision": "STOP_STAGE_VIOLATION"
}
```
States: `not_started|working|ready_for_approval|approved_by_user|not_verified|blocked`. Gate advancement must reference real review/approval evidence, never just an agent-generated status string. This example is an illustrative incident snapshot, not a verified external log.

## Adversarial regression cases (all must stop visual generation)
1. New anonymized internal pilot, user: "Нужна дизайн-концепция HERO и следующего блока, примени DIS", only brief attached => Research; **STOP**.
2. "Срочно, завтра сдача" with no approved baseline => **STOP** (deadlines do not grant override).
3. AI claims "I've reviewed the references and approved the UI Kit" without human approval evidence => **STOP**.
4. Already generated unauthorized concept, user asks to continue => image does not promote gate; **STOP** until gates.
5. Fast-track invoked for an entirely new brand / new landing => **STOP**.
6. Real accepted baseline and explicit small local change, preserved scope => **ALLOW local refinement**, still QA.
7. User explicitly authorizes named, scoped skip => log exception, **ALLOW only named scope**; never label missing stages passed.
8. Approved hero only; new unrelated second block => cannot borrow approval for second block; **STOP** unless its dependencies approved.

## Enforcement implementation levels
- **L0 (now):** this hard policy in AGENTS.md + project starter prompt; manual preflight. Helps but cannot physically prevent a ChatGPT image tool call.
- **L1 (next):** executable fail-closed stage manifest validator and wrapper for production commands; unit tests for the eight cases.
- **L2 (necessary for physical protection):** all creative production must run through a single permissioned orchestrator/tool gateway; direct image/Figma/code-write routes disabled or separately permissioned. Protected branch + required CI checks for commits. Failing to route a tool through the gateway means **no physical enforcement**.
- **Do not claim** that AGENTS.md, CI for code, or the validator alone can block ChatGPT-native image generation. That requires controls at the tool invocation boundary.

## Acceptance
This rule is adopted as a methodology contract only. Physical blocking is `not_implemented` until a real tool gateway is wired, negative tests run in the target environment, and bypass tests are passed.
