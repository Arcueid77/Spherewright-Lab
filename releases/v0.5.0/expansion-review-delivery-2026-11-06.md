# 0.5 首帆与首火箭扩展交审 / First-sail and first-rocket extension review

2026-11-06，本轮扩展已形成可审查结果。候选和实装源码为`d3b7ac897bb44d62c8a7ed54c51a55ff2b8de7b0`，DSP`0.10.35.29151`；[准确产品CI42126914241](https://github.com/Arcueid77/Spherewright/actions/runs/42126914241)成功。**未创建0.5 tag、Release或上传。** 原三项Voyager验收及2026-10-29双包保留其[固定基线](review-delivery.md)，本轮候选另立，不覆盖原件。

## 实机结果 / Live results

| 目标 | 实际结果 |
| --- | --- |
| 外星当地首帆 | 当地原料经过正常机器生产；4帆弹药4→0、原生弹道观察、最终云/轨道增加4，正常恢复保持。 |
| 火箭当地制造 | 冰40→石墨烯40/氢20；石18→玻璃9→棱镜6→合并器3→组件用帆6；钛矿24/硅矿12→钛12/硅6；石墨烯36/钛12→纳米管24；加合金6/硅6→框架6；加帆6/处理器6→组件2；加燃料4/量子芯片2→火箭1。 |
| 最小发射条件 | 唯一发射井与唯一最小接收节点；6铁矿/1铜矿正常制造4铁/2磁铁/1铜→2线圈→2塔，实际建成并将井接入电网；总塔8/9，未突破原范围。 |
| 实际发射与抵达 | 隔离来源后弹药1→0，观察到来源星球与目标匹配的真实火箭；节点结构点0→1，订单/在途火箭均归零。 |
| 跨星支援 | 电路板100、燃料100经正常站点/船运到货；运输中的正常保存恢复及后续实际到货已证，未以背包物料代替。 |
| 保存及冷恢复 | 火箭抵达后06ba正常保存/冷恢复保持节点、电网及空弹药；最终d3源码再次冷恢复，72.890秒内完成空炉正常配方操作，节点1结构点与产线保持。 |
| 最终保全 | Primary与LastExit均124257444；2116项完整保护文件逐项备份核验；游戏/MCP正常退出。累计3168182/3888000tick，保留54000返航与3000清理储备。 |

这些是有限批次的生产/发射证据，不外推批量火箭吞吐或完整戴森球。原C未知与11件扣料、原零产矿未知记录仍隔离保留；后续新鲜有界动作另立原回执。未重放旧动作、修改旧终态或回退到较旧Primary。未用物料、旧带尾2石墨烯和氢副产物保全。

## 同源候选 / Same-source candidates

| 文件 | 大小 bytes | SHA-256 |
| --- | ---: | --- |
| `Spherewright-0.5.0-win-x64.zip` | 37481211 | `323BD75C9F5495CAFF3A9A1CC85F2F6F662650CEBF8307742D807BF65FDE5851` |
| `Spherewright-0.5.0-thunderstore.zip` | 33200755 | `E0BDBD2141CCFEBFD1F74F0A453BDF0A964BD92DC591574C4C9E400D616DD577` |

两包来自同一干净已推送源码。严格手动/Thunderstore结构与中英文链接检查、74工具/1资源、英文内嵌/包指南一致性均通过；共233项程序载荷与本次实际安装的合格程序逐字节相同。1536相关回归、31资源回归、Native/solution构建及准确CI通过。初始06ba候选因研究链接失效被拒，保护原件保留；d3只修正两处链接，资源URI不变，**内嵌指南字节随链接更新**。提交标题误写为bytes不变，此处按实际字节核验更正。

原生SDK宿主按准确SDK字节单独归类，托管产品程序集没有CodeView；两个归档的实际私密标识、用户路径、禁止文件和凭据模式检查无命中。此结论不替代完整任意秘密检测。公开复核清单只有保护证据的哈希；存档、ticket、token、运行描述和原请求均未提交，CI不能读取这些保护原件。

本次真实运行是同源的组合开发安装：Plugin与独立/目录MCP的实际字节已核验，并完成正常冷恢复；**未另行对两份发行布局各重做一套完整冷安装/恢复矩阵**。Thunderstore静态检查器的`runtimeBlackBoxTested=false`保留，实机证据与逐字节载荷一致性分别记录，未把格式检查当作实机验收。

English: the extension proves normally manufactured off-world sails, their launch/swarm conversion, the first locally manufactured carrier rocket, its matching Native flight and exactly one delivered structure point. Auxiliary boards and fuel actually arrived through interstellar logistics. Normal saving and cold continuation retained the delivered point and factory; the final selected d3 source reached real work in 72.890 seconds and was normally saved/exited with a complete 2116-file protected backup. The original three Voyager gates retain their earlier source scopes. Both archives use the clean pushed d3 source, pass bilingual/schema/resource checks and contain 233 payload entries equal to the verified installed cohort. Runtime evidence uses that coherent combined installation, rather than claiming a separate full cold matrix for each distribution layout. Protected-value/credential checks and SDK-host classification have explicit scopes. No tag, Release or platform upload was performed.

详见[公开复核清单](manifests/expansion-review-evidence-2026-11-06.json)、[唯一活动快照](../../scenarios/v0.5-voyager/current-status.md)和[源锁](../../source-lock.json)。 / See the sanitized evidence index, current snapshot and source lock.
