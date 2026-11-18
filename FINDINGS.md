# FINDINGS — 已知发现与盲区

> **定位**：本表收录工具开发过程中的侦查结论（一次性 forensic 发现，不随索引重生变化），
> 供使用者在已知边界内使用。数据本体在索引五件套里；开发账本在本地 rounds\（不入库）。
> 本表是工具侧的侦查档案；每条结论都标注了证据等级，使用前值得一读。

| # | 特例 | 数字 | 定性与口径 | 状态 |
|---|---|---|---|---|
| 1 | 重复分区 GUID | 7 对 14 文件 | `MP_BandarDesert`↔`XP3_Desert` 地形/背景分区 GUID 相同（DLC 复用原版资产）；`--guid` 双路径全列 | 已验证（双源） |
| 2 | 无注册表目录 | 21/70 | 官方 bundles.md 无任何 bundle 的 Levels 目录，**三分法**（订正，原"全是被砍图"定性有误）：①真被砍/未完成多人图 4 张（MP_Canyon 248 分区、MP_WhitePeak 522、MP_BandarDesert 原版版、MP_019）②**资料片资产壳 4 个**（XP3_LeGrandVal 498、XP4_Earthquake 511、XP4_FinancialDistrict 385、XP4_Parliament 354——出货图 XP4_FD/XP4_Parl/XP4_Quake/XP4_Rubble 的资产库，关卡本体在 49 图表内）③测试图与桩 13 个（Testrange×7、COOP_001/005/008 桩、Shared、SP_003/SP_Interrogation 桩） | 已验证（文件系统实测） |
| 3 | 官方 JSON 不收录 | 98 条 (0.13%) | autogen/贴图/mesh/FX 类分区 JSON 版没有；文本转储覆盖更全（GUID 级 99.87% 收敛） | 已验证（全量对账） |
| 4 | GUID 分歧（已知盲区） | 1 例 | `railtarget_figure_rtl`：文本头=FE06218F，官方 JSON 与文本自家注册表引用=32FEAD73 → 文本头孤立；按文件头定位则 32FEAD73 反查不中 | 已验证（三证据） |
| 5 | 裸 GUID 成员 | 2,589 条 | EntityRegistry 成员无路径=同分区引用；官方 JSON 抽验 60/60 在宿主 Instances | 已验证（双源） |
| 6 | member 行格式 | 全库 69 万条 | `路径/实例GUID` 斜杠直连**一个 token**（非空格分隔）；按空格写解析器会抓 0 条 | 已验证 |
| 7 | EntityRegistry 字段 | 608 RC | RC 实例体字段名 `EntityRegistry::array`；VExt 类型页 registrycontainer.md **未列此字段**（"类型页没有≠转储没有"又一例） | 已验证 |
| 8 | 残桩注册表 | ≥1 例 | DLC 图存在**空注册表残桩**：`Levels/XP3_Alborz/RUSH.txt` 仅 4KB、`EntityRegistry *nullArray*`（0 成员），该图真正的 Rush 内容在 `RushLarge0.txt`（3,187 成员）。跨图同模式对比前先看成员数量级，撞上残桩用 compare 工具的可比对象建议 | 已验证（文件+10/10 抽验） |

## 维护说明

- 数据不上表：69 万成员/608 RC/7 万分区的活数据永不表格化，查询即表格（`guid_lookup`）。
- 每条发现均经多口径互证（独立实现计数 / 抽样往返 / 官方 JSON 全量对账），证据细节在本地开发账本（不入库）。
