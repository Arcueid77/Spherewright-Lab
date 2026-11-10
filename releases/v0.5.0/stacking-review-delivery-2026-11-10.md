# 0.5 stacking completion review / 0.5 叠放补齐交审

2026-11-10。所有者要求的合堆实测、大小仓/叠放仓筛选和两种新安装包已完成，最终游戏正常保存退出。当前源码为`19cd5eb505ffd30f4832f3bfbf0ced9ddad4a889`，产品main线性推进，新增merge提交0。[复核清单](manifests/stacking-review-evidence-2026-11-10.json)与[场景快照](../../scenarios/v0.5-stacking-navigation/current-status.md)分别保留本轮结果和续接边界。

## 实测与恢复

- 9模型、19有向组合，47个成员覆盖2个既有根、44座主要测试建筑和1个新配送器。双向层连接、准确模型、姿态、逐层库存/配置/设备状态均已核对。
- 筛选支持普通大小仓任意准确层及配送器父层选择。实际完成叠放小仓顶层、叠放大仓中层、独立大仓、分流器托小仓的筛选/清除/禁格操作，其他层和完整背包数量/增产点保全。过滤及禁格跨手动包冷恢复保持，随后经正常配置恢复原值。
- 原生反向操作复用15条既有基础带，集装机正常进入Pile模式。22件单件石材供料中，实际观察到2件石材成为1个货物堆。全部正常收回，背包石材100→100、inc0，输入/输出带和集装机缓存均空。新增施工0。
- 两种包各自完成实际安装、真实模块及MCP入口核验、同一owned存档冷恢复和必要普通移动。手动布局使用包内目录MCP，启动至首实操278.266秒。Thunderstore布局使用包内Plugin及单文件MCP，276.938秒。均在原300秒门内，47成员与完整背包差异0。
- 源码6347项测试、Native构建、[准确产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/42759702754)、调用端158项回归、真实SDK40请求、74工具/1资源、双语内嵌指南与包面检查通过。

## 本地交审包

文件位于保护本地`artifacts/v0.5.0-stacking-review/`。

| 布局 | 文件 | 字节 | SHA-256 |
| --- | --- | --- | --- |
| 手动 | Spherewright-0.5.0-win-x64.zip | 37584351 | 1032AA3BC38E6B55415161B3FFBF88EE4FECA1B893B476C0D34D4AD9DFFF7BC3 |
| Thunderstore | Spherewright-0.5.0-thunderstore.zip | 33305190 | A255103BA53DE5613DE303C4A7D46F1E1A5F47083B8F5909FFA75555F07B6031 |

手动包的四份Plugin程序集与Thunderstore包对应程序集字节一致。两包分别通过官方结构/校验值/双语指南检查，并补充各自实际冷恢复证据。原静态检查器输出的`runtimeBlackBoxTested=false`保留原件，实机结论由本轮独立证据给出。SourceLock为provisional。

## 最终边界与保留事项

最终Primary=LastExit125438198，2208项完整保护文件核验，Game/MCP正常退出并记录EOF。累计4348936/6000000tick，54000返航及3000清理储备保留，累计已计账65981请求。用量维持44座主要测试建筑、另1配送器、96基础带、6分拣器、5电塔。

较早5铜的最终去向仍未逐件核清。历史中断读档、已付5带但完成回执unknown、启动验收失败、原生弯道准备拒绝及移动货物清理的preacceptance拒绝均保留原件。手动布局切换前，经准确旧同源清单验证的受管单文件主机已保留至保护本地，再调用包内原安装器。旧成对安装档案及存档保护记录保留。

本轮交付为本地交审包，正式tag、Release及平台上传状态为未执行。[首帆/首火箭交审](expansion-review-delivery-2026-11-06.md)保留原来源。

## English

All requested remaining aggregation, warehouse-layer filtering and both review packages are complete on source19cd5eb5.6347 source tests, Native build, successful exact CI,158 caller regressions,40 real SDK requests and bilingual package surfaces passed. Real piler reversal reused15 existing belts with zero construction.22 singleton stone inputs produced an observed two-item single stack and all stock returned100→100 with inc0. Small/large warehouse layers, distributor selection and hosted storage configuration preserved peer stock and settings.

The manual archive's directory MCP and the Thunderstore archive's Plugin/standalone MCP each received actual installation and same-owned-save cold continuation.47 members and the complete package matched. Startup-to-work was278.266 and276.938 seconds. Persisted filters/bans survived recovery and were then normally cleared. Both source-bound archives and checksums are listed above. Final close is125438198 with2208 verified protected files,4348936 cumulative ticks against6000000,54000 return/3000 cleanup and65981 requests. Historical unknowns, failures and five untraced old copper remain recorded. The verified prior standalone host was locally preserved for the manual-layout switch. These are local review candidates with provisional provenance. Formal publication remains unperformed.
