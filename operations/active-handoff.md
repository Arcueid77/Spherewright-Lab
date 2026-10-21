# Active handoff / 活动交接

Use the [single Voyager current snapshot](../scenarios/v0.5-voyager/current-status.md) for source, installation, observed Game state, original limits and the next gate. This file is the entry point, not a second current ledger.

当前事实以[唯一Voyager活动快照](../scenarios/v0.5-voyager/current-status.md)为准，本文件只作入口，不再叠加第二份实时状态。

Prepared source/dependency: **0bf2f0f62a93e18975ae90eff6ccdfdaab3c0fd9**; actual installation remains **d0604dea / Native29151**. This local source-only preparation is not yet committed or Lab-CI verified. The last Game cut remains loaded remote / NativePause / quarantine; physical idle is unproved. The original Move is permanently unknown, while the d060 recovery is terminal known failed and its family retired. Root is the only game writer and has stopped new Game calls.

源码采用准备与实装分开；旧Move永久unknown，d060恢复knownfailed且候选族退役，当前无在执行动作。先取得本次准确LabCI，再由Root鲜核实际状态、原预算和942进度覆盖，完成必要正常退出/安装及一次受保护的0bf精确恢复或失败归因。不重放、不降门、不续原caller/UTC/储备，不把隔离暂停当idle。

Only a development preview is qualified. Historical gates1/3 retain historical credit; sustained Gate2, final applicability and required Save/recovery evidence remain open. Final review packages remain null/null. See the unchanged [acceptance clauses](../scenarios/v0.5-voyager/acceptance.md).

The complete prior handoff is retained at [fixed0aed history](https://github.com/Arcueid77/Spherewright-Lab/blob/0aed74a708c756a7ed258a867079f36eac4d5841/operations/active-handoff.md) and in a protected byte-for-byte backup. All original receipts and frozen0.4 records remain intact. Never overwrite the historical operations/current-status.md.

旧交接完整保留于上述已推送0aed固定历史及受保护原字节副本；旧顶部是历史记录，不是另一份当前快照。原始回执、0.4冻结件及验收条款不删不改。
