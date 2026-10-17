# v0.4.0 final package qualification and publication / 最终包验证与发布

2026-10-17, Asia/Singapore. The owner explicitly authorized formal publication with “都干了吧”. This report records the final package source and its own installed evidence; the preceding [e018 report](package-callability-2026-10-17.md) and frozen production acceptance retain their original scopes.

所有者已明确授权正式发布。本报告记录最终同源双包自己的实装证据；此前 e018 调用/迁移证据和冻结生产验收分别保留原范围，不转记到新源码或 session。

## Source and immutable packages / 源码与固定包

- Package source: `b7c0002dbe2e8f5608c5ca140b0c6326a1818021`, clean and pushed before building; [exact product CI 39018031556](https://github.com/Arcueid77/Spherewright/actions/runs/39018031556) passed. / 打包前源码干净、已推送且准确 CI 通过。
- Active Lab lock/gitlink: `2de0a165e123aa9e4c3a6a153d88f7ba0413f721`, [exact CI 39018555646](https://github.com/Arcueid77/Spherewright-Lab/actions/runs/39018555646) passed before adoption. Frozen evidence/locks remain unchanged; active acceptance stays `historical_reference`. / 活动锁先于实机采用通过 CI，不继承旧生产验收。
- Native: DSP `0.10.35.29151`, Assembly-CSharp SHA-256 `EF314425DADE51F529F184F07BE136CD3C2660A6A81515603C7226FBE7AB1D8C`, BepInEx `5.4.17.0`; five actual native references matched the build cohort. / 实际原生版本与五份引用一致。
- SDK `8.0.424`, full locked Release build: zero warnings/errors. All 3165 tests passed: Contracts 73 / Core 2834 / MCP 258, zero failed/skipped; nine workflow checks passed. Root independently parsed all TRX counters. / 完整构建、全部测试及九项流程通过。

| File / 文件 | Bytes / 字节 | SHA-256 |
| --- | ---: | --- |
| `Spherewright-0.4.0-win-x64.zip` | 36738460 | `A72403495869C4A34DC6A2242354CF3EE6B3DB82E8787AF9F0A6657A609DCBF4` |
| `Spherewright-0.4.0-thunderstore.zip` | 32469734 | `26876DEED92EB824E5C3BA135BC5D71252B3D407D437E04FBD6E4B25A1C29AE2` |

One successful package chain produced this pair. Generation manifest SHA-256: `FE0FE9965F878C1DC6ED81ADDCEF099B5826F3B60071A97D7741517AB676B0A2`; `SHA256SUMS`: `4EBBE5F115B1C74A6FD30CE062A63FE8FB01768EA7D0016F525713E10E7FA315`. Sidecars and every manifest payload hash were independently verified. The manual ZIP has 243 files, including four Plugin DLLs and 224 MCP files; TS has 14 files, including its standard five co-located payload files. The three Spherewright DLLs and both MCP executables identify `0.4.0+b7c0002dbe2e8f5608c5ca140b0c6326a1818021`; Newtonsoft remains its own dependency version.

双包仅生成一次；每份 sidecar、清单和实际文件均核验。手动包为四份 Plugin DLL 加 224 文件 MCP，TS 为标准五文件共置布局；不能把第三方 Newtonsoft DLL 的版本计为 Spherewright 0.4。生成时清单固定记录当时的离线结果，不因后续实机或发布再改写。

The necessary rebuild corrected six bundled-document inputs: stale publication wording and mode-specific recovery-ticket timing. From e018 to b7, the full diff contains only 14 Markdown paths; game code, tests, scripts, projects, resource URI and capabilities are unchanged. All six older 2a/48d/e018 ZIPs remain unchanged. Both new executables independently passed four isolated metadata requests, exactly 64 tools/one resource and byte-identical embedded/packaged English guide; forced bilingual checks passed. Guide hashes: EN `9F48544370E6256F9641565F7B105F2F7667AD851C479F004CC48FCFC7E8476F`, ZH `5A3EEFA0A569D1E5EC216D3CB36E03F4F5BFC81E0A34CF12179DA6AA00C748F6`.

此次必要重包修正随包发布说明和恢复票据时序，没有游戏能力或白名单变化。旧包原字节保留；新双包双语、嵌入资源和准确工具集合均通过。静态公开包审计覆盖 257 文件，敏感信息零发现；308 条可见调试路径均分类为映射根、标准 CI 或相对路径，未知路径为零。这不是杀毒或第三方平台放行证明。

## Bounded installed evidence / 有界实装证据

Each row is its own declared finite phase. Unused requests/time were forfeited; failed phases and their original intents remain preserved. Neither matrix commits a returned valid plan. / 各行独立声明、独立封窗；不拼接失败结果、session 或剩余预算，矩阵不提交返回的有效计划。

| Phase / 阶段 | Declared limit / 原声明上限 | Actual / 实际结果 |
| --- | --- | --- |
| Necessary pre-manual normal Save / 手动切换前保存 | 180 s / 24 RPC / one Save | Passed; 10 RPC, one original poll, 3.656 s, one accepted. Saved 116564210, observed 116564221. |
| First manual cold parent / 首次手动冷切换 | 600 s / 24 RPC / 0 accepted | Failed after one confirmed normal close; 6 RPC / 11.947 s. Archive/install/launch all zero; 1234 protected files unchanged. |
| Manual closed-game continuation / 手动已关闭停点续接 | 600 s / 16 RPC / 0 Close/Save/Load/accepted | Passed; 14 RPC (6 live + 8 isolated), 88.005 s, one archive/official install/known launch, 1234 protected files unchanged. |
| Manual default `29151→29151` resume / 手动默认同版本恢复 | 600 s / 100 RPC / one resume / no manual Save | Passed; 15 RPC, one fresh prepare, four original polls, 9.188 s; one accepted. Saved 116564241, observed 116564317. |
| Complete manual matrix / 手动完整工具矩阵 | 600 s / 148 RPC / 0 accepted | All64 passed in one run; 104 RPC / 36 support reads, normal EOF; recorded RPC span 7.661 s, final observation 116565579. |
| Necessary pre-TS normal Save / TS 切换前保存 | 180 s / 24 RPC / one Save | Passed; 10 RPC, one original poll, 1.688 s; one accepted. Saved 116577349, observed 116577355. |
| Read after owner interruption / 中断后只读核验 | 120 s / 8 RPC / 0 accepted/Save/Load | Passed; 6 RPC, same healthy original world. Saved 116577349, observed 116834806. |
| Necessary interruption-covering Save / 中断后覆盖保存 | 180 s / 24 RPC / one Save | Passed; 10 RPC, one original poll, 1.843 s; one accepted. Saved 116839299, observed 116839307. |
| First final TS cold parent / 首次最终 TS 冷切换 | 600 s / 24 RPC / 0 accepted | Failed after one confirmed normal close; 6 live RPC / 7.094 s. Unit/transaction/metadata probe/launch all unstarted; 1240 protected files unchanged. |
| TS closed-game continuation / TS 已关闭停点续接 | 600 s / 16 RPC / 0 Close/Save/Load/accepted | Passed; 14 RPC (6 live + 8 isolated), 79.478 s, one committed paired transaction/known launch; 1240 protected files unchanged. |
| TS default `29151→29151` resume / TS 默认同版本恢复 | 600 s / 100 RPC / one resume / no manual Save | Passed; 15 RPC, one fresh prepare, four original polls, 8.094 s; one accepted. Saved 116839330, observed 116839427. |
| Complete TS matrix / TS 完整工具矩阵 | 600 s / 148 RPC / 0 accepted | All64 passed in one run; 104 RPC / 36 support reads, normal EOF; recorded RPC span 7.939 s, final observation 116840662. |

Both independent matrices recorded 23 data successes, six prepare successes and 35 expected native safety guards, with zero accepted/unknown actions. Each has 20 unissued colon-bearing sentinel commits strictly before every prepare; actual successful plans are never passed to commit. The identical summary hashes describe identical counts/classes, while separate executable-bound intents and distinct raw RPC/session records prove the two actual runs. Recorded RPC spans are first-to-last logged response timestamps, not an asserted whole-process wall duration.

两种布局分别完整通过 64 工具入口；安全拒绝是实际可调用证据，不表示执行了每项受保护写操作。两轮没有共享成功片段；原始记录及实际可执行文件分别绑定。日志响应时间跨度不冒充整个进程耗时。

The manual failure was a local `Set-Acl` request for unavailable `SeSecurityPrivilege`, before any archive move. Its separate continuation verified existing ownership, used an access-only ACL API without owner/SACL changes or elevation, and retained the already completed close. The TS failure was Root's incorrect selection of a mandatory-parameter metadata CLI wrapper for dot-import; review had checked its hash but missed entry semantics. The separate continuation uses the unchanged official definitions-only helper, whose full source, top-level AST and four-parameter signature were checked. Both original failed results/readiness audits remain, and neither close or Save was replayed. No product code or package changed for either caller correction.

手动失败在移动前，最小修复无需管理员权限；TS 失败在事务意图前，是 Root 配置入口错误及审计入口性质遗漏，修正后明确核对完整 helper 和签名。失败与旧回执全部保留，两次已完成的正常关闭都未重放。两项修正只在本地调用器，不修改候选。

The owner interruption left an unexecuted TS draft expired. It was preserved, never executed or renewed. Fresh verification proved a substantial new natural-running tail; the additional normal Save covered that current progress as a distinct necessary action. It did not replay the preceding terminal Save. The saved checkpoints, not later unsaved tails, are the restore candidates.

中断后先核旧写者已停、实际进程和原身份，健康运行世界没有因此自动重启或恢复。随后为必要冷安装才保存、关闭并默认恢复；过期未执行草稿不续期。自然 tick 不计连续生产信用。

## Continuity, review and limits / 连续性、独审与边界

Both new-source recoveries are same-version default recovery, not another migration. Original 102 Journal entries/five transitions remain durable through sequence 102 with no persistence error; the original two Foundry files and completed generation19 five-object module are retained. The old27 candidate remains retired. The historical unsaved four-unit stone action is not restored-stock credit and was never rekeyed or replayed. No construction, another world or new production acceptance window was added.

两次新源码恢复均为同版本，不重复已确认的 `29145→29151` 迁移；原 Journal、五对象及所有成功前缀保全，未清空或改写旧进度。旧三级链和 36060-tick 生产验收仍适用于冻结 2a/29145 的原 session，不能继承为 b7 的新生产窗口。

Root was the sole game writer; the auditor used offline evidence only, and the offline maintainer serialized Git/gh. Raw identity, credentials, descriptors, requests, private paths and full receipts remain owner-only local. This report contains only sanitized facts and evidence hashes.

| Protected review / 受保护独审 | SHA-256 |
| --- | --- |
| Static final pair / 最终双包静态审计 | `5751A0605FC9D01697B92D9A7F2E5E6E30A9955418E6E9E4C8FF473928D927AA` |
| Manual install / 手动安装 | `25CBD9DB40C2941935FB718EBC017ECFE61F0D9AB27830345846B9C9D38CF06B` |
| Manual default recovery / 手动默认恢复 | `3FE6CA1DDB3410661AF37F72D7B3A1D031848B0C28B534C64129E0BFE6FE2A21` |
| Complete manual matrix, corrected descriptive receipt / 手动完整矩阵已纠正描述回执 | `8ACDE27AA1DC01ADF9A8EA102F73E0FD0E19BF427421F28C06379523899C927B` |
| Pre-TS Save / TS 前保存 | `4499BCB2E158EEFB3F87D662DCF495F3C74D2828185461A76CD87C04FC313CDC` |
| Interruption-covering Save / 中断后覆盖保存 | `6D791D9861BA3DBB151DB2B4D7B4EFCBB7FCC7D8A3E6313337A07997A656424D` |
| Original failed TS boundary / 原失败 TS 边界 | `93872C5B8D9DE4F9387404B33C79BFCB64C07F09A5591F588EBE99841F509431` |
| TS installation / TS 安装 | `E93D976949717B9A9AB394DE7F625991332D59D04122562850B12CA2E30D7DCF` |
| TS default recovery / TS 默认恢复 | `698B2B8CA4DF89C1E5C647A9B70534B676000062ADB7F5AAAF296FC5A5C29D97` |
| Complete TS matrix / TS 完整矩阵 | `29531C374EBFBBC73863695443D24EED08F94EA73AC36313C12BA0DEB0566686` |

All final installation, recovery, matrix and Save result reviews passed independently. Source-specific runtime facts receipt: `77C4902ADB5443904001397FE40C8CE76C3034E8618C282AFD7026F148734A93`. At this qualification checkpoint, no tag/Release/upload has yet occurred; actual publication results are recorded separately after execution. / 所有实机阶段及保存的独立结果审计均已通过，当前双包具备发布资格，实际发布结果以随后真实执行记录为准。

Known unverified areas remain separate Mod Manager/r2modman profiles, another computer, installation transaction-crash restoration, the stationary-carrier-600-tick positive live branch, arbitrary saves, broad third-party compatibility, combat/multiplayer and actual interstellar flight/logistics. Fixing local callers and completing a normal transaction do not prove crash restoration or a new production window.

## Distribution check / 分发核查

The owner authorized GitHub and the existing Thunderstore update; no new namespace or package identity is planned. Candidate bytes and source remain b7; later factual-documentation commits must not move the formal tag to a different source or trigger another package build.

[Nexus mod23 Files](https://www.nexusmods.com/dysonsphereprogram/mods/23?tab=files) was checked read-only at the owner's request. Its existing 0.3.3 primary file is quarantined; top/file version is `0.33`, description/native remain 0.3.3/28529, and its restrictive permission preset differs from its MIT description. Public pages did not expose a detection-engine report; the existing-SHA VirusTotal page returned only a JavaScript shell and the anonymous file-version API returned 401. None of those is a clean scan result or proof of a false positive. The new manual ZIP needs no Nexus-specific rebuild, but no Nexus upload/appeal/contact/rescan occurred. [Official quarantine guidance](https://help.nexusmods.com/article/117-why-has-my-mod-been-quarantined) requires actual platform review; preserve the old file. Protected read-only receipt: `FF50B5EBCF03046040C865F3D4663C4A4D84955B842FC88276AE5EAB35F5F5CB`.

Nexus 当前旧版文件隔离尚未解除，具体命中和原因仍未知，不能称为误报或新包已放行。更新时还需统一版本、支持的游戏版本、手动安装说明、校验和及权限预设；不另建 Mod、不删除旧文件绕过审核。此次仅核查，不代用户联系第三方。

Current writer state: requests stopped, no MCP child/in-flight/unknown action; DSP6308 remains healthy in the original loaded world. Last saved/observed: 116839330/116840662. Five newly accepted actions are three necessary normal Saves and two default same-version recoveries; each finished its own finite phase. Under the old convention only, 637/238 + 5 = 642/243 is arithmetic, not a renewed global budget. Remaining phase budgets are zero/forfeited. Publication requires no automatic Save, exit, restart or Load at task end.
