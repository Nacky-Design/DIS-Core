# RQC-001 — Discovery First-Pass Research Quality Gate

Date: 2026-11-16. Trigger: AUTO-001 repeated RBP: shallow competitor scan and two art ideas followed a brief; only user criticism produced a deep Discovery.

## Contract
RQC supplements HCA-001, PCS-001, DEC-001 and STG-001. Every first-pass Discovery must be audited BEFORE its first presentation to the author. Agent must repair material gaps autonomously. Do not use art direction to disguise incomplete Discovery. Structural readiness is not user approval.

## DBR-001 / floor of substantive expert research

[DBR-001](discovery-baseline-research-standard.md) is mandatory independently of whether the author selects focused, standard or extended scope. internal research baseline demonstrates the minimum rigor of a *well-scoped* desk-research study, not a requirement for a fixed count of findings, review rows or market pages. A pre-launch business can still receive a complete, candid hypothesis-led report; unavailable real operations and interviews remain transparently UNKNOWN. Distinguish RESEARCH_READY_FOR_HUMAN_SRA from POSITIONING_BLOCKED_BY_EVIDENCE. The structural RQC guard now rejects broadly repeated generic test actions and requires explicit support/disconfirmation fields on inferred claims. A passing structure still is not an independent editorial judgment.

## Mandatory dimensions
1. Business context and client facts vs unresolved commercial assumptions.
2. Multiple audience segments and explicit hypothesized JTBD; no invented interviews.
3. Observed direct competition, substitutes and nonconsumption; dated source snapshots.
4. Ordered customer journey, decision barriers and trust uncertainties.
5. Market contradictions and capabilities the client can actually prove.
6. Strategic opportunities causally linked to findings, plus falsification and validation plans.

Every finding includes claim, reasoning, evidence_level (client_fact / observed / inference / hypothesis), source IDs, report anchor, explicit assumption and validation action for untested claims. Each source has original locator, kind, pinned path and SHA256. The report is also pinned by SHA256.

## Self-criticism first, human review later
Self-audit must inspect source coverage, segments/JTBD, alternatives/substitutes, journey/barriers, falsifiability and contradictions/limits, referencing report findings and the exact report hash. Resolve critical and major gaps autonomously. Unknown facts may remain open, explicitly labelled; do not fabricate evidence, customer research, guarantees or promises. Internal critique is not external independent review.

Pass: STRUCTURE_READY_FOR_EDITORIAL_REVIEW (NOT research approval). Fail: STOP_DISCOVERY_INCOMPLETE. Before proposing Art Direction, human approvals for intake, research, prototype and references are additionally required. Image/Figma/HTML production retains all previous STG and DEC gates.

## Invocation
Project manifest should have project, scope, research_quality_ledger (project-root relative path), and stage gates. Example commands from the DIS checkout:

    python -m tools.enforcement.stage_guard --manifest /project/stage.json --root /project --action research_review
    python -m tools.enforcement.stage_guard --manifest /project/stage.json --root /project --action propose_art_direction
    python -m unittest discover -s tests -p 'test_research_quality_gate.py' -v

## Acceptance and enforcement limits
Python checks structural coverage, anchored references and file integrity. It CANNOT verify causal truth, the reliability of a source, genuine research depth, actual independent criticism or human approval. A synthetic report may satisfy the schema; editorial inspection of sources is required. Neither this controller nor repository GitHub Actions intercepts ChatGPT-native text/image generation or Figma directly. Real tool gateway, external human approval service and required status checks are NOT deployed. Mark status controlled_route_only until proven otherwise.

AUTO-001 negative regression: client's rental brief, request for a HERO. A report consisting only of competitor references and two visual options must fail before user sees it as review-ready. Replaying with honest research sources, thorough self-critique and actual user approval is the later acceptance test. Do not award invented numeric research quality scores.