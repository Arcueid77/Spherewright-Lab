# DSP29151 Voyager native audit / Voyager 原生接口审计

Offline audit dated 2026-10-19. This records signatures and normal native branches, not a Plugin build, installation, game execution or Voyager acceptance. / 本文是离线签名与正常原生分支审计，不是 Plugin 构建、安装、实机执行或 Voyager 验收。

- Native cohort / 原生版本: `0.10.35.29151`.
- Installed `Assembly-CSharp.dll` was independently read and SHA-256 matched / 已独立读取安装 DLL 并核对: `EF314425DADE51F529F184F07BE136CD3C2660A6A81515603C7226FBE7AB1D8C`.
- Tool / 工具: `ilspycmd 9.1.0.7988`. Decompiled sources, original paths and the 23-type evidence index remain protected-local; no native source or DLL is committed. / 反编译原文、原路径和 23 类证据索引仅留受保护本地目录，均不入库。

## Visibility and units / 可见性与单位

| Native evidence / 原生依据 | Exact rule / 精确规则 | Minimum adapter / 最小适配 |
| --- | --- | --- |
| Private `UIStarDetail.OnStarDataSet()` and public `RefreshDynamicProperties()` | Required observe level: local star `2`; another star with player-to-star distance strictly `< 14400000` is `3`; otherwise `4`. `observed = history.universeObserveLevel >= required`. / 本星系等级 2；其他恒星距玩家严格小于 14400000 为等级 3；否则等级 4。 | Publish current/required level and observation eligibility separately from scan readiness. / 观察资格与扫描就绪分开返回。 |
| Private `UIPlanetDetail.OnPlanetDataSet()` and public `RefreshDynamicProperties()` | Required level: current planet `1`, other planet in local star `2`, other planet strictly `< 14400000` from player `3`, otherwise `4`. A planet with `factory != null` is observable at level `>= 1`. / 当前行星 1、本星系其他行星 2、其他近距行星 3、其余 4；已有 factory 的行星在等级至少 1 时有原生例外。 | Apply the exact planet rule; do not substitute distance to the destination star for distance to the planet. / 按行星实际距离计算，不以恒星距离替代。 |
| Public `UIStarmap.OnStarClick(UIStarmapStar)` | Planet-view selection permits the current star, observation level 3 within the strict distance boundary, observation level at least 4, and the native factory branch. The star catalogue still displays names, positions and star types. / 行星视图受本星系、等级/距离及原生 factory 分支约束；恒星名称、坐标、类型在星图中可见。 | A star being listed does not reveal its planets' resources or authorize a landing target hidden by the map. / 列出恒星不等于公开其行星资源。 |
| `StarData.scanned`, `PlanetData.scanned`, `StarData.RunScanningThread()`, `PlanetData.RunScanThread()` | UI requests native scans through these methods. `scanned` is generated-data readiness, not proof that the player may observe it. Resource summaries are only consumed when readiness and observation both pass. / 扫描字段只是数据就绪，不是玩家探索许可；资格和就绪同时满足才使用资源汇总。 | An eligible normal scan may be requested; while pending, keep resource values unknown. Do not call generation or inspect hidden vein pools. / 合法正常扫描可请求，未完成继续未知，不调用生成器或读取隐藏矿池。 |
| `StarData.CalcVeinAmounts(ref long[], HashSet<int>, int)` and `CalcVeinCounts(ref int[], HashSet<int>, int)` return `bool`; corresponding planet methods are `SummarizeVeinAmountsByFilter` / `SummarizeVeinCountsByFilter` | `filterType=0` is total remaining resources; `1` is mined/working selection and `2` subtracts that selection. A false summary result means missing runtime vein-group data. Gas items/rates are read only after visibility passes; unknown gas UI entries hide both identity and rate. / 0 是剩余总资源；1/2 是筛选，不可拿筛选的零证明不存在；false 表示数据不全；未观察气体隐藏名称及速率。 | Use `unknown`/null for ineligible, unscanned, incomplete or unavailable summaries. Empty arrays or zero must not stand for unknown. / 未许可、未扫描或汇总不全应返回 unknown/null，不伪装空表或零。 |
| `UIStarmap` distance display and native tick | `1 ly = 2400000` universal distance units; `1 AU = 40000`; displayed local distance is metres. Sail tick uses `dt=1/60 s`; speed is m/s. Star/planet cursor text subtracts display surface offsets, so it is not an exact centre-distance budget. / 1 光年为 2400000 原生距离单位，1 AU 为 40000；原生每 tick 为 1/60 秒；光标显示另减表面偏移。 | Bind full universal coordinates and an explicit distance definition in a fresh plan. / fresh 计划绑定精确坐标和距离定义。 |

