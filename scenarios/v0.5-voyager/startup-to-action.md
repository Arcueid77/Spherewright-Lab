# Startup to actual work / 启动到真实操作

Owner instruction,2026-11-02: each normal launch must reach owned-world loading and actual work within five minutes, targeting two minutes, without a long menu stay. / 所有者要求每次正常启动后五分钟内完成owned世界读档并开始实操，尽量优化到两分钟，不在主菜单长时间停留。

## Contract / 合同

- Complete source/CI/install qualification, complete backup verification, original-action reconciliation, resource budgets and the first actual-operation packet **before launch**. MCP metadata initialization may be warmed before launch. Do not open DSP to wait for coding, review, packaging or planning.
- Start a monotonic300-second hard-limit timer (120-second target) immediately **before normal launch dispatch**, including Steam delay. Record process observation, fresh menu/module/lifetime readiness, fresh public recovery prepare, original recovery completion, owned-world proof and the first real operation with its original terminal receipt and observed state delta.
- Reads, metadata, Load and Save are not actual work. The caller gate requires a successful real operation completed within300 seconds, targeting120, a stricter criterion than mere acceptance. Immediately hand over to the prepared executor; a validation-only executor preserves and normally closes.
- Selecting a required technology counts only with the original successful Native receipt and a verified queue/technology change. Reading the technology tree, selecting an already-current entry or merely accepting a request does not qualify. Enqueueing is not evidence of research completion or matrix production.
- On expiry, submit no additional recovery/work action. Reconcile an already accepted action under its original ID/key even if that takes longer, then preserve/close only a known safe state. An unknown commit blocks competing cleanup and replay. Never force-kill, bypass Native readiness or change resource budgets to meet the timer.
- This is a caller scheduling gate, not new gameplay authority or a promise that Native loading can always finish in time. A failed run remains failed and is diagnosed from phase timings; it is not relabelled or automatically restarted.

- **开游戏前**完成源码/CI/安装资格、完整备份、原动作核销、资源预算与第一笔实操包；可提前预热MCP元数据初始化。不提前打开DSP等开发、审查、工件或方案。
- 正常启动请求发出**之前**启动单调时钟，300秒硬上限包括Steam等待，优化目标仍120秒。逐段记录进程出现、菜单/模块/生命周期就绪、新鲜公开恢复预检、原恢复完成、owned世界证明及首个真实操作的原终态和实际状态变化。
- 读取、元数据、Load、Save不算实操。调用端要求真实成功操作在300秒内完成，尽量达到120秒，比“已接受”更严格；随即交给已准备执行器。仅验证时正常保全并关闭。
- 选择必要科技须同时具有原生原成功回执和已核验的队列/科技变化才计作实操；读取科技树、选择已在当前项或仅接受请求均不算。排队不等于研究完成或已生产矩阵。
- 超时停止新增恢复/工作提交。已接受动作仍核销原ID/幂等键，即使核销超出五分钟；只有已知安全状态才能保全关闭。未知提交禁止竞争清理和重放，不强杀、不绕原生门、不改资源预算赶时间。
- 本门约束调用端排程，不增授权，也不保证任何原生加载都能及时完成。失败保留分段时间证据，不改名为通过、不自动重启。

Implementation: [controller](scripts/startup_to_action.py), [offline fault checks](scripts/test_startup_to_action.py). Runtime evidence belongs in protected local storage and the [active snapshot](current-status.md). / 实现及离线故障检查见链接；真实运行证据保留在保护本地目录，并由活动快照索引。离线替身不代表实机达标。

## Live check / 实机核验

The corrected run completed real first-sail supply work in **79.469 seconds from launch dispatch**, including69.625s to Native menu/module/lifetime readiness and76.750s to completed public recovery. The original successful transfer moved four circuit boards to the player (0→4), with fresh inventory proof; no read or heartbeat was counted. Normal save/menu return and close completed, followed by a verified1662-file/four-save backup. The first failed attempt remains failed. / 修正实测从启动请求到首帆真实备料完成共79.469秒：就绪69.625秒、公开恢复完成76.750秒；原正常转移电路板4个，背包0→4，已核对终态与新鲜库存。正常保存回菜单、关闭及1662项/四档完整备份通过；第一次失败原件保留。

The owner then relaxed the hard limit to300seconds while retaining a120-second optimization target. This changes startup scheduling only; it grants no additional game ticks, items or live-window duration. / 所有者随后将硬上限放宽至300秒，仍尽量优化至120秒。只调整启动排程，不增加游戏tick、物料或实机窗口时长。
