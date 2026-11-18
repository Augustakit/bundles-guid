# REGISTRY-PATHS — 注册表登记路径整理（对比地基）

> 数据：608 个 RegistryContainer 的 EntityRegistry 成员全展开，按**被登记的目标**聚合。
> 用途：后续"图 A vs 图 B / 模式 A vs 模式 B 缺谁多谁"= 两个集合的差集运算，本表即集合本体（机器版 registry_targets.jsonl）。
> 配对总数 690,562；独立目标 39,846 个；登记它们的分区 608 个。

## 分类统计（按目标路径首段；大小写并列是转储原生现象，未归一）

| 首段 | 独立目标数 |
|---|---|
| `Levels` | 29,608 |
| `(同分区裸引用)` | 2,589 |
| `Weapons` | 1,738 |
| `Persistence` | 1,432 |
| `Gameplay` | 1,083 |
| `Characters` | 901 |
| `Vehicles` | 709 |
| `Architecture` | 322 |
| `Objects` | 273 |
| `Props` | 206 |
| `characters` | 172 |
| `XP2` | 118 |
| `xp2` | 115 |
| `XP4` | 104 |
| `XP_Raw` | 96 |
| `UI` | 89 |
| `levels` | 70 |
| `XP5` | 57 |
| `objects` | 55 |
| `XP3` | 23 |
| `Animations` | 19 |
| `xp_raw` | 18 |
| `props` | 11 |
| `gameplay` | 8 |
| `FX` | 8 |
| `architecture` | 8 |
| `vehicles` | 4 |
| `32FEAD73-5BB8-4AF2-B29B-CDE2DAF905CD` | 2 |
| `animations` | 2 |
| `xp3` | 2 |
| `xp5` | 2 |
| `AI` | 1 |
| `Test` | 1 |

## 出场最多的目标 Top 20（几乎所有图都登记的"全图通吃"条目）

| 分区数 | 图数 | 目标路径 |
|---|---|---|
| 370 | 48 | `Weapons/Common/AI_Unlock` |
| 368 | 48 | `Gameplay/XP2/GM_Deploytime` |
| 368 | 48 | `Weapons/Common/AI_Torch` |
| 368 | 48 | `Weapons/Common/NoOptics` |
| 368 | 48 | `Weapons/Common/NoSecondaryAccessory` |
| 366 | 48 | `Weapons/Common/NoCamo` |
| 361 | 48 | `Weapons/AK74M/U_AK74M_TargetPointer` |
| 361 | 48 | `Weapons/Common/NoSecondaryRail` |
| 361 | 48 | `Weapons/M16A4/U_M16A4_TargetPointer` |
| 361 | 48 | `Weapons/M416/U_M416_TargetPointer` |
| 361 | 48 | `Weapons/XP2_SCAR-L/U_SCAR-L_TargetPointer` |
| 361 | 48 | `Weapons/XP2_SteyrAug/U_SteyrAug_Target_Pointer` |
| 360 | 48 | `Weapons/AEK971/U_AEK971_TargetPointer` |
| 360 | 48 | `Weapons/AN94/U_AN94_TargetPointer` |
| 360 | 48 | `Weapons/Gadgets/M320/40mmLowVelocityGrenade` |
| 360 | 48 | `Weapons/Gadgets/M320/40mmLowVelocityGrenade` |
| 360 | 48 | `Weapons/Gadgets/M320/M320` |
| 360 | 48 | `Weapons/Gadgets/M320/M320` |
| 360 | 48 | `Weapons/Gadgets/M320/U_40mm_LVG` |
| 360 | 48 | `Weapons/Gadgets/M320/U_40mm_SHG` |

## 每图登记目标数 Top 15

| 图 | 登记目标数 |
|---|---|
| MP_007 | 5,274 |
| XP1_003 | 4,664 |
| XP1_002 | 4,479 |
| XP5_003 | 4,342 |
| XP3_Valley | 4,327 |
| MP_011 | 4,306 |
| MP_003 | 4,287 |
| XP5_001 | 4,278 |
| XP1_001 | 4,226 |
| XP3_Shield | 4,205 |
| MP_018 | 4,195 |
| XP1_004 | 4,133 |
| MP_Subway | 4,085 |
| MP_017 | 4,074 |
| MP_012 | 4,046 |

## 对比怎么做（下一步的预告）

机器版 `registry_targets.jsonl` 每行含 `maps` 与 `partition_count`，由
`tools\gen_registry_targets.py` 从 `ebx_registry_entries.jsonl` 聚合而成（聚合键是
**(目标路径, 目标GUID)**，不是单独 GUID——12 个 GUID 存在两种路径写法）。做"A 图 vs B 图缺/多"时，
用 `--scope all` 重建成员展开（约 150–210 秒），按分区粒度取两集合差集即可——本表是它的聚合视图。

> 大小写提示：成员路径首段存在大小写并列（`Weapons`/`weapons` 等），做差集前需 casefold 归一，
> 否则同一目标会被当成两个（转储原生现象，非本工具误差）。
