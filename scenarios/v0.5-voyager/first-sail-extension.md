# 0.5 first sail and rocket extension / 0.5 首帆与首枚火箭扩展方案

## Current preserved construction entry / 当前保全施工入口（2026-11-03）

冷启动燃料公开接口e48已准确CI/冷安装。旧Caph站已有电路板slot1及燃料slot2 Demand；实际多料到货仍未证明。必要短走原action0adf因原生接触停止尾部未证明而unknown，禁止重放/自动Resume，已正常退出保存LastExit121202004并完成1750项完整备份；Primary121201952较旧不得加载。累计112742、剩103258tick，返航54000不变；新增外星建筑仍零。下一技术动作先诊断接触/保全缺口，原整体目标和已批准施工上限保留。电塔上限4→9的增量询问尚未收到批准。

### Preserved earlier healthy entry / 保留的早先健康入口

6e68已真实从最新Caph LastExit无损恢复并形成新的completed_health来源，旧失败出航不改。旧站2的电路板Demand槽已真实配置；尚无自动多料到货、新外星建筑或当地制造验收。正常保存关闭后Primary/LastExit均121201181，1736项完整备份通过。累计111919、剩104081tick，继续保留54000返航。启动到首笔配置289.829秒，通过300秒门。先在关游戏状态下细化独立主电网、材料缓冲及当地首帆全线的分段布局/连接，再按原已批准上限执行。

### Preserved failed landing recovery / 保留的失败落地恢复阶段

当前已到Caph402但原出航0125因落地补能交接失败而terminal recovery_required；LastExit121200886完整保全，不重放航行、不退回旧Primary121194676。累计111624/216000，剩104376tick，返航54000不变。物料108燃料及板2随身；外星新施工仍零。源端先完成无损失败落地恢复及已建旧站完整证明后，再按原批准首帆上限执行当地刷新/布局/电网/制造/真实发射。恢复研发现状详见current-status；源码/只读捕获通过不等于已恢复或已施工。

### Preserved departure refinement / 保留的出发阶段细化

母星设备和有限燃料已正常备齐。既有空仓765接原站1657的8组原生直线路径均与既有带重叠，拒绝发生在创建前，新增母星带/分拣器仍为零；不在此处继续铺母星工业。首帆先采用所有者已允许的母星运料：从该仓正常取回为跨星运输准备的燃料100，加随身8共108根，携带原有电路板2及首帆设备前往Caph402。仓内板100保留作后续自动供给。该取料是新的反向正常转移，不重放原存入动作、不退款或修改账目。

出发前仍须fresh公开旧Caph站所有权读回、路线/能源/翘曲器及全程工作加54000返航储备预检。最新已保存121194439，累计105177/216000、剩110823tick；新的Native全程上限取min(108000,实时剩余-3000)，其内继续保留54000返航，不能当作新增时间。到场先刷新旧站、全网、当地石矿/可燃冰、建筑端口和布局；短段保全后按既批总额施工。母星尚无新增连接，因此Caph仍保留原120带/24分拣器及全部主体上限。

背包运料只支援首轮当地制造，不代替多物料供需配置/真实物流到货验收。该验收继续纳入完整0.5闭合：Caph布局和用料确定后再完成母星可行接站路径及跨星真实供给；若届时超既有总额才提出准确增量。火箭扩建/科技完整供料/最小接收目标和最终双包仍全部保留，正式发布另批。

The first-sail expedition now carries the already authorized finite fuel/support packet. Eight mother-world straight feeder proposals were rejected before creation because of existing belts; zero new feeder objects were placed. Fresh ownership, route, energy, warper and conserved return-budget checks still precede departure. Carrying supplies does not close the later multi-material station/real-delivery requirement or any offworld manufacture/launch acceptance. No resource or time allowance increases.

## Current owner intent / 当前执行方案：验证外星系建设

2026-11-02所有者澄清：“就是想验证外星系建设能力”。据此修正此前偏向母星补全产业的方案：**0.5的主验收是远端基地的规划、运输、施工、连接、供电、制造与保存续建；首帆和首枚火箭是该基地的代表性运行成果。** 母星准备完整成品或在母星发射不能替代这项外星建设证据。所有者随后明确续接自主执行，并在启动流程功能实测达标后恢复主目标；此前方案审阅暂停已经被该新指令替代。当前进度和剩余预算仅以[current-status.md](current-status.md)最新条目为准。

