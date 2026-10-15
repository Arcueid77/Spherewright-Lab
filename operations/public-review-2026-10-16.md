# Lab public-visibility safety review — 2026-10-16

Status: the owner-requested change from private to public is complete. The repository remains `AvaloNero/Spherewright-Lab`, ID `1420488739`, with `main` as its default branch. Both the maintainer and root independently verified anonymous API reads return `private=false` and `visibility=public`; root's check completed at `2026-10-15T17:09:13Z` (local date 2026-10-16). This visibility change grants no game or formal product-publication authority.

## Reviewed content and preserved evidence

- The owner explicitly requested public Lab visibility after sensitive-information review, and removal of this split's extra merge commits while retaining separate commits.
- The initial scan covered eight refs and ten commits. After the bounded rewrite, the v6 all-ref scan covered eleven local/remote/PR/preserved refs, eleven reachable commits and 564 unique blobs, including complete raw commit objects. Every tree excluded tracked `.local` files and contained its ignore rule. Ignored protected originals, tickets, Saves, raw private requests, credentials and backups are outside the public payload.
- Root independently scanned 553 current Lab files, excluding the fixed submodule and ignored private/artifact directories. No high-confidence credential, private key, authorization value, absolute local-user path or raw Steam-identity match was found. This tip check supplements rather than replaces history and GitHub-surface review.
- Import/evidence manifests, source locks and the product gitlink remain unchanged. The product remains fixed at `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9`; the immutable evidence snapshot `14478a03c64c550e644c559405c8496b647552e7` is retained. One original ledger remains owner-only local, with only its sanitized derivative in Git.
- After public visibility, root anonymously downloaded the pinned evidence snapshot's source lock. SHA-256 remained `A2537F906A058593E05E1BF155AFE6D955F6B6E5110E3B658648E4B67CAF16C7`, matching the protected expected value. Changing visibility did not rewrite refs, files, manifests or the fixed product dependency.

## Contextual findings

- Two `planToken` pattern hits were the explanatory code expression `PlanToken=string.Empty`, including a closing Markdown delimiter. They issue or contain no token; only that exact empty-code-expression shape is classified as nonsecret.
- Email-like hits in repository/PR clone metadata and six Actions logs were standard GitHub SSH principals and checkout-generated owner rewrite aliases. Root checked the exact SSH fields/`insteadOf` context and verified that the generated alias ID matches the public repository owner's ID. They are connection syntax, not private email or credentials. No log was deleted to hide them.
- Actual commit-author email metadata is retained only after comparison with independently public product commits/profile data. New prose does not publish those raw values. Other unknown identity/credential candidates must be investigated rather than blanket-allowlisted.
- Runner/system paths in logs are classified separately from private workstation paths. No private local backup/ref-map path or raw credential value is included in this report.
- Thirteen UNC-pattern hits occurred only in serialized PR-files JSON. Root and the maintainer independently decoded the response and checked its string fields; the decoded content contained zero UNC matches. This is a JSON-escaping false positive, not a network-share address. No imported evidence was rewritten to suppress it.

## Public surface and verification boundary

The review includes reachable Git history and available repository/PR/issue/review/comment/check/Actions metadata, complete logs, artifacts, release assets, wiki/discussion/Pages/deployment surfaces. Disabled, empty, unavailable and successfully examined surfaces are distinct outcomes. Array pagination is followed to completion; an array length is not a total-count field. Earlier incomplete collector output remains protected-local and is not accepted as complete coverage.

| Surface | Examined result |
| --- | --- |
| PR files | All 551 entries: six pages of 100/100/100/100/100/51. |
| PR/issue metadata | One PR, seven PR commits, one issue comment, one review, no inline review comments, and five timeline events; all returned pages retained. |
| Checks and Actions | Check-run metadata and annotations for observed commits; six historical complete workflow logs in v6, plus the rewritten-main run examined separately below. Later runs require their own incremental check. |
| Releases, deployments, environments, Actions artifacts | Successful API responses returned no entries. No absent release asset or artifact is claimed to have been scanned. |
| Wiki and discussions | Disabled in repository metadata. |
| Pages | Disabled in repository metadata; its endpoint returned 404. |
| Classic Projects / Projects v2 | Classic endpoint returned 404; GraphQL returned 403 with `INSUFFICIENT_SCOPES`. Project contents could not be read and are not certified clean or counted as zero. No broader permission was requested. |

Root rehashed all 43 inventory-referenced response/error originals and all 63 v6 external scan inputs: zero mismatches. The latter include 48 JSON files, six complete logs, six empty log-error files and three other text/error files. The v6 scan reports no high-confidence credential/private-key detector hit; its remaining candidates are the contextual findings above. Inventory SHA-256: `CFD197038FD7D95A2B2CA04B3838FE551A95D86471FA0B9B036ADB3A7E1547B9`. Scan receipt SHA-256: `3E52D9F1441C2F9D2D0E523431D067525123BAA7F3F069EBAB5D72B96B5D1B18`.

The rewritten-main [CI run 38772539205](https://github.com/AvaloNero/Spherewright-Lab/actions/runs/38772539205) completed successfully for exact source `1d1d58dbb979476a70f83825201a0cb6e639fd9b`. Its complete 29,556-byte log, check metadata and annotations were examined as an increment. Root independently confirmed all four email-like matches are the previously verified SSH aliases in the same rewrite context; its 57 path matches are runner/system paths. No new unresolved sensitive candidate was found. Incremental scan receipt SHA-256: `C8E737932D21E70304D62895ACD2192A91CE4265AB1CA655EDB4C01296A19FA3`; complete-log SHA-256: `165CAED163BDA6A07B1E83A89036DC534F373FEF1E343EB3196F9563746D2DCD`.

Raw API/log originals, protected backup bundles, per-ref maps and detailed detector receipts remain owner-only local. Public visibility cannot make those ignored files available, and it does not turn historical evidence into current authority. Pattern checks and contextual review do not imply a new game, install, Save/Load, deployment, formal tag, Release or Thunderstore publication.

## Authored closing delta

The four authored closing documents (`AGENTS.md`, `README.md`, active handoff and this review) are checked separately from immutable imported evidence. Root's delta scan retains the single empty-code-expression quotation in this report as an examined nonsecret finding, rather than claiming zero pattern matches. It found no unresolved sensitive candidate. These documents publish repository/test facts and public hashes, not raw protected logs, identities or private paths. Their commit's CI and final anonymous recursive clone supply the closing repository checks; they do not replace the scoped history/surface review above or certify the inaccessible Projects contents.
