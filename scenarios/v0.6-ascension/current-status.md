# Ascension current snapshot / Ascension活动快照

2026-11-11。游戏已正常保存退出，Primary及LastExit均为126087859，2246项完整保护通过。累计4998597/6000000游戏tick、70494请求，返航54000及清理3000储备保留。下一轮从最新完整保存边界继续。

## 源码与实装

所选及实装源码 `9280c865f7a5ee2f407729da58a7d48d00b8f194` 已线性进入产品main，6531项准确源码回归、完整29151 Native构建、准确CI及同源组合资格通过。实装SDK46请求、同源逐字节检查及当前存档实测通过。调用端176项通过，包含原始期限内未接受STALE重准备及Native单精度零速度回归。游戏已关闭。 [准确产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/43029504005)

9280c865已实测悬停抵达后继续导航、正常下降到Walk、仓储取料、手搓及叠放施工。最近一段导航在Fly状态完成，774tick、地表距离2.9826m，原任务释放及正常下降请求均为真，接地观察为否。随后陆地Walk取料和返程供料通过。抵达完成依据原生到达和任务释放，后续动作分别使用各自原生物理条件。调用端接续采用订单所有权观察，原生低速漂浮动作继续绑定两秒/0.05m/0.15m/s新鲜观察。

本轮正常制造并叠放4座红矩阵研究站，根256及6868–6871形成5层，累计研究站既耗9。正常取用产线569蓝矩阵并手搓1蓝，1504的蓝材料已齐。另正常供1600石墨、400氢，取出390红矩阵供科研。保存前1504观察为52634/108000哈希，机甲蓝/红点数之差334800，尚需93红材料。成品仓260另有9红，原料仓114有565石墨、781有375氢，完整缓冲和部分科研点数已保存。

按自主用料授权正常制造2高速分拣器，原生升级石墨输入257及氢输入782，原筛选分别为1109及1120，正常退还2普通分拣器。准确新增用料为5铁、2电路板及1磁线圈。累计施工分拣器既耗保持33，升级扣还单独留存。一次只读180红等待到期和一次调用端接地等待失败均保留，后者观察到3e-45级手动速度残值。新鲜原生升级随后成功，调用端现按Native单精度平方归零语义判断静止。

1蓝手搓完成后立即进入机甲科研，旧成品背包判定将原动作记为失败。独立原生回读证实蓝点数增加3600，原失败及物料记录完整保留。该完成判定仍需产品修复，后续矩阵供料继续使用已验证的产线取料路径。累计普通分拣器账目曾由替代调用端误填31，已依据原施工回执恢复33并保留错误原件。

历史源码e59f93e3已实测原生起飞、抵达及导航任务释放，水面Drift触发旧接地完成条件，原动作outcome_unknown及2238项保护完整保留。所有者允许抵达水面后继续移向陆地，2a669746起按地表投影抵达及原任务释放完成，空间/地表距离、运动模式及接地观察分别回读。当前正向续行结果见上。

历史启动记录保留300.749秒取20钛合金、超过原300秒门0.749秒的失败，以及185.748秒取20碳纳米管的通过。全部原拒绝、计时和正常保存保护保持，当前库存及科研事实见上。

## 接下来执行

1. 从最新2246项完整保护和126087859保存边界无损恢复，沿300秒原始启动门先正常取成品红矩阵，再补足93红材料并完成1504。原始启动262.840秒正常取32铁及本轮全部回执保持。实装源码和同源组合可复用。
2. 继续1504、1705、1523科研，优先复用现有矩阵站、原料库存及正常生产线。合理有限科研/材料/施工增量自行核算、记录并执行。当前科研上限为蓝4200、红4200、黄3600、紫2000、绿2000。 [当前用料与授权](resource-increment.md)
3. 复用Caph II制造、弹射器和发射井，重新核对8000半径接收层及既有交付点。完成合法闭合设计、持续真实火箭/太阳帆发射、节点/框架/壳面交付、接收器持续非零实际电力，以及正常保存冷恢复后的续建续运。6°候选已完成只读成本证明，11000半径为210结构点、224细胞点，当前应力纬度0°。 [实施与验收](implementation-plan.md)
4. 功能验收闭合后生成最终同源双包及交审证据，正式发布沿独立授权。