### Site and division / 场地与分工

优先现场为 **Caph星系二号星（Caph - II号星）**，复用已实际建设矿机/星际站并完成跨星运输验证的站点。已有原生观测证明该星有铁、硅、钛、石矿、可燃冰、分形硅石和水；铜/煤相对有限，未观测到原油。该记录支持选择候选星球，不代替施工前的新鲜矿点、地形、发电和布局预检。Caph一号气态巨星和三号星的资源观测仍不完整，本轮不先摊开多个基地。

- **母星Gamma Vulpeculae四号星**：复用既有工厂完成必要科技、建筑/燃料/电路板/处理器等备料，组织一次有清单的跨星支援。科研补产属于出发准备，不把建设大套母星新工厂作为本轮验收主体。
- **Caph二号星**：新建/扩建全部验收用制造线、独立主电网、分拣/带路、发射设施和缓冲。当地资源进入当地机器并形成产品，保留原生真实扣料/产出和发射证据。
- **原矿点小网及供矿线**：保留既有成果。新基地供电优先与原已验收的小网分开规划，避免在缺少全网预检时直接把高负载并入仅支撑矿点的两台风机。原站空闲槽位和既有母星站优先复用；多物料槽位、供需方向和母星派船能力先核定，不默认旧单物料配置足够。

### Remote construction stages / 外星建设阶段

| 阶段 | Caph二号星实际建设和运行 | 母星支援/下一阶段关键前提 |
| --- | --- | --- |
| 落地基建 | 站点旁选独立施工区，建立主电网、入料/出料缓冲和可恢复的施工任务 | 设备、燃料与返航储备；完整布局、端口、能源和运输预检；不重复原已完成对象 |
| 首帆制造厂 | 可燃冰采矿→石墨烯/氢；石矿→玻璃→棱镜→光子合并器；石墨烯+合并器→太阳帆；安装弹射器并真实发射 | 初期电路板及必要设备由母星运入；预检发电持续能力、氢副产物缓冲、原生轨道/射界与单一发射来源 |
| 火箭制造扩建 | 钛/硅采矿冶炼；石墨烯+钛→碳纳米管→框架；当地帆+框架+处理器→戴森球组件；当地组件+燃料棒+量子芯片→火箭 | 母星完成必要科技并供应处理器、量子芯片、燃料棒、钛合金等辅料；首轮不要求在无油冰原星复制完整油化/科研链 |
| 首枚火箭 | 安装垂直发射井，接通供电供料，建立该恒星的最小有效原生接收目标，实际发射、飞行并抵达 | 按发射井峰值核准扩容、材料/时间和待建清单；接收目标与原生发射控制接口须先验证 |
| 保存续建/续运 | 至少一次在外星分段施工中保存恢复，识别已建/待建和已付料继续施工；制造/供料状态恢复后继续真实运行 | 世界、星球、任务与实体归属一致；旧动作不重放、材料不重复扣除；保留跨星支援与返航能力 |

本轮允许必要辅料从母星输入，目标是证明远端基地可建设并运转，不要求所有原料在外星自给。但被验收的太阳帆/组件/火箭必须来自外星实际制造线，不能用背包里原有成品替代。现有母星2张帆、储仓物品和弹射器待建体继续保留，其回收转运或作为独立续建回归点另行纳入准确清单，不自动拆除，也不计作外星验收。

### Product capability and acceptance / 产品能力与验收

现有已验收能力主要覆盖外星矿点、被动站、少量供电/分拣及有界带路。扩展必须补足可复用的远端普通制造建筑施工、多物料物流配置、整线分段规划/连接、已付料待建体保存续建，以及发射井/最小结构目标观察与控制，不能仅放宽旧白名单或用场景脚本绕过原生门。

每阶段保留可验收产物：外星真实新建实体及扣料→原生连接和实际供电→当地采矿/制造产出→支援物流实际到货→保存恢复后续建/续运→当地首帆与首枚火箭的实际消耗/飞行/抵达。先做变更范围内的增量回归，再以真实外星场景验收；最终准确源码的完整CI结果复用，不反复本地全量。

