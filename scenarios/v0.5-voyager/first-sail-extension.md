# 0.5 first solar sail extension / 0.5 首帆扩展方案

Owner direction: 2026-11-01, extend 0.5 with the first normally manufactured and actually launched solar sail, and proceed autonomously with as little manual intervention and repeated approval as possible. This file records that goal and the execution design. Current results, selected source and next action remain only in [current-status.md](current-status.md).

所有者于2026-11-01将0.5扩展目标明确为正常制造并真实发射第一张太阳帆，先列方案，然后尽可能减少人工干预和重复审批、自主推进。本文件记录目标及执行设计；当前结果、选定源码及下一动作仍只在[唯一活动快照](current-status.md)维护。

## Acceptance / 验收成果

- Use the public MCP/Plugin interface and ordinary game manufacturing, construction, supply, power and native ejector operation. Prove the original manufacturing action completed, with actual ingredient/product conservation; existing stock alone is not manufacturing evidence.
- Bind one exact ejector, local owned factory/star, its real power and sail input, and one valid enabled native swarm orbit. Reuse a suitable existing building or orbit after inspection. Do not create sails, alter launch counters, call simulation ticks manually, inject resources or replace native launch geometry.
- Observe an actual native launch of a legitimately produced sail. Cross-check the ejector/native consumption evidence with the corresponding swarm bullet/sail transition and captured ticks. A configuration response, transient `fired`, aggregate swarm growth or package success alone cannot prove this ejector launched this sail.
- Normally save the result and verify supported recovery of the configured ejector, remaining inventory, orbit and swarm state. Account for ordinary flight, sail lifetime and other native evolution; do not require impossible bitwise equality after game time advances.

- 经公开MCP/Plugin接口完成普通制造、建设、供料、供电及原生弹射器运行；原制造动作须完成，材料与产物真实守恒，已有库存本身不算制造证明。
- 绑定精确弹射器、本地owned工厂/恒星、实际供电及帆输入、有效启用的原生戴森云轨道。检查后可复用合适建筑或轨道。不创建太阳帆、不改发射计数、不手动调用模拟tick、不注入材料、不替代原生射界计算。
- 观察合法制造帆的真实原生发射，交叉核对弹射器/原生消耗与对应云中弹道或帆的转换及采集tick。配置成功、瞬时`fired`、全局帆数增加或包检查均不足以单独证明该弹射器发射了该帆。
- 正常保存成果，验证支持的恢复后弹射器配置、剩余物料、轨道及云状态；区分飞行、太阳帆寿命和其他正常演化，不要求游戏时间推进后逐位不变。

## Rolling stages / 滚动阶段

| Stage / 阶段 | Reviewable outcome / 可验收成果 | Next-stage prerequisite / 提前核对 |
| --- | --- | --- |
| S0 Scope and whole chain / 范围与整链 | Retain the accepted Voyager baseline and exact Native reference; identify reusable interfaces, actual world readiness and remaining budgets. / 保留原Voyager验收及准确原生参考，明确已有接口、现场就绪和剩余额度。 | Ejector placement, feed, power, orbit, line of sight, launch and recovery must form one feasible chain. / 弹射器放置、供料、供电、轨道、射界、发射和恢复能衔接。 |
| S1 Product capability / 产品能力 | Same-tick ejector/swarm reads and the smallest ordinary prepare/commit configuration extension; reuse normal crafting/building/sorter supply. / 同tick弹射器与云读取、最小普通配置预检提交扩展；复用制造/建造/分拣供料。 | Research exact signatures, defaults, units, ownership and native launch lifecycle before implementing writes. / 写入前核准签名、默认状态、单位、归属和原生发射生命周期。 |
| S2 Qualification / 源码资格 | Focused regression, complete Native build, exact-source CI and coherent installation input. / 相关回归、完整Native构建、准确源码CI及同源安装输入。 | Complete current save/LastExit backup, one writer, supported game version and exact runtime identity. / 完整当前主档/退出档备份、唯一writer、受支持版本和准确运行身份。 |
| S3 First actual launch / 首次真实发射 | Fresh inventory/site plan, ordinary manufacture and construction/supply, then bounded native launch observation with original receipts. / 新鲜库存与场地计划、普通制造建设供料、有限原生发射观察及原回执。 | Exact material and game-time spending, power and view feasibility, finite wait/stop/save envelope. / 准确材料和游戏时间、供电射界可行性、有限等待/停止/保存包络。 |
| S4 Preservation and review / 保全交审 | Normal save/recovery evidence, updated user documents and only then a new qualified review pair. / 正常保存恢复证明、用户文档更新，功能闭合后才形成新双候选。 | Keep old baseline packages/hashes immutable and distinguish all new proof from the old three passed clauses. / 保留旧基线双包与哈希，新增证明不冒充旧三门证据。 |

