# Ascension current snapshot / Ascension活动快照

2026-11-12。原owned游戏进程持续运行，所选、实装及实际加载源码均为14c7d66c。当前唯一oil-source-live调用器已正常取走50红矩阵，全部进入五色科研，1523达到22860/360000。新油井7075、7根出口带、3台风机及电塔已正常建成，独立网4满供电并捕获井内12原油，10件门槛通过。首段12根抬高带已原生完工，出口筛选1007的普通分拣器准确准备通过，连接保留至空载抬高线路完工后。下一19根抬高带由原动作施工中。两次飞行后漂移中的STALE_STATE准备均明确未接受，普通Drift续移到干地后正常建成，原飞行动作保留。

最近普通保存127228150对应累计6138888tick。最近关停完整保护仍绑定Primary/LastExit127035116及2278项文件，该边界累计5945854tick。当前有限累计上限900万，保留54000返航及3000清理，原冷启动起的有限墙钟172800秒，实际截止2026-11-14T03:29:04Z。游戏、原时钟及全部实耗持续保留。

## 实际结果

- 应力科研1523已达到22860/360000，尚余1873份五色矩阵需求。本轮新增50红已正常取入并实际消费50份五色矩阵。当前已观察机甲整件等效点缓存为蓝76、黄1873、紫73、绿95，红0。原生实物、科研点及实际消费分别记账。
- 原五层绿矩阵三批110量子/110透镜正常投料对应220绿，已正常取走全部220个工厂绿。后续完整2000绿科研需求仍待连续生产。
- 6座新MkII、3小仓及2电塔已正常制造并原生完工，原电路板台36正常升级MkII。实际分配为2处理器、2位面过滤器、1卡西米尔及1电路板。新处理器共享仓从空仓捕获5件，后续回读22件。新电路板仓从空仓捕获10件。新增位面共享仓已实际捕获6个过滤器，预声明5件门槛通过。各设备实际主网3完整供电，卡西米尔机尚待新原料正向生产验证。
- 卡西米尔北机的额外高速输入按原生回收后，空出合规输出端点，保留极速输入和正常输出。当前Native非零初始筛选支持2011/2012，极速输入采用0初始筛选及专用/配方需求路径。当前升级策略支持普通→高速及制造台家族，极速升级的明确未接受拒绝保留，已制极速物品通过正常新建使用。
- 新铁矿覆盖8节点，出矿/跨线/入仓链已在满功率主网3验证。首批400及第二批600铁矿已正常送入原仓28。新增高速入料接回274→282→17→20原输送链，原铁熔炉恢复，磁铁入料已接回并升级，原生10秒切面记录铁8件、电路板4件产出。282及24已正常升级高速。594绑定1101，793继续使用1003。旧带1709保持原路径。
- 钛化玻璃仓补200水后，6927/6929原输入已正常升级高速。100卡西米尔及20钛化玻璃已正常投入新位面设备并形成上述6件实存。后续水、石矿、钛块及科研供料继续沿实际库存补充。
- 新油源542已正常建设为7075。3风机/1塔构成独立网4，实际需求/供给14000J/t、容量15000J/t、供电比例1，矿内12原油实存通过10件门槛。7根出口带及首段12根抬高带正常完工，筛选1007的入口分拣器准确准备通过，下一19根抬高带仍由原动作施工。整线输送和新精炼连续产出仍待验证。旧油井附近末段增加绕行点，原生生成的两段18/7点已观察并通过选定旧井保守包围检查，实际全条件逐段施工继续。 [用料记录](resource-increment.md)
- 原氢线10秒Native切面为144/min产出及138/min消耗，原油66/min产出及72/min消耗。该历史短切面保留其时间范围。3座新精炼厂已正常制造，按1基本/2X射线裂解的名义配比规划新增45净氢/游戏分钟及精炼油收支平衡。两座补塔按出口分拣器与后续精炼的实际覆盖使用，累计塔上限23。
- 水面Drift普通续移、后续建矿及自然转Walk已通过。先前要求先Walk的等待过严，已改用普通被动漂移续移。所有受阻移动、未接受准备/提交和已完成前缀均保留原件，accepted/unknown原动作继续单独核销。
- Issue #5已读并核对，当前风机拆除仍需单台原生拆除、电网影响预览、回收及未触及拓扑核验。 [Issue #5](https://github.com/Arcueid77/Spherewright/issues/5)

## 源码、安装与继续边界

产品源码 `14c7d66cda64d40c201577313740be05e6918479`，0.6.0，通过6559产品回归、准确Native构建及对应CI。实装5 Plugin/224 MCP文件清单为 `C1A1D058290A683529DDFD8D9C56A4E49EFD7576AEE536CB37CC68D02D90DCEC`，实际75工具SDK完整生产入口准入通过。原安装事务及超时保全原件保留。 [产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/43098686696)