既有累计时间/物料/返航储备仍保留；当前剩余约36.9分钟游戏时间不能直接作为新跨星往返与完整基地施工的充分预算。待静态方案和可执行能力准备完成，再把出发物料、运输槽位、电源/燃料、施工段数及返航余量集中核算；必要的实际硬额度增量在执行前交所有者决定。当前不出发、不新建、不换装。

## Resumed executable plan / 本次续接执行方案（2026-11-02）

本次用户续接撤销此前的方案暂停。按下列阶段推进；只在确需增加实际硬额度时集中提交准确增量。首帆和首火箭均在Caph二号星402制造、供料和发射，母星104仅作科研、设备和必要辅料支援。母星已有2帆及原弹射器待建体继续保全，不作为外星成果。

| 阶段 | 当前可执行工作与验收 | 下一阶段关键前提 |
| --- | --- | --- |
| A 安装与现场预检 | 核销中断安装的意图/回执，复用c595合格工件；同源冷安装、菜单/模块验证；fresh公开恢复方案必须覆盖121172578及完整身份。恢复后限时刷新库存、科技、路线与旧站点证据，正常保全。 | 不带尚未具备的制造/发射能力出发；确定完整料单、同网功率、返航与保存预算。 |
| B 外星首帆 | 先勘察旧站附近独立施工区；建独立电网、辅料缓冲，配置多物料支援。当地可燃冰→石墨烯/氢；当地石矿→玻璃→棱镜→光子合并器；母星运电路板；当地组装太阳帆、储仓/分拣供弹射器，交叉核对扣料、弹道和抵达。 | 原生端口/供电、氢副产物去向、发射轨道/射界；保存后准确识别已建/待建对象，不重复扣料。 |
| C 外星首火箭 | 扩当地钛/硅冶炼、碳纳米管、框架、戴森球组件和火箭；母星运钢/硫酸、处理器、量子芯片、燃料棒及设备。建发射井和Caph恒星最小有效接收目标；验证火箭1503制造、精确消耗、真实飞行及抵达。 | 波函数干扰→量子芯片→垂直发射井正常研究；公开发射井和结构目标能力先完成Native研究及测试。 |
| D 保全交审 | 分段施工中、供料制造中各正常保存/恢复续建续运；发射结果保全后完成同源手动/Thunderstore格式双包及审查。 | 功能闭合才出最终双包；正式发布仍另批。 |

### Construction envelope / 建设清单与额度

首帆施工预检清单：石矿/可燃冰矿机各1（满足覆盖的已有设施可抵扣）、玻璃熔炉1、化工厂1、棱镜/合并器/太阳帆Mk.II制造台各1、外星弹射器1；独立可持续电源候选微型聚变站1，电塔上限4、氢缓冲罐1、物料缓冲仓上限3。即最多17座主体设施，普通分拣器上限24、平带上限120（按原生可行路径逐段，每段不超过现有12新增带能力）。**本次所有者已明确答复“批准上述首帆施工上限”。** 这份批准覆盖上述准确新增数量上限，不证明已建或可建；实际数量仍用端口/路径预检抵扣复用设施后冻结。保留原时间和54000返航储备，不外推火箭扩建或新增时间。不把原矿区2风机视作新厂供电。

2026-11-02本轮fresh目录实测：聚变站2211额定250000J/tick=15MW，燃料类型mask2；两矿机共14000J/tick、玻璃炉6000、化工厂12000、3台Mk.II共27000、弹射器30000、24分拣器最多7200，主体额定合计96200J/tick=5.772MW，未计接网/站充电。既有站保持被动且不借用旧2风机容量；先验证新完整同网可持续服务再接厂。聚变站额定烧热15MW，燃料清单按该上界及准确运行时段、1802目录热值核算，不能按负载推断节省。

火箭扩展候选：钛/硅/钛合金冶炼各1、碳纳米管化工厂1、框架/组件/火箭制造台各1、发射井1；电源、缓冲、物流槽位及连接另按全线负载/端口收敛。初轮只放行最少可归属的产物，预留恢复后继续生产/发射的有限物料；不要求外星全产业自给。所有item/recipe、每轮产出、额定功率及科技条件均以已保存目录和fresh公开目录核定，不用记忆填参数。

### Conserved time and reserves / 守恒时间与储备

