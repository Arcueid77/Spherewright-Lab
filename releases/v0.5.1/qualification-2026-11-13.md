# Spherewright 0.5.1 qualification / 0.5.1 发行资格

The owner requested the Issue #5 wind change on the 0.5 maintenance line as 0.5.1. The release source is `c632f2d6b01f8a037aa556225e6c038e909956c7`, based on the published 0.5.0 line. The shared fix also reached the 0.6 development line. [Issue #5](https://github.com/Arcueid77/Spherewright/issues/5)

所有者要求将 Issue #5 风机修改同步到 0.5，发行 0.5.1。准确来源为 `c632f2d6b01f8a037aa556225e6c038e909956c7`，基于已发布的 0.5.0；相同修正也进入 0.6 开发线。

The locked Native build and 6,379 source tests passed on DSP 0.10.35.29151 with BepInEx 5.4.17. The [exact-source CI](https://github.com/Arcueid77/Spherewright/actions/runs/43391889129) passed. The read-only impact preview, one ordinary wind dismantle, exact item recovery and independent normal rebuild passed on the current owned save. Native readback confirmed preserved structures, inventory inc, factory links and unrelated networks. A normal save and cold continuation preserved the rebuilt turbine and powered network.

锁定原生构建和 6,379 项源码测试通过，原生版本为 DSP 0.10.35.29151、BepInEx 5.4.17。[准确来源 CI](https://github.com/Arcueid77/Spherewright/actions/runs/43391889129) 通过。当前存档中只读影响预览、单座普通拆除、准确回收及独立正常重建通过；原生回读确认建筑、库存增产点、工厂连接和其他电网保全。正常保存冷恢复后，重建风机及供电电网保持。

| Layout / 包 | Bytes / 字节 | SHA-256 |
| --- | ---: | --- |
| `Spherewright-0.5.1-win-x64.zip` | 37,608,256 | `7ECD1B60DFB65FB50C911E12B29545497C52FE530333A1891FDB374D13DFBF9D` |
| `Spherewright-0.5.1-thunderstore.zip` | 33,324,374 | `F7918EF2E2277951D945E634A4A7EEB956173C52537BE53CB97BB8B0516DA489` |

Both archives passed their layout and bilingual-guide checks. Their actual directory and standalone MCP entry points each exposed 74 tools and one resource, with matching embedded guide. All 229 installed program files matched the corresponding final archive payloads; the two archive layouts were not each separately cold-installed into the game. Product-managed debug paths were absent. The package manifest records the exact source and payload hashes.

双包通过结构及双语指南检查，实际目录版和单文件 MCP 入口各提供 74 个工具及 1 个资源，内嵌指南一致。已装程序的 229 项文件与最终包对应载荷逐项一致；没有分别将两种发行布局再次冷安装进游戏。产品托管程序集无调试路径记录。包清单记录准确来源和载荷哈希。

The original successful dismantle remained queryable after the entity ID was reused in the same Plugin process. A read after restarting returned `ACTION_NOT_FOUND`, consistent with the documented process-scoped action-result interface. The original receipt and the cold query are retained; missing old process evidence does not authorize replay. This document records qualification only; GitHub and Thunderstore publication are recorded separately after observation.

实体编号复用后，原进程内仍可查询拆除成功回执；重启后只读查询返回 `ACTION_NOT_FOUND`，符合动作结果接口的进程作用域。原回执和冷查询均保留，旧进程结果不可用不授权重放。本文仅记录资格，GitHub 与 Thunderstore 的实际发布结果另行记录。
