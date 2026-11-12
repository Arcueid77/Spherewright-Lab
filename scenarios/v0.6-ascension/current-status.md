# Ascension current snapshot / Ascension活动快照

2026-11-12。当前owned游戏持续运行，所选、实装及实际加载源码均为14c7d66c。唯一调用器已正常交接到ore-crossing-live，游戏进程沿用，原冷启动时钟保留。首批11矿切面127134331对应累计6045069tick。有限累计上限900万，54000返航及3000清理储备持续保留，本次冷启动起的有限墙钟上限86400秒。

最近普通保存动作在127124075成功。最近关停后完整保护仍绑定Primary/LastExit127035116及2278项文件，该边界累计5945854tick。后续实耗继续按原游戏tick累计，新关停完整备份待本阶段收尾。

## 当前实机结果

- 应力科研1523已达到4860/360000，尚余1973份五色矩阵需求。本轮新增15红已原生消费，100个新产绿已正常进入机甲科研缓存。最近明确切面为蓝176、黄1973、紫173及绿95整件等效科研点，红缓存0。实物、科研点及实际消费分别记账。
- 五层引力矩阵工厂已完成原生建造、供电和首批新增入仓验证。首两批正常投料合计90量子/90透镜，对应180绿。已有120个工厂绿正常取入机甲。另取30量子及20透镜，第三批20/20正常投料已完成，对应累计220绿。基础铁料阶段的正常资本制造已完成，资本备齐切面回读40带、8普通分拣器、1仓、2塔、2矿机及3熔炉，新矿及出矿接力已完工并开始实存供料。
- 卡西米尔供料仓新增200钛晶石和400石墨烯。钛化玻璃仓新增400钛块，玻璃线新增1000石矿，碰撞器供料仓新增400铁。均有原转移终态。处理器、水和后续产物仍需连续补充与产能平衡。
- 基础电路板和处理器停产链已追到原铁矿输入短缺。新矿机覆盖8矿点，已通过两座接线塔接入主网3，第三座塔覆盖出矿接力，矿机和接力均为完整供电。新仓从原生空仓起点实际捕获11铁矿，10件预声明门槛通过，正在自然积累首批400矿。旧带1709由独立短带和正常分拣器跨越，原路径保持。 [阶段用料](resource-increment.md)
- 首次实际工作在268.125秒通过启动门，正常补入8燃料。前次300.656秒超时和数量拒绝原件保留。运行中本次附接的正常导航在78tick完成原生Fly、地表投影抵达及任务释放，随后观察到Walk及20透镜取料成功。
- 水面低速Drift普通移动及后续8矿点建矿已经通过，结束时仍曾观察到Drift，随后自然转为Walk。先前要求先Walk的等待过严，已改用当前存档的普通被动漂移续移路径。原建筑阻挡、233米飞行门槛拒绝、低速拒绝及严格Walk等待失败原件保留。调用端对准确可重试低速准备拒绝的有限重新观察通过205项离线回归、源码锁、证据核验及准确CI。 [调用端CI](https://github.com/Arcueid77/Spherewright-Lab/actions/runs/43165778859)
- Issue #5已重新读取，仍为OPEN且无评论。当前产品拆除白名单覆盖矿机、分拣器、限定空仓和基础带头，风机仍需补单台原生拆除、电网影响预览、回收和未触及拓扑核验。 [Issue #5](https://github.com/Arcueid77/Spherewright/issues/5)

## 源码和执行边界

产品源码为 `14c7d66cda64d40c201577313740be05e6918479`，版本0.6.0。准确Native构建、6559项产品回归及源码CI通过。实装清单SHA-256为 `C1A1D058290A683529DDFD8D9C56A4E49EFD7576AEE536CB37CC68D02D90DCEC`，5项Plugin文件及224项MCP文件已核，实际75工具SDK已用于本轮方案完整准入。原安装事务及外层超时保全记录持续保留。 [产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/43098686696)

当前调用器采用199992请求上限，另保留8次已完成只读观察，合计受200000全局上限约束，最终边界统一合并实际账目。标准输出/错误流额度为512MiB/16MiB。当前有限施工上限为矿机2、熔炉6、小仓18、普通分拣器75、电塔18、基础带325、高速分拣器5及极速分拣器4。新增极速分拣器以原生无初始筛选模式接入专用铁矿线，原生非零初始筛选当前支持2011/2012。其余额度沿用。全部既耗、原动作和隔离记录持续保留。

## 继续顺序

1. 完成首批400铁矿转运。投入混合仓28前将原铁料出口594筛选绑定1101，硅矿出口793继续使用1003。接通原熔炉及新增冶炼，核对第三批绿矩阵的真实产出，再恢复电路板、线圈、处理器与其他矩阵的连续供料。
2. 按剩余1973份五色科研需求推进生产与实际消费，完成1523。随后在Caph II重新核对6度闭壳设计的210结构点/224细胞点准确成本及现有库存，连续完成当地制造、发射和真实交付。
3. 建造接收器并绑定实际电网，按预声明游戏tick跨度及最大采样间隔验收持续非零实际电力。正常保存、冷恢复后复核设计、进度、设备及持续电力，再生成最终同源手动/Thunderstore双包。 [实施与验收](implementation-plan.md)

## English

The owned game continues on selected, installed and loaded14c7d66c. One caller handed normally to ore-crossing-live while preserving the game process and original cold-launch clock. The first11-ore cut at127134331 corresponds to6045069 cumulative spent ticks. The9000000 ceiling retains54000 return/3000 cleanup. The finite wall allowance is86400 seconds from that same cold launch.

The ordinary save completed at127124075. The latest complete stopped-process protection still binds primary/LastExit127035116 and2278 files, with5945854 spent at that boundary. Later live spending remains cumulative. A new complete stopped backup follows stage cleanup.

Stress research1523 reached4860/360000, leaving1973 of each matrix color. Fifteen additional red cubes were normally consumed. One hundred newly produced green cubes entered the mecha point buffer. The latest explicit whole-equivalent buffers hold176 blue,1973 yellow,173 purple and95 green, with zero red. Physical items, research points and actual consumption retain distinct accounting.

The five-layer green factory passed normal construction, power and first new stored-output proof. The first two feeds total90 quantum/90 lenses and fund180 greens.120 factory greens were normally withdrawn. Another30 quantum/20 lenses were acquired. The third20/20 feed completed and cumulative feeds fund220 greens. Normal iron-stage capital manufacture completed, with40 belts, eight ordinary sorters, one store, two towers, two miners and three smelters observed in the backpack. The new eight-vein miner completed after a successful ordinary passive-drift move. Native terminal receipts also preserve200 titanium crystals/400 graphene into Casimir supply,400 titanium into titanium glass,1000 stone into glass and400 iron into collider supply.

Board/processor stoppage traces to missing original iron-ore input. The complete84-node iron survey and exact existing connections are retained. The bounded support stage reserves one miner, three smelters, one store, eight ordinary sorters, two towers and40 belts. New capital costs35 iron,11 boards, six bricks and three coils. Current ceilings are2 miners,6 smelters,18 stores,75 ordinary sorters,18 towers,325 belts,5 fast sorters and4 gradeIII sorters. The new mine and relays have full power on main network3. A normally empty depot captured11 real iron ore, passing the predeclared ten-item gate. It is accumulating the first400-ore shipment. A separate short belt and normal sorters preserve legacy belt1709. The gradeIII pair uses Native unfiltered initialization on the dedicated iron-ore line. Nonzero initial filters currently support2011/2012. Existing allowances and actual spending continue.

The startup gate passed at268.125 seconds with eight normally loaded fuel rods, retaining the earlier300.656-second miss and exact-count refusals. This attachment's78-tick navigation proved Native Fly, projected arrival and task release, followed by observed Walk and successful20-lens withdrawal. Earlier obstruction,233m-arc refusal, low-speed refusals and the180-second strict-Walk wait remain preserved. The caller now reobserves the exact retryable Native low-speed prepare refusal within the original60-second/16-attempt allowance.205 offline tests, source/evidence checks and exact CI passed. Ordinary low-speed Drift continuation and the following eight-vein construction passed. Drift was still observed immediately after arrival, followed by natural Walk. The earlier requirement to wait for Walk was overly strict and has been corrected in this execution path.

Product14c7d66c passed6559 cases, exact Native build and source CI. Installed manifest C1A1D058290A683529DDFD8D9C56A4E49EFD7576AEE536CB37CC68D02D90DCEC binds five Plugin/224 MCP files. Actual75-tool SDK admission passed. Original installation/timeout reconciliation is retained. The new writer reserves199992 requests plus eight separately preserved observer requests under the200000 global maximum, with512MiB/16MiB stdout/stderr allowances.

Issue #5 remains open without comments. Wind turbines remain outside the current dismantle whitelist and need single-target Native demolition, power-impact preview, recovery and unaffected-topology verification. Continue full research, Caph II manufacture/launch/delivery, the210-point/224-cell closed face, receiver electricity and cold continuation before the final coherent package pair.

[前次快照 / Previous snapshot](https://github.com/Arcueid77/Spherewright-Lab/blob/b50363b1545dc1286097088f774b86bbd01a4003/scenarios/v0.6-ascension/current-status.md) · [持续授权 / Standing authority](../../operations/standing-authority.md)