- 本次已通过fresh原生退出档恢复并正常保存，最新Primary/LastExit同为121175805。已耗86543/216000 tick，剩余129457（35.960分钟），不退款、不重置旅程；此前83316及121172578截点保留。
- 继续保留原返航储备54000 tick及已有能源/翘曲器下限；剩余可分配工作预算至多75457 tick（20.960分钟），其中还须扣除出航、勘察、施工、制造、原生射界等待和正常保存。54000是保留旧储备，不能当作新往返时长证明。fresh路线预览能源/翘曲器通过，距离2.77594光年，原生翘曲器6/所需3，返程核心下限1.28GJ；1660tick仅理论最大速度下限，不作为航程承诺。
- 原母星方案蓝/紫/红补产理想关键路径约27分钟，已大于上述工作余额，且尚不含新航程/建设。它不是新方案已测工期，也不能据此认定36.9分钟够用。先核库存抵扣、实际研究速度和路线，再给出需要的准确新增tick；未经批准不消耗超额。
- 原施工额度记录为矿机1/被动ILS1/电塔1/风机2/带12，已用于旧矿区。本次首帆准确新增施工上限已由所有者批准，如上；支援消耗、火箭扩建及游戏时间增量仍保留准确预检/决定边界。相关研发持续进行。

### Proven public capability gaps / 已证实的公开能力缺口

c595源检已确认：`StructuredConstructionBinding.SupportsItem`只覆盖2301/2104/2201/2203/2205/2001/2011，不能直接承担普通制造厂；`ValidateVoyagerJourneyLocalCommit`远端配置只支持站存储/输出/充电，制造配方和弹射器配置未纳入有界远端预算；公开合同缺少发射井与结构目标的完整读写。多槽站配置已有逐槽原生接口，但旧被动站/恢复准入是否接受运行中的多物料制造厂须补核，不把单槽矿区证据外推。

修复必须补足同源公开合同、Native绑定、预算/回读、持久恢复及相关回归，不能只删白名单。当前阶段先完成安装/菜单身份与无损恢复预检，随后围绕实际最小产线补齐能力；同SHA5522项CI复用，不重复本地全量。

本次新增afebbbd2已补上述首帆工厂主体/有限配置/整线保存准入，217+21增量、Native/solution、独立只读审查和准确SHA的5580完整CI通过；开发目录v2同源资格合格。已同源安装并通过真实模块/菜单核验，尚未恢复世界或实机证明新外星路径。火箭最小原生接收目标创建仍未补齐；只读火箭/节点观察不冒充该写入能力。

当前阶段的限量制造目标为当地4帆：recipe32一次用可燃冰2→石墨烯2+氢1；recipe57六次用当地石矿12→玻璃6；recipe11两次→棱镜4；recipe68两次加母星电路板2→光子合并器2；recipe70两次→太阳帆4。这是最低整链产物与原料账，不将正常采矿/上游缓冲余量隐去。设备直层备料上限（假设全无设备库存）为铁144、钢28、钛合金12、石材26、玻璃12、石墨烯24、碳纳米管8、齿轮64、磁线圈10、超级磁场环20、电路板34、处理器21、Mk.I制造台3；**非递归最终扣料表**，先按现场设备/背包抵扣，再展开缺失可手作辅件。母星已有2帆不进入此当地4帆归属账。

供电须明确冷启动：新聚变站最初无燃料，而供料分拣器自身需电。先核原小网的完整成员/真实服务率，仅在其足以驱动有限引燃模块时选择连接；先建并供燃料形成真实15MW服务，再接制造负载。不能把无燃料的额定15MW当已供电，也不能默认原两风机承担完整5.772MW新厂。液罐使用原生portPoses带口，非slotPoses分拣口；母星支援站须真正接通供料，配置Supply/Demand不代表货物已入站或跨星送达。必要的额外母星喂料连接如超出现有施工额度，应先形成具体公开预检和准确增量再交所有者决定。

This continuation resumes authorized work, with Caph II as the manufacturing/launch site. The construction numbers above are planning ceilings awaiting native layout and an exact owner decision for any increase beyond existing hard allowances. Preserve 83316 spent ticks, the latest121172578 progress boundary and all return/energy/warper reserves. Source gaps are proven; deployment, loaded runtime and off-world acceptance remain separate evidence layers.

