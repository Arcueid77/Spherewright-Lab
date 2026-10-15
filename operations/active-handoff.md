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

## Repository migration checkpoint

The owner selected the canonical repository name `Spherewright-Lab`. GitHub rename preserved the private repository, draft PR #1, commits and successful CI. Local checkout is also named `Spherewright-Lab`; only these authored names/links changed, with imported manifests and product pin unchanged.

- Sample draft PR: [#1](https://github.com/AvaloNero/Spherewright-Lab/pull/1). Tested tool/import commit `8750a24537e904e484e207317beab57209440869` has exact successful CI [38718529989](https://github.com/AvaloNero/Spherewright-Lab/actions/runs/38718529989). The subsequent report commit records these results without changing the tested scripts, gitlink, archive, evidence manifest or source locks.
- 259 originals / 5,871,981 bytes were independently verified. Git contains 258 byte-exact originals; one ledger original remains protected-local with owner-only ACL. Import-manifest SHA-256: `984E6FCB2126379E4B8898D862D60C849FB6D6E9ED99F113B1E9AA2FEA7E740F`.
- All 259 normalized derivatives match evidence-manifest SHA-256 `F191917B5279F2A4EA5BE3CF3A6F227801C3AB1CC42693C078531AD22CF62C50`. Paired source-lock SHA-256: `A2537F906A058593E05E1BF155AFE6D955F6B6E5110E3B658648E4B67CAF16C7`.
- A genuine clean remote clone passed bootstrap, source lock, evidence, offline scenario and seven fail-closed cases with explicit exit 0 and a clean fixture. It correctly reports protected-original unavailable=1. The tool/import commit verified 750 relative links; the facts report adds six checked links, totaling 756. 80 historical unresolved references retain their limitations.
- Preview packaging passed from the clean fixed product, using product scripts and a separate ignored output. Manual ZIP: 239 files + 2 directories; Thunderstore ZIP: 12 files; 0 PDB. Hashes, sizes, sidecars and manifest agree. Original accepted ZIPs remain unchanged. Detailed values are in the migration report.
- The first incomplete clone and first negative invocation logs remain local; neither is counted as a passed run. The first clone's missing diagnostic leaves its root cause unproven. The later captured runs supply the successful proof.
- Root owns authored migration facts and product documentation preparation; the offline maintainer serializes explicit-path Git and exact-SHA CI receipts. Product cleanup stays on its feature branch and references a clean, pushed Sample commit with successful CI.
- No game window, accepted action, Save/Load, installation, deployment, recovery or publication was opened. Historical game ticks, Journal and writer boundaries above remain imported observations. No background game work is running under this migration.

Next sole objective: finish the product draft PR and exact-SHA validation, then deliver both drafts for review. No merge is authorized here. The recommended owner review order is Sample ownership transfer first, product cleanup only after the required separate owner confirmation or formal tag gate, then formal v0.4 publication under its separate approval.