## Autonomy and budgets / 自主执行与预算

Proceed with the necessary bounded source/caller investigation, fixes, tests, normal commits/pushes, qualification and evidence maintenance. Routine same-owned-world save, close/launch and no-loss recovery retain the standing technical safeguards. Batch related proven changes and reuse qualified inputs. Native refusal is an implementation/caller/site diagnosis, not a request to waive it. Reconcile every original accepted/unknown action; never rekey or replay it.

按目标连续进行有限源码/调用端调查、修复、测试、正常提交推送、资格检查及证据维护；同owned世界的常规保存、退出启动及无损恢复保留原持续授权的技术约束。集中修复已证实的相关问题，复用合格输入。原生拒绝应先区分产品、调用或现场问题，不请求绕过。逐项核销原accepted/unknown，不换键重放。

This target adds no arbitrary resource allowance. First inspect existing stock and facilities, derive the minimum exact bill, and preserve every previous debit and return/energy/save reserve. If an actual required material/time increase falls outside the latest approved limits, finish the reviewable preflight and consolidate the exact increment into one owner decision. Each live window remains finite and at most one hour after readiness. Progress loss/rollback, another world, new access/paid permissions, Computer Use and formal tags/Releases/uploads retain their separate owner gates.

目标不自带无限资源额度。先查已有库存和设施，推导最小准确清单，保留全部历史支出及返航/能源/保存储备；若实际必需的材料或时间增量超出最新批准硬上限，先完成可审阅预检，再将准确增量集中一次交所有者决定。每个实机窗口仍在就绪后起算、有限且最多一小时。进度损失/回退、另一世界、新访问/付费权限、Computer Use及正式tag/Release/上传保留原独立审批。

## Initial evidence and limits / 初始证据与边界

The accepted source/install baseline remains `30bd61198a6a3b2ff4e41eaf172c5d97fb66a19d`, DSP `0.10.35.29151`, Native assembly SHA-256 `EF314425DADE51F529F184F07BE136CD3C2660A6A81515603C7226FBE7AB1D8C`. Existing recorded recipes show solar sails and the electromagnetic rail ejector unlocked. Current inventory, power, site and orbit still require fresh runtime evidence. One ordinary recipe execution consumes one graphene and one photon combiner and yields two sails. A new ejector recipe consumes twenty steel, twenty gears, five processors and ten super-magnetic rings, before external supply/power connections; this is a bill, not an approved additional debit or proof of stock.

原验收/实装基线仍为上述准确源码和DSP29151/EF3144原生装配。已有配方记录显示太阳帆和电磁轨道弹射器已解锁；当前库存、电力、场地及轨道仍待新鲜现场证据。一轮普通配方用石墨烯1、光子合并器1产太阳帆2；新弹射器配方用钢20、齿轮20、处理器5、超级磁场环10，另计外部供料/供电连接。这只是清单，不是新增扣料授权或库存证明。

Long-route generalization, multi-outpost scheduling, rockets and Dyson node/frame/shell design are outside this first-sail slice. Existing twelve-belt restrictions remain disclosed until separately changed and validated; they are not silently relaxed for this goal.

长线路通用化、多矿点调度、火箭及戴森节点/框架/壳层设计不纳入本次首帆切片。现有十二节限制在另行修改验证前继续披露，不因首帆目标而静默放宽。
