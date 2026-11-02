# Startup to actual work / 启动到真实操作

Owner instruction,2026-11-02: each normal launch must reach owned-world loading and actual work within two minutes, without a long menu stay. / 所有者要求每次正常启动后两分钟内完成owned世界读档并开始实操，不在主菜单长时间停留。

## Contract / 合同

- Complete source/CI/install qualification, complete backup verification, original-action reconciliation, resource budgets and the first actual-operation packet **before launch**. MCP metadata initialization may be warmed before launch. Do not open DSP to wait for coding, review, packaging or planning.
- Start a monotonic120-second timer immediately **before normal launch dispatch**, including Steam delay. Record process observation, fresh menu/module/lifetime readiness, fresh public recovery prepare, original recovery completion, owned-world proof and the first real operation with its original terminal receipt and observed state delta.
- Reads, metadata, Load and Save are not actual work. The caller gate requires a successful real operation completed within120 seconds, a stricter criterion than mere acceptance. Immediately hand over to the prepared executor; a validation-only executor preserves and normally closes.
- On expiry, submit no additional recovery/work action. Reconcile an already accepted action under its original ID/key even if that takes longer, then preserve/close only a known safe state. An unknown commit blocks competing cleanup and replay. Never force-kill, bypass Native readiness or change resource budgets to meet the timer.
- This is a caller scheduling gate, not new gameplay authority or a promise that Native loading can always finish in time. A failed run remains failed and is diagnosed from phase timings; it is not relabelled or automatically restarted.

- **开游戏前**完成源码/CI/安装资格、完整备份、原动作核销、资源预算与第一笔实操包；可提前预热MCP元数据初始化。不提前打开DSP等开发、审查、工件或方案。
- 正常启动请求发出**之前**启动单调时钟，120秒包括Steam等待。逐段记录进程出现、菜单/模块/生命周期就绪、新鲜公开恢复预检、原恢复完成、owned世界证明及首个真实操作的原终态和实际状态变化。
- 读取、元数据、Load、Save不算实操。调用端要求真实成功操作在120秒内完成，比“已接受”更严格；随即交给已准备执行器。仅验证时正常保全并关闭。
- 超时停止新增恢复/工作提交。已接受动作仍核销原ID/幂等键，即使核销超出两分钟；只有已知安全状态才能保全关闭。未知提交禁止竞争清理和重放，不强杀、不绕原生门、不改资源预算赶时间。
- 本门约束调用端排程，不增授权，也不保证任何原生加载都能及时完成。失败保留分段时间证据，不改名为通过、不自动重启。

Implementation: [controller](scripts/startup_to_action.py), [offline fault checks](scripts/test_startup_to_action.py). Runtime evidence belongs in protected local storage and the [active snapshot](current-status.md). / 实现及离线故障检查见链接；真实运行证据保留在保护本地目录，并由活动快照索引。离线替身不代表实机达标。
