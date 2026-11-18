# bundles-guid

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![smoke](https://github.com/Augustakit/bundles-guid/actions/workflows/smoke.yml/badge.svg)](https://github.com/Augustakit/bundles-guid/actions/workflows/smoke.yml)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/deps-stdlib%20only-brightgreen.svg)](#前置条件)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#前置条件)
[![EBX](https://img.shields.io/badge/EBX-73%2C475%20partitions-informational.svg)](BUNDLES-GUIDE.md)

**中文** | [English](README.en.md)

Venice-EBX（战地3 / Battlefield 3）文本转储的本地检索小工具。**默认 bundles 口径**：扫全库但只装
bundles 工作流要打交道的 GUID 链——608 个带注册表（RegistryContainer）的模式分区，一条链 =
"bundle 名 → 模式分区 GUID → 注册表 GUID"。解决两件日常琐事：

1. **按 GUID 找文件**：官方只给了 bundle 名单，分区 GUID 全靠整库 grep——本工具一次建索引，之后 0.3 秒定位
2. **bundles 工作流速查**：给某图注入 bundle / AddRegistry / 按实例挂钩，要用的 GUID 全在
   [BUNDLES-GUIDE.md](BUNDLES-GUIDE.md) 按图列好（`--scope all` 可扩全库口径）

**单一真相源永远是转储本体**——索引是可随时重生的派生物。

## 文件总地图（每个东西是什么）

| 路径 | 是什么 | 给谁看 |
|---|---|---|
| `BUNDLES-GUIDE.md` | **旗舰文档**：按图分组的 bundle→分区→RC 链 + 用法附注 | 人 |
| `REGISTRY-PATHS.md` | 注册表登记路径的聚合摘要（39,846 个目标） | 人 |
| `FINDINGS.md` | 已知发现与盲区（7 条） | 人 |
| `对比报告\` | 按需生成的全模式对比产出（**不入库**；`tools\run_compare_batch.py` 跑一次约 2 分钟重建） | 人 |
| `data\` | 已放好的索引（约 85MB，随仓库发布，clone 即可查） | 程序 |
| `tools\` | 八个脚本（建索引/查询/对比/文档生成器/批量对比/目标聚合/清理/自证） | 人+程序 |
| `meta.json` 等 data 内四个 json/jsonl | 版本戳、分区总账、地图视图、bundle 交叉 | 程序（人看用 BUNDLES-GUIDE） |
| `registry_targets.jsonl` | 39,846 个被登记目标的聚合表（由 `gen_registry_targets.py` 生成） | 程序 |

## 前置条件

- Python 3.7+（纯标准库，无需 pip）
- **查询不需要转储**：`data\` 里已经放好索引，clone 下来直接就能查
- 只有这三件事才需要 [Venice-EBX 文本转储](https://github.com/VeniceUnleashed/Venice-EBX)（约 1.4GB）：
  重建索引、`--open` 拼绝对路径、`--verify` 回读核对

## 快速开始

```text
:: 0) 不用建索引——data\ 已随仓库带好，clone 下来直接查

:: 1) 查一个 GUID（转储里哪个文件）
python tools\guid_lookup.py --guid 8F5E0383-52A4-11DF-AC80-BC6EA2597601
::  -> Levels/MP_001/MP_001.txt  guid=8F5E0383-…  RC=EEBC7D5F-…

:: 2) 某张图有哪些模式分区
python tools\guid_lookup.py --map MP_001 --rc

:: 3) 索引元信息（版本戳 / 口径 / 计数）
python tools\guid_lookup.py --stats
::   想反查"哪些图登记了某把枪"（--registered）需先本地生成 69MB 的注册表展开，
::   见「数据文件」一节——那条命令开箱不可用，别在第一步试它

