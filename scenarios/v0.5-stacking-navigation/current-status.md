# Stacking/navigation current snapshot / 叠放与步行活动快照

2026-11-10。合堆实测、普通大小仓/叠放仓筛选、两种新安装包及各自实装冷恢复已完成，游戏正常保存退出。[交审记录](../../releases/v0.5.0/stacking-review-delivery-2026-11-10.md)、[逐项矩阵](native-matrix-2026-11-10.json)及[复核清单](../../releases/v0.5.0/manifests/stacking-review-evidence-2026-11-10.json)分别记录结果、范围和包来源。

- 产品main、固定依赖及已装程序为`19cd5eb505ffd30f4832f3bfbf0ced9ddad4a889`。源码6347项、Native构建、[准确产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/42759702754)、调用端158项、SDK40请求、74工具/1资源与双语包面通过。新增merge提交0，SourceLock为provisional。
- 9模型、19有向组合建造与47成员冷恢复通过。主要测试建筑44/44，另1座已批配送器，基础带96/100、分拣器6/24、电塔5/5。自演化研究站由所有者移除，原垂直高度拒绝及受高架带阻挡底座计入原预算。
- 配送器正常付料安装，选中挂件后正常增加小仓，同一配送器提升至新顶层。身份、父层、姿态、连接、配置、库存及空配送机状态跨恢复保持。
- 筛选现支持普通大小仓任意准确层与配送器父层选择，实测覆盖叠放小仓顶层、大仓中层、独立大仓和分流器托小仓。筛选、清除和禁格保全其他层及完整背包，设置跨手动包冷恢复保持，随后经原生正常操作恢复原值。
- 原生反向复用15条既有带，使集装机进入Pile模式。22件单件石材实际产生2件/1货物堆，正常收回后石材100→100、inc0，输入/输出带及集装机缓存空。新增施工0。此前4铁分料流转、4铁喷涂获得4点、剩余8喷涂和液罐2/0/0氢均保全。普通研究站4蓝矩阵、1板缓冲及背包1线圈账目保持，自动科研供料关闭、点缓冲空。
- 两种交审ZIP已生成。手动包经包内原安装器实装，使用目录MCP，首实操278.266秒。Thunderstore包Plugin及单文件MCP实装，276.938秒。分别核对47成员、完整背包和设备缓冲，差异0，均满足原300秒启动门。
- 最终Primary=LastExit125438198，2208项保护文件核验，Game/MCP均正常退出并记录EOF。累计4348936/6000000tick，54000返航及3000清理储备保留，累计65981请求。保护末轮为`.local/sn-ts19/`。当前无需再开游戏重复已完成案例。
- 旧5铜仍未逐件追清。历史中断读档、已付5带但完成回执unknown及所有失败/拒绝均保留原件。自由高架挂件接触已提交前拒绝，原5带实体/连接/成本保全。首次弯道反向准备被拒后修正原生输入边分类。合堆清理遇移动货物STALE拒绝后，在真实尾部停稳时正常收回。
- 手动布局切换前，准确原同源清单证明的旧单文件主机已保留至保护本地，再调用包内原安装器。正式tag、Release及平台上传状态为未执行，下一步为所有者审核交审包。原[首帆/首火箭交审](../../releases/v0.5.0/expansion-review-delivery-2026-11-06.md)保留原来源。

English. The remaining piler aggregation, small/large warehouse-layer filtering and both review packages passed on19cd5eb5.6347 source cases, Native build, successful exact CI,158 caller regressions and40 SDK requests passed. Real reversal reused15 belts,22 singleton stone inputs yielded a two-item single stack and all100 stone returned with inc0. Peer-layer stock/configuration and saved filters/bans were preserved. The manual directory MCP and Thunderstore Plugin/standalone MCP each passed real installation and cold continuation with47 members and the complete package unchanged, reaching work within278.266/276.938 seconds. Final normal close is125438198 with2208 protected files,4348936/6000000 ticks,54000 return/3000 cleanup and65981 requests. SourceLock is provisional. Original unknowns, failures and five untraced old copper remain recorded. Next is owner review of the local candidates.
