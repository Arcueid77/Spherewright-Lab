# Spherewright 0.5.0 Voyager 交审记录

0.5 原三项验收已闭合。门1（缺失资源往返）与门3（受控失败及精确恢复）保留[原条款](../../scenarios/v0.5-voyager/acceptance.md)及其历史源码适用范围；本轮门2在源码 `30bd61198a6a3b2ff4e41eaf172c5d97fb66a19d`、DSP `0.10.35.29151` 完成。最终双包仅供审核，未创建 tag、Release 或上传。

## 实机结果 / Live evidence

| 阶段 | 实测与证据 |
| --- | --- |
| 矿源、连接、供电 | 1矿机、1被动ILS、1电塔、12传送带及2风机；零启动矿物库存；原矿脉减少、完整带货物、站内库存5→10→16。复用既有母星需求与recipe62消费链。 |
| 保存前持续运输 | 两次完整出发/装货返回/母星停靠，合计200矿物；30.163/min，母星消费产物0→130。 |
| 保存恢复后续运 | 完整129892边界正常恢复；再一轮完整运输100矿物，50.350/min；产物132→192。累计三轮300矿物。 |
| 最终保全 | 完整保存121137254；1624文件备份验证；游戏保留主菜单，无已加载世界。累计47992/216000游戏tick，历史4773舍弃仍计费，本轮新增丢失0。 |

实际原生供电为6998J/tick，名义满负载7000J/tick，约99.9714%服务；不声称100%满功率，也没有补第三台风机或给返航/材料预算加能量。数量、速率与持续消费按实际运行验收。

## 最终双包 / Final review candidates

| 包 | 大小（bytes） | SHA-256 |
| --- | ---: | --- |
| `Spherewright-0.5.0-win-x64.zip` | 37265257 | `77C60BD5024FB8CBDA1CBD902F33DBDF898BE97742E5951146B9AE1CD275559A` |
| `Spherewright-0.5.0-thunderstore.zip` | 32989891 | `BB457CF8D9D97837F27FC3E1006C9BF2699D8E8204BE145F116189E7FD427389` |

两包在功能独立复核通过后生成，复用同一干净已推送源码的合格程序字节。手动包与Thunderstore格式检查、完整中英文指南、74工具/1资源、内嵌指南、233项程序载荷绑定及实际打包MCP到游戏主菜单的只读调用均通过。没有为本次归档重新构建或换装游戏。

[准确产品CI](https://github.com/Arcueid77/Spherewright/actions/runs/40671860835)通过5469项回归；本地Native/solution构建和76项相关环境验证通过。257归档条目/248独立载荷隐私核对无真实泄露、无未知项；原SDK清单尺寸字段碰撞保留精确归类，不冒称原始扫描零命中。

Thunderstore结构检查器自身只做静态验证，因此其原始 `runtimeBlackBoxTested=false` 保留。真实游戏证明来自同字节安装源的完整闭环；最终两个打包MCP另已通过实际主菜单接口只读探测。正式发布及平台上传仍须所有者另行决定。

English: all original Voyager clauses are closed with historical clauses1/3 retaining their original source scope. Clause2 proves three actual mined-ore transport cycles (300 total), real home consumption and continuation after supported recovery. Both same-source archives are review-ready; original raw evidence remains protected, and no formal publication occurred.

详见[公开复核清单](manifests/review-evidence.json)、[唯一活动快照](../../scenarios/v0.5-voyager/current-status.md)与[源锁](../../source-lock.json)。