Absence proof requires legal observation, all relevant planets scanned, complete unfiltered amount/count summaries, and explicit zero for the resource under that scope. Current depletion is not proof that a resource never existed. Theme-based `PotentialResourceTypes` in the existing local-star reader is only a theme possibility, not a vein observation or absence proof. / “母星系缺失”须合法观察、相关行星全部扫描、未筛选汇总完整且明确为零；当前耗尽不等于种子从未生成。现有主题推断的 `PotentialResourceTypes` 只是可能性，不能证明存在或缺失。

## Native flight and warp / 原生飞行与曲速

| Signature / 签名 | Verified normal behavior / 已核正常行为 |
| --- | --- |
| `PlayerMove_Fly.GameTick(long)` | Fly-to-Sail requires `targetAltitude >= 50`, `currentAltitude > 49`, controller horizontal speed `> 12.5`, and `mecha.thrusterLevel >= 2`. The branch clears Build command if necessary, sets the movement frame to Sail, resets Sail, synchronizes camera and notifies scenario. Existing same-star launch already mirrors this branch. / 沿用现有已核起飞路径，不能仅改状态或坐标。 |
| `PlayerMove_Sail.GameTick(long)` | There are no public `EnterWarp` or `ExitWarp` methods in this type. The warp input branch requires sailing, alive/enabled controller, `thrusterLevel >= 3`, no local planet, and strict `coreEnergy > warpStartPowerPerSpeed * maxWarpSpeed`. It calls native `Mecha.UseWarper()` before accepting `warpCommand=true`; the existing auto-replenish branch calls `AutoReplenishWarper()` and then `UseWarper()`. An existing warp command is stopped by `warpCommand=false`. / 无独立进入/退出方法；须完整保留守卫，先正常消耗翘曲器，再提交原生命令。 |
| Getter-only `VFInput._warpKey`; private `PlayerController.GetInput()` | Warp reads override key slot 24 or button axis 29 `onDown`. There is no warp slot in `controller.input0/input1`, and normal GetInput clears those vectors each tick. `UISailPanel` observes warp state; it supplies no public warp-button callback. / 曲速键只读，普通控制向量没有曲速槽；不可改全局按键表冒充正常调用。 |
| `Mecha.UseWarper(): bool`, `HasWarper(): bool`, `AutoReplenishWarper(): bool` | `WARPER_ITEMID=1210`, `WARPER_COST=1`, warp chamber capacity 20. `UseWarper` removes one real item with native `TakeTailItems` and records consumption. Auto replenishment moves up to 20 real package items into `warpStorage` and returns leftovers normally. / 每次进入消耗一枚真实 1210；自动补充是实际背包转移，不是赋库存。 |
| Private `PlayerController.UpdateEnvironment()` | Before action ticks: a true command raises `warpState` by `0.0055655558f`, capped at 1; a false command lowers it by `0.06667667f`, floored at 0. Nominal ramp is approximately 180 ticks in / 15 out. `Player.warping` remains true while either command or state is positive. / 取消后须等原生状态退净，不可直接改 `warpState`。 |
| `PlayerMove_Sail.currentWarpSpeed`, `currentWarpVelocity` | Speed is `V * (1001^(w*A*q) - 1) / 1000`; velocity follows `player.uRotation` forward. Here `V=mecha.maxWarpSpeed`, `w=warpState`, `A=targetAtten`, `q=warpSpeedControl`. The speed control is natively bounded to `[0.2,1]` while warping. Gravity/planet/hive/message proximity affects attenuation. / 不能假设全程最高速度或用最低直线航时作安全保证。 |
| `PlayerMove_Sail.UseWarpEnergy(double dt, double scale=1)` | Exact energy formula appears below. It queries the real core; only a returned energy ratio `>0.5` permits native consumption and continuation, otherwise the command is cleared. / 总燃料热值足够也不能绕过瞬时核心/功率门。 |
| `PlayerMove_Sail.UseSailEnergy(ref VectorLF3 force, double dt, double scale=1)`, `UseSailEnergy(double dvel, double scale=1)`, `UseSailEnergy(ref VectorLF3 dvel, double scale=1)` | These are three distinct overloads. The two-argument vector call selects the `dvel,scale` overload: existing steering `0.36` and braking `1.5` are energy scales, not dt. Ordinary acceleration, steering and braking use these native energy debits. / 复用现有有能耗控制，不额外重复扣能或重跑完整 tick。 |
| `PlayerNavigation.Navigate(int astroId, VectorLF3 ofs)`, `Abort()`, `Pause()`, `Resume()`, `DetermineSailVelocity()` | Navigation flags and thresholds exist, but `GameTick(long)` is empty and this version's `DetermineSailVelocity` only adjusts the destination-orbit stage. It does not provide complete cross-star warp autopilot. / 不能把该接口当作完整自动星际航行。 |

