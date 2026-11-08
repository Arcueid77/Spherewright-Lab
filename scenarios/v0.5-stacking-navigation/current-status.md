# Stacking/navigation current snapshot / 叠放与步行活动快照

2026-11-08。所有者要求全部原生可叠放建筑、模型、样式和宿主组合，并在当前owned存档验证。[验证计划](validation-plan.md)和[现行任务授权](../../operations/standing-authority.md#current-stackingnavigation-task-2026-11-08--当前叠放与步行任务)记录范围。本轮源码、同源安装、目录、步行与拒绝检查已完成，游戏已正常保存退出。下一施工步骤待[集中用料决定](validation-plan.md#next-material-decision--下一集中用料决定)。

- 产品main、选定依赖与实装均为`a2916c5a11acff98c4e1ba38d8b44b55e1428467`。五项特性/修复为线性提交，新增merge提交0。[准确产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/42478897263)的6258项回归成功，Native/solution构建、1667项相关同源资格、63项调用端回归、双语/内嵌指南通过。
- 同源开发程序已通过官方原子安装，5Plugin/224MCP文件、模块身份、74工具/1资源、真实SDK36请求通过。冷恢复实机模块身份与该源码一致。SourceLock为development，当前Game/MCP停止。
- 最新Primary=LastExit124338142，2140项完整保护文件，累计3248880/3888000tick，已计账调用55428。54000返航、3000清理及能源/翘曲器下限通过。关闭后再次核验完整保护集、安装字节和模块身份通过。旧首帆/火箭结果与未知原件保全，详见[既有交审](../../releases/v0.5.0/expansion-review-delivery-2026-11-06.md)。
- 实机目录完整，`stackingCatalogComplete=true`且缺项0。覆盖6类建筑的10个可叠放模型行及配送器选择器、基站宿主行。实际仓储上限3层、研究站5层、全局建造高度19.4m。集装机和喷涂机沿用原生高度/可达范围。喷涂机实读BuildMode5，分派修复和7项回归已进入a291。喷涂机、自演化研究站及基站尚未解锁。
- 最终源码冷启动到首笔正常Move为75.172秒。冷恢复前后完整背包count/inc一致，角色姿态差0.0001101m。此前33db首笔8m Move为93.062秒，98cc首笔5m Move为90.016秒。
- 空路预览返回完整tokenless路线，普通Move实际到达停稳。最终源码又给出规划长17.2623m的两段绕树路线，首段实际到达后从真实停稳位置重新预览，再以新鲜普通Move完成第二段。两轮地表和净距观察完整。占用终点及过近绕树终点保留`search_exhausted`，后者目标净距1.43m低于拐点后保留的1.65m。
- 真实卡住案例保留原`action_failed`回执，剩余距离2.6962m、径向误差0.0925m、容差1.5m。诊断为`possible_physical_obstruction`，完整几何的唯一候选为电磁轨道弹射器64，来源`current_scene_proximity`，身体净距约-0.00010m。健康物理停稳已证实。
- 最终源码完成7项真实拒绝检查，分别为缺少自有建筑、错误仓库等级、逆向宿主组合、非法模型、错误整链哈希、混用地面/叠放参数及未解锁喷涂机。每项返回预期错误码，缺料原生原因确认为`NotEnoughItem`。前后完整背包count/inc、整链哈希一致，待建列表均为空，提交动作0。
- 本轮新增施工额度0，完整叠放建造、逐层功能、全部兼容边/宿主边及其保存恢复仍待用料决定。已解锁案为8模型/17有向边、38座测试建筑，完整案为10模型/22有向边、44座，均另需至多100条基础带、24分拣器和4电力感应塔。完整案还需320蓝矩阵及800黑雾矩阵科研，2座自演化研究站另耗2普通研究站、40黑雾矩阵、20硅基神经元和8量子芯片。武器系统前置科研正常奖励10箱机枪弹药。当前已读本地库存无黑雾材料。

English summary. Product main, the selected dependency and the installed development runtime are all `a291`. Its exact 6258-case CI, Native build, 1667 qualified related cases and 63 driver regressions passed. Installation, runtime module identity and 36 actual SDK requests passed. Cold recovery reached real work in 75.172 seconds and preserved whole-package count/inc with 0.0001101m pose drift. The Native catalog is complete across 6 families and 10 stackable model rows.

A free corridor and a planned 17.2623m tree detour were traversed through fresh ordinary Moves and an intervening fresh preview. A real blocked Move identified ejector64 through current-scene physical contact. Seven construction-refusal cases returned their expected codes with unchanged package/stack and zero new prebuilds or accepted actions. The protected close is tick124338142, with 2140 files, 3248880 cumulative spent ticks and 55428 accounted calls. All protected files, installed bytes and module stamps were reverified after normal close.

Positive stacking, function, host and recovery cases await the concrete material decision. The unlocked option allows 38 test buildings across 8 models and 17 directed pairs. The full option allows 44 across 10 models and 22 pairs. Both reserve 100 belts, 24 sorters and 4 Tesla towers. The full option additionally requires the listed technology and Dark Fog inputs and has a normal 10-ammo-box technology reward. Source and installed support remain separately tracked from pending live stacking acceptance.
