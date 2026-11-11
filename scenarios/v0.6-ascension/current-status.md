# Ascension current snapshot / Ascension活动快照

2026-11-12。游戏已正常保存退出，Primary及LastExit126412724，2254项完整保护通过。累计5323462/6000000tick、72193请求，剩余676538tick，返航54000及清理3000储备保留。

## 源码与实装

所选及实装 `21be561cc0b06c2452ce740983c558aea0d93afc` 已通过6546项准确回归、完整29151 Native构建、准确CI、同源安装、实装SDK46请求及当前存档实测。手搓完成复用主线原任务实现并支持合法队尾合并。调用端184项通过，覆盖原子计划发布、dump引用、资源建筑及正常拆除入口。 [准确产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/43054994764)

本轮71.594秒完成首笔正常石墨取用。原任务连续制造2蓝，原生读回version1、准确配方9/初始及请求次数2、剩余0、队列释放、交付缓冲0，终态成功。`inventoryProductsObserved=false`，前后背包蓝均0，科研缓存准确增加7200点。旧版1蓝失败及3600点守恒原件保持。

## 当前玩法证据

- 1504已正常解锁。1705保存前322200/576000哈希，1523仍待完成。研究根84增加6876/6877，两层均继承1705研究模式，形成3层，累计研究站施工15。新增2站使用24铁、8铜、8磁铁及16石矿。
- 蓝根76保持5层，输入573/312已原生升级2012。2蓝与2高速分拣器使用5铁、4磁铁及3铜，复用2普通分拣器并正常退还升级旧件。
- 供铁源6706已由错误板筛选1301改为铁1101，仓6657接收600铁，其中24用于研究站、18用于18条基础带。曾观察奇异物质和透镜各6/min。保存前碰撞器重氢8、单次需10，后续供料仍需核对。镜片输出仍流向原翘曲器产线。
- 当前星球仍有84铁节点。携带矿机正常建成6878，覆盖50/55，电网3服务比1，实际矿物缓冲50。旧空矿机1496正常拆除，其ID随后被铜带原生复用，须读取新鲜类型及端点。
- 铜矿2435至熔炉10正常建成11带及分拣器6889，保存前实际铜48/min。累计带施工203、上限214，普通分拣器34、上限48。背包有11带、1分拣器、1矿机及1小仓。
- 新矿6878输出尚待接通。直接绑定6270超出Bridge覆盖范围，独立输入及带间桥候选由原生碰撞检查拒绝，均未接受。原6270–6273空路、6274、1507/1508/1509及熔炉1500保留，1500出料1512已改铁1101。优先以新鲜实际几何完成短连接。
- 背包保留802黄、200紫和原燃料/翘曲器。机甲蓝7200点、黄2872800点，红0。仓6657有359铁。全部当前存档进度已正常保存。

## 接下来执行

1. 从2254项完整保护及126412724无损恢复，先从当前角色范围内6657正常取1铁，沿原300秒启动门执行，继承最新私有保存输入中的实耗及施工数。
2. 接通6878至铁输入/熔炉，使用实际端口及原生几何，保留原拒绝。推进铜、矩阵、重氢/奇异物质/镜片、1705/1523及缺失量子链。 [当前用料](resource-increment.md)
3. 完成Caph II合法闭合设计、持续制造/发射/交付、接收器持续非零实际电力及保存冷恢复。功能闭合后生成最终同源双包，正式发布沿独立授权。 [实施与验收](implementation-plan.md)

## English

Normal save/close preserved primary/LastExit126412724 with2254 verified files,5323462/6000000 ticks and72193 requests.676538 remain with54000 return/3000 cleanup reserves. Selected/installed21be561c passed6546 exact cases, Native29151 build, exact CI, coherent installation,46 installed-SDK requests and live acceptance.184 caller cases passed.

First real graphite withdrawal took71.594 seconds. The original two-blue task completed with version1 exact task/recipe9/requested and initial count2, remaining0, queue release and delivery buffer0. Inventory observation was false, both package blue counts0 and research increase exactly7200. Preserve the earlier failed one-blue original and3600-point proof.

1504 unlocked.1705 reached322200/576000 and1523 remains pending. Research root84 gained6876/6877, all three layers researching1705, with15 cumulative placements. Two laboratories consumed24 iron, eight copper/eight magnets and16 stone ore. Five-layer blue root76 now has normally upgraded2012 inputs573/312. Two blue/two fast sorters used five iron, four magnets and three copper, reusing two ordinary sorters and recovering old upgrade items.

Input6706 changed from the wrong board1301 filter to iron1101. Storage6657 received600 iron, with24 reallocated to laboratories and18 to18 belts. A real window observed6/min each strange matter/lenses. Final collider deuterium was8 against10 per cycle, requiring further supply work. Lenses still feed the original warper line.

There are84 local iron nodes. Normal miner6878 covers50/55, has full network3 service and50 ore. Empty old1496 was normally recovered and its ID later reused by a copper belt. Fresh type/endpoint checks remain essential. New copper2435-to-smelter10 supply placed11 belts/sorter6889, producing48/min. Cumulative belt placement203 under214 and sorter34 under48. The player retains11 belts, one sorter, one miner and one warehouse.

Miner6878 still needs its output. Direct6270 coverage was outside the Bridge subset. Independent input and belt-sorter bridge candidates failed Native collision checks before acceptance. Preserve6270–6273,6274,1507/1508/1509 and smelter1500, whose output1512 now filters iron1101. Resolve the short connection from fresh actual geometry. The package retains802 yellow,200 purple and original fuel/warpers. Mecha buffers hold7200 blue points/2872800 yellow with zero red. Storage6657 holds359 iron.

Resume the latest full boundary with one normal nearby6657 iron withdrawal within300 seconds, inheriting fresh private spending and placement inputs. Continue iron/copper and matrix supply, deuterium/strange matter/lenses,1705/1523 and the missing quantum chain. Complete Caph II closed design, sustained manufacture/launch/delivery, actual receiver electricity and save/cold continuation. Final coherent packages follow functional closure, with independent formal-publication authority.

Earlier cuts remain in fixed history. [前次快照 / Previous cut](https://github.com/Arcueid77/Spherewright-Lab/blob/0a19a188ad70cc808daf1b2f375bf601a72f63e4/scenarios/v0.6-ascension/current-status.md) · [持续授权 / Standing authority](../../operations/standing-authority.md)