A minimal adapter can mirror the exact guarded native warp-input branch once, use native warper transfer/consumption and submit the native command. Leave warp-state progression, warp energy, movement integration, collision and environment transitions to DSP. Do not call the entire Sail/Controller tick a second time, set position, inject items, assign core energy, set `warpState`, or use the available sandbox fast-travel methods. / 最小适配可一次性复现完整原生输入分支，正常补充/消耗翘曲器并提交命令；实际状态、能耗、位置积分和碰撞仍由 DSP 推进，不能再调用一遍完整 tick，也不能直接写位置/能量/曲速状态或调用沙盒快移。

Native approach protection is a fallback, not the plan's braking margin. While warping with a command and a local star, each planet is checked using centre distance `d`, angle cosine `dot` between the planet direction and normal `uVelocity`, `R=planet.realRadius`, and:

- `b = min(R + 500 + 0.1 * currentWarpSpeed, R + 4000)`;
- `c = R + 0.20000000298023224 * b`;
- if `d < b` and `dot > sqrt(max(0, d*d-c*c))/d`, DSP stops the command and applies its native 50 m/s exit velocity.

接近时应提前退出曲速，保留原生退曲速和制动距离。不能仅靠上述近星体自动退出触发；它用的是普通 `uVelocity` 方向，不能只核曲速朝向。非气态行星原生 Sail-to-Fly 还要求未曲速、非教学状态，且满足高度/速度组合：`height<46 && speed<75 && abs(vertical)<7`，或 `height<25 && speed<85 && abs(vertical)<18`，或 `height<7`。随后由 Fly 正常下降并稳定进入 Walk；海面 Drift 仍复用现有有限安全上岸逻辑。

## Energy and return reserve / 能量与返程储备

Read live values instead of assuming `ModeConfig` defaults. / 读取实时字段，不能用默认配置代替实装值。

