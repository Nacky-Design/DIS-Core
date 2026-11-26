# DIS — Playwriter browser adapter

**Status (2026-10-29):** documented in DIS; **not confirmed installed or connected** in local Mac / cloud Codex / client repository. This document is **not** a required CI check.

## Why
Inspect existing browser tabs, rendered typography and section geometry, interaction states and mobile behavior using a single browser automation interface, so DIS can verify changes rather than just describing intent. Browser evidence must be associated with exact artifact version per [Execution Evidence Contract](execution-evidence-contract.md). This is **technical QA**; it does not decide visual quality or human art approval.

## Recommended setup
Official: https://playwriter.dev/docs/installation

```sh
# On the actual machine/environment running Codex or another agent:
npm i -g playwriter
npx -y skills add https://playwriter.dev -g -y

# In local Chrome, install official extension and enable on a specific target tab.
playwriter session new
# Then inspect enabled pages with the returned session ID:
playwriter -s 1 -e 'console.log(context.pages().map(p => p.url()))'
```

The `1` above is only an **example**, not a promised session id.

Playwriter supports a skill-first CLI. MCP fallback when needed:
```json
{"mcpServers":{"playwriter":{"command":"npx","args":["-y","playwriter@latest"]}}}
```
See https://playwriter.dev/docs/mcp-setup . The config belongs to the **actual MCP host**, not merely the DIS documentation repository.

## Environments
- **Local Codex + Mac Chrome:** extension enabled on project test tab; CLI skill available. Must pass smoke test.
- **Browser/cloud Codex:** local Mac Chrome is **not automatically available**. Browser agent and user's machine are separate. Prefer cloud project's own approved Playwright/browser QA; remote Playwriter requires explicitly approved secured relay, host and token. Do not enable tunneling by default.
- **CI:** headless/isolated browser is usually preferable; integration requires real tests and branch-protection configuration. Do not claim CI enforcement from this document.

## DIS QA gate
Follow [dis-browser-qa-playwriter](../.agents/skills/dis-browser-qa-playwriter/SKILL.md) and the existing [dis-design-qa](../.agents/skills/dis-design-qa/SKILL.md). Record measured DOM/computed CSS, exact viewport/screenshots, keyboard/interactions, errors and regression checks against approved baseline; mark unavailable capabilities `not_verified`.

## Separation of responsibilities
Playwriter: browser observation / interaction evidence.
DIS: approved rules and intended composition.
UI Kit: typography/grid design source of truth.
Human: final artistic acceptance.

## Readiness checklist
1. CLI/skill installed in actual agent environment.
2. Browser connected and correct target URL visible.
3. Tested one viewport and extracted real computed styles.
4. Confirmed all specified viewport sizes.
5. Evidence saved for exact version and no protected regressions.
Only then say `playwriter_connected`; no browser test means `not_verified`.
