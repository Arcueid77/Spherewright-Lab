# Spherewright-Lab

Spherewright-Lab 是 Spherewright 的公开场景、运行交接与黑盒验收仓。产品的 Plugin、MCP、Contracts、Bridge.Core、通用测试和打包实现保留在 [Spherewright](https://github.com/Arcueid77/Spherewright)；本仓通过固定、只读的产品子模块消费准确源码，不反向成为产品构建依赖。

This repository owns public scenarios, operational handoffs and black-box acceptance evidence. It consumes an exact read-only Spherewright submodule and is never a product build dependency.

## 中文

### 先读这些文档

| 目的 | 入口 |
| --- | --- |
| 工作规则与写入边界 | [AGENTS.md](AGENTS.md) |
| 当前源码、实装、候选与历史锁 | [source-lock.json](source-lock.json) |
| 当前授权范围 | [operations/standing-authority.md](operations/standing-authority.md) |
| 现在从哪里续跑 | [活动交接页首：已证结果、卡点、下一步](operations/active-handoff.md) |
| 0.6 Ascension 整版目标和依赖 | [实施与验证计划](scenarios/v0.6-ascension/implementation-plan.md) |
| 0.6 各次实跑的依据 | [Ascension 场景记录](scenarios/v0.6-ascension/current-status.md) |
| Voyager 固定结果与经验 | [Voyager 快照](scenarios/v0.5-voyager/current-status.md)、[0.5 经验复盘](operations/lessons/v0.5-voyager-2026-10-29.md) |

`operations/current-status.md` 是受 manifest 保护的历史导入，不得覆盖。续跑只从活动交接页首取下一步；需要核实某个结果时，再查对应日期的场景记录。

### 当前基线

0.6 Ascension 验证 Caph II 持续制造与发射、壳面闭合、接收站实际供电，以及正常存读档后能否延续。所选产品源码、实装与候选包状态从根目录的 `source-lock.json` 读取，首页不另抄版本号。

0.5 的结果保留在 [Voyager 基线交审](releases/v0.5.0/review-delivery.md)、[首帆/首枚火箭交审](releases/v0.5.0/expansion-review-delivery-2026-11-06.md)和[叠放/步行快照](scenarios/v0.5-stacking-navigation/current-status.md)中，可按需引用。

### 初始化与离线核验

```powershell
git clone --recurse-submodules https://github.com/Arcueid77/Spherewright-Lab.git
cd Spherewright-Lab
pwsh -File scripts/bootstrap.ps1
pwsh -File scripts/verify-source-lock.ps1
pwsh -File scripts/verify-evidence.ps1
```

`bootstrap` 只初始化固定子模块并建立忽略目录，不追踪最新产品 main，也不覆盖意外 HEAD 或 dirty 子模块。上述检查只验证文件、锁和证据，不执行游戏动作；缺席的受保护本地原件或冻结 ZIP 会明确报告为未核验，不能伪报通过。

### 产品采用与预览包

`deps/Spherewright` 默认只读。通用产品修改必须在独立 clone/worktree 中完成，先通过完整相关测试和准确 SHA 的绿色 CI，再由本仓更新 gitlink 与根锁。源码采用、实际安装、最终候选和实机验收分别记录。

```powershell
pwsh -File scripts/update-spherewright.ps1 -Sha <FULL_SHA> -NewLockPath .local/reviewed-next-lock.json
```

更新入口要求 Lab 干净、准确产品 CI 成功，只暂存子模块和锁文件并生成摘要，不自动 commit/push。开发锁的 `acceptance.scope: historical_reference`、`sourceLock` 和 `sourceLockSha256` 固定历史验收来源；旧验收不转移到新源码。未构建最终候选时两个 `packages` 字段必须同时保持 `null`，不得借用旧包或伪造 hash。

需要本机合法 DSP Native 引用和 .NET 8 SDK 时，可生成独立开发预览：

```powershell
pwsh -File scripts/package-from-submodule.ps1 -DspDir <LOCAL_DSP_DIRECTORY> -DotNetPath <DOTNET_SDK_EXECUTABLE>
```

预览输出到忽略的 `artifacts/previews/`，不覆盖冻结包、不部署、不接触游戏。预览资格不等于最终候选或实机验收。

### 场景与证据导航

- [CommandDeck 蓝矩阵验收](scenarios/commanddeck-blue/acceptance-2026-11-15.md)：独立测试世界的自动产线、连续采样与正常保存。
- [叠放/步行快照](scenarios/v0.5-stacking-navigation/current-status.md)和[验证计划](scenarios/v0.5-stacking-navigation/validation-plan.md)：0.5 的九模型范围及逐行结果。
- [Voyager 场景](scenarios/v0.5-voyager/README.md)、[固定验收](scenarios/v0.5-voyager/acceptance.md)和[活动快照](scenarios/v0.5-voyager/current-status.md)：已闭合基线与首帆/首枚火箭扩展。
- [v0.4 场景](scenarios/v0.4-final/README.md)、[原验收](scenarios/v0.4-final/acceptance.md)和[拓扑边界](scenarios/v0.4-final/topology.md)。
- [0.4 最终摘要](releases/v0.4.0/validation-summary.md)、[完整证据](releases/v0.4.0/evidence/README.md)、[规范化清单](releases/v0.4.0/manifests/evidence-manifest.json)和[冻结包校验和](releases/v0.4.0/hashes/SHA256SUMS.txt)。
- [公开安全审查](operations/public-review-2026-10-16.md)、[游戏时间线](operations/gameplay-timeline.md)、[脱敏经验](operations/experience-ledger.md)和[事故记录](operations/incident-log/full-history.md)按各自日期和范围查阅。

正式 [`v0.4.0`](https://github.com/Arcueid77/Spherewright/releases/tag/v0.4.0) 绑定 `b7c0002dbe2e8f5608c5ca140b0c6326a1818021`；冻结生产验收源码 `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9` 和不可变迁移快照 `14478a03c64c550e644c559405c8496b647552e7` 保留各自历史范围。Thunderstore 网站上传结果单独跟踪，不授权再次发布。

Save、ticket、凭据、私有身份、未脱敏请求、运行描述符、私有路径和转储不得进入 Git。`.local/` 与 `artifacts/` 保持忽略；经验账本原件依所有者选择仅保存在受保护本地目录，Git 只含脱敏派生副本。公开仓库不代表本地原件可用，也不授予游戏或发布权限。

## English

### Start here

Start with [AGENTS.md](AGENTS.md), [source-lock.json](source-lock.json) and the top of the [active handoff](operations/active-handoff.md). The [Ascension plan](scenarios/v0.6-ascension/implementation-plan.md) describes 0.6 outcomes and dependencies; the [scenario record](scenarios/v0.6-ascension/current-status.md) holds dated evidence. See the [standing authority](operations/standing-authority.md) for the existing grants.

The separate [CommandDeck blue-matrix acceptance](scenarios/commanddeck-blue/acceptance-2026-11-15.md) records its automatic line, continuous samples and normal save.

`operations/current-status.md` is a manifest-protected historical import; never overwrite it. Resume from the top of the active handoff. Consult dated entries when an earlier result matters.

### Current baseline

Ascension tests sustained local manufacture and launch on Caph II, a closed shell, actual receiver output, and continuity after a normal save and cold recovery. The root lock records the selected source, installation and package state.

0.5 results remain in the [Voyager baseline review](releases/v0.5.0/review-delivery.md), [first-sail/first-rocket review](releases/v0.5.0/expansion-review-delivery-2026-11-06.md) and [stacking/navigation snapshot](scenarios/v0.5-stacking-navigation/current-status.md) with its [validation matrix](scenarios/v0.5-stacking-navigation/validation-plan.md).

### Checks and source adoption

```powershell
git clone --recurse-submodules https://github.com/Arcueid77/Spherewright-Lab.git
cd Spherewright-Lab
pwsh -File scripts/bootstrap.ps1
pwsh -File scripts/verify-source-lock.ps1
pwsh -File scripts/verify-evidence.ps1
```

These are file/lock/evidence checks, not gameplay. Missing protected originals or frozen ZIPs remain explicitly unverified.

Develop reusable product changes in an independent clone/worktree. Commit and obtain green exact-SHA product CI before advancing Lab's read-only gitlink and lock. Source adoption, installation, candidate generation and live acceptance are separate states.

```powershell
pwsh -File scripts/update-spherewright.ps1 -Sha <FULL_SHA> -NewLockPath .local/reviewed-next-lock.json
pwsh -File scripts/package-from-submodule.ps1 -DspDir <LOCAL_DSP_DIRECTORY> -DotNetPath <DOTNET_SDK_EXECUTABLE>
```

The update entry stages only the submodule and reviewed lock; it does not commit or push. Preview packaging writes only to ignored `artifacts/previews/` and neither deploys nor touches the game. Unbuilt final packages remain paired `null`; historical evidence never substitutes for new-source qualification.

The published [`v0.4.0`](https://github.com/Arcueid77/Spherewright/releases/tag/v0.4.0) source is `b7c0002dbe2e8f5608c5ca140b0c6326a1818021`. Frozen production source `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9` and immutable transfer snapshot `14478a03c64c550e644c559405c8496b647552e7` retain their distinct historical scopes.

Saves, tickets, credentials, private identities/paths, unsanitized requests, runtime descriptors and dumps stay out of Git. `.local/` and `artifacts/` remain ignored. Public visibility supplies neither protected originals nor execution/publication authority.