## English

The game normally saved and quit with primary and LastExit126087859,2246 verified protected files,4998597/6000000 spent ticks and70494 requests. Return54000/cleanup3000 remain. Selected and installed source9280c865 passed6531 exact-source cases, full Native build, exact CI, coherent installation,46 installed-SDK requests and live owned-save acceptance.176 caller cases passed, including original-deadline unaccepted-STALE retries and binary32-zero velocity checks.

Source9280c865 proved onward navigation from hovering arrival, normal descent into Walk, storage withdrawal, handcraft and stack placement. Its latest leg completed in Fly after774 ticks at2.9826m surface distance, with original task release and Native descent requested and grounding observed false. Subsequent land-based Walk supply and return passed. Arrival follows Native arrival/task release. Each later action applies its own Native physical conditions. Caller attachment checks order ownership, while bounded floating actions retain the two-second/0.05m/0.15m/s inspection.

Four normally manufactured red laboratories now form five layers256/6868–6871, with nine cumulative placements. This window withdrew569 blue cubes and crafted one blue, completing the blue-material requirement for1504. Normal supply added1600 graphite and400 hydrogen and withdrew390 red cubes for research. The final observation showed52634/108000 hashes and a334800-point blue/red difference, requiring93 further red cubes. Storage260 held nine red,114 held565 graphite and781 held375 hydrogen. All buffers and partial research points were saved. The first real iron withdrawal passed262.840 seconds from the original launch.

Two normally manufactured fast sorters upgraded graphite input257 and hydrogen input782, retaining filters1109/1120 and refunding two ordinary sorters. Exact new raw use was five iron, two boards and one coil. Cumulative sorter placement remains33, with upgrade debit/refund recorded separately. A bounded read-only180-red wait expired. A caller grounded wait failed on3e-45 manual-velocity residue, after which fresh Native upgrades passed. Caller idle checks now follow Native binary32 squared-zero semantics. A replacement caller's incorrect31-sorter ledger was corrected to33 from original construction receipts, retaining the wrong record.

The crafted blue immediately entered mecha research. The backpack-only completion check marked its original action failed, while independent readback proved an exact3600-point increase. The original failure and material record remain preserved. This product completion check still needs a fix. Continue matrix supply through the qualified production-withdrawal path. Resume from the latest complete boundary, first normally withdraw finished red within the original300-second startup limit, then finish1504 and the remaining0.6 acceptance.

Historical sourcee59f93e3 flew, arrived and released its Native task. Water Drift encountered the earlier grounded-completion condition, retaining the original as outcome_unknown with2238 protected files. The owner permits onward water-to-land movement. Since2a669746, completion follows Native surface-projected arrival/task release, reporting movement and grounding independently. Current positive continuation appears above.

Historical startup evidence retains the300.749-second20-alloy withdrawal, exceeding its300-second limit by0.749 seconds, and the earlier185.748-second nanotube operation. Their original refusals/timings and complete saved boundaries remain preserved. Current inventory and research facts appear above.

Continue research1504/1705/1523, normal production and Caph II design/launch/cell/electricity/save acceptance under the owner's reasonable-resource autonomy. Current matrix ceilings are4200/4200/3600/2000/2000 blue/red/yellow/purple/green. The11000-radius6° read-only triangle costs210 structure/224 cell points with current unlocked latitude0°. Final packages follow functional closure and formal publication retains its separate authority.

Earlier source, installation, stacking and production cuts remain in fixed history. [前次完整快照 / Previous complete snapshot](https://github.com/Arcueid77/Spherewright-Lab/blob/573bf75e643935bfd71088f061955225f915ff49/scenarios/v0.6-ascension/current-status.md) · [持续授权 / Standing authority](../../operations/standing-authority.md)
