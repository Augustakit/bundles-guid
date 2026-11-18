#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BUNDLES-GUIDE.md 生成器：从 bundles 口径索引数据生成人读的 GUID 链速查表。

输入（同目录上级的索引四件）：ebx_guid_index.jsonl / ebx_bundle_crossref.json
输出：上级目录 BUNDLES-GUIDE.md

表列设计对应 bundles 工作流的官方语义（references/vext/guides/custom-content.md）：
  * ResourceManager:MountSuperBundle('超级包名')      -> 用 superbundle 列
  * LoadBundles 队列注入（hook:Pass(bundles, compartment)）-> 用 bundle 名列
  * RegisterInstanceLoadHandler(Guid(分区), Guid(实例)) -> 用分区 GUID 列 + 实例 GUID
  * 运行期定位 SearchForDataContainer / FindInstanceByGuid -> 用分区 GUID 列
"""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cross = json.load(open(os.path.join(BASE, 'data', 'ebx_bundle_crossref.json'), encoding='utf-8'))
part2bundles = {}
for b in cross['bundles']:
    for p in b['partitions']:
        for sb in b['superbundles']:
            part2bundles.setdefault(p.lower(), {'bundles': [], 'superbundles': []})
            part2bundles[p.lower()]['bundles'].append(b['bundle'])
            part2bundles[p.lower()]['superbundles'].extend(
                s for s in b['superbundles'] if s not in part2bundles[p.lower()]['superbundles'])

rows = []
for line in open(os.path.join(BASE, 'data', 'ebx_guid_index.jsonl'), encoding='utf-8'):
    r = json.loads(line)
    for rc in r['registry_containers']:
        rows.append((r['path'], r['guid'], rc))

by_map = defaultdict(list)
for ppath, pguid, rc in rows:
    mp = ppath.split('/')[1]
    info = part2bundles.get(ppath.lower(), {'bundles': [], 'superbundles': []})
    by_map[mp].append((ppath, pguid, rc, info))

out = []
out.append('# BUNDLES-GUIDE — bundles 工作流 GUID 总结（按图分组）')
out.append('')
out.append('> 数据口径：bundles 口径索引（608 个带 RegistryContainer 的模式分区，实测全部在 Levels/），')
out.append('> 与官方 bundles.md 路径同构匹配。★ = 实战用例（VT 模组 AirSuperiority 注入链）。')
out.append('> 本文件由 tools/gen_bundles_guide.py 从索引数据生成；转储更新后重跑生成器即可刷新。')
out.append('')
out.append('## 怎么用这些 GUID（官方语义 × 四个场景）')
out.append('')
out.append('| 场景 | 用哪列 | 语义出处 |')
out.append('|---|---|---|')
out.append('| 把内容块带进内存：`ResourceManager:MountSuperBundle(\'超级包名\')`（在 `Level:LoadResources`） | ④ superbundle 名 | custom-content.md：MountSuperBundle 吃**超级包**名（如 `xp3chunks`、`levels/xp3_alborz/xp3_alborz`） |')
out.append('| 往加载队列里塞 bundle：`Hooks:Install(\'ResourceManager:LoadBundles\', 100, …)` 里改 `bundles` 后 `hook:Pass(bundles, compartment)` | ① bundle 名 | custom-content.md：LoadBundles 队列条目是**bundle**名 |')
out.append('| 把某图注册内容并入：`AddRegistry(RegistryContainer(Guid(…)))` | ③ RegistryContainer GUID | 案例 04 / venice-ebx-structure §4（AddRegistry 实战） |')
out.append('| 按实例挂钩：`RegisterInstanceLoadHandler(Guid(分区), Guid(实例), fn)` | ② 分区 GUID + 实例 GUID | custom-content.md / ebx-retrieval.md §2 |')
out.append('| 运行期定位：`SearchForDataContainer` / `FindInstanceByGuid` | ② 分区 GUID | ebx-retrieval.md §2（只能命中已加载分区） |')
out.append('')
out.append('> 生命周期与三种注入时机（换图重放 / LoadResources 挂载 / 注册期自消解）见 lua-patterns.md §13。')
out.append('')
out.append('**两分钟看懂（实战例子就是这条链）**：')
out.append('')
out.append('```')
out.append('MountSuperBundle(\'xp3chunks\') + MountSuperBundle(\'levels/xp3_alborz/xp3_alborz\')   ← ④ 超级包')
out.append('  └─ LoadBundles 注入 \'levels/xp3_alborz/rushlarge0\'                                ← ① bundle')
out.append('       └─ 分区 26997AC4-F3C5-42CF-BBC6-CEC65C881911  (Levels/XP3_Alborz/RushLarge0.txt)  ← ②')
out.append('            └─ RegistryContainer 6C72B9D2-484E-A4D0-94FA-8A8D39357040                  ← ③ AddRegistry 用')
out.append('```')
out.append('')
out.append('> 注意：`xp3chunks` 这类 **chunks 超级包不在本表**——它们没有同名分区，角色是"内容块容器"')
out.append('>（武器/配件数据住里面，靠图包链间接拉起）。')

out.append('')
out.append('## 附注：compartment——注入的内容进哪个抽屉')
out.append('')
out.append('注入/注册的内容不是进一个大池子，而是进**带标签的资源隔间**（`ResourceCompartment` 枚举）。')
out.append('抽屉决定三件事：这些数据**何时加载、何时清空、服务器与客户端各自是否可见**。')
out.append('')
out.append('| 抽屉 | 值 | 装什么（官方原文意译） |')
out.append('|---|---|---|')
out.append('| `Static` | 0 | 启动期加载、关游戏才清的核心数据（共享配置、关卡列表） |')
out.append('| `Frontend` | 1 | UI 数据与资产（菜单流程） |')
out.append('| `LoadingScreen` | 2 | 读图画面数据 |')
out.append('| `Game` | 3 | 某张图的主游戏数据（通常＝主关卡 bundle 全部内容） |')
out.append('| `Dynamic_Synchronized` | 4–104 | 动态分配——模式包数据（服务器+客户端都加载） |')
out.append('| `Dynamic_ClientOnly` | 105–205 | 动态分配——武器包数据（仅客户端加载） |')
out.append('')
out.append('两个实战要点：')
out.append('')
out.append('1. **`AddRegistry` 官方签名是两个参数**：`(registry, compartment)`，生产模组实战就是**显式两参**')
out.append('   （VehicleOptics thermal.lua:1174：`AddRegistry(Registry, ResourceCompartment.ResourceCompartment_Game)`）')
out.append('   ——模式内容一律用 `Game` 抽屉；且 registry 参数需先包成 RegistryContainer：')
out.append('   `RegistryContainer(ResourceManager:SearchForInstanceByGuid(Guid(RC_GUID)))`。')
out.append('2. **`LoadBundles` 回调第二参＝队列当前目标隔间**：官方示例原样透传（`hook:Pass(bundles, compartment)`），')
out.append('   含义是"不改目的地，只改货"——注入的 bundle 跟着队列进它本来的抽屉。')

star = {('Levels/XP3_Alborz/RushLarge0.txt'), ('Levels/XP3_Alborz/ConquestLarge01.txt')}
total = 0
for mp in sorted(by_map):
    lst = sorted(by_map[mp], key=lambda x: x[0])
    total += len(lst)
    out.append('')
    out.append('## %s（%d 个注册表）' % (mp, len(lst)))
    out.append('')
    out.append('| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |')
    out.append('|---|---|---|---|---|')
    for ppath, pguid, rc, info in lst:
        mark = ' ★' if ppath in star else ''
        bl = '、'.join(sorted(info['bundles'])) if info['bundles'] else '—'
        sl = '、'.join(sorted(info['superbundles'])) if info['superbundles'] else '—'
        out.append('| `%s`%s | `%s` | `%s` | %s | %s |' % (ppath.split('/', 2)[2], mark, pguid, rc, bl, sl))

out.append('')
out.append('## 没有注册表的 21 个目录（三分法，AddRegistry 在这些目录无锚点）')
out.append('')
out.append('转储 70 个 Levels 目录里 21 个没有注册表，**不全是被砍图**（文件系统实测订正）：')
out.append('')
out.append('| 类别 | 目录 | 对 bundles 工作流的含义 |')
out.append('|---|---|---|')
out.append('| 真被砍/未完成多人图（4） | MP_Canyon（248 分区）、MP_WhitePeak（522）、MP_BandarDesert 原版版、MP_019 | 有大量分区但无主分区/无注册表——AddRegistry 无锚点，注入需另找锚 |')
out.append('| 资料片资产壳（4） | XP3_LeGrandVal（498）、XP4_Earthquake（511）、XP4_FinancialDistrict（385）、XP4_Parliament（354） | **不是图**：出货图 XP4_FD/XP4_Parl/XP4_Quake/XP4_Rubble 的资产库，关卡本体在本表 49 图内 |')
out.append('| 测试图与桩（13） | Testrange×7、COOP_001/005/008、Shared、SP_003、SP_Interrogation | 测试/桩目录，无注入价值 |')
out.append('')
out.append('完整定性见 FINDINGS.md #2。')

# ---- 附录 B：每图全量 bundle 清单（自官方 bundles.md；找不到源则跳过） ----
def _parse_bundles(md_path):
    """解析 bundles.md：superbundle(##) -> Contained bundles 表行集合。"""
    result = {}
    current = None
    for line in open(md_path, encoding='utf-8', errors='replace'):
        s = line.strip()
        if s.startswith('## ') and not s.startswith('###'):
            current = s[3:].strip().strip('`').strip()
            result.setdefault(current, [])
        elif s.startswith('|') and current and not s.startswith('| ---') and 'Bundle name' not in s:
            cells = [c.strip().strip('`').strip() for c in s.strip('|').split('|')]
            if cells and cells[0] and cells[0] not in result[current]:
                result[current].append(cells[0])
    return result

bundles_md = None
for cand in (os.path.join(os.path.expanduser('~'), '.bundles-guid', 'bundles.md'),
             os.path.join(BASE, 'bundles.md')):
    if os.path.isfile(cand):
        bundles_md = cand
        break

out.append('')
out.append('## 附录 B：每图全量 bundle 清单（自官方 bundles.md）')
out.append('')
if bundles_md:
    bm = _parse_bundles(bundles_md)
    out.append('> 用途：LoadBundles 注入选包 / 判断某包拉起什么。命名解码：`_parent`=区域逻辑层、')
    out.append('> `_art_parent`=美术层、`_gameconfiglight`=轻量配置、`_settings_win32`=图设置、`_ui*`=菜单流程包。')
    n_b = 0
    for mp in sorted(by_map):
        key = 'levels/%s/%s' % (mp.lower(), mp.lower())
        contained = bm.get(key)
        if not contained:
            continue
        n_b += len(contained)
        out.append('')
        out.append('**%s**（superbundle `levels/%s/%s`，%d 个 bundle）' % (mp, mp.lower(), mp.lower(), len(contained)))
        out.append('')
        out.append('、'.join('`%s`' % b for b in sorted(contained)))
    out.append('')
    out.append('> 覆盖 %d 个 bundle；全量表见 VU 官方文档 bundles 页（本工具索引目录缓存一份于 ~/.bundles-guid/bundles.md）。' % n_b)
else:
    out.append('> 跳过：未找到 bundles.md（放 ~/.bundles-guid/bundles.md 或本目录后重跑本生成器）。')

# ---- 资料与出处（与本地技能库的桥） ----
out.append('')
out.append('## 资料与出处（技能桥）')
out.append('')
out.append('| 本表内容 | 出处（本地技能库镜像 = VU 官方文档同名页） |')
out.append('|---|---|')
out.append('| MountSuperBundle / LoadBundles / compartment 官方语义 | `references\\vext\\guides\\custom-content.md` |')
out.append('| compartment 枚举全表 | `references\\vext\\ref\\shared\\type\\resourcecompartment.md` |')
out.append('| AddRegistry 签名 (registry, compartment) | `references\\vext\\ref\\shared\\library\\resourcemanager.md` |')
out.append('| 生命周期三时机与注入时机 | `lua-patterns.md` §13 |')
out.append('| 检索纪律（GUID→文件头、禁止按名猜） | `ebx-retrieval.md` §2 / §C.1 |')
out.append('| AddRegistry 实战（133F6403 注入链） | 案例 04 / venice-ebx-structure §4 |')
out.append('| 数据口径与特例 | 本目录 FINDINGS.md |')

out.append('')
out.append('---')
out.append('注册表合计 %d 个，覆盖 %d 张图。' % (total, len(by_map)))

path = os.path.join(BASE, 'BUNDLES-GUIDE.md')
open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
assert total == 608, 'RC 总数异常: %d' % total
print('BUNDLES-GUIDE.md: %d 行, %d RC, %d 图（断言 608 通过）' % (len(out), total, len(by_map)))