## Superseded proposal / 旧母星集中方案（已撤回，不执行）

2026-11-02所有者要求先不执行、先给出完整产线与星球分工方案，并采用影响范围内的增量回归。当前停止施工、换装、读档和发射；本节是待审方案，不是新增施工或硬预算增量授权。已有2张太阳帆、1个储仓物品和1座准确已付料弹射器待建体继续保留，不重新制造/下单。

### Planet allocation / 星球分工

- **Gamma Vulpeculae四号星（当前母星，地中海）**：全部新增科研、化工补料、高端组装和发射设施。依托现有仓储、电网、油/水相关设施及物流站；分科研、化工、精密制造和发射四区。具体空地、射界及同一电网可用余量尚未完成施工预检，不虚构坐标。
- **已验收的外星分形硅石矿区**：继续复用采矿/供电/跨星运输/母星晶格硅消费，不新增第二套矿点或运输线路。该原线不是新增工厂的带数或建筑预算。
- **本星系一号熔岩星、二号黑石盐滩**：首帆/首枚火箭阶段不新建产线；可见资源类型不能替代实际矿点和产能证明，后续持续生产的硅/钛缺口另行核定。
- **三号气态巨星**：首发阶段不新建采气设施。已有氘核燃料棒库存支持首枚火箭；气体成分和既有采集能力尚未核实。

### Science critical path / 科研关键路径

最近科技快照证明仅需按顺序补波函数干扰→量子芯片→垂直发射井；它们的前置科技已解锁。合计需要蓝3600、红3600、黄1600、紫2600矩阵，共1224000研究哈希。已观察到的仓储加背包为蓝332、红3221、黄6040、紫1032；按这个可见范围估算需补蓝3268、红379、紫1568。未包含物流站/液罐和此后自动产出，因此不是当前完整库存承诺或最终扣料预算。

科研补产必须与首帆验证并行，避免首帆完成后才开始等科技。优先复用现有科研站，以实际研究速度决定补站数量；目标让研究尽量在约27分钟的补料生产期内完成。

### Production modules / 母星新增或扩建模块

下表是所需**目标总产能/配置估算**，已有机器和产能先抵扣，不代表全部新增。制造台按已解锁Mk.II基础速度计算；研究站/化工/冶炼同样按基础速度估算，最终以现场实际速度校准。供料限量，成品达到本轮目标即停止追加，产能目标不授予无限运行。

| 模块 | 目标能力与建议配置 | 复用与依赖 |
| --- | --- | --- |
| 磁线圈→蓝矩阵 | 线圈至少180/min，2制造台；蓝180/min，9生产研究站 | 磁铁、铜块、电路板用现有库存/生产 |
| 红矩阵补产 | 20/min，2生产研究站，补足约379 | 复用高能石墨和氢，不扩黄矩阵 |
| 塑料 | 60/min，3化工厂 | 补紫矩阵需要的塑料约1383；现有精炼油支持大部分，净需额外精炼油约389，先核现有炼油/储罐能力 |
| 碳纳米管 | 120/min，4化工厂 | 紫矩阵及成品本体合计较可见库存缺约1280，用现有石墨烯和钛块，不新探刺笋 |
| 粒子宽带→紫矩阵 | 宽带60/min，8制造台；紫60/min，10生产研究站 | 晶格硅可见库存3277，补1568紫需3136；处理器库存可供首阶段使用 |
| 玻璃→棱镜→光子合并器→太阳帆 | 玻璃约90/min，3炉；棱镜、合并器、帆各1制造台，帆30/min | 与钛化玻璃共享玻璃供给；现有2帆先用于首射/恢复验证 |
| 卡西米尔晶体→位面过滤器→量子芯片 | 卡西米尔1台、钛化玻璃1台、位面过滤器2台、量子芯片1台；芯片约5/min | 使用现有钛晶石、氢、水、钛块和处理器；配方逐级随科技解锁 |
| 框架材料 | 1制造台，目标6/min | 复用碳纳米管、钛合金、高纯硅；与发射井/组件共用 |
| 重氢→奇异物质→引力透镜 | 1对撞机分批切换重氢/奇异物质，透镜1制造台 | 对撞机是不能用背包制造替代的实际生产环节；金刚石、粒子容器和铁块用现有库存 |
| 戴森球组件→运载火箭 | 组件1制造台、火箭1制造台；目标火箭1/min的可复用能力，首轮限量1枚 | 共享帆、框架和量子芯片；燃料棒取现有库存 |
| 发射设施 | 完成已有弹射器待建体；新增垂直发射井1座 | 正常供电、储仓/分拣供料，预检端口/跨度/射界后才铺连接 |

