# Caph movement and preservation audit / Caph移动与保全审计

2026-11-15，当前实机Caph行程在一次已接受普通移动后进入Native Pause与精确写隔离。原动作终态为unknown：失去地面接触后，有限尾部未能证明接地Walk；暂停不是物理静止或成功。此前不同移动以距目标1.72米明确失败并证明静止。两笔原件分别保留，不重放。

本次路线选择有执行失误：调用端将未确认地表的分段点作为远端移动目标。相关原生地表预览为`unavailable / surface_span_outside_bounded_preview`，不是干地或岸线证明。产品现有操作指引要求远端跨水使用当前世界中重新验证的Walk目的地、障碍与有限储备，不应制造未知水面中间目标。此前行走成功不证明当前路径安全。冻结原位只读地形切面确认当前位置浅水、沿候选方向约34米有露出水面的地面；约15米处另一候选点的九点地形切面均比水面高至少0.1米。两个目标的新鲜移动预览完整但因原隔离禁止提交，且不证明障碍清除或实际可达。后续先核查完整现场地形、路径和目标，再作独立新动作。

现有同会话核销只支持准确unknown建造或已证明的远端idle隔离，不接受此Move。保全保存仅接受特定已接纳远端idle/checkpoint隔离；当前缺少该见证。正常返回菜单另要求接地。三种新鲜原生预检均拒绝，因此保持现有进程及原生暂停，不自动Resume、不热替换、不强制退出、不回退存档。冻结快照中的零速度/漂浮不证明恢复后静止。已完整复制并校验现有保护文件和自动档，但这些文件不是当前内存保存，不能声称无损恢复。

调用端防线源码提交`7f91af793035ff4c84460a10cf97c100862ac364`通过216项本地回归及[准确CI](https://github.com/Arcueid77/Spherewright-Lab/actions/runs/43691530232)。它未加载到当前已暂停调用端，也未经过新的远端实机移动验收。

本次Lab调用端补充提交前防线：多星配置缺少普通施工星球分类时拒绝普通移动；配置为远端的普通移动仅在新鲜、完整、最多64米且每米至少一采样的干地切面通过后提交。只读预检不受此限制；原生导航依旧使用自己的准入。该防线不证明障碍或实际落地，也不覆盖远端水面续行。水面到陆地应作为独立状态模型与旅程预算问题审查：原动作和原储备保留，明确冻结/漂浮/陆地接触的不同状态及失败保全，再经原生实现、准确测试和实机验证；不能单纯放宽接地检查或把预览当到达。

进一步产品设计应单独评估严格绑定原unknown移动、同会话/世界/旅程、原生暂停稳定尾部及无其他活跃动作的**仅序列化保全**，并区分其与核销、Resume、Load和健康返航。现行运行中的版本不能从离线源码修复中获益；必须先形成不丢当前进度且得到Native支持的具体恢复路径。旧自动档较当前暂停切面早，进度回退仍是单独决定，不能以新累计额度抵销。

## English

On2026-11-15 an accepted Caph Move reached Native Pause and exact write quarantine. Its original outcome remains unknown because the finite post-contact tail did not prove grounded Walk. An earlier distinct movement failed at1.72m with idle proved. Retain both originals and never replay them.

The route choice was an execution error: intermediate remote waypoints were selected without proving their surface. The relevant Native surface preview was `unavailable / surface_span_outside_bounded_preview`, not evidence of dry land or a safe shore. Existing product guidance requires a freshly verified Walk destination, obstruction evidence and finite crossing/recovery reserves for an incompletely observed crossing; unknown intermediate water targets are not admitted. Previous successful walks do not prove this route safe. A read-only frozen cut observed shallow water at the player and above-water terrain about34m along one candidate direction. Nine read-only terrain samples around another candidate about15m away were all at least0.1m above water. Fresh Move previews covered these candidates but could not commit under the original quarantine; it does not prove obstruction clearance or arrival.

The existing same-session reconciliation handles an exact unknown build or a proved remote-idle quarantine, not this Move. Preservation Save requires a specific admitted remote-idle/checkpoint witness; that witness is absent. Main-menu return separately requires grounded contact. All three fresh Native preflights refused. Keep the same process and Native pause; no automatic Resume, hot replacement, forced exit or older Load. Zero speed in a frozen Drift is not physical-idle proof. The copied, hash-verified protected files and autosaves are not a current-memory save and do not prove lossless recovery.

Caller source commit `7f91af793035ff4c84460a10cf97c100862ac364` passed216 local cases and [exact CI](https://github.com/Arcueid77/Spherewright-Lab/actions/runs/43691530232). It has not been loaded into the current paused caller or validated by a new remote live Move.

The Lab caller now refuses normal Move commits on classified remote planets unless a fresh complete dry surface cut covers at most64m with at least one sample per metre. Multi-planet configurations must classify ordinary-construction planets; absent classification, unavailable, partial or sparse cuts reject before action. Read-only prepares remain available and Native navigation retains its separate admission. This is advisory terrain evidence, not obstacle clearance or landing, and does not admit remote water continuation. Audit water-to-land continuation as a distinct state-and-journey-budget model: preserve the original action/reserves, distinguish frozen, drifting and ground-contact states, and require Native implementation, exact tests and live proof. Do not simply weaken grounded checks or treat preview as arrival.

A separate product design should evaluate serialization-only preservation bound to the exact unknown Move, same world/session/journey, stable Native-paused tail and no other active actions, without conflating Save with reconciliation, Resume, Load or healthy return. Offline changes cannot alter the running cohort. First establish a Native-supported path that preserves current progress; the older autosave is earlier than the frozen cut, and rollback remains a separate decision rather than a budget refund.
