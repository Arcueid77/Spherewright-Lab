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
| 当前安全交接 | [operations/active-handoff.md](operations/active-handoff.md) |
| 当前叠放/步行任务 | [scenarios/v0.5-stacking-navigation/current-status.md](scenarios/v0.5-stacking-navigation/current-status.md) |
| 当前验证计划 | [scenarios/v0.5-stacking-navigation/validation-plan.md](scenarios/v0.5-stacking-navigation/validation-plan.md) |
| Voyager 固定结果与经验 | [Voyager 快照](scenarios/v0.5-voyager/current-status.md)、[0.5 经验复盘](operations/lessons/v0.5-voyager-2026-10-29.md) |

`operations/current-status.md` 是受 manifest 保护的历史导入，不是当前状态，不得覆盖。活动快照和交接采用“最新段落在前”的记录方式；较早段落只保留各自历史范围，不要把其中的“下一目标”当成当前指令，也不要加载完整历史账本作为工作计划。

### 当前基线

| 项目 | 当前状态 |
| --- | --- |
| 当前任务 | 叠放/步行验证：9 个模型、19 组有向组合，自演化研究站及黑雾科研/材料已移出本轮 |
| 活动源码与开发实装 | `28f4af96ba666998d9f82f8cd529c9a7911978ed`，产品 `0.5.0`，DSP `0.10.35.29151`；以根锁为机器可读依据 |
| 当前运行态 | `not_running`；最新正常保存、完整备份和后续逐行验收以叠放/步行活动快照为准 |
| 当前候选字段 | 根锁为 `development`，`packages.manual` / `packages.thunderstore` 均为 `null`；最终发行包留待当前功能验收闭合 |
| Voyager 基线 | 原三项条款已闭合，[固定基线交审](releases/v0.5.0/review-delivery.md)及旧双包不改 |
| 首帆/首枚火箭扩展 | 2026-11-06 已有界闭合并形成交审双包，选定源码 `d3b7ac897bb44d62c8a7ed54c51a55ff2b8de7b0`；[固定交审记录](releases/v0.5.0/expansion-review-delivery-2026-11-06.md)保留证据边界，不正式发布 |

当前验证目标包括 44 座测试建筑上限及对应科研/物料范围；每个模型、组合、功能和恢复行仍须分别通过，不能用已完成的小仓库三层正例代替完整矩阵。游戏和 MCP 当前均正常退出，不因阅读文档自动启动、载入或推进游戏。

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

- [叠放/步行活动快照](scenarios/v0.5-stacking-navigation/current-status.md)和[验证计划](scenarios/v0.5-stacking-navigation/validation-plan.md)：当前九模型任务及逐行结果。
- [Voyager 场景](scenarios/v0.5-voyager/README.md)、[固定验收](scenarios/v0.5-voyager/acceptance.md)和[活动快照](scenarios/v0.5-voyager/current-status.md)：已闭合基线与首帆/首枚火箭扩展。
- [v0.4 场景](scenarios/v0.4-final/README.md)、[原验收](scenarios/v0.4-final/acceptance.md)和[拓扑边界](scenarios/v0.4-final/topology.md)。
- [0.4 最终摘要](releases/v0.4.0/validation-summary.md)、[完整证据](releases/v0.4.0/evidence/README.md)、[规范化清单](releases/v0.4.0/manifests/evidence-manifest.json)和[冻结包校验和](releases/v0.4.0/hashes/SHA256SUMS.txt)。
- [公开安全审查](operations/public-review-2026-10-16.md)、[游戏时间线](operations/gameplay-timeline.md)、[脱敏经验](operations/experience-ledger.md)和[事故记录](operations/incident-log/full-history.md)按各自日期和范围查阅。

正式 [`v0.4.0`](https://github.com/Arcueid77/Spherewright/releases/tag/v0.4.0) 绑定 `b7c0002dbe2e8f5608c5ca140b0c6326a1818021`；冻结生产验收源码 `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9` 和不可变迁移快照 `14478a03c64c550e644c559405c8496b647552e7` 保留各自历史范围。Thunderstore 网站上传结果单独跟踪，不授权再次发布。

Save、ticket、凭据、私有身份、未脱敏请求、运行描述符、私有路径和转储不得进入 Git。`.local/` 与 `artifacts/` 保持忽略；经验账本原件依所有者选择仅保存在受保护本地目录，Git 只含脱敏派生副本。公开仓库不代表本地原件可用，也不授予游戏或发布权限。

## English

### Start here

Read [AGENTS.md](AGENTS.md), [source-lock.json](source-lock.json), [standing authority](operations/standing-authority.md), [active handoff](operations/active-handoff.md) and the [stacking/navigation snapshot](scenarios/v0.5-stacking-navigation/current-status.md) before current work. The [validation plan](scenarios/v0.5-stacking-navigation/validation-plan.md) defines the current matrix. Voyager results remain in its [snapshot](scenarios/v0.5-voyager/current-status.md) and [0.5 lessons](operations/lessons/v0.5-voyager-2026-10-29.md#english).

`operations/current-status.md` is a manifest-protected historical import, not current status; never overwrite it. Active snapshots place newer sections first. Earlier “next target” paragraphs retain only their historical scope and are not current instructions.

### Current baseline

- Current scope: nine models and 19 directed pairs, with the self-evolution lab and Dark Fog research/material dependency removed from this run.
- Active source and development installation: `28f4af96ba666998d9f82f8cd529c9a7911978ed`, product `0.5.0`, DSP `0.10.35.29151`, with the root lock as machine-readable authority.
- Runtime is `not_running`; use the stacking/navigation snapshot for the latest normal save, complete backup and per-row acceptance.
- The root lock is `development`, with both final package fields `null` until current functional acceptance closes.
- The original Voyager clauses are closed in the [fixed baseline review](releases/v0.5.0/review-delivery.md). The first-sail/carrier-rocket extension is review-ready on `d3b7ac897bb44d62c8a7ed54c51a55ff2b8de7b0` in the [fixed expansion review](releases/v0.5.0/expansion-review-delivery-2026-11-06.md). Neither is a formal 0.5 publication.

The current matrix has a 44-building ceiling and explicit research/material limits. Each model, combination, function and recovery row requires its own evidence; the completed three-layer small-storage example does not close the full matrix. Reading documentation does not start or advance DSP/MCP.

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
