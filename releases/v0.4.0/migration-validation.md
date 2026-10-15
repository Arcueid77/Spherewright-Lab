# Repository migration verification

The private Sample import is verified from a real remote clone at `8750a24537e904e484e207317beab57209440869`. Its fixed product is the accepted candidate `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9`; operational facts were imported from the later product commit `e7d5f7d8661092b7c8089710488c448f290638be`. These are separate provenance boundaries. The lock remains `status: provisional`, `releaseTag: null`.

| Check | Actual result |
| --- | --- |
| Original import | 259 files / 5,871,981 bytes independently checked against source bytes before product cleanup |
| Git raw archive | 258 byte-exact files / 3,860,959 bytes |
| Protected exception | One 2,011,022-byte ledger original retained locally with owner-only ACL; its sanitized derivative is committed by explicit owner choice |
| Normalized evidence | All 259 derivatives match the evidence manifest; original identifiers, failures and applicability boundaries retained |
| Links | 750 links at the tested tool/import commit; 756 after the six report links were added and checked; 80 pre-existing unresolved references remain explicitly labeled historical context |
| Remote clone | Exact Sample head, exact gitlink/product HEAD, clean module and clean Sample; bootstrap, lock, evidence and offline scenario entry pass |
| Private original in clone/CI | Unavailable = 1; never reported as inspected by CI |
| Fail-closed regressions | Explicit terminal exit 0; all 7 cases pass; disposable fixture restored clean |
| Sample CI | [38718529989](https://github.com/AvaloNero/Spherewright-Lab/actions/runs/38718529989), completed/success for exact tested head `8750a24537e904e484e207317beab57209440869` |
| Game / deployment / publication | 0 game calls; no install, Save/Load, recovery, deployment, merge, tag or publication |

The seven negative cases reject a mismatching gitlink, corrupted frozen package, corrupted normalized evidence, a credential, an absolute path, manifest traversal even with a recomputed manifest digest, and a dirty product submodule. The first test invocation lacked a captured terminal result and is not counted as passed. A later complete invocation provides the explicit successful terminal result.

The owner corrected the repository name to `Spherewright-Lab`. The private repository, original draft PR, commits and successful CI retain their identity and history. Only authored names and canonical links changed; the raw archive, 259 normalized derivatives, product gitlink, source locks and frozen candidates did not change.

## Manifest boundaries

- [Import manifest](manifests/import-manifest.json): SHA-256 `984E6FCB2126379E4B8898D862D60C849FB6D6E9ED99F113B1E9AA2FEA7E740F`.
- [Evidence manifest](manifests/evidence-manifest.json): SHA-256 `F191917B5279F2A4EA5BE3CF3A6F227801C3AB1CC42693C078531AD22CF62C50`.
- Root and [release lock](source-lock.json) are byte-identical: SHA-256 `A2537F906A058593E05E1BF155AFE6D955F6B6E5110E3B658648E4B67CAF16C7`.
- [Machine-readable migration result](manifests/migration-validation.json) records the same actual checks. This report is an authored migration fact, not a change to the imported acceptance manifest.

A multiline Markdown normalization defect was repaired against verified prior hashes with local preimages retained. Raw archive bytes did not change. One earlier incomplete clone is retained; its original Git diagnostic was not captured, so its root cause is unproven.

## Independent preview packaging

The clean remote clone called the product's own `package-release.ps1` → `package-thunderstore.ps1` chain once, with a unique ignored Sample artifacts output. Product source remained clean at `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9`; no uncommitted external product source was used. The manual package manifest records that product commit, `sourceDirty: false`, DSP `0.10.35.29145` and BepInEx `5.4.17.0`.

| Preview file | Bytes | SHA-256 | Contents |
| --- | ---: | --- | --- |
| Spherewright-0.4.0-win-x64.zip | 36759398 | `BB9B8CF1734B8AA83053B4D1A6B9C51B89360C4046505F8C9EFAAE82AEDD344E` | 239 files + 2 directories; 0 PDB |
| Spherewright-0.4.0-thunderstore.zip | 32492607 | `7847B52989595ECC2CFBF3213C9617F56C4A8D67EA9280F2957FAFF12383701B` | 12 files; 0 PDB |

Hashes, sizes, sidecars and the run manifest agree. Fresh preview archive metadata produces different ZIP hashes; these outputs are not substituted for the two frozen accepted candidates. The original candidate hashes in [SHA256SUMS](hashes/SHA256SUMS.txt) were rechecked unchanged. Preview packages are not committed, installed or published.

The historical installation, recovery and continuous-window acceptance remains in [the final validation summary](validation-summary.md) and its original evidence. This repository migration does not repeat or enlarge that acceptance. The product cleanup is a separate draft; absent a formal v0.4.0 tag it requires the owner's separate merge gate.

## Product repository verification

The product split is now a separate three-commit draft at `1619223ad388f0a970f615b75862b2c85adfe9d5`, pushed and clean at the verification boundary. [Product PR #1](https://github.com/AvaloNero/Spherewright/pull/1) remains open/draft. Its [exact Windows Core CI 38723951815](https://github.com/AvaloNero/Spherewright/actions/runs/38723951815) completed successfully: Contracts 73, Bridge.Core 2777, MCP 258, total 3108; all passed with zero failed/skipped.

The independent full `Spherewright.sln` locked restore and Release build passed with SDK `8.0.424`, zero warnings and zero errors. All five legal Native references match the accepted candidate, including Assembly-CSharp SHA-256 `B84B60DF5A24947A014801F23B9B85D1E77853F42A331918E2DC85B153E50527`. An older main-local reference cache was preserved unused; the feature build used the verified matching set. No Lab source is a product build input.

The product branch changes 271 paths: 258 short redirects, six files with link updates, and seven authored product documents. All 555 Lab targets resolve to the fixed transfer commit `14478a03c64c550e644c559405c8496b647552e7`; the product does not follow a floating Lab branch. 488 protected code/test/script/CI/build/resource inputs retain their feature preimage bytes and unchanged Git content. The embedded playbook SHA-256 `2E354DB900B7822F47092B023EA971BEEA688DEF97798D666D8C12C3FC16AB70` matches the frozen manual candidate. The packaging README has exactly four link replacements and no other content changes.

Original product main remains `e7d5f7d8661092b7c8089710488c448f290638be`, clean and unchanged. No existing tag/history, frozen ZIP, game state, installation or deployment was modified. Native build and CI receipts are indexed by their hashes in the machine report; local raw logs are protected/ignored rather than claimed to ship in a clone.

The immutable transfer boundary stays at `14478a03c64c550e644c559405c8496b647552e7` with successful Lab CI 38722214953 and a genuine canonical-URL clean clone. These subsequent closing facts do not change imported manifests, source locks, tested tools or the product submodule, and do not cause another product build or package. The final CI status for this closing note belongs to Lab PR #1.

Both drafts are ready for owner review. No formal v0.4.0 tag/Release exists; the product cleanup merge still requires the owner's separate approval or the formal-tag gate. Recommended order: review/merge Lab ownership first, explicitly approve the product cleanup merge, then separately review formal v0.4 publication from the accepted candidate boundary.
