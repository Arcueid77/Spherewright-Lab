# Spherewright 0.6.0 review candidates / 交审候选

## 包体与校验

本地候选来自产品源码 `78274df5e93ca912a2d4b6670f7eb707d3562e94`，版本 `0.6.0`，Windows x64，支持 DSP `0.10.35.29151` 和 BepInEx `5.4.17`。两个压缩包及其 `.sha256` 校验文件保存在本地候选目录。

| 包体 | 字节数 | SHA-256 |
| --- | ---: | --- |
| `Spherewright-0.6.0-win-x64.zip` | 37765705 | `6CA368F5BA0E4BF64D64273B5104F727D34A9F916B850D4287A0B12901F57BB9` |
| `Spherewright-0.6.0-thunderstore.zip` | 33475571 | `11D02381C3DB567230A5E58966099E464338869104E4393B74F09B7F9B1E0403` |

手动包解压、清单与校验值核验通过；MCP 实际启动并报告 76 个工具、1 份资源，包内英文指南与内置资源一致，双语指南及链接检查通过。Thunderstore 包的 14 项布局、版本、来源、校验值、图标及双语指南检查通过；另从包中启动自包含 MCP，核对 76 个工具、1 份资源、内置指南一致和 47 项停机接口形状。两包的四个插件程序集及英文指南逐字节一致；两种 MCP 分别为目录版与单文件版。

手动包另在隔离的模拟目录完成五阶段安装检查：首次安装、同版本保护、明确重装、运行时记录保留及部分安装恢复均有结果，实际包内 MCP 通过探测；没有启动游戏，也没有修改真实安装。Thunderstore 的独立管理器 profile 和网站上传未由这些检查证明。

较早候选的双语包检查发现英文及中文指南有源码相对链接在包内失效，已保留该失败并通过后续指南修正重新生成；上述哈希对应修正后的候选。

## 实机与版本关系

闭壳、日照采样、冷恢复和修复后的正常退出在已安装源码 `e221b263496c6f786f1c42e7b71d38e4312f9b62` 实测，详见[实机验收](../../scenarios/v0.6-ascension/acceptance-2026-11-20.md)。候选 `78274df5` 相对此实装只增加或修改六个说明文件；其中英文指南也是 MCP 内置资源，因此包体的版本标识和内置指南不同，不能将其说成已在游戏中加载过的同一字节。候选源码的[准确 CI](https://github.com/Arcueid77/Spherewright/actions/runs/44729612538)已通过。

这些是本地交审候选，不是 Git 标签、GitHub Release 或 Thunderstore 正式发布。近距施工预算尚未单独实机施工，路线预览仍有 16 米实现范围，接收功率结果仅覆盖声明的日照采样区间。

## English

The local Windows x64 candidates use product source `78274df5e93ca912a2d4b6670f7eb707d3562e94`, version `0.6.0`, DSP `0.10.35.29151` and BepInEx `5.4.17`. The table above records each ZIP's byte count and SHA-256; checksum sidecars are retained locally.

The manual ZIP passed extraction, manifest and checksum checks, bilingual guide/link checks and an actual MCP metadata probe: 76 tools, one resource and packaged/embedded English guide parity. The 14-entry Thunderstore layout passed source, version, checksum, icon and bilingual guide checks. Its extracted single-file MCP separately started and passed the same 76-tool / one-resource guide check plus 47 stopped-game SDK interface cases. The four Plugin assemblies and English guide are byte-identical across the two ZIPs; the MCP layouts differ intentionally.

An isolated five-stage installer test exercised initial installation, same-version protection, explicit reinstall, runtime-record preservation and partial-install recovery, including a real packaged MCP probe. It did not start DSP or alter the real installation. These checks do not establish a separate Mod Manager profile or a website upload. An earlier candidate failed the stricter bilingual package check because navigation-guide links were relative to the source tree; that failure is retained and the candidates above were regenerated after the links were fixed.

Closure, daylight observations, cold recovery and the corrected normal exit were exercised on installed source `e221b263496c6f786f1c42e7b71d38e4312f9b62`; see [live acceptance](../../scenarios/v0.6-ascension/acceptance-2026-11-20.md). Candidate `78274df5` differs from that runtime only in six documentation files. The English playbook is also an embedded MCP resource, so the candidate's version stamp and resource differ; these exact package bytes were not loaded into the game. The candidate's [exact-source CI](https://github.com/Arcueid77/Spherewright/actions/runs/44729612538) passed.

These are local review candidates, not a Git tag, GitHub Release or Thunderstore publication. Measured-reach construction did not receive a separate live build exercise, the walking-route preview retains a 16 m implementation range, and receiver-power results cover only the declared daylight sampling intervals.
