# Wind recovery maintenance / 风机回收维护

2026-11-13。所有者要求“issue5的修改需要额外同步到0.5里，出一个0.5.1”。当前任务实现并交付风机原生拆除、电网影响预览及独立正常重建验证，同时同步0.6开发线。0.6玩法目标处于暂停状态，保存交接见[Ascension快照](../v0.6-ascension/current-status.md)。 [Issue #5](https://github.com/Arcueid77/Spherewright/issues/5)

## 来源与实现

维护实现基于正式v0.5.0来源b574c616346c4e087b433de3633e23fb12075add，原生DSP0.10.35.29151程序集SHA-256为EF314425DADE51F529F184F07BE136CD3C2660A6A81515603C7226FBE7AB1D8C。共用风机修复采用单独提交同步到0.6开发线，0.5.1使用独立版本提交。

`prepare_dismantle(previewOnly=true)` 提供只读电网影响及未满足条件。普通准备绑定准确玩家、风机端点及完整电网拓扑。提交调用一次原生DoDismantleObject，核对原实体/电力节点/发电组件消失、精确建筑物品返还、增产点、世界对象/连接及电网变化。重建使用重新检查后的普通建造操作。

## 验证顺序

1. 核对版本兼容、旧请求默认值、只读参数转发、序列化、电网连通分量、消费者连接、其他电网保全及拓扑哈希变化。构建实际29151 Plugin，核对双语文档和嵌入资源。
2. 在独立离线原生对象上对照真实PowerSystem.OnNodeRemoving，覆盖独立节点、链、桥、星形、环、多个电网及确定种子随机拓扑。保存准确程序集与实现摘要。该层记录单独保留。
3. 通过准确提交CI及同源Plugin/MCP资格后，在最新受保护owned存档执行MCP验收。优先复用现有风机和回收物品，逐笔记录材料及施工。先检查只读影响和未满足条件，再选择有界正常拆除，核对回收和其他电网，随后独立准备正常重建。
4. 核对原动作重复查询/同键提交及旧ID复用后的历史结果，原accepted/unknown边界持续保留。正常保存、完整关停保护和冷恢复后复核风机、网络及原结果。
5. 固定0.5.1准确来源，生成同源手动/Thunderstore包，核对字节、安装/SDK和运行结果，完成标签及发行记录。0.6开发线取得同修复准确CI，交接保持可续。

## English

The owner requested Issue #5 on the0.5 line with0.5.1 delivery. Implement native wind recovery, read-only power-impact preview and independently prepared normal rebuilding, and synchronize the shared fix to0.6. The Ascension gameplay goal is paused. [Issue #5](https://github.com/Arcueid77/Spherewright/issues/5)

Maintenance starts at formalv0.5.0 sourceb574c616346c4e087b433de3633e23fb12075add with DSP0.10.35.29151 and the assembly hash above. A shared fix commit reaches0.6;0.5.1 has a separate version commit. Preview-only preparation reports power impact/readiness. Executable preparation binds player/endpoint/full topology. One ordinary Native removal verifies exact refund/inc, entity/component disappearance, surviving world data and expected network membership. Rebuilding uses a fresh ordinary build.

Verify legacy defaults, request mapping, serialization, topology/hash changes and unrelated-network preservation. Build the actual29151 Plugin and paired embedded documentation. Compare detached Native OnNodeRemoving against isolated/chain/bridge/star/ring/multiple-network and deterministic random graphs, retaining its separate evidence. After exact-source CI and coherent Plugin/MCP qualification, validate through MCP in the latest protected owned save, reusing existing/recovered wind items and recording every actual debit/placement. Verify original-action idempotency, reused IDs and preserved unknowns. Normal save/complete stopped protection/cold continuation must preserve turbine/network/original-result evidence. Then create and verify the manual/Thunderstore pair, installation/SDK/runtime and release records, while retaining the synchronized0.6 source and continuation handoff.
