# DIS PCS — Universal Stage Start Prompt v1.1
Template ID PCS-START-1, schema PCS-001/v1.

INPUT: Load cumulative verified primary documents from Controller's exact snapshot, including original client brief/site, prior approved stage artifacts, current UI Kit, all active decision IDs and user-approved sources. Separate LOADED, APPROVED, PROPOSED, MISSING.
INHERIT: Preserve all applicable LOCKED and GUIDED properties from ALL previous stages, with decision IDs, source links and scope. Explicitly flag contradictions and absent documents; never repair them from a guessed memory.
TASK: Work only on the approved stage and scope. Do not restart past stages without dependency evidence.
FREEDOM: Explore OPEN choices while keeping LOCKED unchanged and interpreting GUIDED with artistic originality.
FORBIDDEN: No fabricated ROI, customers, logos, UI, kickers or diagrams contrary to the current project contract.
OUTPUT: Keep one readable active stage document with attachments and traceable decisions.
ACCEPTANCE: Check actual deliverables against sources, not prompt intentions; present separately for user exit approval. Never self-approve.
This universal prompt is a template, not an approval to execute any stage by itself.

## Required DEC-001 traceability
**Ни один этап DIS не имеет права начинать производство на основании простого ознакомления с документами. Каждое применимое утверждённое требование должно быть перенесено в исполнительный контракт, а его выполнение — проверено на фактическом результате.**

After explicit user SSA approval but BEFORE any production, run DEC-01..04: read actual full input, extract every applicable requirement with source hash/anchor/status/lock, map to a concrete implementation plan, and obtain `DEC_PRE_EXEC_PASS`. Missing/incomplete contract => `STOP_DEC_001`; do not generate. SSA-001 alone is never sufficient.
