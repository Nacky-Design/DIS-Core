# DIS — Alpha author review procedure v1
**Status:** PROCEDURAL_ONLY; not a deployed authenticated approval service.

## Stage Exit
When the human writes **«Переходим к следующему этапу»**, DIS checks the agreed criteria, presents the actual stage version and a structured decision register, distinguishes source-backed observations from hypotheses and explains unverified requirements. If REQUIRED is FAIL/NOT_CHECKED, do not show approval as an available successful transition.

## The three choices
- **Углубить:** remain in current stage; offer specific additional inquiry and value.
- **Доработать:** remain and revise exact material; retain prior version.
- **Утвердить этап:** request an explicit confirmation including stage ID, artifact version and what is being accepted.

## Record an explicit author decision
When an independent approval issuer is **NOT_CONNECTED**, save a proposed decision as `PROCEDURAL_REVIEW_ACCEPTED` with exact scope, author-visible wording, stage version and GitHub record link. The operator should be able to review the record. Never set `stage_status=APPROVED` solely from a text instruction or a model-produced JSON value.

The protected controller route still **requires valid signed SRA-001 + successful GitHub readback**, and then **separate signed SSA-001** to start the next stage. Do not synthesize receipt/signature or put an issuer key into GitHub, Codex, chat or prompts. If an independently trusted service is not available, return `TRUSTED_APPROVAL_NOT_CONNECTED`.

## Alpha limitations
This lets a novice learn the sequence and provide real feedback while honestly distinguishing rehearsal from fully protected orchestration. It is **not** independent two-factor identity verification and does not block native image_gen/Figma/browser Codex tool calls. The actual authenticated issuer and tool gateway remain a release blocker for full DIS enforcement.