调用端48小时启动容量修正7a95eb21通过206本地回归及准确CI43183645171，原24小时拒绝发生于进程创建前。本轮低速commit登记前分类和fresh间隔通过208本地回归及准确CI43195714901。 [48小时调用端CI](https://github.com/Arcueid77/Spherewright-Lab/actions/runs/43183645171) · [拒绝分类CI](https://github.com/Arcueid77/Spherewright-Lab/actions/runs/43195714901)

已完成外部只读观察82请求单列保留，下一写方上限199918，全局200000，最终保存边界合并真实计数。新油源支撑后的累计施工额度为矿机2、油井1、精炼厂3、风机3、熔炉6、MkII14、小仓21、电塔23、普通90/高速8/极速8分拣器及550基础带。当前原写方的51请求预留配置原件保留，下次交接应用82请求后的额度，原生几何/成本及实耗继续核验。

1. 保留当前已接受抬高带原动作，逐段完成空载线路。按80米实际建造范围分段移动，末段绕开旧井后下降，通过新鲜原生准备接入筛选明确的旧油路，验证真实原油输送及1基本/2裂解的连续产出。全部正常取料、制造、施工和准备拒绝保持原账目。
2. 补齐氢/原油、钛化玻璃、处理器、粒子宽带及各矩阵的完整连续供料，完成剩余1873份五色科研。当前Voyager要求空机甲科研缓冲及限定工厂科研元数据，先完成1523再做Caph航段。
3. Caph只读统计显示主网2实际发电0、站点电量0，到场先恢复实际供电。重新核对6度闭壳设计210结构点/224细胞点的准确成本及现有库存，完成当地制造、持续发射、真实交付、闭壳及接收器持续非零电力。
4. 正常保存、完整关停保护及冷恢复后复核设计、进度、设备和持续电力，最后生成同源手动/Thunderstore交审双包。 [实施与验收](implementation-plan.md)

## English

The original owned game continues on selected, installed and loaded14c7d66c. The sole oil-source-live caller normally withdrew50 red cubes, all consumed in five-color research, advancing1523 to22860/360000. New extractor7075, seven outlet belts, three winds and one Tesla normally completed. Independent network4 provides full service and the extractor's12 stored crude passed the ten-item gate. The first12 raised belts completed and the exact filtered1007 source-sorter prepare passed. Preserve the empty raised path until complete. The next19 raised belts are constructing through their original accepted action. Two known-unaccepted stale prepares during post-flight Drift remain archived. Ordinary Drift continuation reached dry ground and construction succeeded.

Latest ordinary save127228150 corresponds to6138888 cumulative spent ticks. Complete stopped protection remains primary/LastExit127035116 and2278 files with5945854 spent at that cut. Preserve9000000 cumulative ticks,54000 return/3000 cleanup and172800 finite wall seconds from the original cold launch, ending2026-11-14T03:29:04Z.

Stress1523 reached22860/360000, leaving1873 of each color. Fifty additional red cubes entered normal research and50 five-color sets were consumed. Observed whole-equivalent mecha buffers hold76 blue,1873 yellow,73 purple and95 green, with zero red. The original five-layer green factory's110/110 feed funded220 normally produced greens, all withdrawn. Complete green research production remains pending.

All six additional MkII machines, three stores and two towers normally completed. The original board machine upgraded to MkII. Actual allocation is two processor/two plane-filter/one Casimir/one board machine. The new processor store passed five products from zero, later holding22. The board store passed ten from zero. The plane store passed its five-product gate with six physical filters. All have full main-network3 power. The new Casimir producer still needs its raw-material positive proof.

A normally recovered extra Casimir fast input freed a compliant output. Initial nonzero filters support2011/2012, and gradeIII uses normal zero initialization. GradeIII upgrade requests were explicitly rejected by the current supported-pair policy. Manufactured gradeIII items were used through new construction. Retain all original refusals and settled prefixes.

The eight-vein ore source passed full-power relay/storage flow.400 then600 ore reached the original store28 and274→282→17→20 chain. The original iron supply resumed and the magnet inlet was reconnected/upgraded. A Native ten-second cut recorded8 iron/4 boards.282/24 upgraded normally.594 filters1101 and793 retains1003. Legacy1709 stays in its original path.200 water replenished titanium glass and6927/6929 upgraded to fast.100 Casimir/20 titanium glass funded the six new stored filters.

The earlier bounded Native sample of144 hydrogen/min produced/138 consumed and66 crude/min produced/72 consumed retains its original time scope. New oil source542 is now normally built as7075. Three winds/one Tesla provide14000J/t demand/service against15000J/t capacity, with full service and12 physical crude stored. Seven outlet/12 raised belts completed, the filtered source-sorter prepare passed and the next19 raised belts are constructing. Complete-line flow and new refining remain pending. A dry-side bypass avoids the old oil-extractor envelope. Its18/seven Native-generated points passed a conservative selected-pump screen, with actual construction checks still required. Three new refineries are normally manufactured for one basic/two X-ray allocation. The two supplemental Teslas support source-sorter and refinery coverage within cap23. Ordinary Drift continuation to dry ground and source construction passed. Issue #5 wind dismantling still needs its Native power-impact/recovery implementation.

Product14c7d66c passed6559 tests, exact Native build and CI, with five Plugin/224 MCP files bound by manifest C1A1D058290A683529DDFD8D9C56A4E49EFD7576AEE536CB37CC68D02D90DCEC and actual75-tool SDK admission. The48-hour caller7a95eb21 passed206 tests/exactCI43183645171. The208-test commit classification passed exactCI43195714901. Preserve82 external reader requests, the next199918 writer allowance and200000 global ceiling. The current51-request-reserved writer input remains immutable until its normal handoff. Revised cumulative caps include one oil extractor, three refineries/three winds,23 Tesla towers,90 ordinary/eight fast/eight gradeIII sorters and550 belts.

Continue the accepted original equipment manufacture, normal-save/handoff and fresh Native oil construction, complete normal material supply and1523, then restore actual Caph power before manufacture/launch/delivery. Its main network2 currently reports zero actual generation and the station zero energy. Fresh-check210 structure/224 cell costs, complete the shell/receiver power and normal cold continuation before final coherent review packages. Voyager currently requires empty mecha research buffers and restricted factory-research metadata.

[前次快照 / Previous snapshot](https://github.com/Arcueid77/Spherewright-Lab/blob/0c64813df7ce9f615157399e47a7fbab17ced1bf/scenarios/v0.6-ascension/current-status.md) · [持续授权 / Standing authority](../../operations/standing-authority.md)
