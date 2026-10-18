# Spherewright-Lab

Spherewright 的公开场景、运行交接与黑盒验收仓。产品的 Plugin、MCP、Contracts、Bridge.Core、通用测试和打包实现继续保留在 [Spherewright](https://github.com/Arcueid77/Spherewright) 一个 monorepo 内。公开审查的范围与限制见[安全审查记录](operations/public-review-2026-10-16.md)。

本仓通过只读子模块消费精确产品提交，不反向成为产品构建依赖。0.4 历史验收与正式发布保留；所有者 2026-10-19 的指令已启动 [0.5 Voyager](scenarios/v0.5-voyager/README.md)。活动工作是原三项跨恒星验收、最小产品实现与同源码候选交审，仍保留原生、安全、隐私和确认门，不自动正式发布。

**当前2/3：门1在463通过，门3在216通过，持续星际物流仍开放。** 实机先观察到原生Fly，再于曲速前取消，原flight明确失败为recovery_required；唯一checkpoint/action/journey、精确检查点恢复至新session、原deadline/返程预算不重置、材料/能量读回和一次正常HomeSave均已证明。36RPC/14.906s/四原动作接受，保存117713689/观察117713780，资源1013×10、Journal104条原prefix/五衔接保留，0pending/unknown、正常EOF；600s/128RPC/4write原窗关闭，未用额度作废。

**Voyager2/3: clause1 passed on source463; clause3 passed on source216; sustained interstellar logistics remains open.** The real controlled flight reached Native Fly, then cancelled before warp and ended as the original recovery_required action. Its one unique checkpoint/action/journey binding, exact checkpoint reload into a new session, preserved deadline/reserves, material/energy readback and one normal home Save passed36RPC/14.906s/four original accepted actions. Saved117713689/observed117713780, item1013×10 and the full104-entry/five-transition Journal prefix were retained, with zero pending/unknown and normal EOF. The600s/128RPC/four-write window is closed; unused allowance was forfeited.

另一个60s/8RPC/0commit负向窗仅fresh准备原reload token，原生较新主档保护明确拒绝回滚，0Load/Save；正常Save后仍为recovered的原票据，按现有lazy retirement设计由该fresh覆盖检查退役于117713689。主档/session/resume票据未变，原26份Native检查点全文件hash均未改，本次只新增1DSV，现27份均被主档覆盖、禁止恢复。Root18项独审SHA `95AECD3D7A3626853EAFEBB5D41CE77C5D80114141A424298DF670FAF44AAD4E` 已过。该负向窗观察117726168/保存117713689，累计582RPC/20accepted，全部窗关闭无额度续用；该截点Root唯一writer已停、无未决动作，健康DSP在home保持运行，不自动Save/退出/Load。

**Latest home research boundary:** Native fresh CanEnqueueTech selected3404 and one normal Save completed22RPC/two original accepted actions, zero pending/unknown. Saved117739585, session observation117739635, item1013×10 and Journal105 with the original104-entry/five-transition prefix retained; closed stage total604RPC/22accepted. Technology3404 is queued and **unlocked=false**, with116/300000 hashes at its progression read. The later diagnostic in the same protected receipt observed117739645/hash122. Required matrices remain1000 each of6001/6002/6003/6004; selection is not completion. Its original observation budget remains at most360000 observed game ticks/7200 wall seconds/zero additional writes, without reset or reselect; new tools wait for the queue to become idle.

**最新母星科研截点：** 经原生fresh CanEnqueueTech选择3404并正常保存，22RPC/两个原动作接受且completed，0pending/unknown；保存117739585、session观察117739635，资源1013×10、Journal105及原104条/五衔接prefix保留，累计604RPC/22accepted。3404仅queued、**unlocked=false**，progression读回116/300000hash；同一原回执后续诊断观察117739645/hash122。真实成本6001..6004各1000，入队不等于解锁。原观察预算仍最多360000观察tick/7200秒/额外writes0，不重置、不重选；新工具使用须等原队列idle。

下一唯一目标为持续星际物流。先按原有限预算观察已入队3404，尚未解锁；更早库存读回的蓝矩阵差584、其余三色足够，仅为当时库存证据。仅修实际母星科研阻塞、复用已有设施，再按有限任务包接通已验证目标的矿机/供电/物流站。未完成分页不代表全厂缺失；数量/速率、库存及能耗/翘曲器趋势、多个完整真实船运周期、母星实际消费和正常保存恢复后继续运输仍须声明并证明。

实际安装/活动只读依赖仍为216 /Native0.10.35.29151；同源开发预览包及5ECC安装锁不变，最终候选仍双null。完整证据、历史463检查点P1和下一入口见[活动快照](scenarios/v0.5-voyager/current-status.md)。

## 开始使用

```powershell
git clone --recurse-submodules https://github.com/Arcueid77/Spherewright-Lab.git
cd Spherewright-Lab
pwsh -File scripts/bootstrap.ps1
pwsh -File scripts/verify-source-lock.ps1
pwsh -File scripts/verify-evidence.ps1
pwsh -File scenarios/v0.4-final/scripts/verify-acceptance.ps1
```

当前工作从 `main` 的 [AGENTS.md](AGENTS.md)、[活动交接](operations/active-handoff.md)与 [Voyager 活动快照](scenarios/v0.5-voyager/current-status.md)开始。复核冻结证据时使用不可变迁移快照 `14478a03c64c550e644c559405c8496b647552e7`，不要把历史授权当作当前授权。`bootstrap` 只初始化固定子模块并建立忽略目录，既不追踪 latest main，也不会覆盖意外 HEAD 或 dirty 子模块。

[活动 source-lock.json](source-lock.json) 的兼容 v2 格式明确区分 `development.targetVersion: 0.5.0`、`spherewright` 的完整 gitlink 源码 SHA/实际版本、`installed` 的真实 216 `0.5.0`/`29151` 开发预览双包及安装记录、尚未生成的 null 最终双候选与 `historical_reference` 历史验收。锁的 `status: development` / `releaseTag: null` 不取消已发布的 [GitHub v0.4.0](https://github.com/Arcueid77/Spherewright/releases/tag/v0.4.0)，其 annotated tag 仍准确指向 `b7c0002dbe2e8f5608c5ca140b0c6326a1818021`。[冻结发布锁](releases/v0.4.0/source-lock.json) 则继续固定原验收 `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9` / `29145`，历史清单、锁、包和验收不变。未知或缺失工件不填假 hash，旧包不计为 0.5 候选。

The backward-compatible v2 [active lock](source-lock.json) separates the `0.5.0` development target, exact consumed source/version, recorded actual development-preview installation, null final-review candidates and explicitly pinned historical acceptance. A development lock has no active release tag or claimed candidate hash; the published b7 `v0.4.0` tag and pair remain intact. The frozen `2a7a98d1932c404e3a7abc2c11233d9c0b8780d9`/`29145` acceptance lock and all immutable manifests/package bytes are unchanged. Source adoption, installation, candidate generation and live acceptance are separate evidence. See [the active snapshot](scenarios/v0.5-voyager/current-status.md) and [the historical formal report](operations/formal-release-2026-10-17.md). The owner's Thunderstore website self-upload result remains unverified; that fact does not block unrelated Voyager development or authorize another upload.

## 查找场景与证据

- [v0.4 真实场景](scenarios/v0.4-final/README.md)、[原验收与结果](scenarios/v0.4-final/acceptance.md)、[拓扑边界](scenarios/v0.4-final/topology.md)。
- [Voyager 活动快照](scenarios/v0.5-voyager/current-status.md)、[活动交接](operations/active-handoff.md)、[受保护历史截面](operations/current-status.md)、[游戏时间线](operations/gameplay-timeline.md)、[经验](operations/experience-ledger.md)、[事故记录](operations/incident-log/full-history.md)。
- [0.4 最终摘要](releases/v0.4.0/validation-summary.md)、[完整证据](releases/v0.4.0/evidence/README.md)、[原样导入清单](releases/v0.4.0/manifests/import-manifest.json)、[规范化清单](releases/v0.4.0/manifests/evidence-manifest.json)、[冻结包校验和](releases/v0.4.0/hashes/SHA256SUMS.txt)。
- [v0.5 Voyager](scenarios/v0.5-voyager/README.md)、[原三项验收](scenarios/v0.5-voyager/acceptance.md)、[有限场景配置](scenarios/v0.5-voyager/scenario.json)。

```text
deps/Spherewright/                 exact, read-only product submodule
scenarios/v0.4-final/              real scenario, acceptance, topology, offline entry
scenarios/v0.3.2-black-box/         historical comparison
scenarios/v0.5-voyager/             active snapshot, three gates, finite settings
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

活动源码需要更新时，在根锁的 `acceptance` 中明确设置 `scope: historical_reference`，并用 `sourceLock` / `sourceLockSha256` 固定既有 `releases/v<历史版本>/source-lock.json`，无需伪造新版本的冻结锁。旧 manifest、spec 和来源必须与该冻结锁一致；它们只证明冻结源码，验证输出明确 `acceptanceAppliesToActiveSource: false`。不带这三个字段的旧格式仍要求根锁与发布锁逐字节一致。更新入口先验证准确产品 SHA 的 CI，仅暂存根锁与 gitlink，永不改写冻结发布锁。开发未生成包时 `packages.manual` / `thunderstore` 必须同时为 null；输出 `packagesNotBuilt: 2`、`candidatePackagesReady: false`，不把缺失包说成已验收。构建候选必须改为精确版本/源码的双包记录；已存在的 v2 包还须核验包内 source/version/Native，不能借 null 绕过校验。

For a different active source/version, pin the actual historical release lock using `acceptance.scope: historical_reference`, `sourceLock` and its real hash. Manifest/spec/provenance must match that frozen lock, independent of the active version. Legacy locks retain their byte-identical release rule. Development locks require two null unbuilt packages and never report ready candidates; provisional/tagged locks still require the real pair. Existing v2 package files also undergo exact-source/version/Native manifest checks. The update entry requires successful exact-SHA product CI and stages only the gitlink/root lock. Preview packaging rejects a product version that has not yet adopted its development target. New live results are recorded separately.

需本机合法安装的 DSP Native 引用和 .NET 8 SDK 时，可以生成独立本地预览：

```powershell
pwsh -File scripts/package-from-submodule.ps1 -DspDir <LOCAL_DSP_DIRECTORY> -DotNetPath <DOTNET_SDK_EXECUTABLE>
```

它从子模块自身 HEAD/clean 状态调用产品 `package-release.ps1`，由该入口调用 `package-thunderstore.ps1` 一次，输出到 Lab `artifacts/previews/` 并生成 run manifest。所需外部输入是 SDK 和合法游戏程序集，不是未提交产品源码。不会覆盖原冻结候选、部署或接触游戏。预览包哈希与冻结包哈希分开记录。

完整规则见 [AGENTS.md](AGENTS.md)。原记录和场景参数不能授予新的游戏写入或正式发布权限。
