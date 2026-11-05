# Paused space state audit / 暂停太空状态审计

## 中文

此审计落实同组件连续候选失败后的完整状态回放要求；当前进度只见[活动快照](current-status.md)。不得把源码回放、原生加载成功或正常退出保存称为已补舱、健康返航或火箭验收。

真实响应：61d761ac的LastExit提交在原生加载前租约交接拒绝；原凭据消费不恢复。76977f23经新数据身份、真实加载器和原生LoadComplete暂停，正常打开同一保存：world owned、Sail、planet=null、tick123569741、warp0/command=false、唯一打开隔离；宇宙速度约7.807988米/秒。调用器把绝对速度<=0.5当作暂停源条件而拒绝；Native库存/源准入存在同一错误模型。尚无补舱或返航被接受。保护原响应、正常保全关闭及1975项完整备份均在`cold-space-76977f23`保护目录，原三门/首帆及累计2480479tick不变。

固定原生29151的`GameMain.Pause`只置暂停标志，不把保存的惯性速度改为零。`GameData.Import`通过正常`DetermineLocalPlanet/ArriveStar`确定太空本地恒星；加载器frame10在Begin之后通知LoadComplete。暂停和地表严格停稳是不同状态，不能互相代替。

| 状态/转换 | 必须保留的生产证据 |
| --- | --- |
| 菜单→精确数据打开 | 当前完整LastExit、主存档覆盖、保护身份/Journal/消费来源、摘要；不恢复旧任务/时钟/结果 |
| LoadComplete→暂停Sail源 | 实际Native回调，world/player/controller引用、精确保存tick、Sail/warp退出、全部宇宙位置和速度分量；无地表/工厂事实即不适用 |
| 暂停源→库存事务 | 同一world/actor/controller/tick和完整动量切面持续冻结，唯一源隔离，真实1210过滤舱形状及精确容量/零inc；速度非零不等于在暂停中移动 |
| 库存事务→同步读回 | 实际包/舱数量与inc守恒、设置不变、同一冻结动量指纹；unknown使当前暂停执行角色失效，不重放 |
| 暂停源→返航准入 | 原Journey/原母星、当前位置/惯性速度/天体相对速度、储备及2P能源包络；新有限记录先于正常Resume |
| Native151/501/601运行 | 只经正常原生生命周期；501前控制/输入/订单/租期/预算检查，601正常付费运动；不手工模拟、不写零速度 |
| Sail/Fly/Drift→地表Walk | 现行接触归属、向下支撑/法线/高度、严格停稳、五向量零尾部和原生无人机idle；绝对宇宙速度不作为地表局部零尾部 |
| 严格落地→健康保存 | 暂停复核同切面，解除仅自己的源隔离，正常完整保存及新健康凭据，保守核销原Journey；旧失败仍失败 |

回放应将真实速度和null物理事实送入生产冻结guard、原commit权限入口及库存守恒策略，覆盖同速反向、位置变化、tick推进、失去暂停、world/player/controller替换、跃迁尾部、非有限值和unknown失效。合成的库存槽形状须明确为固定Native合同，不冒充该只读响应已执行转移。旧速度阈值不直接放宽；以完整冻结切面和同步动量守恒替代错误参考系假设，地表支持门不改。

下一实机候选必须等整批源码/真实SDK、准确CI、同源安装、模块/独立进程路径及当前完整备份全部合格；从最新LastExit开始，原动作不重放，300秒门及所有储备不变。

## English

This is the whole-state replay audit required after consecutive live candidate failures. Current facts remain in the active snapshot. Source replay, successful Native data opening and normal quit preservation do not prove UI supply, healthy return or rocket acceptance.

The actual first candidate rejected the LastExit lease role before Native dispatch. The next candidate normally opened the same owned save paused at the exact tick, in Sail with no local planet or warp and only its opening quarantine. Its inertial speed was about7.807988m/s. The caller and Native source/inventory checks incorrectly demanded absolute speed<=0.5. No inventory supply or home return was accepted; normal preservation retained the full1975-file boundary without advancing the tick.

Pinned Native Pause changes a pause flag, not stored inertial velocity. Native import initializes the local star before the frame10 LoadComplete callback. A frozen saved Sail cut therefore differs from grounded strict idle. Bind exact world/player/controller references, tick and every authoritative universe position/velocity component; UI transfers require that whole cut to remain frozen, synchronous stock/inc conservation and equal momentum fingerprints. Unknown transfer outcomes invalidate current paused execution without replay. Null ground/factory facts remain inapplicable.

Normal Resume ends frozen-source authority. A separate original-home return must bind the unchanged Journey, actual momentum/orbital motion, Native observer, control availability, finite time/ticks and funded2P envelope. Native151/501/601 and ordinary paid motion perform the transition. Landing still requires existing contact ownership, downward support, strict Walk/zero local tails and physical drone idle before a covering normal save and healthy credential. Old consumption, failures, deadlines, cumulative spending and reserves stay intact.

Replay real nonzero speed and null physics through production guards/commit access/conservation, with negative world/controller/actor/tick/position/momentum-direction/pause/warp/unknown cases. Label substituted Native slot details honestly. Do not replace the old scalar threshold with a wider scalar threshold or weaken ground safety. Qualify the complete batch before another live candidate; retain300-second startup, full backups, one writer and all original outcomes.
