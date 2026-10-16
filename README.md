# Spherewright-Lab

Spherewright 的公开场景、运行交接与黑盒验收仓。产品的 Plugin、MCP、Contracts、Bridge.Core、通用测试和打包实现继续保留在 [Spherewright](https://github.com/Arcueid77/Spherewright) 一个 monorepo 内。公开审查的范围与限制见[安全审查记录](operations/public-review-2026-10-16.md)。

本仓通过只读子模块消费精确产品提交，不反向成为产品构建依赖。0.4 的历史验收已完成，本次拆仓只组织 Git、文件、工具和 CI，不部署、不读写游戏、不重做验收、不发布版本。

## 开始使用

```powershell
git clone --recurse-submodules https://github.com/Arcueid77/Spherewright-Lab.git
cd Spherewright-Lab
pwsh -File scripts/bootstrap.ps1
pwsh -File scripts/verify-source-lock.ps1
pwsh -File scripts/verify-evidence.ps1
pwsh -File scenarios/v0.4-final/scripts/verify-acceptance.ps1
```

拆分已经合并，当前工作从 `main` 的 [AGENTS.md](AGENTS.md) 与[活动交接](operations/active-handoff.md)开始。复核冻结证据时使用不可变迁移快照 `14478a03c64c550e644c559405c8496b647552e7`，不要把历史授权当作当前授权。`bootstrap` 只初始化固定子模块并建立忽略目录，既不追踪 latest main，也不会覆盖意外 HEAD 或 dirty 子模块。

[活动 source-lock.json](source-lock.json) 固定本次 `29151` 调用验证候选 `e018b7f45c70f5fe029418cad987af794b5cb9bf` 及同 SHA 双包；[冻结发布锁](releases/v0.4.0/source-lock.json) 仍对应原验收源码 `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9` 和 `29145`。活动锁通过明确的 `historical_reference` 及冻结锁 hash 保留历史引用，不把旧验收计入新候选。没有正式 `v0.4.0` tag，因此 `releaseTag: null`、`status: provisional`。原证据仍导入自文档提交 `e7d5f7d8661092b7c8089710488c448f290638be`；冻结清单、锁和双包字节不变，新候选实机验证尚未通过。

The [active source lock](source-lock.json) pins candidate `e018b7f45c70f5fe029418cad987af794b5cb9bf` and its two packages for the current `29151` callability check. The [frozen release lock](releases/v0.4.0/source-lock.json) retains accepted source `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9` on `29145`. An explicit `historical_reference` and frozen-lock hash preserve that history without granting acceptance to the active candidate. No formal `v0.4.0` tag exists; the lock remains provisional. Imported evidence stays bound to documentation source `e7d5f7d8661092b7c8089710488c448f290638be`; frozen manifests, locks and package bytes are unchanged. The new candidate has not yet passed runtime validation.

## 查找场景与证据

- [v0.4 真实场景](scenarios/v0.4-final/README.md)、[原验收与结果](scenarios/v0.4-final/acceptance.md)、[拓扑边界](scenarios/v0.4-final/topology.md)。
- [当前历史截面](operations/current-status.md)、[本次迁移交接](operations/active-handoff.md)、[游戏时间线](operations/gameplay-timeline.md)、[经验](operations/experience-ledger.md)、[事故记录](operations/incident-log/full-history.md)。
- [0.4 最终摘要](releases/v0.4.0/validation-summary.md)、[完整证据](releases/v0.4.0/evidence/README.md)、[原样导入清单](releases/v0.4.0/manifests/import-manifest.json)、[规范化清单](releases/v0.4.0/manifests/evidence-manifest.json)、[冻结包校验和](releases/v0.4.0/hashes/SHA256SUMS.txt)。
- [v0.5 预留入口](scenarios/v0.5-voyager/README.md)，尚无游戏执行授权。

```text
deps/Spherewright/                 exact, read-only product submodule
scenarios/v0.4-final/              real scenario, acceptance, topology, offline entry
scenarios/v0.3.2-black-box/         historical comparison
scenarios/v0.5-voyager/             scope placeholder
operations/                       status, handoff, timeline, incidents
releases/v0.4.0/                   summary, evidence, manifests, hashes
archive/imported-from-spherewright/<facts-sha>/   unchanged original bytes
archive/roadmap-history/           normalized historical roadmap
scripts/                          bootstrap, lock/import/evidence checks, bump, preview
schemas/                          machine validation
.github/workflows/                light Lab validation
.local/                           ignored protected originals and local logs
artifacts/                        ignored frozen inputs or local previews
```

## 原样归档与脱敏

258 份安全原文按字节归档，另有 1 份经验账本原文依所有者明确选择仅保存在本地受保护目录；Git 只含去除一处标准系统绝对路径的派生副本。导入清单同时声明原文和派生副本的范围与哈希。CI 可以验证 Git 中的归档及全部派生副本，不能验证缺席的受保护原文；原始 Save、ticket、私有身份、未脱敏请求和转储均未迁入 Git。

原样归档中的相对链接按原来源目录解释。规范化副本将有效链接改为本仓路径或产品不可变提交；原来已经缺失的目标明确标为历史未解析引用，并链接原文上下文，不制造缺失的证明。详见 [link-resolution.json](releases/v0.4.0/manifests/link-resolution.json)。R 编号、tick、revision、Journal、action/幂等信息、来源/安装 SHA、Native 版本、失败结论和原证据索引均保留。

## 产品开发与预览包

`deps/Spherewright` 默认只读。产品修改使用独立 clone/worktree；在产品仓测试、提交并通过准确 SHA 的 CI 后，才更新子模块。子模块更新需要完整 40 位 SHA；换源码必须提供已审查的新锁文件，不能把旧包或旧验收自动移植为新源码的结论。

```powershell
pwsh -File scripts/update-spherewright.ps1 -Sha <FULL_SHA> -NewLockPath .local/reviewed-next-lock.json
```

更新入口要求 Lab 干净、产品 CI 绿，只暂存子模块与锁文件并写 bump 摘要，不 commit/push。Lab 的提交记录消费版本与场景事实；可复用能力回产品仓实现。脚本中的既有 Sample 函数名和文件名是兼容接口，不代表另一个仓库。

活动候选需要换源码时，可在根锁的 `acceptance` 中明确设置 `scope: historical_reference`，并用 `sourceLock` / `sourceLockSha256` 固定既有 `releases/v<产品版本>/source-lock.json`。旧 manifest、spec 和来源必须与该冻结锁一致；它们只证明冻结源码，验证输出会明确 `acceptanceAppliesToActiveSource: false`。不带这三个字段的旧格式仍要求根锁与发布锁逐字节一致。更新入口先验证准确产品 SHA 的 CI，仅暂存根锁与 gitlink，永不改写冻结发布锁。新候选的实机结果另行记录，历史引用不算新验收。

For an active candidate with different source, explicitly set `acceptance.scope` to `historical_reference` and pin the existing `releases/v<product-version>/source-lock.json` with `sourceLock` and `sourceLockSha256`. Its manifest, specification and provenance must match that frozen lock. They prove only the frozen source; verifier output reports `acceptanceAppliesToActiveSource: false`. Legacy locks without these three fields must remain byte-identical to the release lock. The update entry verifies successful CI for the exact product SHA, then stages only the root lock and gitlink, never rewriting the frozen release lock. Record new runtime results separately; historical references are not new acceptance.

需本机合法安装的 DSP Native 引用和 .NET 8 SDK 时，可以生成独立本地预览：

```powershell
pwsh -File scripts/package-from-submodule.ps1 -DspDir <LOCAL_DSP_DIRECTORY> -DotNetPath <DOTNET_SDK_EXECUTABLE>
```

它从子模块自身 HEAD/clean 状态调用产品 `package-release.ps1`，由该入口调用 `package-thunderstore.ps1` 一次，输出到 Lab `artifacts/previews/` 并生成 run manifest。所需外部输入是 SDK 和合法游戏程序集，不是未提交产品源码。不会覆盖原冻结候选、部署或接触游戏。预览包哈希与冻结包哈希分开记录。

完整规则见 [AGENTS.md](AGENTS.md)。原记录和场景参数不能授予新的游戏写入或正式发布权限。
