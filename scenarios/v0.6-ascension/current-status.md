# Ascension current snapshot / Ascension活动快照

2026-11-12。游戏已正常保存退出，Primary及LastExit均为126289034，2250项完整保护通过。累计5199772/6000000游戏tick、71219请求，返航54000及清理3000储备保留。当前剩余800228tick，从最新完整边界继续。

## 源码与实装

所选及实装源码为 `21be561cc0b06c2452ce740983c558aea0d93afc`。复用主线原生手搓完成修复，并修正同配方队尾合并时初始次数的合法范围。6546项准确源码回归、完整29151 Native构建、准确CI及同源开发组合资格通过，官方冷安装完成一笔事务，实装SDK46请求通过，程序当前关闭。调用端182项通过。 [准确产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/43054994764)

`handcraftReadback`核对保留的原生任务、初始/剩余执行次数、队列移除和交付缓冲。背包净变化及自动科研另行观察。原1蓝手搓失败及3600点守恒原件保留，新实现的当前存档正向实测待完成。当前采用主线实现及21be561c合并兼容修正。

## 当前玩法证据

- 本轮71.797秒完成首个正常红矩阵取用，随后补齐余下92红。射线接收1504已正常解锁，108000/108000哈希。引力矩阵1705已入队，保存前69779/576000哈希。应力1523尚未解锁。
- 正常将1000铜中的984供入原箱26，16用于新增研究站依赖制造；将1784磁铁移入562。原板机36输入979的错误齿轮筛选已正常改为铜1104，线圈机73复用原铜输入722。原蓝矩阵根76已正常叠放4层，6872–6875形成5层，累计研究站施工13。
- 新增4站的完整原料为48铁、16铜、16磁铁及32石矿，沿原生依赖制造。新制1小仓使用4铁及4石材。其有界位置候选被原生拒绝，物品仍在背包。仓施工既耗9、有限上限10，分拣器施工既耗33、上限48，背包另有2普通分拣器。
- 本轮追加1600石墨供入已有114，保存前1598。箱26有305蓝、366铜、1210黄，红成品260为空，781有88氢，背包保留200紫及原燃料/翘曲器。
- 非原子计划信封在写完前被读取，原调用端以JSON解析失败正常关闭，所有原写入均已终态核销。已补充完整落盘后原子发布、旧流式JSON有限5秒等待及dump实体引用解析。接续保持原启动时钟、世界进度和累计账目。原水面导航unknown继续按原身份隔离。

## 接下来执行

1. 复用已实装21be561c及2250项完整保护，准备第一笔从114正常取1石墨，沿原300秒启动门无损恢复126289034。
2. 正常取原料，验证2蓝手搓在首件提前进入自动科研时的原生完成读回、背包净变化及7200科研点数。继续核对板/线圈/蓝矩阵与研究供料，优先修复现有端点。闭合Caph II原生制造、合法壳面交付、持续发电及保存冷恢复验收。 [实施与验收](implementation-plan.md)
3. 继续1705及1523科研。科研上限为蓝4200、红4200、黄3600、紫2000、绿2000。合理有限材料/施工增量按所有者自主授权核算和记账，保留累计tick及返航储备。 [当前用料与授权](resource-increment.md)
4. 功能验收闭合后生成最终同源双包及交审证据，正式发布沿独立授权。

## English

Normal save/close preserved primary and LastExit126289034 with2250 verified files,5199772/6000000 spent ticks and71219 requests.800228 ticks remain, retaining54000 return and3000 cleanup reserves. Selected and installed source21be561c reuses the upstream Native forge-task completion fix and admits legitimate same-recipe queue merging.6546 exact-source cases, full29151 Native build, exact CI, coherent development qualification, one official installation transaction and46 installed-SDK requests passed.182 caller cases passed. The game is stopped.

Handcraft completion now binds the original task, initial/remaining execution counts, queue removal and delivery buffer. Inventory deltas and automatic research remain separate observations. Retain the original failed one-blue action and its exact3600-point proof. Positive current-save validation of this installed implementation is pending. The selected implementation follows upstream plus21be561c.

This window reached real red withdrawal in71.797 seconds and supplied the remaining92 red cubes. Receiver1504 unlocked at108000/108000 hashes. Gravity-matrix1705 is queued and last observed at69779/576000. Stress1523 remains pending.984 of1000 normally withdrawn copper entered storage26 and16 supplied new laboratory dependencies.1784 magnets moved to562. Board assembler36's input979 changed from its wrong gear filter to copper1104. Coil assembler73 reuses copper input722. Four new layers6872–6875 expanded blue root76 to five layers, bringing cumulative laboratory placements to13.

Exact new laboratory raw inputs were48 iron,16 copper,16 magnets and32 stone ore through normal dependency recipes. One new warehouse consumed four iron/four stone bricks and remains carried after bounded Native placement refusals. Cumulative warehouse placement is9 under ceiling10 and sorter placement33 under48, with two ordinary sorters still carried. Another1600 graphite entered existing warehouse114, holding1598 before save. Storage26 held305 blue,366 copper and1210 yellow. Red output260 was empty and hydrogen781 held88.200 carried purple cubes and original fuel/warpers were retained.

An incomplete streaming plan envelope caused the original caller to close normally with a JSON parse failure after its original writes had settled. Atomic complete-file publication, a bounded five-second legacy streaming read and dump-reference resolution now have regression coverage. Replacement callers retained the original startup clock, world progress and cumulative accounting. Preserve the historical water-navigation unknown under its original identity.

Resume from this exact complete boundary with a normal one-graphite withdrawal within the original300-second startup gate. Then verify a two-blue task whose first product enters research before task completion, preserving original completion/inventory and7200-point observations. Continue the existing component/matrix/research supply,1705/1523, Caph II manufacture, legal closed-shell delivery, sustained receiver electricity and save/cold continuation. Matrix ceilings remain4200/4200/3600/2000/2000 blue/red/yellow/purple/green under reasonable-resource autonomy. Final coherent packages follow functional closure and formal publication retains its independent authorization.

Earlier cuts remain in fixed history. [前次完整快照 / Previous complete snapshot](https://github.com/Arcueid77/Spherewright-Lab/blob/886bb1cfe24c6721dd174c5a83f413e723b4782e/scenarios/v0.6-ascension/current-status.md) · [持续授权 / Standing authority](../../operations/standing-authority.md)
