# Spherewright-Lab

Spherewright 的公开场景、运行交接与黑盒验收仓。产品的 Plugin、MCP、Contracts、Bridge.Core、通用测试和打包实现继续保留在 [Spherewright](https://github.com/Arcueid77/Spherewright) 一个 monorepo 内。公开审查的范围与限制见[安全审查记录](operations/public-review-2026-10-16.md)。

本仓通过只读子模块消费精确产品提交，不反向成为产品构建依赖。0.4 历史验收与正式发布保留；所有者 2026-10-19 的指令已启动 [0.5 Voyager](scenarios/v0.5-voyager/README.md)。活动工作是原三项跨恒星验收、最小产品实现与同源码候选交审，仍保留原生、安全、隐私和确认门，不自动正式发布。

Voyager 当前 **1/3**：源码 `463fc888b1e4cf4a90e08cb1022d2b8896447700` / Native `0.10.35.29151` 已正常跨恒星往返，将合法母星系缺失的1013分形硅石10个带回精确原home并正常保存、读回资源及航程完整文件证明。另两门（持续物流、可恢复飞行失败及精确恢复）仍开放，最终双候选仍为null。已发现的每腿重复检查点P1现已由216修复并通过准确CI/必要冷部署实核，唯一新检查点及受控恢复待实测；当前较新主档覆盖全部旧检查点，严禁回滚。详见[活动快照](scenarios/v0.5-voyager/current-status.md)。

Voyager clause1 passed on the installed463 development preview: a real cross-star round trip brought ten legally home-absent item1013 resources back and saved them normally. Progress is **1/3**, with sustained logistics and exact failed-flight recovery open and final candidates still null. The discovered duplicate-checkpoint P1 is fixed and cold-verified on216; its unique new checkpoint and controlled recovery still need live proof; the newer primary covers every old checkpoint. The later home-logistics read closed at 477 RPC/14 accepted in total; it proves prerequisites, while sustained logistics remains open. The later216 home-tech/stocks read completed14RPC/3.469s with zero writes/accepted, normal EOF and unchanged ticket: latest observed117684437, saved117673183, item1013×10 and Journal104/five-transition prefix retained. Closed stage total538RPC/16accepted; all allowances are closed, Root is the sole idle game writer and no action is pending. This is stock/prerequisite evidence, not logistics or failure-recovery acceptance.

母星物流前置只读窗已完成19RPC/2.922s/0writes，累计477RPC/14accepted；一座ILS有3个空物流槽、另两座PLS，recipe62可将1013×1制成1113×2（Assemble/90tick），仅为前置证据。P1修复216f4075e983d78fa4d4f5d222bdd279813e1d86已通过完整Plugin/3726tests及[准确CI39172966526](https://github.com/Arcueid77/Spherewright/actions/runs/39172966526)，活动锁/gitlink现采用216；同源新开发双包已核验并实际冷安装216，同版本默认恢复完成，保存117673183/观察117673206/J104五衔接，冷部署/默认恢复截点累计524RPC/16accepted；后续14RPC只读后最新累计538RPC/16accepted，观察117684437/保存117673183、资源10/J104五衔接保留。216的唯一新航程检查点及故障恢复仍待实测，既有463的1/3证据保留，最终候选仍null；详见[活动快照](scenarios/v0.5-voyager/current-status.md)。

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
