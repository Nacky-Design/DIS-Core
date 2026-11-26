# DIS · DBR-001 — Discovery Baseline Research Standard v1.0

**Date:** 2026-11-16. **Author's decision:** AUTO Discovery R0.3.1 is accepted as the **minimum substantive baseline** for every new DIS Discovery, even without existing client operations, empirical interviews or surveys.

## Non-negotiable floor (scope-adaptive, never silently lowered)

The goal of Discovery is a **thorough, critical, source-aware expert research model**, not a decorative introduction before Art Direction. Scarce business data changes **certainty and the status of claims**, NOT the obligation to investigate the external market and establish explicit falsifiable hypotheses. A company may be pre-launch or entirely hypothetical; correctly frame its proposed products and capabilities as *unknown*. Do not generate fake operational facts or testimonials. If an external source is unavailable, try a grounded substitute or mark the limit. Stop only when material research cannot honestly be performed or evidence claims would otherwise be fabricated.

internal research baseline is a **quality calibration artifact**, not a reusable subject matter or template to copy. Its numbers (35 findings, 22 sampled reviews, 3 scenarios, 6 JTBD statements) are **incidental**, not universal quotas. The standard is completeness **relative to an explicit stage scope**, honest evidence, meaningful counter-analysis and usable decisions.

### Minimum content every Discovery must contain

1. **Source-of-truth map.** Exact original brief(s) and client wishes, real business facts versus proposed products and unknown operations, confirmed constraints and conflicting claims, source links and dated source snapshots.
2. **Market and choice architecture.** Actual direct providers AND relevant substitutes/nonconsumption, avoiding double counting the same offering. Explain the user's trade-off across distinct models. Compare equivalent tasks where feasible; explicitly mark text-only comparisons versus observed interactive journeys.
3. **Audience and JTBD matrix.** Distinguish trigger, goal, usage context, contract/customer type, time/duration and constraints instead of inventing disjoint personas. Multiple plausible job stories with outcome, anxiety, trade-offs, evidence status and validation method; do not choose the primary segment by taste.
4. **End-to-end journey.** From need and eligibility to action, response, service delivery, completion, returns and post-service consequences *as applicable*. Include mobile constraints and failure/empty/error states at a research level, never disguise a storyboard as a ready UI.
5. **Customer voice when genuinely available.** Qualitative public statements may identify themes, objections and countercases, but must disclose sampling method, provenance, contradictory cases, authenticity limits and representative unknowns. **Do not require a review count** and do not fabricate reviews. When no review evidence is available, document analogous public signals and explicit absence.
6. **Baseline UX requirements separate from positioning.** Required usability/transaction properties are not automatically a differentiated brand promise. Strategic territory needs target job, business value, observed gap, **provable operational capability**, competing explanation, disconfirming criterion and what would rule the territory out. No arbitrary "winner" while key evidence is absent.
7. **Decision-oriented uncertainty register.** For each consequential unknown: owner/possible evidence, whether it blocks *research completion*, a later *claim*, *positioning*, *prototype*, or *production*. No generic assumption that absent interviews are a research failure.
8. **Falsifiable validations.** Every material inferred/hypothetical finding must have a claim-specific, actionable test, expected supporting observation and disconfirming observation. Repeated generic “ask the client” cannot count. Planned testing is NOT completed testing.
9. **Autonomous second critical pass BEFORE first delivery.** Check source traceability, exact task comparability, contradiction handling, category deduplication, segment/JTBD overlap, contrary examples, whether recommendations outrun proof, and prospective client claims. Repair material editorial gaps without relying on the user's criticism.
10. **One complete and readable stage document.** Evidence/review assets can be attached; preserve original source references, fact/inference/hypothesis labels, what changed, known limits, reproducible QA and separate user result approval. Accessible navigation and mobile reading on long documents are expected.

**Explicit acceptance constraints:** an aesthetically clean but shallow report FAILS; a checked-box report with boilerplate claims/test actions FAILS; unverified source claims presented as facts FAIL; converting hypotheses to approved marketing promises FAILS; prematurely moving to Art Direction FAILS.

## Research grade vs readiness to choose a business strategy

- `RESEARCH_BASELINE_READY_FOR_HUMAN_SRA`: scoped desk research is complete to this minimum and uncertainties are explicitly classified; this still needs user judgment.
- `RESEARCH_NEEDS_WORK`: gaps in the **research itself** (shallow source inspection, omitted alternative tasks, generic verification, contradictory framing, missing critical pass) must be fixed before SRA.
- `POSITIONING_BLOCKED_BY_EVIDENCE`: desk research may still be approved, but a promised business advantage cannot be selected until its proof arrives. Preserve this distinction in handoff.
- `NOT_VERIFIED`: technical tool/citation access or test execution missing. Never silently report PASS.

## Mandatory human choices and critique checkpoint

Before each stage, DIS automatically compiles a **Stage Start Packet** containing the exact sources and prompt, recommended workflow, legitimate alternatives/tool choice, QA expectations and asks for **SSA-001**. After execution and self-audit, DIS offers **SRA-001 approval OR a substantive critical review/author edits**. Either path is an author decision; critique is not automatic approval. A scoped internal revision (e.g. R0.3 → R0.3.1) can occur within the same SSA, without pretending a new stage was started. After SRA, compile the next packet; never auto-start it.

**Important:** Prompt text and GitHub CI are not a native ChatGPT interceptor. A passing programmatic RQC is only a structural gate; meaningful editorial acceptance remains human. The tool route must be demonstrably connected before claiming physical enforcement.

## internal research baseline calibration tests and evidence

Source (approved by author 2026-11-16): `projects/auto-rental/discovery-r031-result-register.md` and original attached `AUTO_Discovery_R031_Extended.md` / `AUTO_Discovery_R031_Extended.html`.

- R0.3 failed: 28 of 33 identical generic validation actions, mixed JTBD taxonomies, repeated commercial models counted separately, and UX baseline confused with position.
- R0.3.1 corrected: claim-specific support/disconfirming signals, situational JTBD matrix, deduplicated alternative models, comparable public information tasks, explicit sampling caveats, baseline/position split, decision-specific blocking unknowns.
- Validation must reject the old failure even if source count and structural category count are high.
- No artificial mandatory totals of comments, findings or pages. Human review tests source evidence **and content**, not only metadata.

## Implementation contract for controlled DIS routes

- **P0 policy:** AGENTS.md + Universal Discovery Prompt inherit this baseline on every project.
- **Machine:** extend RQC with anti-boilerplate and hypothesis-specific support/falsification checks; use positive and negative regression cases.
- **Delivery:** present a readable `Approve / Critically Review` choice, preserve the user's ability to comment freely, and record exact SRA evidence before next SSA.
- **Reality check:** a structural validator cannot evaluate actual semantic truth; no cryptographic approval service or complete ChatGPT gateway is declared until actually present.
