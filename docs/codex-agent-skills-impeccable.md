# Codex + DIS Agent Skills + Impeccable

DIS skills live in this repository and can be copied into the checkout that Codex will edit. Impeccable is an optional external tool with its own installation and hook approval.

## Connect DIS at project start

Use this command from a checked-out DIS repository.

```bash
DIS_SKIP_IMPECCABLE=1 bash scripts/setup-codex-design-tools.sh "/absolute/path/to/client-project"
```

The script copies the current DIS skills into the target’s `.agents/skills`. It creates a short `AGENTS.md` when the target has none. With an existing `AGENTS.md`, add the links and QA routing below to that file. Keep the project’s existing instructions.

At intake, link the current brief and record the user, the main journey and what a usable first result must let that user do. Add just the checks relevant to that journey. For example, a rental customer comparing offers should see the base daily price and its included mileage before opening the date picker. Record unresolved decisions as open.

When a baseline and UI Kit are accepted, link their exact versions from the project instructions. Also link the working preview and build or test commands. Keep shared methods in DIS and link to the handoff or decision log for project-specific detail. For an existing site, link the actual accepted implementation and recover the decisions already made.

Use the smallest check that can verify the change. Review a label in its actual component and at the widths where it can wrap. Review a change in selection or validation through the page or state that consumes the result. Expand to the affected journeys, breakpoint transitions and integrations for a release review.

For staged DIS projects, continue with the [Project Bootstrap Router](../methodology/project-bootstrap-router.md). Checkout setup can happen during intake. Stage approvals and execution evidence follow the adopted project route.

Run the setup script without `DIS_SKIP_IMPECCABLE=1` when the project also needs the official Impeccable installer.

**Manual alternative (from target project):**
```bash
npx impeccable install --providers=codex --scope=project
```

No automatic approvals. Codex needs a restart/refresh; inspect `/skills`. Open `/hooks` and explicitly approve the project hook after reviewing what it executes. The upstream package may retrieve a platform binary on its first execution and has its own telemetry options (see official privacy documentation). The **skill itself** can be used before optional automatic hooks are trusted.

## Onboarding and precedence

1. Check that `dis-design-qa` and `dis-browser-qa-playwriter` are visible in Codex. Check `impeccable` when installed.
2. Point the client project at its approved **Project UI Kit** and previously accepted design (DIS may not invent a new DESIGN.md as truth).
3. For existing A2: run `$impeccable audit` on the current HTML, collect findings, compare with project's constraints, then run `dis-design-qa` and real browser QA. **Do not run colorize/bolder/new-work** just because the tool offers them.
4. For a new project: `$impeccable document` may extract a draft `DESIGN.md`, then require art director's review before promotion.
5. Each approved token change goes into one project UI Kit. Agent Skills are reusable procedures; Impeccable is external critic; neither substitutes human approval.

## Validation

- Agent Skills spec: https://agentskills.io/specification
- Official Impeccable: https://github.com/pbakaus/impeccable
- Upstream CLI (when installed): `skills-ref validate .agents/skills/dis-design-qa` (format only).
- Browser/geometry/interaction QA remains necessary: metadata validation and the external audit do **not** certify artistic fidelity.
- No client screenshot or extra ZIP/PDF/PNG report is required by this setup.

## Honesty of status

`AGENTS.md + .agents/skills` present in GitHub means **skill packaging is delivered**. `scripts/setup-codex-design-tools.sh` means the **local installation path exists**. Neither means the installer has been executed in a client workspace, that the user approved hooks, or that actual design checks passed.
