# CommandDeck blue-matrix acceptance / CommandDeck 蓝矩阵验收

## 中文

2026-11-15 在独立的和平、非沙盒测试世界中，按所有者授权载入并继续原有存档。该测试不改变另一项 Ascension 世界或其活动交接。运行时使用 CommandDeck `2bd7d34e8d7954ad1ba9ea3939093383f9f44820` 和同源 Spherewright Plugin/MCP `fbe39898c0724f7c4121e41676178f42f2d93d6e`；这是本次实机来源，不代替本仓当前源码锁或其他场景的验收。

生产链通过正常采矿、冶炼、线圈和电路板生产，向四座蓝矩阵研究站供料并自动入库。原有模型任务已停止，完成施工与验收由有界操作及独立只读采样完成；不把旧任务界面的暂停状态或零进度当作本次采样结果。

最后一次施工后，原生工厂统计的 21 个重叠、各 10 游戏秒采样窗口连续覆盖 61.5 游戏秒；每次采样速率为 66–84 个/分钟，所检查的电力采样均满供。两个成品仓在采样读数之间增加 64 个，按这段入库读数间隔计算约 74.6 个/分钟。铁块缓冲仓在覆盖至少 60 游戏秒的前后读数均为满仓，新增矿机与熔炉的原料和工作状态得到读取；该检查用于辅助判断补料，并非无限期产能保证。

验收窗口结束后已执行一次普通保存，回读确认保存覆盖该窗口。未在本次验收后进行冷启动及读档复验；原始动作、采样和保存回执保留在受保护的本地证据中，不提交存档、私有路径或运行描述符。

桌面源码的 [Windows 回归](https://github.com/Arcueid77/Spherewright-CommandDeck/actions/runs/43679417820)和[回执检查](https://github.com/Arcueid77/Spherewright-CommandDeck/actions/runs/43679417822)通过；该 Spherewright 运行来源的 [Windows Core CI](https://github.com/Arcueid77/Spherewright/actions/runs/43669228500)通过。各项结果分别绑定上述准确提交，不将其扩大为其他提交的实机验证。

## English

On 2026-11-15, the owner's authorized existing save was loaded and continued in a separate peaceful, non-sandbox test world. This test does not alter the separate Ascension world or its active handoff. The runtime used CommandDeck `2bd7d34e8d7954ad1ba9ea3939093383f9f44820` and the same-source Spherewright Plugin/MCP `fbe39898c0724f7c4121e41676178f42f2d93d6e`. These are the tested runtime sources, not a replacement for this repository's current source lock or another scenario's acceptance.

The line normally mines and smelts ore, manufactures coils and circuit boards, feeds four matrix labs and stores their output. The previous model task was stopped; bounded operations and an independent read-only monitor completed construction and acceptance. The old task's paused state and zero progress are not the result of this observation.

After the final construction, 21 overlapping native factory-statistics windows of 10 game seconds each continuously covered 61.5 game seconds. Every sampled rate was 66–84 matrices per minute and all sampled power readings showed full service. The two output stores increased by 64 matrices between storage readings, equivalent to about 74.6 per minute over that reading interval. The iron buffer was full at two readings at least 60 game seconds apart, and the added miner and smelter's inputs and operating state were inspected. This supports the replenishment assessment, not an indefinite capacity guarantee.

One normal save was completed after the acceptance window and its readback covered the window. A cold restart and reload after this acceptance were not tested. Original action, sampling and save receipts remain in protected local evidence; saves, private paths and runtime descriptors are not committed.

The desktop source passed its [Windows regression](https://github.com/Arcueid77/Spherewright-CommandDeck/actions/runs/43679417820) and [receipt audit](https://github.com/Arcueid77/Spherewright-CommandDeck/actions/runs/43679417822); the tested Spherewright runtime source passed [Windows Core CI](https://github.com/Arcueid77/Spherewright/actions/runs/43669228500). Each result applies to the exact source above and does not claim live validation of another commit.
