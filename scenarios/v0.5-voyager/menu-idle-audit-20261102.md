# Menu idle audit / 主菜单长停留核查

Evidence: retained public receipts and protected-local file write times on2026-11-02, Asia/Singapore. File times bracket caller work; they are not precise Native internal loading stages. / 依据当日保护本地的公开回执及文件写入时间；文件时间用于界定调用端工作，不冒充原生内部加载耗时。

| Time / 时间 | Observed activity / 已核实活动 |
| --- | --- |
| 17:02:52–17:11:55 | DSP process existed; module/recovery checks and caller corrections continued before the first Load submission. / 游戏已启动，仍做模块/恢复检查和执行器修正，约9分钟后才提交读档。 |
| 17:11:55–17:12:02 | Resume submission to successful terminal receipt, about7seconds. / 从提交恢复到成功终态约7秒。 |
| 17:12:07 | Native drone-enable operation completed. / 正常无人机开关操作完成。 |
| 17:13:18–18:33:55 | Returned to menu, then remote factory source/tests/CI/review/artifact preparation continued until normal close. / 回菜单后继续远端工厂源码、测试、CI、审查和工件准备，约1小时21分钟。独立审查为17:55:19–18:11:13；工件v2资格在18:15:24已通过。 |
| 18:42:26–18:43:30 | New source process started; module/menu/fresh recovery preparation passed in about64seconds. / 新源启动到模块/菜单及新鲜恢复预检通过约64秒。 |
| 18:43:30–21:29:50 | No executor Load was submitted; the process was retained through interruption, and a fresh read again found the menu. / 未提交新的读档，中断时仍保留进程，21:29再次新鲜读取确认菜单。 |

The dominant cause was caller scheduling: offline development/review/artifact work was performed after opening DSP, and an already ready menu was retained without an executable next packet. It was not hours of required game loading. Keeping the process after interruption explains part of the interval but does not justify leaving the menu as a planning workspace. / 主因是调用端排程：本可离线完成的工作放在开游戏后，菜单就绪却尚未备齐下一执行包。不是游戏需要加载几小时；中断保留进程解释部分间隔，但不能将主菜单当作规划工作区。

The new [startup gate](startup-to-action.md) moves offline readiness before launch and measures120seconds from launch dispatch through proven real work. Its first live attempt encountered a read-only readiness `REQUEST_TIMEOUT` before any Load/work commit; its initial cleanup also hit the same observation failure. The attempt is retained as failed. A later fresh public read proved the menu, normal close succeeded, and all1658 protected files/four Native saves remained unchanged. / 新门将重准备前置，并从启动请求到真实操作证明计120秒。首次实机在Load/工作提交前遇到只读就绪超时，初始收尾也遇到该观察失败；该次保留为失败。随后新鲜公开读取确认菜单，正常关闭成功，1658项保护文件和四份原生档均未变。

The correction retries only transient read observations within the original deadline, retains both original failure and cleanup failure, and never retries an accepted write. A fresh corrected live run still needs acceptance; offline tests and CI are not timing acceptance. / 修正仅在原截止内重读瞬时读取错误，同时保留初始/收尾失败，不重试已接受写入。修正后的独立新实测仍须验收，离线测试/CI不等于计时达标。