:: 4) 想重建或换口径时才跑（可选，约 7 分钟）
python tools\build_guid_index.py --ebx "D:\Venice-EBX" --out "data" --scope all --verify 30
```

索引目录的解析顺序：`--index-dir` 参数 > `~/.vu-guid-index/index-path` 缓存 > **仓库自带 `data\`**。
所以新 clone 的仓库不需要缓存文件，也不需要任何参数。

**只想看结果？** 直接打开 [BUNDLES-GUIDE.md](BUNDLES-GUIDE.md)——按图分组的
"bundle 名 → 模式分区 GUID → RegistryContainer GUID" 速查表（608 个注册表 / 49 张图），
bundles 工作流要用的 GUID 全在里面，不必先建索引。

## 能查什么

| 查询 | 说明 |
|---|---|
| 分区 GUID → 文件 | bundles 口径 608 个模式分区（扫描仍覆盖全库 73,475 个，只装 bundle 链；`--scope all` 扩全库）；同 GUID 多文件全列 |
| RegistryContainer 层 | 608 个（实测全部在 `Levels/`），支持 GUID 反查"它属于哪个分区" |
| 注册表展开（EntityRegistry） | 需 `--scope all` 重建：608 个 RC 共 690,562 条成员——`--registered <实例GUID>` 反查"哪些图登记了它"；`--rc-content <RC或分区>` 列出某图登记的全部实例 |
| 地图视图 | 按地图分组：模式分区 + RC + `official_bundles` 官方 bundle 计数（=0 多为被砍未出货内容，实测 21/70 图） |
| bundle 交叉 | bundles 口径下只收与模式分区同构命中的 bundle 及其 superbundle 归属；全量清单见官方 bundles.md |

实例（instance）级 GUID 不在索引内——那是逐分区解析工具/全文 grep 的领域，索引刻意保持轻量（百 KB 级）。

## 全部命令

| 命令 | 作用 |
|---|---|
| `build_guid_index.py --out <目录> [--ebx <根>] [--scope bundles\|all] [--verify N]` | 建索引/重生；默认 bundles 口径；`--verify N` 抽样回读转储自证 |
| `gen_registry_targets.py [--index-dir <目录>]` | 从 `ebx_registry_entries.jsonl` 聚合出 `registry_targets.jsonl`（目标 → 地图数/分区数/地图列表） |
| `clean_generated.py [--data] [--force] [--dry-run]` | 清可重生产物（`对比报告\`、`data\对比样例\`、`__pycache__`）；`--data` 连索引一起清，但**已入库文件默认拒绝**，要删须加 `--force`；`--dry-run` 只列不删 |
| `selfcheck.py [--json]` | **一条命令自证**：编译、数据完整、查询可用、缺文件提示可照做、清理空跑、中英文档章节对齐；退出码 0/1，`--json` 输出机器可读结果 |
| `guid_lookup.py --guid <GUID>` | GUID → 分区路径（RegistryContainer GUID 自动反查；重复 GUID 全列） |
| `guid_lookup.py --path <相对路径>` | 路径 → GUID + RC（大小写不敏感） |
| `guid_lookup.py --map <图名> [--rc]` | 地图 → 模式分区 + RC（`official_bundles=0`＝官方清单无此图） |
| `guid_lookup.py --bundle <bundle名>` | bundle → 同构分区 |
| `guid_lookup.py --registered <实例GUID>` | 哪些图的注册表登记了它（需 all 口径索引） |
| `guid_lookup.py --rc-content <RC或分区>` | 某图登记的全部实例（需 all 口径索引；`--limit N` 截断） |
| `compare_registry.py --a <分区A> --b <分区B>` | **两分区登记内容差集**：A 独有 / B 独有 / 共有三段式报告（明细缺失自动 `--scope all` 重建，约 150-210 秒，用完自动删；`--keep` 保留） |
| `guid_lookup.py --stats` | 索引元信息 + 版本戳（转储更新自动告警） |
| `guid_lookup.py --verify N` | 抽样回读转储核对（审计自证） |
| `guid_lookup.py … --open` | 命中结果拼绝对路径 |

路径查询均为大小写不敏感（与 Windows 文件系统口径一致）。

**改完任何东西，跑一条命令自证：** `python tools\selfcheck.py` —— 8 项断言一次跑完，退出码 0/1。CI 跑的就是这一条，外部审核方读的也是同一份输出（`--json`）。

## 对比两个模式（实例）

```text
python tools\compare_registry.py --a "Levels/XP3_Alborz/ConquestLarge01.txt" --b "Levels/XP3_Alborz/RushLarge0.txt"
```

真实结果：两个模式注册表各有约 3,200 条登记，**共有 2,975 条**（全图通吃的武器/解锁池），
**Conquest 独有 301 条**（直升机飞行员装具等——大征服有直升机出生）、**Rush 独有 212 条**
（`Gameplay/GameModes/Rush` 模式逻辑实例等）。完整三段式表格输出到 Markdown 报告。

## 数据文件（已随仓库发布）

EBX 转储是 2013 年的冻结快照（`Version=1147186; DateTime=2013-02-14`），十几年没变过。
所以生成好的索引**直接入库**——clone 下来就能查，不必先下载 1.4GB 转储再等 7 分钟重建。

| 文件 | 大小 | 内容 |
|---|---|---|
| `meta.json` | 469 B | 版本戳 + 计数 + 口径 |
| `ebx_guid_index.jsonl` | 92 KB | 608 条 bundle 链总账 |
| `ebx_levels_by_map.json` | 126 KB | 地图视图 |
| `ebx_bundle_crossref.json` | 117 KB | bundle 交叉 |
| `registry_pairs.txt` | 78 MB | 扁平配对，`compare_registry.py` 的数据源 |
| `registry_targets.jsonl` | 6.6 MB | 39,846 个目标的聚合表 |

唯一没入库的是 `ebx_registry_entries.jsonl`（69 MB）——它只服务 `--registered` / `--rc-content`
两个命令，却要占仓库一半体积。要用就本地生成一次（约 7 分钟）：

```text
python tools\build_guid_index.py --out "data" --scope all
```

### 重新生成

转储更新，或改了脚本想重跑时：

```text
python tools\build_guid_index.py --out "data" --scope all      :: 约 7 分钟
python tools\gen_registry_targets.py --index-dir "data"        :: 数秒
```

`registry_targets.jsonl` 的聚合键是 **(目标路径, 目标GUID)** 而不是单独 GUID——12 个 GUID
存在两种路径写法（常规名与 `*_nongroupable_autogen` 变体），按 GUID 归并会少 12 条；
排序为 `partition_count` 降序、同值内保持首次出现顺序，所以重跑只产生真实 diff。

## 清理临时产物

跑过对比或建过索引后，目录里会攒下一些"删了随时能再生成"的东西。一条命令清掉：

```text
python tools\clean_generated.py --dry-run         :: 先看要删什么（不动手）
python tools\clean_generated.py                   :: 清临时产物
python tools\clean_generated.py --data            :: 连 data\ 索引一起清（已入库文件会被拒绝）
python tools\clean_generated.py --data --force    :: 确实要从仓库移除索引才这么用
```

默认只清这些（都不入库，删了零损失）：

| 路径 | 是什么 | 怎么回来 |
|---|---|---|
| `对比报告\` | 批量对比产出，最多约 242MB | `run_compare_batch.py`，约 2 分钟 |
| `data\对比样例\` | 手动留存的对比报告 | `compare_registry.py`，1 秒 |
| `__pycache__\`、`*.pyc` | Python 字节码缓存 | 下次运行自动重建 |

`--data` 会连 `data\` 下的索引本体一起清（约 84MB）。**但这些文件已经随仓库发布**，删掉等于把仓库的数据移除，所以：

- 被 git 跟踪的文件**默认拒绝删除**，脚本会列出它们并让你确认意图（退出码 2）
- 误删想恢复：`git checkout -- data\`（秒回，不用重建）
- 确实要从仓库移除：加 `--force`，然后 `git add -A` 并提交——**clone 的人就没有索引了**

也可以直接重建，约 7 分钟：

```text
python tools\build_guid_index.py --out "data" --scope all
python tools\gen_registry_targets.py --index-dir "data"
```

脚本只删仓库内、且不在 `.git` 里的路径——源码和提交历史永远不碰。

## 已知发现与盲区

见 [FINDINGS.md](FINDINGS.md)：重复分区 GUID、被砍未出货图清单、一例文件头与引用侧 GUID 分歧、
裸 GUID 成员语义等——使用前值得一读。

## 生态定位

- [VeniceUnleashed/Venice-EBX](https://github.com/VeniceUnleashed/Venice-EBX)：文本转储本体（本工具的数据源）
- [VeniceUnleashed/Venice-EBX-JSON](https://github.com/VeniceUnleashed/Venice-EBX-JSON)：同一转储的 JSON 格式
  （本工具已用它做全量对账：GUID 级覆盖 99.87%、成员抽验全部在位）
- 在线查看器 wEBX（webx.powback.com）：网页端按 GUID 浏览
- 本工具补的是**本地 CLI 秒查 + RegistryContainer 层 + 地图视图 + bundle 交叉**这个组合

## 口径与边界（诚实声明）

- bundle 交叉是**路径同构近似**，非运行时精确归属
- RegistryContainer 只收列 0 实例定义行（缩进行=引用，已抽查实证）
- EntityRegistry 成员为"路径/实例GUID"斜杠直连 token；裸 GUID（无路径）= 同分区引用
  （官方 JSON 抽验 60/60 在宿主分区在位）
- 转储静态登记 ≠ 游戏内全部生效（懒加载/条件注册属运行时语义，不在本工具范围）
- 隐私约定：索引产物与脚本只存转储内相对路径，零本机绝对路径

## LICENSE

[MIT](LICENSE) © 2026 Augustakit

> 战地3 及 Venice-EBX 转储内容版权归 EA/DICE 与 Venice Unleashed 各自所有；本工具仅本地处理
> 用户自有的转储副本，不分发任何游戏数据。
