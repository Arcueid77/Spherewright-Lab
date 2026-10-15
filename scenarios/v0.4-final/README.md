# v0.4-final — real bounded acceptance scenario

The original local owned, single-player peaceful, non-sandbox, 1× progression world supplied the accepted Overseer/Foundry/Governor evidence. This is a real historical scenario, not a fixture or a new game plan. It prepares the departure system; interstellar flight belongs to v0.5.

Read [scenario.yaml](scenario.yaml), [acceptance.md](acceptance.md), [topology.md](topology.md), the [imported delivery contract](delivery-contract.md), and the [current historical boundary](../../operations/current-status.md). All original live failures, narrow scopes, and protected evidence indexes remain available in [the release evidence](../../releases/v0.4.0/evidence/README.md).

```powershell
pwsh -File scenarios/v0.4-final/scripts/verify-acceptance.ps1
```

This executable entry verifies source and evidence only. It makes zero game calls and does not reuse any old prepared plan, token, action, or accepted key. Re-execution against a game requires a separate approved finite plan and the original native safety checks; the old completed prefixes must not be rebuilt for repository acceptance.

`scenario.yaml` uses JSON syntax, which is valid YAML 1.2, so the lightweight validator needs no external YAML package.
