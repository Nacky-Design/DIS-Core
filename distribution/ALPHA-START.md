# DIS v2 Alpha — Entry & Scope
**Release channel:** Alpha (controlled pilot) · **Date:** 2026-11-26

**This is the current operator-facing entrypoint for the DIS Alpha.**
- [Operator Guide](../docs/dis-operator-guide-v2-alpha.md)
- [Universal Project Start v2](../prompts/dis-project-bootstrap-v2.md)
- [Master Process](../methodology/dis-master-process-v1.md)
- [Stage and GitHub integration](../methodology/v2-migration-crosswalk.md)
- [Alpha approval procedure](alpha-approval-procedure.md)
- [Novice pilot protocol](../tests/novice-pilot-protocol-v1.md)
- [Anonymized Knowledge Base](../knowledge/README.md)

## What works
The checked-in Python routing modules validate process options, snapshots, signed receipt formats, file hashes, GitHub CAS/readback interfaces and fail-closed entry/exit checks on controlled code routes. GitHub Actions runs tests on changes. Skills and prompts contain stage-specific instructions.

## What must never be claimed
**No authenticated independent author signer or ChatGPT-native/Figma/Codex tool interception has been deployed.** Existing HMAC signature checks require a separate trusted issuer. Alpha operator review in chat is **PROCEDURAL ONLY**, not a cryptographically authenticated SRA. A GitHub commit does not prove an independent user approval. Do not elevate a procedurally accepted draft to controller status `APPROVED` or use protected next-stage routes without a genuine receipt.

## Working in Alpha
1. Create a **private project repo** for the client.
2. Copy the full v2 bootstrap prompt and attach actual client source materials (where sharing is permitted).
3. Select the recommended or alternative strategy and three independent scopes.
4. During a stage, apply real sources and the stage's explicit acceptance criteria.
5. On **«Переходим к следующему этапу»**, present an exit summary including selected/rejected decisions, sources, hypotheses and checks; offer deepen/revise/approve.
6. If human chooses approve and no trusted signer is connected, record **`PROCEDURAL_REVIEW_ACCEPTED`** separately, and **STOP** before a protected technical transition; do not forge `APPROVED` in `.dis/project-state.json`.
7. Never promise a verified file write unless it actually succeeded and was reread from GitHub.

For a pure novice concept trial without a trusted approval issuer, the operator may discuss the next stage *as an unprotected exploratory exercise*, but it must be labelled `UNCONTROLLED_ALPHA_EXPLORATION`; this does **not** count as passing DIS's stage-control hypothesis. Full process validation requires a protected approval issuer.

## Publication
The original DIS repository includes client-derived historical material. **Do not switch the existing repository to Public**. An export tool can generate a separate ALPHA core candidate from an explicit allowlist. That candidate needs an independent privacy, Git-history and licensing review before publication from a clean repository.
