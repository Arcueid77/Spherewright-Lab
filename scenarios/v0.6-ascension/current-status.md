# Ascension current snapshot / Ascension活动快照

2026-11-12。游戏及MCP已正常保存退出，Primary/LastExit126605389，2258项完整保护通过。累计5516127/6000000tick、73990请求，剩余483873tick，返航54000及清理3000储备保留。同源程序、实装标记及全部备份已在关停后重新核验。

## 源码与实装

所选及实装 `21be561cc0b06c2452ce740983c558aea0d93afc` 沿用6546项准确回归、Native29151构建、准确CI及实装SDK资格。本轮首笔正常取铁在57.344秒完成，随后沿同一游戏进程交接调用端，保持原一小时截止。额外完整工厂只读观察的76请求已单独核对正常EOF，并计入累计73990。 [产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/43054994764)

## 当前玩法证据

- 新铁矿6878通过11条新带及分拣器6901接入6269和原熔炉1500，曾观察铁30/min。铜输入6889、铁输入6901、线圈混合输入722和电路板出料714均已正常升级2012。线圈输入筛选为0，板出料筛选1301，420铁正常补入原仓28。
- 卡西米尔制造台6902采用已解锁配方28，共享仓6903已接石墨烯/钛晶石输入及成品输出。既有氢路径188经4新带、6912/6913供料，3座新增电塔覆盖新生产区域。首件晶体已实际入仓，保存前仓内26件。
- 玻璃熔炉6916/6917及钛化玻璃制造台6919/6920已接通两仓和9分拣器，共享电网3、服务比1。正常供入1000石矿、200水及500钛块。保存前仓6918有102钛化玻璃，末次10秒窗口玻璃30/min、钛化玻璃24/min、卡西米尔6/min。
- 正常取出新产出的2卡西米尔和4钛化玻璃，结合2现有处理器，原生手搓2位面过滤器及首枚量子芯片。原任务均成功，保存前背包有1量子芯片。
- 原仓114正常补入1100石墨，保存前821。1705为393436/576000哈希，1504已解锁，1523待完成。末次蓝矩阵0/min、红12/min。原仓26为满仓，磁铁0，后续优先恢复基本供料和仓容。
- 两只2013已按原生配方制造，使用9铁、6磁铁、3铜和2携带普通分拣器，另留1线圈。当前升级入口只支持2011→2012，2013升级准备未接受，6912/6913保持2011且各持有1氢，2只2013保存在背包。共享调用端已增加可选建造itemId，后续可按新鲜原生准入选择普通拆装或2012升级。
- 被拒的旧位置、未接受的批量取料和缓冲等待均保留。实际调整了钛化玻璃仓位置及水的分批量。600磁铁从562取出后因26仓容不足未能转入，已正常送回562，6磁铁用于分拣器制造。全部原终态和历史unknown保持隔离。

## 实际施工与下一步

当前累计施工为基础带218/274、普通分拣器49/64、小仓12/13、MkII制造台6/6、熔炉3/5、电塔14/14、研究站15/15。背包保留2备用熔炉、1小仓、56带、6普通分拣器、2极速分拣器、1量子芯片和原科研/返航物资。升级与普通制造沿独立扣还记录核销。

1. 从2258项保护及126605389边界续接。私有保存输入已更新，当前角色附近768正常取1钛块作为首操作，沿原300秒启动门执行。
2. 恢复满仓26的混合供料。先按新鲜库存及容量将有界铜批次移入有空间的现有仓储，再补磁铁，并核对28的铁和实际蓝产量。继续按实际扣还处理氢输入速度。
3. 推进自动位面过滤器/量子链、绿矩阵及1705/1523。候选位置合读完整工厂快照与原生网格，再由fresh prepare核碰撞和端点。使用已支持的悬停抵达、续行到陆地及实际停稳流程，按操作需要选择落地点。
4. 继续Caph II闭合设计、持续制造/发射/交付、接收器持续实际电力及保存冷恢复，按功能结果推进最终同源双包。 [实施与验收](implementation-plan.md) · [当前用料](resource-increment.md)

## English

Normal save/close preserved primary/LastExit126605389 with2258 verified files,5516127/6000000 ticks and73990 requests.483873 ticks remain with54000 return/3000 cleanup reserves. Stopped-process cohort, installed revision stamps and the entire backup were reverified. Selected/installed21be561c retains its6546-case qualification, Native29151 build, exact CI and installed-SDK evidence. First actual iron withdrawal took57.344 seconds. Caller handoffs retained the original one-hour deadline. The complete factory reader closed normally with76 requests included exactly once.

Miner6878 now reaches6269 and smelter1500 through11 new belts/sorter6901, with an observed30/min iron window. Iron6901, copper6889, mixed coil input722 and board output714 all completed Native2012 upgrades. Filters are0/1301 for722/714. Existing storage28 received420 iron.

New assembler6902 runs unlocked Casimir recipe28 with shared storage6903. Existing hydrogen path188 supplies four new belts/6912/6913. Three new towers serve the production area. The first Casimir crystal entered storage, with26 stored before save. Glass smelters6916/6917 and titanium-glass assemblers6919/6920 use two stores/nine sorters on fully served network3. Normal supply transferred1000 stone ore,200 water and500 titanium. Storage6918 held102 titanium glass. The final10-second window observed30/min glass,24/min titanium glass and6/min Casimir.

Two newly produced Casimir/four titanium glass and two owned processors normally manufactured two plane filters and the first quantum chip. Original tasks succeeded and the backpack held one chip. Storage114 received1100 graphite and retained821. Technology1504 is unlocked,1705 reached393436/576000 hashes and1523 remains pending. Final blue production was0/min and red12/min. Storage26 is full with zero magnets, making input/capacity repair the next priority.

Two gradeIII sorters were normally manufactured from nine iron, six magnets, three copper and two carried ordinary sorters, leaving one coil. The current upgrade entry supports2011→2012. The2013 prepare was refused before acceptance, leaving6912/6913 as2011 with one hydrogen each and both2013 carried. The shared caller now accepts an optional construction itemId. Fresh Native admission will select ordinary replacement or a2012 upgrade. Original location/transfer refusals and waits remain intact. The corrected titanium-glass row and smaller water batch passed. Of606 magnets withdrawn from562,600 could not enter full26 and were normally returned, with six used in sorter manufacture. Historical unknowns remain isolated.

Cumulative placements are218/274 belts,49/64 ordinary sorters,12/13 warehouses,6/6 MkII assemblers,3/5 smelters,14/14 towers and15/15 laboratories. The backpack retains two spare smelters, one warehouse,56 belts, six ordinary/two gradeIII sorters, one quantum chip and original research/return materials. Updated private inputs resume this boundary with one normal nearby768 titanium withdrawal within300 seconds. Restore storage26 capacity/magnets and storage28 iron, then continue automatic plane-filter/quantum/green production,1705/1523, Caph closed delivery, sustained receiver electricity and cold continuation. Use supported hovering arrival, onward navigation and actual land-based settling as operations require.

Earlier cuts remain in fixed history. [前次快照 / Previous cut](https://github.com/Arcueid77/Spherewright-Lab/blob/4cf7327402fca4f07de2d1a089c94704b5aa92bc/scenarios/v0.6-ascension/current-status.md) · [持续授权 / Standing authority](../../operations/standing-authority.md)
