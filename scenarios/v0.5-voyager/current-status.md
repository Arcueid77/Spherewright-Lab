# Voyager active snapshot / 0.5 活动快照

This is the only current snapshot. 历史验收、当前候选、磁盘安装和实机结果分别记录。

## Candidate, installation and current world / 候选、实装与当前世界

The owner explicitly approved discarding the exact **12488-tick** interval from paused RAM120919464 to the latest complete owned primary120906976, then requested that ordinary saved-world opening be separated from expiring automatic-task authority. This supersedes the former no-rollback requirement only for that exact primary and interval. It does not authorize an older checkpoint, another world, new task time or replay.

用户明确批准舍弃当前暂停RAM120919464到最近完整主档120906976之间的 **12488tick**，并要求修正普通读档与旧自动任务期限耦合。该批准仅覆盖此主档及此差额，不扩展到更旧检查点、其他世界、新任务时间或重放。准确主档已完整核验并备份。

| Identity / 身份 | Current fact / 当前事实 |
|---|---|
| Product HEAD and integration candidate / 产品HEAD及唯一候选 | **13a3f3ea45ce980c9692d696fc96421c4f78aebe / 0.5.0** |
| Lab source-lock and gitlink / Lab固定依赖 | **13a3f3ea45ce980c9692d696fc96421c4f78aebe**, offline adoption / 离线采用 |
| Disk installation / 磁盘实装 | **db97832ee4eb4f7589370714f971fbd2a923c4e0 / disk_verified**; unchanged / 未变 |
| Loaded module / 实际加载 | Existing process35176 from verified db97832 cohort. Public API does not expose loaded source SHA; **running_unverified** retained / 旧进程及未核标记保留 |
| Native | **0.10.35.29151**, Assembly SHA **EF314425DADE51F529F184F07BE136CD3C2660A6A81515603C7226FBE7AB1D8C**; five references unchanged / 五引用未变 |
| Current world / 当前世界 | Fresh MCP **120919464 / quarantined / writesAllowed=false**, primary120906976, complete LastExit120906946; no game mutations this repair / 本轮未改游戏 |
| Historical healthy recovery / 已发生的健康恢复 | db97832 original resume completed; healthy admission and normal Save120906976 proved. Later original return-wall guard paused/quarantined at120919464 / 成功恢复后又被原时间守卫暂停 |
| Final review pair / 最终交审双包 | **null / null**; Gate2 open / 门2开放 |

Original Move remains **outcome_unknown**; the d6 execution family stays retired. Its first failed conjunction member remains unknown; later fixes do not establish that original root cause. Existing ordinary-research enqueue authority is retained. 原Move仍unknown，d6执行族退役，原合取首错未知，不倒推根因；既有普通科研入队授权保留。

## Ordinary opening is independent of task expiry / 普通读档与任务过期分开

Public MCP preparation now defaults to **open_saved_primary**. It verifies both protected ownership replicas, the complete exact same-Native primary and original durable Journal, including after days/weeks of inactivity or a quarantine. The exact Native loader completion calls supported Pause and verifies the saved tick/identity/planet. Journal adoption issues a fresh **saved-world-only** credential, usable for later opening despite expiry. Every existing automatic execution/recovery mode rejects that credential. No old action is resumed or relabelled; no charging, automatic Save, fresh task clock, energy/tick/warper grant or checkpoint loading occurs. Original Journey/Journal/consumption history stays intact. Human game controls remain available. Automatic health/takeover and any new return mission are separate and remain unproved/ungranted here.

公共MCP准备默认 **open_saved_primary**：即使闲置数日/数周或处于隔离，也核验归属双副本、同Native精确完整主档及原持久Journal；精确原生加载完成时调用受支持Pause并核存档tick/身份/星球。Journal接管后仅签发以后读档用的凭据，旧执行/恢复入口均拒把它当自动操作许可。旧动作结果、Journey/Journal及消费历史不改，不续跑、充能、自动保存、增加时间/能源/tick/翘曲器或加载检查点。玩家可使用游戏自身操作；自动健康接管与新的返程任务仍须另行完成原生核验和适用授权，本次尚未证明或授予。