仅计算**1座发射井+1枚火箭本体**：量子芯片12、框架材料36、引力透镜20、钛合金80（另框架消耗36）、戴森球组件2、燃料棒4；组件另需太阳帆6和处理器6。量子链需位面过滤器24、卡西米尔24、钛化玻璃48；透镜需奇异物质20和金刚石80，奇异物质需重氢200，可见重氢120，需补约80。以上不含新增生产设备、科研站、分拣器、电塔、带路和缓冲设施的建设成本，不能冒充完整施工料单。

### Layout, power and preservation / 布局、供电与保全

- 科研区靠矩阵仓储和现有研究站，化工区靠现有油/水和氢缓冲，精密制造区靠处理器/钛硅仓储，发射区接同一可用主网并核真实射界。跨水移动允许，以可停稳的落点为边界；不在水中间点停留后立即施工。
- 先核每段源/目的端口、native跨度、完整带路和供料可达，再提交该段。提前检查下一段接口，保留已完成实体。研究/化工阶段的新增负载先按约50–60MW余量筛选，实际以同一网络可持续供电和燃料为准；总名义容量不能代替现场供电证明。对撞机与研究/发射可错峰，是否扩大发电按实测缺口决定。
- 氢副产物必须有缓冲和去向，避免反堵精炼油/塑料；现有物流站和储罐优先复用。成品精确限料，临时储仓和接收节点都纳入保存清单。
- 最小原生戴森结构目标只为接收第一枚火箭，不扩大成完整戴森球施工或额外应力升级/绿矩阵链。验收到达后结构施工量增加，不要求一枚火箭建完节点。恢复验证尽量安排在生产/供料已保存后再放行发射，具体待原生发射控制预检确认。

### Order, time and verification / 阶段、时间与验证

1. 补齐并集中验证施工开关、产线分段保全/续建、发射井观察和最小结构目标能力，统一同源换装；沿用原世界与准确待建体。
2. 只读核实现有设备/研究速度/全库存/电网/场地，冻结本阶段准确新增清单。搭或扩蓝/紫/红补产，排三项科技；同时完成首帆的实际发射、抵达和保存恢复。
3. 随科技解锁，接通量子芯片、框架、奇异物质/透镜、组件及火箭线，正常制造发射井和限量火箭。
4. 验证最小接收目标、真实火箭消耗/飞行/抵达、保存恢复后继续运行，再统一形成同源双包交审。

理想满速补产的关键路径约27分钟，研究并行；施工、移动、预热、射界等待和恢复另计。目前守恒剩余游戏时间约36.9分钟，尚不能证明足够覆盖本方案。必须在新开实机窗口前，以已核实设备/吞吐和完整建设料单判断是否需要一次集中申请实际材料/时间增量，不执行到一半再追认。

回归采用影响范围内的增量验证：开关/施工、化工与科研、发射归属、保存续建各验自己的变更与实际场景。最终准确源码保留一次完整回归，可直接复用同SHA的CI结果，不在本地重复；打包后仅做必要的包面、同源载荷及运行验收。当前已通过的5522项回归继续复用。

2026-11-02所有者新增：将真实发射第一枚火箭也纳入0.5。在首帆后完成普通研究、最小材料制造、垂直发射井供电供料及原生发射，核对真实火箭飞行与抵达、准确物料消耗，并正常保存恢复。该目标所必需的最小有效戴森结构接收目标纳入本次范围；完整结构规划、批量建设和发射网络仍留在后续版本。沿用现有授权、累计硬预算、唯一writer及正式发布边界，不逐动作重复请批。

Latest owner direction (2026-11-02): include the first normally manufactured and actually launched carrier rocket in0.5. This includes the minimum valid native structural receiving target required for real arrival, ordinary technology/materials/silo/power/supply and save/recovery evidence. Full structural planning, mass construction and launch networks remain later work. Existing cumulative hard budgets and formal publication gates remain unchanged.

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

