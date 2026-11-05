# Voyager active snapshot / 0.5 活动快照

2026-11-06：续接已核最新完整边界及唯一writer；9eaca完成恢复落盘全链审计、精确拒绝诊断、准确CI/同源冷安装，游戏仍关闭。保留c79健康接管失败及约326秒启动失败，不改写为通过；LastExit123766112、Primary123757596较旧不得加载，累计2676850tick，2020项全备份重新核对。下一次受保护恢复先做原正常装燃料，再续当地火箭；当地首火箭/接收点/双包未闭。

- **授权：** [现行授权](../../operations/standing-authority.md)及[火箭准确增量](rocket-scope-increment.md)有效，不再重复请批。累计实耗、54000返航、能源/翘曲器下限、Native门、单writer/维护者、物料守恒及unknown隔离保留；不正式发布。
- **源码/实装：** 选择 **9eaca0763801cf6fad3ac19a76c499685422c51f**，[准确SHA CI成功](https://github.com/Arcueid77/Spherewright/actions/runs/42066979826)。保留c79不可变Journey作用域修复；新增完成阶段精确绑定谓词、Store拒绝及tick/储备/期限观察，未放宽门。生产协调器/Store回放、Native编译、SDK/PE及同源目录/单文件资格通过；**磁盘已同源冷安装9eaca**，官方事务仅提交一次，安装后实际PE/MVID及完整备份通过；实机新恢复仍待证明，不生成双包。
- **最新完整边界：** **LastExit123766112**为新失败恢复的最新完整保全，**Primary123757596**较旧不得加载回退；**2020项**全量副本通过，累计**2676850 tick**，游戏/MCP均关闭。原航行和新resume均已known terminal failed，绝不重放；原生暂停稳定切面仅作保全，不冒充idle。副本：`cold-scope-c79b5aa6/failed-resume-normal-preservation/after-normal-close-complete-backup/`。此前765850/2016项副本与旧账完整保留。
- **实耗/范围：** 有限累计上限3888000；已付矿1/2、聚变1/1、塔6/9、化工1/1、仓3/3、炉1/1、MkII3/3、带48/120、分拣21/24、弹射器1/1；新批井0/1。旧13段高架不退款。新Caph出航确切消耗1枚翘曲器；当前返航后续消耗以原动作实测回执为准。母星板/燃料各100→0，Caph各0→100、在途订单归0；原帆4制造/弹药4→0/弹道→云及恢复保持成果不重跑。
- **首错/修复：** 旧恢复进度扣账污染新Journey的根因已由c79修复：生产tracker/Store及真实低核心回放通过，原借窗/改额/倒账仍拒绝。实机新resume到健康接管落盘处失败：`failed_landing_healthy_admission_persistence_unproved`，generic firstFailure未带当次Native细分；当前durable run为failed_health、spent7908/anchor123766112、LastLanded=null。先完整审查CompleteRemoteResumeAdmission→释放租约→TryFinishFailedLandingAdmission→Store验证/原子落盘与失败保全，补足真实回放和精确拒绝因子；不删检查、不先断言I/O或某个谓词，不再连续开候选逐点试。
- **当前/下一动作：** [完整审计](recovery-completion-audit.md)已覆盖启动、源文件租约、接管、Store、重存及失败保全。c79的45.44→285.84秒确为原生原型/模型预加载拒绝等待，未绕过；旧失败内因仍未观察，不断言I/O或某谓词。9eaca沿同一最新Caph准备新鲜恢复及正常装燃料20；既有井1/Q2/合金6/处理器6/板3/燃料100保全。随后当地有限配方、最小接收点、真实首火箭及最终双包继续。新原件`cold-admission-9eaca076/`，旧原件`cold-scope-c79b5aa6/`；历史见[c0ef05c](https://github.com/Arcueid77/Spherewright-Lab/tree/c0ef05c)。

| 验收 | 当前真实状态 |
| --- | --- |
| 外星扣料/建成/连接/供电 | 已证；已付43恢复续建无重复扣料，复用当地实体；目前聚变燃料已空，后续需正常供料 |
| 当地原料→目标制造整链 | 已证；冰→石墨烯、石→玻璃→棱镜→合并器→帆4 |
| 首帆精确消耗/弹道/云转换 | 已闭；弹药4→0、最终弹道池0/轨道+4，恢复保持 |
| 跨星辅料真实到货 | 已闭：板/燃料源各100→0、Caph各0→100 |
| 保存恢复后续建/续运 | 已证：续建/首帆保持；同船/货100保存恢复后真实续行并到货 |
| 科研/接收结构/当地首火箭 | 1141/1303/1522正常解锁；母星芯片12/井1制造与保存已证；接收点/当地首火箭未闭 |
| 最终同源手动/Thunderstore交审双包 | 全功能闭合后生成；尚未形成，不正式发布 |