Primary normally covers the known floor, including any same-owned fixed LastExit. Explicit exact loss acceptance binds both floor and primary tick plus the full source and matching LastExit fingerprint; it is not a generic >= relaxation or source fallback. The actual current ticket minimum was freshly read as120919464, correcting the earlier diagnosis's unverified120906976 guess. A newer complete preservation primary can be opened without inventing an equal ticket minimum.

普通主档须覆盖已知下限及同owned固定LastExit。用户明确舍弃进度时绑定精确下限、主档tick及两个完整来源指纹，不以泛化>=或换源放宽。当前票据minimum鲜读为120919464，纠正诊断中未核实的120906976推测；较新的完整保全主档可直接核验，不伪造同值票据。

## Candidate qualification / 候选验证

Exact **Push** CI [39742663779](https://github.com/Arcueid77/Spherewright/actions/runs/39742663779) succeeded for13a3f3e. Complete local Plugin/solution build uses the current five Native references with zero warnings/errors; full implementation regressions and the complete subsequent MCP-default regression passed. Final official dual packaging rebuilt the exact final Native Plugin/source. The pre-fix exact78034e9 archived production Store/coordinator rejects the same days-old quarantined opening expectation; repaired Store/coordinator, real full-file leases/Journal/consumption and the production event/adoption guard reach saved-world opening with old automation stopped. Unknowns/order/ownership/file/Journal/digest/floor changes, unapproved rollback, consumed provenance and ambiguous dispatch remain fail closed. Native loader/Pause substitutes are explicit; this is not Unity runtime proof.

准确Push CI及当前Native完整构建、回归已过；最终官方双包按准确SHA重建。修前原始78034e9代码复现拒绝；修后真实Store/coordinator、文件/Journal/消费租约及生产事件守卫可到达仅读档终态。未知、乱序、归属、文件/账本/digest/下限变化、未准回退、已消费及模糊dispatch仍拒绝。加载/Pause替身不认证Unity实机。

|13a3f3e development payload / 开发载荷|SHA256|Bytes / 字节|
|---|---|---:|
|Manual / 手动|453E9887238F5F0594EAFBF8BFDEB0F79B5F3E303F54B75F7F81329AC532C12B|37156890|
|Thunderstore layout|3486FF98DFD1E45B6F98D59DABCAF263E30CFE3DC90EB7D07BB11845E1F33781|32884649|

Actual manifests/files, matching72tools/1resource/schema/default, bilingual embedded/package guides, fresh Contracts processes and every actual product module stamp match13a3f3e. Raw payload scan remains **1finding / child2 / driver2 / passed=false**: exact manifest-size collision for the actual immutable System.Security payload, newly rebound to this manifest/ZIP. Original needles and matcher remain;236 exact unchanged file hashes reuse only their prior no-finding evidence, all new needles scan all bytes and21 changed files scan all needles. **0real path leaks /1classified /0unclassified; payloadQualified=true / allChecksPassed=false**. Earlier invalid guessed seven-module report is retained but excluded; the corrected complete actual-module inventory is authoritative. Positive installation sandbox, disk installation and real Native opening have not been performed for this candidate. No Tag/Release/upload.

真实文件/接口/默认模式、双语嵌入指南、Contracts和实际模块标记一致。扫描原异常1项及child2/driver2/passed=false保留；仅对本manifest/ZIP与实际System.Security文件的精确size/hash归类。原针及检查器保留，按完整文件SHA复用未变证据，新增针覆盖全部字节，变化文件全针扫描；无真实路径泄漏或未知项。载荷合格，allChecksPassed仍false；原猜测模块清单的无效报告保留但不使用，以更正后实际清单为准。新候选尚未做正向安装沙箱、实装或实机读档，未发布。

The actual db97832 installed manual/Thunderstore pair remains7916E7F33A91C468A7EF518C701100DBE10F2A65F9B4963CF699999D3AA44089 /3FFD370ED8C281A04076A36237DDD7F4716D05FC20A91AC2FDE4C676F14C1517. Its old installation and successful Native recovery evidence is historical for that cohort, never13a3f3e proof.

## Failure, repair and runtime eligibility / 失败、修复与实机条件

|Failure evidence / 失败证据|Phase/dependency / 阶段与依赖|Repair / 修复|Positive/negative proof / 正反验证|Runtime eligibility / 实机条件|
|---|---|---|---|---|
|Old automation expiry blocks ordinary opening / 旧许可过期挡读档|MCP default → ownership/full primary/Journal → exact Native completion|13a3f3e separates saved-world opening; old tasks stay stopped / 分离读档，停止旧任务|Pre-fix RED, repaired real Store/coordinator/event guard, weeks-later opening; execution reuse/unknown/changed evidence denied / 修前复现、修后组合与反例通过|Offline ready; not installed / 离线就绪，未安装|
|Paused quarantine Save bootstrap / 隔离保存自举|Save before old required progress-preserving cold deployment|36ec081 save option retained in13a3f3e; owner's exact12488tick discard removes this Save prerequisite for the current chosen primary / 保留修复，本次明确舍弃使该主档不再必须先覆盖保存|Full current primary/backup verified; no new Save or Close / 已核完整主档备份，未保存退出|Current UI unavailable; do not inject/hot-swap / 界面不可用，不注入热换|
|Completed predecessor and expired Journey / 成功前驱及旧旅程过期|Old automatic continuation/admission|78034e9 unchanged-window continuation retained;13a3f3e ordinary opening does not continue it / 保留原续接，普通读档不继续旧任务|Old completed/unknown outcomes unchanged; new file-opening credential grants no automatic work / 终态不改，不授自动作业|Automatic return/health still separate, unproved / 自动返程与健康仍未证明|

## Remaining Native automatic-recovery audit / 保留的自动恢复Native审计

The following unchanged audit applies to the existing automatic contact/charging/takeover path. Saved-world-only opening stops at Native load completion/Pause and Journal adoption; its151/501/601/charging/strict-idle stages are **not_reached**, never counted as passed. 下表保留自动接触/充能/接管路径；仅读档停在原生完成/Pause和Journal接管，不把未执行的后续阶段算通过。

This audit uses the current EF3144 assembly and sealed source extractions, not a new Native invocation. **P** is the captured bounded cost per actual Native601; budgets below are checks, never energy grants. 本审计据当前程序集和保护的反编译原件，未为补表新增 Native 调用。P 为实际601的已证每 tick费用上界；表中预算只检查，不加能量。

|Call point / 调用点|Sample tick / 采样点|Frozen binding / 冻结项|Allowed natural change / 合法自然变化|Forbidden / 禁止|Budget and pass / 预算及通过|Failure and preservation / 失败与保全|
|---|---|---|---|---|---|---|
|Covering primary → historical outbound witness|Before prepare and again at commit / prepare及commit鲜活核对|Original exact successful action, CP bytes, Journey, Journal, Native and full primary/source hashes / 原成功与完整来源|A normal primary save may retire reload capability / 正常覆盖可退役重载权|Reloading retired CP, borrowing old digest, inconsistent failure/reload/retirement, source older than primary / 禁退役加载、旧digest、矛盾及回滚|Bound retired tick/time with sealed success; LastExit >= current primary and all original budgets / 退役历史绑定且不变预算|Unknown/missing/mutated evidence rejects without Load; retired checkpoint remains non-loadable / 未知缺失变化拒绝且退役档不可重载|
|Exact loader completion → Session preflight|Exact source tick / 精确源 tick|world/player/session, source/primary/Journal/checkpoint leases, whole Journey JSON contents; detached Store copies are not managed-reference identity / 全内容而非托管引用|Ordinary load completion only / 正常完成加载|Wrong loader/world/Native, newer-progress rollback, unknown original action attested known / 换加载器、世界、版本或冒认 unknown|Original ownership, prefix, Journal, confirmation and return proof / 原归属、完整源、Journal、确认、返程门|Known original code; Pause/quarantine only exact owned binding, retain leases / 原码，精确 owned 才暂停隔离，保留租约|
|Paused Native Update/LateUpdate → initialization hold|Same source tick; <=8 host observations /2s;0Native ticks|actor pose/energy/input/materials, surface references, Journey contents / actor与旅程不变|Native registration and Dirty refresh may settle; PlayerController skips universal projection while paused / 原生注册刷新可完成，暂停时角色跳过宇宙重投影|Manual Update/Init/Sync calls, owner rebind, treating Dirty=false as mesh mutation epoch / 手工调用、重绑、伪称 mesh 恒定|Count>0, Dirty explicitly false and current support/ground proof, once-only Resume; original funding remains / 集合非空、明确刷新完、当前支撑证明，一次 Resume|Unknown Dirty, changed frozen state,2s/8 exhausted latch failure; no tick reset / 未知或变化、耗尽即锁存，不改 tick|
|Arm loaded frame → actual151|source+1 before first601|Original double uPosition and exact ARM float→double projection endpoint, other pose/body/input/energy / 原值及精确端点|Ordinary unpaused LateUpdate may choose exactly the original or ARM projection / 只能原值或 ARM 精确投影|Tolerance widening, third endpoint, rebasing with later151 frame / 容差放大、第三端点、后换 frame|Same151 full retained-player/terrain/binding decision; then pin its selected endpoint / 同次完整通过后锁定端点|First failed predicate with copied values; no idle owner or Save / 同次首错与数值，未接管不可保存|
|First actual501 → pre-player|Same first source+1|151-pinned uPosition and all original first-frame state / 锁定值及原首帧不变项|Actual local physics/terrain lifecycle is observed / 观察真实物理与地形生命周期|501 before151, endpoint switch, duplicate first physics / 乱序、换端点、重复|Real501 observer and exact same retained references; current601 must remain funded / 真实501、精确引用，仍支付当帧601|Fail closed, retain first snapshot/leases; Pause does not abort entered LogicFrame / 锁存保租约，Pause不取消已进入帧|
|Bound near support → contact151/501 transition|Every real151 then same-tick501; <=8actual601 /2s|world/scene/current pool+support chain, exact positive local scales and complete uniform ancestor chain, cost envelope / 精确引用、缩放输入、父链与费用包络|Native gravity may rotate actor and change derived lossyScale; measured bounded inward/tangential motion/velocity / 允许原生旋转及受限自然接触位移|Resize/reparent/body replacement, foreign/lost support, mode/input/work changes / 禁缩放重绑、归属丢失、输入作业变化|All non-ground sources: production mode/input/order/work/drone checks, proved movement+independent cost reserve, finite bounded controller/body/vertical motion. Contact does not require idle=true / 非接地前提含生产检查、费用及运动；不伪造 idle|Stable support code plus first failing copied predicate; no post-Pause re-sample / 稳定原码与同次首错，不事后补采|
|Foot/ground observations → contact result|Same decision/tick / 同次同 tick|Exact support identity and query configuration / 当前支撑及查询配置|Sphere=false +0foot is airborne; Sphere=true +>=1owned foot may still be moving / 未接地可过渡，接地仍可移动|Unknown query/count/ownership, contradictory sphere/foot, foreign overlap; no cast-as-ground / 未知、矛盾、异物，cast不算接地|Cast<=.25m, normal>=.5, inward[-.01,.25]m, tangent<=.05m, speed<=1.5m/s unchanged;14P and all original tick/UTC/loaded/warper floors each step; Ready requires real ground+strict idle / 原界不放大，每步14P，真实接地且严格空闲才 Ready|At eighth501 Ready or Pause before its601; still pays failure frame / 第八步接管或停，仍付失败帧|
|Grounded low-core → natural recharge|Original charge start and each actual501; no reset / 原起点逐501|Original cost envelope, loaded return floor, elapsed/spent/max/UTC/warper proof / 原费用及总预算|Native GenerateEnergy, actual fuel/energy changes inside proved envelope / 原生自然充能及已证变化|Borrowing future generation, contact with idle=true surrogate, renewing caps / 借未来能量、伪 idle、续上限|Grounded bootstrap2P; strict13P before takeover. Contact14P can reach strict13 directly; no ground→charge→idle circular premise. ReturnCoreMin remains separate future-return gate / 分离2P与13P，接触14P可直达，不把返程核心门加成接管门|No promise of positive net generation; original caps/return deadline stop path and retain raw budget / 不保证净增，耗尽即保全终止|
|Strict idle → Session completion/lease release|Only real501 after original Journal proof / 真实501|Exact adopted world/session and bound durable evidence / 精确世界会话与持久证据|Publish current idle owner, then release original leases / 先守卫接管再释租约|151 publishing success, terminal/repeated admission, unknown proof as pass / 禁151冒成功、终态重复、未知当通过|Same production strict mode/ground/energy/tick/UTC/warper admission / 同一生产严格门|Pending/failure keeps real Store leases; only passing completion releases / 未决失败保留真实租约|
|Normal Save → covering Native prefix and renewed ticket|Fresh immediately before Save and completed native file / 保存前与完整文件完成时|Owned identity, Journal, original budgets and current strict owner / 原身份账本预算与严格 owner|Only supported ordinary Native Save / 仅受支持正常保存|Save while failed/pending/quarantined; loading an older full file / 禁失败未决隔离保存、旧档回滚|Strict recheck, native complete file covers latest RAM and prefix/Journal verified / 严格重核且完整档覆盖最新进度|Current db97832 Save is blocked after the later idle quarantine; pause boundary919464 is not yet covered / 当前919464尚无完整覆盖，停止冷动作|
|Any failed decision / observer loss / cancel|Failure decision or explicitly unsampled Session event / 同次失败或明确无采样事件|First code/predicate/stage/tick/copied values; true/false/unknown/not_reached / 首次证据锁存|Pause can change later physics; new observations remain separate / 后续变化另记|Replacing first cut, stale successful sample as failure instant, fake all-passed table / 禁覆盖、借旧样、凑全表|Bounded recorder and detached Copy; unsampled event has factsState=not_observed and no invented raw values / 有界深拷贝，无采样无伪造值|Original code and current601 exposure preserved; no automatic replay / 原码及当帧费用保留，不自动重试|

Offline composition links the production contact fact factory,151/501 transition and Session completion with real coordinator/Store leases and a sanitized original preflight fixture. It covers paused Dirty initialization, original-vs-projected endpoint pinning, multi-tick motion/contact, strict takeover, negative ownership/unknown/order/budget/cancel cases and failure601 funding. Existing expired-ticket, changed durable Journey, newer-primary and original-unknown regressions remain. **Unity collision/rotation decomposition/registration, the full Session tracker, actual Load/Save and runtime recovery are not simulated or certified.** The original missing failure instant cannot be recreated as an asserted historical member.

离线用生产事实工厂、151/501转移及 Session 接管片段、真实 coordinator/Store 租约和脱敏原始预检观察组合；覆盖暂停 Dirty、双精度端点锁定、多 tick接触、严格接管、归属/未知/乱序/预算/取消反例及失败601。保留过期票据、持久 Journey变化、较新主档和旧unknown回归。**不模拟/认证 Unity碰撞、旋转分解、注册、完整Session、真实Load/Save或实机健康**；原缺失失败瞬间不能伪造为已知单项根因。

## Original bounds, acceptance and next unique result / 原限额、验收与下一唯一结果

|Original bound / 原约束|Retained value / 保留值|
|---|---:|
|Journey maximum / 总tick|108000|
|Current elapsed / 当前elapsed|42027|
|Spent / 已spent|6365|
|Return reserve / 返程tick|54000|
|Conservative remaining work / 工作余量|5608|

Original absolute NativeUTC,18000tick/300s caps, return/core/loaded/warper floors and consumed records remain intact. The one functional recovery used the already-authorized finite20-minute continuation scope with unchanged18000tick/300s charge caps; the original Journey UTC record and spent/maximum/return floors were preserved. No further proposal is created after the current idle guard stop. Existing same-owned/same-Native/no-rollback standing authority remains; it does not make the present coverage gap pass.

原 UTC、18000tick/300秒上限、全部返程/核心/loaded/翘曲器底线及消费记录不改；本次单次功能恢复沿用既有20分钟续接范围及18000tick/300秒充能上限，未改原Journey UTC或储备；当前idle停机后不再生成提案。同 owned、同Native、不回滚 standing 仍有效，但不把覆盖缺口算通过。

**Next unique result: open the owner-approved complete primary120906976 with the qualified candidate, leaving old automation stopped.** The owner cannot currently unlock Windows; only Native menu/normal-close UI requires that desktop. The existing db97832 process stays open and paused until that supported interface is available. No Close/Load/install/Resume occurred this repair. Existing same-owned/same-Native standing cold authority and this exact loss grant are retained; fresh actual process/primary/LastExit/protected-record checks still precede the single deployment/opening. A new automatic return window is not inferred from read authorization.

**下一唯一结果：用合格候选打开用户明确获准的完整主档120906976，旧自动任务停止。** 用户暂时无法解锁，原生菜单/正常退出需要可操作桌面；现有db97832进程保持打开、暂停。本轮未Close/Load/安装/Resume。同owned同Native常规冷部署standing及本次准确舍弃批准保留；执行前仍鲜核进程、主档/LastExit和保护记录。读档授权不推导新的自动返程时间。

Historical Gates1/3 retain their original scopes; Gate2 is open. Historical condition counts are not current-source release maturity. After healthy recovery, reuse the already selected resource1013 target and existing home recipe62 consumer: minimal real vein/miner/power/passive ILS, legal vessels/warpers, several declared complete shipment cycles, actual consumer use, and ordinary Save/recovery continuation. Declare quantity/rate and a window based on real flight times before running; separate startup, mined, in-transit, station-received and consumed stocks. No0.4 replay, macro-factory, speculative research or relaxed gate. Final manual/Thunderstore review candidates remain **null/null**; formal Tag/Release/upload needs separate explicit approval.

历史门1/3及累计范围保留，门2仍开放，历史条件计数不代表本候选发布成熟度。健康恢复后沿用既定1013目标与母星recipe62消费端，最小真实矿机/供电/被动ILS、合法船/翘曲器、多完整船运循环、实际消费、普通保存恢复后续运；执行前按真实航时声明数量/速率/窗口，区分启动、矿源、在途、接收与消耗。不重做0.4、不扩厂或无据科研、不改验收。最终双包仍null/null，正式发布另需明确批准。

Root is the sole game writer/offline Git maintainer. No recursive consultation, new governance platform or monitor/ACK/notification change. The [original acceptance](acceptance.md), frozen0.4 and [handoff route](../../operations/active-handoff.md) are unchanged. Historical failure/install/source cuts remain at [198c00a](https://github.com/Arcueid77/Spherewright-Lab/blob/198c00ac8d0bc3e8d0534d1e931fa5f89a973445/scenarios/v0.5-voyager/current-status.md).

Current protected evidence is under **.local/v0.5-voyager/progress-preserving-save-audit-20261022-v1/**: exact Native save/UI type cuts, live read-only sharing facts, actual-Core Windows lease fixture and its limits, pre-fix failure and repaired coordinator regressions, full Native build/tests, exact Push CI, same-source dual development payloads/manifests/metadata/three Contracts/seven stamps, unchanged raw scanner and exact contextual disposition, **before-manual-save/** fresh public reads, **preservation-final.private.json**, and protected normal-save inputs/backups. Prior coherent-recovery-correction-20261022 and original d6 continuity receipts remain sealed. One authorized normal close and its complete Native exit save are proved in normal-close-intent/result, normal-close-preservation and latest-complete-save; one exact paired installation, Native-complete menu launch and read-only menu reconciliation are proved; one functional recovery completed; its later idle guard stop and the exact-primary checker reconciliation are retained in recovery-and-later-guard-reconciliation.private.json. No Gate2 construction or publication occurred. The resulting Lab commit/CI is recorded locally after terminal. Private identities, tokens, absolute paths and original UTC remain protected.

The additional **.local/v0.5-voyager/paused-quarantine-save-correction-20261022-v1/** retains the unchanged-parent access RED reproduction, repaired full regression TRX, exact36ec081 Native build, original-needle source scan, exact Push CI and fresh current-paused MCP read proof. No Save/Close/Load/Resume or UI input was performed during this offline repair. 新保护目录保留修前复现、修后完整回归、准确SHA Native构建、原检测针扫描、Push CI及fresh MCP只读回执；本次离线修复没有保存、退出、加载、Resume或界面输入。

Latest implementation/qualification originals: **.local/v0.5-voyager/saved-world-open-20261022-v1/**, including exact-parent RED, Native build/regression, default-dispatch MCP checks and source scans; **final-candidate/** holds exact13a3f3e dual payloads, manifests, fresh metadata/Contracts/module stamps, exact Push CI, raw incremental scan/contextual disposition and offline-repair-qualification.private.json. **last-readback/** independently confirms the unchanged installed db97832/current paused boundary. **owner-approved-primary-rollback-20261022-v1/** retains the exact owner grant, complete current primary and full-hash backup. No private identities/tokens/absolute paths enter Git.

新增保护证据目录保存修前复现、准确源码/双包及CI、原异常和精确归类、最终离线限定、fresh旧实装只读及明确舍弃批准。唯一活动快照沿用；不新增治理平台或修改监控/ACK/通知。
