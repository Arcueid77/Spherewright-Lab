# 2026-10-17 package callability / 发布包调用验证

Status: **passed for the owner-defined installed MCP-callability phase; independent result audits passed**. This phase uses the owner's criterion that every MCP capability can be called. Data, preparation and expected native safety rejection are distinct outcomes; it does not claim that every guarded write was executed. Formal publication remains pending owner review.

状态：**本次实机 MCP 调用验收通过，两种布局各自完整 64 工具结果及独立审计均通过**。本阶段按所有 MCP 能力可调用验收；数据、预检成功与预期原生安全拒绝分别记录，不声称执行了所有受保护写操作。正式发布仍待所有者审核。

| Criterion / 原条款 | Existing evidence and applicable version / 证据及适用版本 | Real gap / 真实缺口 | Minimum next step / 最小下一步 | Pass condition / 通过条件 |
| --- | --- | --- | --- | --- |
| Exact package identity / 精确包身份 | Clean pushed `e018b7f45c70f5fe029418cad987af794b5cb9bf`, exact successful product CI, matching manual/Thunderstore packages and installed Plugin/MCP/Contracts/Core. / 同一干净已推送源码、准确 CI、双包和实机四组件一致。 | None for this pair. / 此双包无身份缺口。 | Preserve the immutable candidate bytes. / 保留原候选字节。 | Same clean source SHA and exact payload hashes throughout installation/runtime. / 全程同源且 payload hash 匹配。 |
| Every installed MCP capability callable / 实机 MCP 全部可调用 | Each layout independently completed all 64 names in one v2 run: 104 RPC, 23 data successes, six prepare successes and 35 expected native guards; zero accepted/unknown. / 每布局各一轮完整 64，104 RPC，23 数据、6 预检、35 预期原生拒绝，无接受或未知。 | No remaining callability gap. / 调用验收无剩余缺口。 | Preserve the independent audit of raw envelopes, order, original sentinels and normal EOF. / 保留原封包、顺序、原哨兵及正常退出的独立审计。 | Exact registered set/one readable resource; every tool invoked without protocol, schema, transport or internal failure. / 完整注册集合及可读资源，逐工具调用无协议、参数结构、传输或内部错误。 |
| Original-world continuity / 原世界连续性 | Owner-confirmed `29145→29151` migration retained all 102 Journal entries, made the fifth transition durable and normally saved; subsequent `29151→29151` default recovery succeeded. / 明确确认的迁移保留全部 102 条，落盘第五链并正常保存，随后同版本恢复成功。 | No remaining continuity gap in this phase. / 本阶段连续性无剩余缺口。 | Preserve the independently verified original identity, complete Journal, module bytes and renewed ticket. / 保留已独立核验的身份、完整 Journal、模块原字节及新票据。 | Same original world, complete durable Journal/five links, completed five objects, normal save and same-version recovery. / 原世界、完整持久 Journal/五链、五对象、正常保存及同版本恢复。 |
| Local update layout / 本机更新布局 | Official manual transaction proved 4 Plugin + 224 MCP files; later standard TS transaction proved 5 Plugin + preserved matching 224 manual MCP files. Both loaded through their actual installed executable. / 手动 4+224 与标准 TS 5+224 事务及实际安装程序调用均完成。 | No remaining local-layout gap. / 本机布局无剩余缺口。 | Preserve all verified file hashes and terminal records/no pending marker. / 保留全文件 hash、终态及无待处理标记的核验。 | Matching source, no pending transaction, normal MCP exit, live calls and protected recovery. / 同源、无待处理事务、正常退出、实机及恢复有证据。 |

## Candidate, support and build / 候选、支持与构建