| Symbol / 符号 | Native field and unit / 字段与单位 |
| --- | --- |
| `V` | `mecha.maxWarpSpeed`, m/s |
| `K`, `S` | `mecha.warpKeepingPowerPerSpeed`, `mecha.warpStartPowerPerSpeed`; multiplied by speed produce W / 与速度相乘得到瓦 |
| `C` | `mecha.reactorPowerConsRatio == mecha.energyConsumptionCoef`, dimensionless / 无量纲 |
| `w`, `A`, `q` | `player.warpState`, `actionSail.targetAtten`, `actionSail.warpSpeedControl`, dimensionless / 无量纲 |
| `G` | `actionSail.energy_scale`, normally 1; native tutorial sets 0 / 正常 1，原生教学状态为 0 |
| `Ecore`, `Ereactor` | `mecha.coreEnergy`, `mecha.reactorEnergy`, J; `coreEnergyCap`, J / 焦耳 |
| Fuel / 燃料 | real `reactorStorage` counts, `ItemProto.HeatValue` J per item, fuel eligibility and `ReactorInc`; `reactorPowerGen` W / 实际有效堆叠、单枚热值和补充功率 |

For one native tick, with `dt=1/60` and default scale 1:

```text
Pkeeping = K * (V * w * A * q)
Pstarting = S * V * (warpCommand ? (1-w)^3 : 0)
EwarpTick = (Pkeeping + Pstarting) * dt * G * C
```

This keeping term uses linear `V*w*A*q`, not the exponential actual warp speed. The entry check `Ecore > S*V` is a separate strict native gate; it is not an immediate debit of `S*V` J and does not multiply that gate by `C`. / 保持能耗用线性项，不是实际指数曲速；启动核心门是独立严格条件，不是立即扣除 `S*V`，该门本身不乘 `C`。

For an explicitly finite leg horizon of `H` ticks, nonnegative native coefficients and ordinary `G=1`, a coarse absolute warp-only ceiling is `V*(K+S)*C*H/60`. A tighter ceiling can sum the start-ramp term once and use `K*V*C*H/60` for keeping. Neither is a travel-time guarantee. The UI fastest ETA uses optimistic speed factors and fixed overhead; it does not certify fuel, power, attenuation, detours, landing or return. / 有限窗口可作上述曲速能耗上界，或单独积分启动曲线；二者均不证明能在窗口内到达。星图“最快”时间不是安全预算。

A conservative currently loaded fuel-energy lower bound reuses the existing product calculation:

```text
Eavailable = max(0,Ecore) + max(0,Ereactor)
           + sum(valid reactorStorage count * native HeatValue)
```

Do not add an extra full item for `reactorItemId`: its unspent energy is already `reactorEnergy`. Ignoring productive fuel enhancement is conservative. Package fuel only counts after the existing native refuel transfer/readback or a separately proved native auto-replenish path. `Mecha.GenerateEnergy(double dt)` caps delivery at available core capacity and `reactorPowerGen * fuel/ReactorInc factor * dt`; replenishment rate and core capacity must sustain each tick, not merely the sum of stored heat. / 当前燃烧物剩余热值已计入，不能重复加整枚；忽略增产是保守值；未完成正常补充与读回的背包燃料不计可用；还需检查逐 tick 补充功率和核心上限。

The plan must reserve separate outbound launch/sail/warp/exit/landing, return leg, and withdrawal margin, plus at least the real warpers needed for each planned entry. A normal uninterrupted two-leg trip consumes at least two warpers; retries or extra entries need extra declared reserve. Recheck current core, fuel, warpers, technology, visibility and destination before commit and before each entry; read back actual item deltas after entry. / 计划分别锁定去程、返程和撤回余量；最短两程至少两枚真实翘曲器，额外进入需额外声明储备；提交和每次进入前 fresh 核验，进入后核真实扣料。

## Existing reuse and remaining gates / 复用与待过门

The existing `NormalGameActionCoordinator.InterplanetaryFlight.cs` supplies normal launch, energy-debited sail control, body avoidance, landing stability, bounded Drift shore recovery and a single pre-flight checkpoint. Its `max(coreCap*1.5, distance*1000)` budget and same-star guard are a same-star contract, not a cross-star implementation. Keep that compatibility path while adding an explicit Voyager plan and phase machine. / 现有同星系飞行提供大部分局部控制和唯一检查点；其能量估算不能直接沿用为跨星预算，更不能只删除同星系守卫。

