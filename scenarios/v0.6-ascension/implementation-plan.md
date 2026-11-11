# Ascension implementation and validation / Ascension实施与验证

2026-11-11。所有者明确要求“继续0.6的推进”，按产品已批准的Ascension范围推进戴森设计、持续发射和接收功率。当前阶段沿用本owned世界的完整保存、原动作核销、有限预算及唯一writer流程。原生程序集为29151，SHA-256为 `EF314425DADE51F529F184F07BE136CD3C2660A6A81515603C7226FBE7AB1D8C`。

## 实施顺序

1. 完成当前恒星的有界戴森拓扑/进度与接收器实际电力观察。核对节点、框架、壳层边界及各类进度，提供完整设计hash、在途火箭和太阳帆计数。射线接收器同时提供最近实际发电、容量、光子缓冲、预热和透镜账目。
2. 完成确定性设计候选与成本计算，再接入原生节点、框架及壳层的有限正常写入。每次prepare绑定当前已有层、科技、完整拓扑、成本及原生合法性，commit和结果按原动作核销。多对象设计保留逐对象进度与重试边界。
3. 复用既有当地制造、弹射器、发射井、供料和电网，形成持续发射候选。通过准确原生目录推导科研、物料和建筑增量，按整案真实额度确定执行范围。
4. 通过已绑定接收器、电网和预声明游戏tick区间验证持续非零实际发电，保存观察样本、材料/缓冲与功率变化。
5. 正常保存并冷恢复，核对设计、在途/已交付进度、设备模式和持续运行状态，汇总源码、实装和玩法证据。

持续接收器验证使用共享驱动的 `observe-receiver-power`。到场后依据实际组件声明接收器、恒星、电网、游戏tick跨度及最大采样间隔，正向区间从首个原生样本开始。逐样本核实际电力、原生组件和电网成员，保存零输出及所有失败切面。通过记录最小采样功率、完整跨度和最大采样间隔，冷恢复后用新声明区间复核同一保存设计及接收器。完整实机验收继续使用当前存档及累计运行额度。

## 当前观察接口

设计/建造源码df32bd78已完成6455项准确回归、Native构建及对应CI。所选层观察支持 `designPreview` 的有界独立原生多对象成本计算，普通配置动作支持 `dyson-structure` 单项新鲜prepare/commit及守恒回读。外星2208接收器沿付费无人机流程核对准确组件，设计沿原单tick即时旅程预算。同源冷安装、实装SDK及完整保护核验已完成，继续已有存档正向验证。

`spherewright_get_dyson_state`支持当前owned本地恒星及所选层，返回最多10层、256节点、512框架、128壳层、4096个壳层边界节点和256接收器。覆盖不完整时汇总值可空。工厂详情通过 `rayReceiver`提供相同接收器观察，继承既有工厂动作hash域。

先完成相关源码回归、完整Native构建、准确源码CI和固定Lab采用。实机前准备同源开发安装、完整备份和第一笔真实普通操作包，继续沿300秒启动到实操门执行。实机目录调查为后续整案科研/用料提供依据。

## 首次现场核对

- 核对最新保护保存、已装模块、准确owned身份及当前材料/科技，累计计入原实耗。
- 在新接口核对现有戴森层/节点、接收器、原发射设备和供料状态，记录完整性及当前输出。
- 依据当前已解锁纬度、轨道与原生条件选择合法闭合设计，计算准确结构/细胞需求及制造链。
- 将新增科研、材料和建筑额度与当前已批剩余额度比较，对确实需要的增量形成一次准确整案决定。

## English

Designdf32bd78 passed6455 cases, Native build and exact CI. Selected-layer observations now support bounded detached multi-object design costs, while normal configuration supports individually prepared Native structures and conservation readback. Finite remote receiver construction binds its exact generator/model. Design operations retain the original one-tick immediate journey budget. Coherent cold installation, installed SDK and complete protection checks passed. Continue positive current-save validation.

The owner requested continued0.6 development on2026-11-11. Follow the approved Ascension scope through observation, deterministic design/cost planning, bounded Native structural writes, sustained manufacture/launch, receiver-power measurement and normal save/cold continuation. Use DSP29151 and the assembly hash above.

The first source slice exposes a bounded local-star Dyson graph and identity-bound receiver electricity through `spherewright_get_dyson_state`, plus optional factory-detail `rayReceiver`. Complete source regressions, Native build, exact-source CI and fixed Lab adoption before coherent development installation. Prepare complete backups and the first real ordinary action before launch, retaining the300-second startup gate and cumulative spending.

The first on-site survey establishes the latest owned save, existing structures/devices, technology and stock. Derive a legal closed design and exact construction/manufacturing bill from current Native facts. Existing authorizations, actual remaining material ceilings, reserves, original-action reconciliation and one writer govern execution. Present a consolidated exact increment when the selected plan actually needs additional research, materials or buildings.

Use the shared `observe-receiver-power` entry for sustained receiver validation. Bind the actual receiver, star and network, and predeclare the game-tick span and maximum sample gap. Its first Native cut starts the interval. Verify actual electricity, Native component and network membership in every sample, retaining zero output and failed cuts. Report minimum sampled watts, covered span and largest gap. After cold recovery, declare a new interval against the preserved design/receiver. Full live acceptance continues on the current save under cumulative runtime authority.
