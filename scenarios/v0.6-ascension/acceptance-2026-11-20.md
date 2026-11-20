# Ascension live acceptance / Ascension 实机验收

## 实际结果

2026-11-20 在当前自有、和平、非沙盒 1× 存档的 Caph II，使用正常制造、供料及原生发射完成三节点、三框架、一壳层设计。实际结构为 **150 / 150**、壳面单元为 **224 / 224**，吸收订单为零。冷恢复前后逐项比较节点位置、框架连接、壳层边界及轨道参数，拓扑一致；恢复后的结构与单元计数仍完整。发射和吸收是游戏实际进程，蜂群和在途订单没有提前计入完成数。

同一恒星、电网和射线接收站在日照下的实际发电采样如下；功率为样本最低值，覆盖结论限于声明区间和采样精度：

| 阶段 | 覆盖游戏 tick | 样本数 | 最大间隔 | 最低采样功率 |
| --- | ---: | ---: | ---: | ---: |
| 闭壳后、保存前 | 1800 | 45 | 42 tick | 123660 W |
| 冷恢复后 | 1846 | 40 | 50 tick | 122520 W |

此前两次采样跨越当地日落而降至零，未通过各自的连续非零区间；冷恢复后的首次采样有两个正功率样本，但因间隔 218 tick 超过声明的 180 tick 上限而未通过覆盖检查。均保留原记录，不将日落视为产品故障，也不声称单座接收站昼夜持续发电。冷恢复后提高采样频率，再于日照恢复时取得上表结果。

旧版一次回主菜单动作在完整保存及请求原生退出后回读超时，原结果保持 `outcome_unknown`。独立 MCP 观察确认世界已卸载，随后正常关停并核验完整备份；原动作没有重放。修复版在冷恢复后另一次正常保存、原生回菜单、主菜单回读和正常关停均实际成功，不改写旧结果。最新主档和 LastExit 均为 tick **136886110**，累计 **15796848 tick**，3288 项受保护文件完整备份核验通过。

## 版本与范围

实装和本次玩法证据对应产品源码 `e221b263496c6f786f1c42e7b71d38e4312f9b62`、DSP `0.10.35.29151`。该源码的完整构建、16 项回菜单针对性测试及[准确 CI 的 7136 项测试](https://github.com/Arcueid77/Spherewright/actions/runs/44723503219)通过；同源 5 个插件文件、224 个 MCP 文件和 47 项实装接口形状核验通过。冷启动到首笔真实操作为 285.891 秒，低于当前 600 秒上限，未达到 120 秒优化目标。

回菜单等待修复已通过本次实际正常退出验证。按实际距离计算的近距普通施工预算已通过源码测试与 CI，尚未在本次冷恢复后另做针对性施工；只读步行路线预览仍保留 16 米实现范围。无线塔已正常付料建成并接入电网，机甲实际充电仍缺独立实证。本记录不等同于正式发布，也不证明其他存档、整日接收或其他安装环境。

## English

On 2026-11-20, the current owned peaceful non-sandbox 1× Caph II save completed a three-node, three-frame, one-shell design through normal manufacturing, supply and Native launches. Observed structure was **150 / 150**, cells **224 / 224**, and absorption orders zero. Node positions, frame connections, shell boundaries and orbit parameters matched across the normal save and cold recovery; the restored delivered counts remained complete. Swarm sails and in-flight orders were not counted as delivered early.

For the same star, network and ray receiver, the declared daylight observations covered **1800 ticks / 45 samples / maximum 42-tick gap / minimum 123660 W** after closure, and **1846 ticks / 40 samples / maximum 50-tick gap / minimum 122520 W** after cold recovery. These are sampled results for the declared daylight intervals. Two earlier intervals failed when local sunset reduced output to zero. The first post-recovery attempt retained two positive samples but failed its declared coverage when a 218-tick gap exceeded 180; the later observation used faster polling. Neither nighttime output nor all-day generation is claimed.

An old-runtime menu-return action remains `outcome_unknown` after its readback timeout, despite a confirmed complete save and native exit request. An independent MCP observation saw the world unloaded, followed by normal process close and a verified complete backup; the action was not replayed. A distinct normal save, native menu return, menu readback and normal close succeeded on the fixed runtime after cold recovery. Latest primary and LastExit both cover tick **136886110**, with **15796848 cumulative ticks** and 3288 verified protected files.

Installed and gameplay evidence use product source `e221b263496c6f786f1c42e7b71d38e4312f9b62` on DSP `0.10.35.29151`. Its full build, 16 targeted menu tests and [7136 exact-CI tests](https://github.com/Arcueid77/Spherewright/actions/runs/44723503219) passed; the coherent five-plugin / 224-MCP-file installation and 47 installed interface cases were verified. Cold startup reached the first actual operation in 285.891 seconds, within the current 600-second limit but above the 120-second target.

The menu-wait fix was verified by the later normal exit. The measured-reach ordinary construction budget passed source tests and CI but did not receive a separate construction exercise after this recovery; the read-only walking-route preview still has a 16 m implementation range. A wireless tower was normally paid, built and connected, but mecha charging lacks independent proof. This record does not itself constitute publication or prove another save, all-day reception or another installation environment.
