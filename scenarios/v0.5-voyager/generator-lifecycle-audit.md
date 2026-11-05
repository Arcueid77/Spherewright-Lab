# Exhausted generator lifecycle / 耗尽发电机生命周期

2026-11-06. Current authority, limits and complete boundary remain in [standing authority](../../operations/standing-authority.md) and the [single snapshot](current-status.md). The existing `player-to-generator-fuel` subset remains bounded to1..10 zero-inc real package fuel and normal Native insertion. No new materials or hot-refill authority is added.

The actual observed fusion component has buffered fuel ID/count/inc/heat0, loaded fuel ID1802, loaded energy0, retained productive=true, and capacity/generation0. The first `player-to-storage` attempt was a caller family error; after correcting the direction, the Native refusal was `generator_cold_start_empty_unlit_generator_required`. Neither prepare accepted a fuel action or debited the requested8.

The pinned Native29151 component was replayed in isolation with its actual compiled methods. Consuming the last heat **exactly** subtracts it to0 and returns before clearing `curFuelId`. `EnergyCap_Fuel` then returns0, and the next zero-demand `GenEnergyByFuel` call retains the ID. This reproduces the captured shape without loading a world, modifying saves, advancing game time or editing live fields. Other component/package premises in that isolated replay are explicitly synthetic; it is not live insertion acceptance.

| State | Admission |
| --- | --- |
| New empty generator, no loaded identity/energy/capacity/generation | Existing cold subset |
| Exhausted generator, same selected Native-admitted retained identity, all fuel/heat/capacity/generation0 | Fixed cold subset; retain the identity |
| Different/negative retained identity, nonempty buffer, buffered heat/inc, loaded energy, capacity or generation | Refuse |
| Insertion | Fresh exact binding; normal package debit and `PlanetFactory.InsertInto`; only the four buffered-fuel fields may differ |
| Following burn and power | Observe actual Native simulation separately; no generation/heat is credited by the insertion receipt |
| Save/recovery | Preserve the retained fields and already-paid construction; no old failed action or historical budget is reset |

The product change keeps the empty-unlit Native echo, exact item/count, single original commit and complete unaffected-component comparison. Core replay covers the captured exhausted state plus hot/foreign/nonzero-capacity refusals. MCP echo tests and pinned Native compilation pass; exact CI is linked in the current snapshot. Cold installation and live refill/power/manufacture remain separate required evidence.

中文：已完整核对“新建空机→装料→原生燃烧→恰好耗尽→零负载保留ID→普通补料→保存恢复”的状态模型。根因是把残留ID误当作余热，实际原生程序集隔离回放已复现；不是来源库存不足、接口成功或推测性I/O。修复仅承认同种已被原生接受燃料的空冷态，继续要求真实缓冲/热值/余热/容量/发电均零，并在插入后保持旧加载ID和所有无关字段。保留实际扣料、Native检查、唯一writer、54000返航及全部失败原件；尚不声称新版本实机补料或当地火箭已完成。