Source is `e018b7f45c70f5fe029418cad987af794b5cb9bf`, product version `0.4.0`. The full locked Release build passed with SDK 8.0.424 and zero warnings/errors. All 3165 tests passed (Contracts 73 / Core 2834 / MCP 258), with nine workflow checks and [exact product CI 38951284927](https://github.com/Arcueid77/Spherewright/actions/runs/38951284927). The active Lab gitlink/lock adopted e018 at `fc6ab40974ca0d91cc69befa5d5ba359445ed745`; the pre-runtime checkpoint `bfe750e3aa02d52411f162f8d7258b2da5e665f7` passed [exact Lab CI 38954203956](https://github.com/Arcueid77/Spherewright-Lab/actions/runs/38954203956). Later factual documentation does not rebuild these packages.

源码和产品版本如上，完整锁定构建零警告/错误，3165 测试、九项流程与准确源码 CI 通过；Lab 已固定采用 e018。后续事实文档引用此候选，不因此反复打包。

| Candidate / 候选 | Bytes / 字节 | SHA-256 |
| --- | ---: | --- |
| `Spherewright-0.4.0-win-x64.zip` | 36737536 | `D4988D572F84FEB317ABC9D0E75B404E3CE68ED6F4FD39B0E334C865237C4833` |
| `Spherewright-0.4.0-thunderstore.zip` | 32469237 | `067F8598B6E4FA986F63B634E0C712AC57CE6B2EFA5F8018FA287CA15E782231` |

Both manifests declare the same clean source and native `0.10.35.29151`; bilingual package smoke, exact 64-name tool set and one readable resource passed. Candidate-manifest SHA-256 is `F46BD6A4B628E0C18C4B8AFBC9C7245F29E31702405F9D5930BB058BCB3668B9`. The checksum list and per-ZIP sidecars agree.

双包清单同源且目标原生为 29151，双语包检查、准确 64 工具集合及单个可读资源通过；清单、校验和表与逐包 sidecar 一致。

Actual tested environment: Windows x64, DSP `0.10.35.29151`, BepInEx `5.4.17.0`, the original peaceful owned non-sandbox 1× world. Native Assembly-CSharp SHA-256 is `EF314425DADE51F529F184F07BE136CD3C2660A6A81515603C7226FBE7AB1D8C`. The three Spherewright DLLs and each layout's MCP executable report `0.4.0+e018b7f45c70f5fe029418cad987af794b5cb9bf` and match their package bytes. The manual MCP executable hash is `17A650257D4EB4E227D125D77A363C5A2716E979AD997BD0AC2F5F31FCF5D4D2`; TS single-file MCP is `9AD48173B3C84E790FD6B011A8BD92AC0A693C8DF5F3AA91E7404D6A33795F31`.

实际环境是 Windows x64、29151、BepInEx 5.4.17.0 与原和平、非沙盒、1× owned 世界。本库 Plugin、Contracts、Core 与 MCP 四组件的版本和包字节一致；两个 MCP 程序分别按其原包 hash 验证。

Frozen `2a7a98d` and maintenance `48d84e1` packages remain byte-unchanged. Frozen source-lock SHA-256 is `A2537F906A058593E05E1BF155AFE6D955F6B6E5110E3B658648E4B67CAF16C7`; evidence manifest is `F191917B5279F2A4EA5BE3CF3A6F227801C3AB1CC42693C078531AD22CF62C50`. The active lock explicitly labels that acceptance `historical_reference`, with `acceptanceAppliesToActiveSource=false`.

冻结旧包、锁和验收原件未改。旧生产验收不继承到新源码或新 session；本次仅认证下述真实包调用、安装和连续性。

## Actual finite stages / 实际有限阶段

Every stage declared its own finite limits before execution, closed afterward and forfeited unused requests/acceptances. No running window was extended and no session or gap was combined. Root was the sole game writer; the runtime auditor used protected files only, with zero Game/Bridge/MCP/process-control calls.

每阶段均事前声明预算、结束即关闭并放弃余量，不运行中续期、不拼 session/缺口。Root 单写者，独立审计者只读受保护文件，不调用游戏或控制进程。

Load/Save counts cover this caller's published requests; preservation covers the declared protected-file set. Native normal resaves performed by the resume coordinator are reported in the accepted recovery rows. / Load/Save 按本调用器的公开请求计数；保护检查覆盖声明的原件集合，恢复协调器的原生正常重存已在相应恢复行说明。

| Stage / 阶段 | Declared bound / 事前上限 | Actual / 实际结果 |
| --- | --- | --- |
| Manual cold installation / 手动冷安装 | 600 s / 24 RPC; one close/install/launch; 0 accepted/Load/Save. / 各一次关闭、安装、启动。 | 72.45 s / 22 RPC, paired transaction and launch succeeded; all 1224 protected originals unchanged. Final prepare correctly refused incomplete native preloading; this failed final preflight is retained. / 事务成功，原件无变化，末端预载拒绝保留。 |
| Stable-menu preflight / 稳定菜单预检 | 120 s / eight RPC, read-only. / 只读。 | 2.43 s / seven RPC; exact expired-primary prepare successful, sole blocker subsequent owner confirmation. Zero consumption/Load/Save/accepted. / 精确预检成功，仅待后续确认。 |
| Confirmed original migration / 明确确认的原档迁移 | 600 s / 100 RPC, 570 s request deadline, one resume accepted, no separate manual Save, at most 80 original-action polls ≥2 s apart. | 12.922 s / 15 RPC / four polls / one accepted and terminal success. Candidate 116353747, saved 116353778, observed 116353817. Original 102 entries/four links retained; fifth durable link proved before automatic normal resave/new matching ticket. / 原条目与链保留，第五链持久化后原协调器正常重存、签票据。 |
| Manual first matrix / 手动首轮矩阵 | 600 s / 148 RPC, zero accepted. | All 64 invoked, 62 passed, 104 RPC; two caller parameter errors, zero accepted/unknown. This attempt remains failed and is not combined with v2. / 两处 caller 参数错误，整轮失败保留，不与后轮拼接。 |
| Manual complete v2 / 手动完整第二轮 | Fresh 600 s / 148 RPC, 575 s request deadline plus cleanup reserve, zero accepted. | 64/64, 104 RPC, 36 support reads; 23 data / six prepare / 35 expected native guards. First-to-last recorded RPC span 6.142 s, normal EOF within the fixed window. / 独立完整通过，RPC 时间跨度不冒充整个进程耗时。 |
| Necessary pre-TS save / 切换前必要保存 | 180 s / 24 RPC, one Save accepted, at most 12 original polls ≥2 s apart. | 1.797 s / ten RPC / one poll / one accepted, terminal success. Saved 116386485, observed 116386495; renewed native51 ticket. / 保留手动验证期间自然运行进度。 |
| TS standard cold installation / TS 标准冷安装 | 600 s / 24 RPC (live ≤16, isolated metadata ≤8), one close/install/launch, zero accepted/Load/Save. | 80.889 s / 20 RPC (12 live + eight isolated); 5+224 exact-file transaction, one normal launch, healthy unloaded menu. All 1230 current protected files unchanged. / 精确安装、正常启动，1230 份当前原件无变化。 |
| Same-version default recovery / 同版本默认恢复 | 600 s / 100 RPC, 570 s request deadline, one resume accepted, no separate manual Save, ≤10 preloading-only prepares and ≤70 original polls ≥2 s apart. | 9.687 s / 15 RPC / one prepare / four polls / one accepted and terminal success. Exact 29151→29151 candidate 116386485; normal saved 116386517, observed 116386612. Original identity, 102 entries and all five links retained; new matching ticket. / 原世界同版本正常恢复，无新迁移、无额外手动保存。 |
| TS complete v2 / TS 完整第二版矩阵 | Fresh 600 s / 148 RPC, 575 s request deadline plus cleanup reserve, zero accepted. | 64/64, 104 RPC, 36 support reads; 23 data / six prepare / 35 expected native guards. First-to-last recorded RPC span 7.993 s; normal EOF within the fixed window. Final session observed 116388612, saved 116386517, healthy/writable/no unknown. / 单轮完整通过，末次 session 健康。 |

The matrix uses 24 reads, then all 20 commits with unique impossible `:`-containing sentinel tokens before any prepare, then 20 fresh prepares. Returned valid plan tokens are never committed. Exact published schemas, all 64 unique names and the resource are checked. Expected native refusals prove callable guarded routes, without bypassing gates or mutating the world. The v2-only changes use freshly read accepted fuel/count/stack size for refuel and an inspected miner in the existing dismantle scope; classifier, order, barriers and budgets did not change. No product tool, whitelist or upgrade type was expanded.

矩阵先 24 读取，再用绝不可能由原生签发且含冒号的独立哨兵调用 20 commit，最后 20 fresh prepare；不提交返回的有效计划。第二版只修正真实燃料数量/栈大小和现有拆除范围中的矿机参数，未放宽验收或原生能力。

## Preserved state and next safe entry / 保留状态与下一安全入口

- Last actual save is `116386517`, last MCP observation `116388612`; Journal is 102/102 durable with five transitions, no persistence error or pending persistence. The same completed five-object generation 19 and its original two protected history files are retained; no rebuilding or repeated five-object continuation was performed. / 最新保存/观察与持久 Journal 如上，五对象和历史文件保留，无重复施工。
- Three new accepted actions occurred in three separate one-accepted stages: migration, necessary normal Save and same-version resume. Historical lifetime 634 / whole 235 would arithmetically become 637 / 238 if its old convention is retained; this is explicit arithmetic, not an invented new global budget contract. The old fixed-20 window stays closed at ten accepted/ten unused forfeited; every new phase is closed with no reusable remainder. / 三次独立接受不续旧预算，637/238 仅沿旧口径的明确算术。
- The old 27-object candidate remains retired. The historically unsaved four-unit stone action is neither restored-stock credit nor permission for a new-key replay. Prior blueprint/Governor passes are not reopened. / 旧 27 对象退役，未保存石矿不补记或换键，旧通过范围不重开。
- No new ≥36000-tick production window, throughput, kit refresh or mid-chain construction recovery was claimed. Natural elapsed ticks and completed-module recovery cannot substitute for those original criteria. Frozen long-window results keep their original source/session scope. / 本次不把自然时间、建成后的恢复冒充新长窗、出发套件或三级链中途续建证明。
- Current installation is TS standard five files plus the matching 224-file manual MCP, all source e018/native29151. Root has stopped issuing game requests, all MCP children exited, and the healthy loaded DSP remains running. There is no in-flight or unknown action. A chat/session boundary alone is no reason to Save/Exit/Load. / 当前安装同源；无请求在途、无 unknown，健康世界保持运行，交接不自动保存/退出/重载。
- Root owns only this report and `operations/active-handoff.md`; the offline maintainer alone serializes explicit-path commit/push/exact-SHA CI. No source hot replacement, immutable evidence rewrite or candidate rebuild is needed for these facts. Any later entry first confirms the old writer stopped and freshly checks process/source/native/session/ownership; healthy DSP resumes observation directly. / dirty 归属、单写者和下一 fresh 入口明确，纯事实保存不改候选。

## Protected evidence index / 受保护证据索引

Raw requests, plan/action/key, identities, ticket/primary replicas, paths, runtime descriptors and logs remain protected-local under the owner-only validation evidence root, never Git. The following names are local evidence labels with hashes, not published raw payloads.

原始请求、计划/action/key、身份、票据/主档、路径、描述符和日志只留仅所有者可访问的本地证据目录；下列仅为脱敏标签与校验和。

| Receipt / 回执 | SHA-256 |
| --- | --- |
| Original migration result independent audit / 原迁移结果独立审计 | `418BC9DEAF475B87E2ADEE9E1EDAD7BA3A99F15214D7EE72B4FC35F48E448606` |
| Manual complete v2 independent audit / 手动完整 v2 独立审计 | `06B05DB8101DFA8C048FF3B8C20C33D9775726AD4E792362F1FEA355327A16B1` |
| Necessary-save caller audit / 必要保存 caller 审计 | `90B53A42A53E2FCF586DFEE32823C0D1C79361A54944B99B2DB7F43F2715B448` |
| TS cold parent independent readiness audit / TS 冷切换事前独立审计 | `CFA48F8D08DF43B82886259D93278D89A5CF9B556E215B7121824243D4129BDA` |
| Same-version resume caller independent audit / 同版本恢复 caller 独立审计 | `7C52BACDF5F5C9CC7DB6348D43E3D6CEF3A603EFC49BCF666D438686EC56AEFE` |
| TS installed result independent audit / TS 安装结果独立审计 | `22B06C5C6F3237C06D5589DB8E5DD972D12C30289A3AE4FD55039AB482F668F1` |
| Same-version recovery result independent audit / 同版本恢复结果独立审计 | `BF150048B2E480D04D84E99107F109450E910275B804907671F301B3C59E0556` |
| TS complete v2 independent audit / TS 完整 v2 独立审计 | `B7EB832FC442D5B10219ED259040C5062453318682DB543F6BA0A17EB4B8CFDC` |

The first manual installation's independent result audit remains `DFE1D9D9FCFA4843990480987C540872EB6AE52EDF5B3FE350CC151765A1CD15`, covering all 228 payload hashes, terminal paired transactions/no pending marker, owner-only 609-file handoff, preserved old TS archive and 613 key originals. Original pre-dispatch timestamp-type failure, prior caller/config/audits, initial startup timeout and native preload rejection remain preserved. None is retroactively counted as a successful complete phase.

首轮手动安装审计及历史失败记录仍保留；不隐藏失败、不补写事前计划、不把部分成功冒充完整阶段。

## Updating the mod / 如何更新 Mod

The current public Thunderstore package is still **0.3.3**, under team **Arcueid_77**, name **Spherewright**. [Official package page](https://thunderstore.io/c/dyson-sphere-program/p/Arcueid_77/Spherewright/) and [Thunderstore update rules](https://wiki.thunderstore.io/mods/updating-a-package) were checked on 2026-10-17. The existing package is updated by keeping team/name and uploading a higher numeric `version_number`; published version contents are immutable, including README changes. This task has not uploaded 0.4.0, created a tag or GitHub Release.

当前商店仍是 Arcueid_77/Spherewright 0.3.3。更新原包须保持团队/名称，使用更高的数字版本；已发布版本内容（包括 README）不可替换。本次没有上传 0.4.0、创建 tag 或 GitHub Release。

For local manual updates, normally save any intended progress, stop the connected MCP and exit DSP, then run the complete matching package installer. Reinstalling the same MCP version uses its documented `-Force` without bypassing integrity/process/transaction gates. For a published manager update, use the selected profile and keep Plugin/MCP/shared assemblies together; register the profile's new MCP path. Do not leave duplicate Plugin copies or overwrite loaded DLLs. The local standard TS layout and official transaction path were actually tested here; a separate r2modman/Mod Manager profile and another computer were not.

本机手动更新先正常保存需保留的进度，停 MCP、正常退出 DSP，再运行完整同源包安装器；同版本重装按文档使用 `-Force`，不能绕过校验或事务门。商店正式发布后可在选定管理器 profile 更新整套组件，并使用该 profile 的 MCP 路径，避免双 Plugin 或覆盖已加载 DLL。本次实际测试标准 TS 布局及官方事务路径，不冒充独立管理器 profile 或另一台电脑验证。

The package-callability candidate passed independent audit and is ready for owner review after the factual checkpoint is saved and its exact CI completes. Known unverified areas retain their original limits: arbitrary saves, Dark Fog/combat, multiplayer/Nebula, broad third-party Mods, another computer, independent manager profiles, installation crash-restoration and the stationary-carrier-600-tick positive live branch. See the product's [release notes](https://github.com/Arcueid77/Spherewright/blob/e018b7f45c70f5fe029418cad987af794b5cb9bf/docs/release-notes/v0.4.0.md) and [installation guide](https://github.com/Arcueid77/Spherewright/blob/e018b7f45c70f5fe029418cad987af794b5cb9bf/docs/release-installation.md), read alongside this newer runtime evidence.

本次调用验收及独立审计通过，事实检查点保存并取得准确 CI 后即可由所有者审核；任意存档、战斗/多人、广泛其他 Mod、另一台电脑、独立管理器 profile、安装中断恢复与静止运输船 600 tick 正向实机分支仍未验证。候选自带说明按原源码固定，由本报告补充更新的实机事实。