`FlightCheckpointStore` already binds exact save/tick/session/route, a 24-hour ticket lifetime and lifecycle states, and seals successful flight before a covering primary save retires it. At audit time its newer-primary comparison ran only in the constructor. Fresh prepare/commit must also reject a newer primary in the same process; exact checkpoint header replacement and expiry remain rejection cases. / 检查点已具备精确绑定、24 小时寿命和退役状态；审计时“较新主档”仅构造期比较，须补同进程 prepare/commit 的 fresh 阻断及集成回归。

Still unproved: current live technology/core/fuel/warpers and visibility; an attenuation-aware bounded route budget; the complete cross-star controller; real native entry/exit, landing and return; controlled failed-flight recovery; sustained mined-resource vessel logistics and save/recovery continuity. DLL signatures and offline tests cannot close those live gates. / 当前实时科技与储备、航线预算、跨星控制、往返、可控失败恢复和持续真实物流均须后续实证，离线审计不予代关。

## Star-only arrival and owned cancel / 仅恒星目标抵达与受控取消

- `UIStarmap.OnCursorFunction3Click` permits a visible star navigation marker without an exploration gate; this marker is not an autopilot. / 原生允许给可见恒星设置导航标记，无须先看到行星；标记本身不提供自动航行。
- Normal `UniverseGameTick → DetermineLocalPlanet → ArriveStar` adopts a nearby star on the same `GameData`; actual `localStar == destination` then allows the local planet list even at observe 0. / 正常原生 tick 接纳目标恒星，不更换世界或 owned SessionId；须等真实 localStar 匹配后才读取当地行星。
- With no prior star, native adoption searches strictly inside 3,239,999.914 game m (about 1.35 ly); choose a finite shell that also covers visible star radius, warp exit, control latency and braking. Do not use hidden planets or `systemRadius`, or aim at the star center. / 捕获半径不是安全保证；壳层必须另证排除恒星、退出及制动余量，不能预读隐藏轨道。
- Planet-list visibility does not authorize resource summaries: current-planet detail needs observe 1 and complete current-star detail needs observe 2, with native scan readiness separately checked. Normal 4101→4102 can supply local survey; 4103 is not required merely to fly to a star. / 行星列表可见不等于资源已知；扫描不代替探索等级，未勘探不等于缺失，不把三级探索追加为飞行验收前提。
- In-flight reads must bind the original owned session, `GameData`, player, controller and action while allowing `localPlanet == null`; a grounded `ValidateOwnedPlanet` guard cannot stand in for transit validation. / 在途观测须沿原 owned 身份 fresh 核验，不能把出发星球冒作当前星球，也不新接纳另一世界。
- Native warp exit clears only the owned `warpCommand`, consumes no new warper and refunds none; never write `warpState`, position or energy. With advancing native ticks, the 0.06667667f decay reaches zero from full state within 15 ticks. / 先阻止原 action 再次启动，随后清除其曲速命令；必须 fresh 观测命令为假且曲速状态为零，才核销退出。
- Warp energy is still spent during decay; ordinary `uVelocity` persists, so exit distance, remaining energy and a separate normal braking/withdrawal path need finite reserve. `disableController` can stop position integration while still advancing warp and charging energy. / 清命令不等于停车；不得用禁用控制器代替取消、制动或返航。
- Before enabling persistent warp control, release exact owned commands/inputs on the Unity main thread before Host/session disposal and on component disable; never clear another world's controls. A stopped Host cannot observe later ticks, so retain the original unresolved action/checkpoint until reconciled. / Host 释放不能假报退出完成；不自动保存、退出或载入，真实状态未知则保留原身份与恢复门。
- These are verified native call conditions, not proof of a completed controller, safe live flight or Voyager acceptance. / 本条仅记录合法原生路径和实现约束，不代关实机往返、故障恢复或持续物流验收。
