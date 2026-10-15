# Repository split handoff

This is a file/Git/CI migration, not a game session. No game process, bridge, save, deployment, or recovery is called by this work.

- Product main import boundary: `e7d5f7d8661092b7c8089710488c448f290638be`, clean/pushed and exact CI successful before migration.
- Accepted candidate and read-only submodule: `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9`; no formal v0.4.0 tag, lock remains provisional.
- Historical final game boundary: saved tick 116353747, observed 116353967, revision 2, Journal 102/102 durable, four historical version transitions, 6660 built/0 prebuild. This is an imported observation, not a fresh game read.
- The prior fixed-20 window was closed at 10 accepted, lifetime 634 / whole 235. Unused slots were forfeited. The prior game writer stopped; accepted actions and their original keys remain historical facts, never replay instructions.
- The original unsaved four-unit stone transfer is not restored-stock credit. Its historical action is preserved in the imported evidence; it must not be rekeyed or repeated.
- Original experience-ledger bytes stay protected-local; only the explicitly sanitized derivative enters Git. No Save, ticket, raw private request, credential, or identity was copied into Git.
- Product cleanup stays on `chore/split-sample-operations`; Sample import stays on `chore/import-v0.4-sample`. Both are for draft review. Product main, old tags, and frozen ZIP bytes remain untouched.

Current migration verification and its limits are recorded in [migration-validation.md](../releases/v0.4.0/migration-validation.md). Before any future game work, confirm the old writer is stopped and perform the original fresh native/session/ownership checks; a healthy game is not automatically saved, exited, reloaded, or resumed because this chat ends.

Next entry: review the two repository PRs, merge the Sample ownership transfer first, and merge product cleanup only after the required owner confirmation or formal tag gate. Formal v0.4.0 publication remains a separate review.
