# DIS PCS-001 · Discovery / JTBD / source validation · Universal Stage Prompt v1.1

**Contract**: use the verified Stage Start Snapshot assembled by PCS Controller. This prompt is an immutable procedural template; project facts only come from linked, verified inputs. Preserve source IDs and human approvals. Do not execute until SSA-001 explicitly approves this exact packet.

**INPUT**: full accumulated chain of all applicable stage documents, original client baseline, current project state, original evidence, UI Kit (with actual approval state), and author's additional scoped instructions. Never ignore old-but-active approved decisions.

**TASK**: Transform the original client briefing and verified original site into a cited, human-readable Discovery stage document. Separate client's facts, source observations, tested user insights and untested JTBD hypotheses. Audit evidence gaps before review. Do not invent research or customer interviews. On exit: pin the approved discovery document and pass ALL original input and discovery decisions forward.

**INHERIT**: respect every applicable LOCKED decision; treat GUIDED artistic properties as intent to express, not copied pixels; OPEN properties may be creatively explored. Explain any conflicts/insufficient evidence before execution. Do not fabricate source facts.

**OUTPUT**: one live readable stage artifact plus registered media evidence where genuinely needed. Keep exact links and source versions. Produce a concise differences/change record within the same stage doc.

**QUALITY / EXIT**: compare the actual artifact to inherited decision IDs and selected source properties; distinguish mechanical checks from artistic opinion; DO NOT self-approve. Present the same document/artifact and evidence for separate Stage Result Approval (SRA-001). Exit status cannot change on a generated claim or unverified upload.


## P0 / DEC-001 · обязательная исполнительная проверка (редакция 1.1)

> **Ни один этап DIS не имеет права начинать производство на основании простого ознакомления с документами. Каждое применимое утверждённое требование должно быть перенесено в исполнительный контракт, а его выполнение — проверено на фактическом результате.**

Apply [DEC-001](../methodology/document-to-execution-contract.md) without exceptions: `DEC-01` read and pin actual source bytes, `DEC-02` extract every applicable approved requirement (source id/hash/anchor/scope/LOCKED|GUIDED|OPEN/criterion), `DEC-03` map every such requirement to a non-generic concrete implementation plan, `DEC-04` require `DEC_PRE_EXEC_PASS` before any stage production, and `DEC-05` check the **actual output**, recording evidence and `PASS|FAIL|NOT_CHECKED` per ID. Missing source, omitted mapping, stale hash, unresolved conflict => `STOP_DEC_001`. Critical output failure => REJECTED, no next-stage propagation. Approval status cannot be inferred. The Stage Start signature, when available, is an independent prerequisite, not a replacement. This is a procedural stop when no tool gateway is connected; do not claim hard blocking of direct ChatGPT/Figma calls.

### Stage-specific enforcement

**Discovery: for each client fact record exact source and evidence; label untested JTBD as hypotheses; verify real final research artifact, not just planned methodology.**

For every mapped requirement, present its exact artifact evidence and stop on critical violations. Neither a confident summary nor the existence of an artifact counts as verification.


## DBR-001 — Author-accepted minimum expert research baseline (16.11.2026)

For ANY Discovery, read and enforce [DBR-001](../methodology/discovery-baseline-research-standard.md) **before first production**. The depth and accuracy demonstrated by approved the approved minimum-depth research calibration are the BASELINE, not a premium extended-only mode. Research depth options can adjust scope and number of closely inspected business tasks, but **never omit minimum substantive dimensions** or replace claim-specific falsification with generic language. No client, interviews or actual business operations? Research competitors, substitutes, usage scenarios and alternatives; label empirical gaps as unknown rather than inventing answers. Research can be approved with open downstream POSITIONING blockers; distinguish research completeness from readiness to make commercial claims. In every SRA presentation expose **accept / critical-review / free author revisions**. Do not seek SRA on an internally discovered major editorial gap.

## Required AUTO-001 Research Quality pre-review (RQC-001)

Before the FIRST presentation of Discovery to the author, perform an autonomous internal critical second pass, fix material gaps, create the source-pinned, report-bound RQC ledger described in [research-quality-gate.md](../methodology/research-quality-gate.md), and run `stage_guard.py --action research_review` against the current actual report. Missing market alternatives/substitutes, distinct audience/JTBD, customer journey, anxieties, business capabilities, evidence chain, contradictions, validation actions or independently traceable internal audit => `STOP_DISCOVERY_INCOMPLETE`. A passing structural validator is ONLY `READY_FOR_HUMAN_RESEARCH_REVIEW`: it does not assert empirical validity and cannot self-sign SRA. Do not suggest Art Direction until upstream approvals and `--action propose_art_direction` PASS. Unknown client facts must be identified, not invented. Do not ask the user to find shallow-research errors for you.
