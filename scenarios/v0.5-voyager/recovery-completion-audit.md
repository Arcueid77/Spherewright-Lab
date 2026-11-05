# Recovery completion audit / 恢复完成审计

2026-11-06. Scope: the preserved failed Caph admission, its current complete LastExit, completion persistence and startup scheduling. Authority and current runtime facts remain in [standing authority](../../operations/standing-authority.md) and the [active snapshot](current-status.md). This audit grants no replay, rollback or publication.

## Lifecycle / 生命周期

| Boundary | Required evidence and ownership | Failure handling |
| --- | --- | --- |
| Closed → menu | Stopped game/MCP, exact clean source/CI/cohort, complete backup, one immutable first-work packet; actual process/module/job proof | No loaded-world work; retain the original launch and timings |
| Fresh prepare → commit | Fixed newest complete LastExit, older primary protected, original checkpoint/Journal/Journey unchanged, finite current proposal, exact digest/key | A refusal before acceptance is not a failed Load; never rekey an accepted or unknown action |
| Registered → adopted | Append one admission to the original failed Journey, release only the registration Journey lease, retain source/primary/checkpoint/Journal leases; real Native load/Journal/session/world binding | Pending/unknown cannot open another admission; the old outbound stays failed |
| Native 151/501/601 | Real loader/terrain/contact/stop/energy/paid-site evidence and the original cumulative allowance | Pending contact/charge keeps leases; first actual refusal is immutable |
| Strict idle → durable health | Exact same adoption/session/world, no retained failure; conserved observed ticks and unchanged return reserve; atomic Journey validation/replacement | Distinguish binding, tick regression, charge cap, deadline, reserve, record/transition and I/O rejection; publish no successful admission on failure |
| Health → primary resave | The new completed-health landing remains bound to the same actor, scene and Native guard; normal Save and fresh credential | Save/credential/retirement failures remain separate from successful contact or Store completion |
| Known failed → exit | Exact owned paused cut, terminal original action, first failure, real elapsed debit, release held source leases; normal close and complete backup | Pause is preservation, never idle proof; unknown forbids competing cleanup |

## Current evidence and limits / 当前证据与限制

The production public coordinator/Store replay covers registration, binding, completion, lease release and paused failure. The linked test shell substitutes Native import and callbacks; it does not establish Unity or real save health. The separate net472 Plugin replay accepts the sanitized capture-shaped record in isolation. A held read lease reproduces an I/O refusal and preserves the original durable admission. Tick regression and charge-cap refusals leave it byte-identical.

The retained c79 live failure supplies only `failed_landing_healthy_admission_persistence_unproved`, without an observed inner predicate. Thus neither an I/O collision nor a particular binding/policy rejection is a proven root cause. The completion path now retains each actual binding predicate and the Store's bounded rejection, with numeric tick/reserve/deadline observations; private exception text, paths and records are excluded. This is diagnostic qualification until the same-source live result exists.

The last run reached module/menu observation at45.437s and completed prepare at285.843s. Captured refusals specifically say Native prototype/model preloading was unfinished. This was repeated readiness polling, not a240s accepted Load. The pinned Native `VFPreload` coroutine waits for assets, menu demo, music/splash and its own `done/dbDone`; the current guard must remain. No field, coroutine, clock or simulation is advanced to satisfy the [300s startup gate](startup-to-action.md). Full preflight and first work stay before launch; a missed deadline stays failed.

中文：已按公开协调器、原生生命周期、接管落盘、正常重存及失败退出完整审查。离线生产回放和实际Plugin隔离回放通过，不等于实机健康。旧实机错误缺少内部拒绝因子，尚不能认定根因；本批仅补全当次绑定谓词、精确Store拒绝和数值观察，不删除检查、不把技术失败改成待批。启动耗时已核实主要处于原生原型/模型预加载等待，保留真实预加载门、300秒首实操门及全部失败原件。下一次必须从最新完整LastExit做新鲜受保护恢复，核销原句柄，不回退旧Primary或重放原动作。