新增滚动阶段：先关闭首帆及恢复证明，再进入R1火箭科技/材料闭环、R2最小原生结构目标和发射井供电供料、R3真实发射/抵达及保存恢复，最后统一交审双包。当前共同底座先补无人机正常开关与施工前置检查，复用已制造物品及准确待建实体，不重复创建。

火箭前提已有配方观察（待恢复后刷新）：量子芯片、垂直发射井及小型运载火箭尚未解锁；因此必须先核对正常研究依赖、矩阵库存/生产和研究时间。小型运载火箭实际物品为1503；一枚需戴森球组件2、氘核燃料棒4、量子芯片2。一个发射井需钛合金80、框架材料30、引力透镜20、量子芯片10。材料库存、真实供能、结构目标和原生发射生命周期仍待验证；不以此清单冒充已付料、已获任意增量或已能发射。

## Autonomy and budgets / 自主执行与预算

Proceed with the necessary bounded source/caller investigation, fixes, tests, normal commits/pushes, qualification and evidence maintenance. Routine same-owned-world save, close/launch and no-loss recovery retain the standing technical safeguards. Batch related proven changes and reuse qualified inputs. Native refusal is an implementation/caller/site diagnosis, not a request to waive it. Reconcile every original accepted/unknown action; never rekey or replay it.

按目标连续进行有限源码/调用端调查、修复、测试、正常提交推送、资格检查及证据维护；同owned世界的常规保存、退出启动及无损恢复保留原持续授权的技术约束。集中修复已证实的相关问题，复用合格输入。原生拒绝应先区分产品、调用或现场问题，不请求绕过。逐项核销原accepted/unknown，不换键重放。

This target adds no arbitrary resource allowance. First inspect existing stock and facilities, derive the minimum exact bill, and preserve every previous debit and return/energy/save reserve. If an actual required material/time increase falls outside the latest approved limits, finish the reviewable preflight and consolidate the exact increment into one owner decision. Each live window remains finite and at most one hour after readiness. Progress loss/rollback, another world, new access/paid permissions, Computer Use and formal tags/Releases/uploads retain their separate owner gates.

目标不自带无限资源额度。先查已有库存和设施，推导最小准确清单，保留全部历史支出及返航/能源/保存储备；若实际必需的材料或时间增量超出最新批准硬上限，先完成可审阅预检，再将准确增量集中一次交所有者决定。每个实机窗口仍在就绪后起算、有限且最多一小时。进度损失/回退、另一世界、新访问/付费权限、Computer Use及正式tag/Release/上传保留原独立审批。

## Initial evidence and limits / 初始证据与边界

The accepted source/install baseline remains `30bd61198a6a3b2ff4e41eaf172c5d97fb66a19d`, DSP `0.10.35.29151`, Native assembly SHA-256 `EF314425DADE51F529F184F07BE136CD3C2660A6A81515603C7226FBE7AB1D8C`. Existing recorded recipes show solar sails and the electromagnetic rail ejector unlocked. Current inventory, power, site and orbit still require fresh runtime evidence. One ordinary recipe execution consumes one graphene and one photon combiner and yields two sails. A new ejector recipe consumes twenty steel, twenty gears, five processors and ten super-magnetic rings, before external supply/power connections; this is a bill, not an approved additional debit or proof of stock.

原验收/实装基线仍为上述准确源码和DSP29151/EF3144原生装配。已有配方记录显示太阳帆和电磁轨道弹射器已解锁；当前库存、电力、场地及轨道仍待新鲜现场证据。一轮普通配方用石墨烯1、光子合并器1产太阳帆2；新弹射器配方用钢20、齿轮20、处理器5、超级磁场环10，另计外部供料/供电连接。这只是清单，不是新增扣料授权或库存证明。

Long-route generalization, multi-outpost scheduling and general Dyson node/frame/shell design remain later work. The owner has now included the first carrier rocket and its minimum receiving structure in0.5. Existing twelve-belt restrictions remain disclosed until separately changed and validated; they are not silently relaxed for this goal.

长线路通用化、多矿点调度及通用戴森节点/框架/壳层设计仍属后续工作；首枚火箭及其最小接收结构已由所有者纳入0.5。现有十二节限制在另行修改验证前继续披露，不因新目标静默放宽。
