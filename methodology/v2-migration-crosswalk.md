# DIS v2 — Migration Crosswalk & Activation Gate
**Date:** 2026-11-25 · **Status:** implementation branch candidate, NOT active in main.

## Single method source and existing contracts
- [Master Process v1](dis-master-process-v1.md): scope, alternative strategies, stage map, Stage Cycle, HERO-first.
- [Operator Guide v1](../docs/dis-operator-guide-v2-alpha.md): visible novice workflow and exact next-stage phrase.
- [Universal Bootstrap v2 candidate](../prompts/dis-project-bootstrap-v2.md): initial conversation only, NOT automatic production.
- **PCS-001 + SSA-001/SRA-001** remain the approval evidence contract. v2 uses `pcs_controller.verify_approval` with stage/version/scope and exact snapshots. An actual trusted issuer is **not deployed**.
- **DEC-001** remains mandatory requirement mapping and real-output check; controller calls `validate_pre_execution` and `audit_actual_artifact`.
- **DBR-001/RQC-001** still govern research quality; controller requires a pinned RQC ledger for Discovery and protected visual routes. Structural PASS does not guarantee research truth.
- **STG-001** still governs production prerequisites and art-direction proposals; updated to allow distinct Research and Design Scope while retaining legacy format.
- Existing **UI Kit, HCA-001, ABPG-001, FA-01/FA-02** keep their current meanings until individual scope-aware migration. v2 does NOT silently reinterpret them.

## State ownership
Central DIS repository: rules, tools, tests.  
Each client repo: `.dis/project-state.json` and source/decision/artifact/evidence data; private by default. New projects can initialize this file with `route=null`. Route selection is a separate signed operator decision at `project_configuration`; it is not a model default.

## Stage machine status (controlled route)
- Bootstrap: `initialize_project()` with verified GitHub readback.
- Route: `describe_routes() → propose_route_selection() → confirm_route_selection()` with independently signed choice.
- Start: `propose_next_stage() → activate_next_stage()` with prior SRA and a separate new SSA.
- Work: `review_execution()` verifies stage-start receipt, pinned DEC, relevant RQC and STG before controlled production.
- Exit: `review_stage_result()` verifies actual artifact and stage acceptance criteria.
- Approval: `publish_approved_stage()` recomputes evidence, validates SRA snapshot, writes through GitHub CAS, checks readback.
- Recovery/next request: `transition_request()` revalidates stored SRA, prepares next stage but never starts it.

## Not connected — never claim otherwise
- Direct ChatGPT image generation, Figma and browser Codex are **not intercepted**.
- GithubContentsClient is an optional authenticated backend adapter: requires an installed backend environment and repo-scoped GitHub credential. There is no claim that ChatGPT's read-only GitHub integration supports writes.
- No trusted human-approval issuer, UI button, protected client branch, required client CI or live private-repository E2E has been deployed.
- Existing v1 projects are not automatically migrated. Reconstruct accepted state from actual project files, mark unverified approvals `NOT_VERIFIED`, obtain explicit operator review before v2 promotion.
- Running unit tests on mocked GitHub clients proves controller logic, **not** actual cross-app enforcement.

## Definition of activation
1. Author reviews and accepts PR #9 architecture and mapping.
2. PR #10 code tests (unit + adversarial) and original PCS/DEC/RQC tests pass on exact merge commit.
3. Demonstrate a real **private client repository**: init → choose route → one stage → author approval → restart from GitHub → next SSA; failed write must block status.
4. Deploy operator-identity/trusted signer outside creative agent; never supply signer keys in prompts, agent workspace or repository.
5. Connect supported tool routes and declare native/uncontrolled actions `NOT_ENFORCED`, not `PASS`.
6. Review client materials and source history before any DIS Core public release.
7. **Only after these gates**, explicitly switch normative bootstrap and AGENTS.md links in main to DIS v2. Main remains v1 until acceptance.
