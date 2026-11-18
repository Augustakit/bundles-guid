#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EBX bundles 口径索引生成器（独立工具，不依赖任何技能目录）。

扫 Venice-EBX 转储，产出 bundles 工作流要用的 GUID 数据（写到 --out）：
  meta.json                   版本戳 + 计数 + 口径（单一真相源永远是转储本体，索引可随时重生）
  ebx_guid_index.jsonl        每行一个分区：{path, guid, registry_containers[]}
  ebx_levels_by_map.json      地图级视图：地图 -> 分区列表 + RC + 官方 bundle 计数
  ebx_bundle_crossref.json    bundle <-> 分区交叉（含 superbundle 归属）

--scope all 时额外产出两件（体积大，均为可随时重生的派生物）：
  ebx_registry_entries.jsonl  注册表展开，每行 {partition_path, partition_guid, rc_guid, entries[]}
                              —— guid_lookup.py 的 --registered / --rc-content 数据源
  registry_pairs.txt          扁平配对，一行一对（分区GUID|目标路径|目标GUID）

registry_targets.jsonl 不在此产出：由同目录 gen_registry_targets.py 从
ebx_registry_entries.jsonl 聚合生成（聚合键是 (路径, GUID)，非单独 GUID）。

口径（--scope）：
  bundles（默认）  只收**带 RegistryContainer 的模式分区**——即 bundles 工作流要打交道的
                   "bundle 名 -> 分区 GUID -> RC GUID" 链条；AI/贴图/FX 等无关分区不进数据
  all              全库口径（73,475 分区都收，并额外写出注册表展开 ebx_registry_entries.jsonl
                   与扁平配对 registry_pairs.txt）

分区判定：首行必须形如 `Partition <8-4-4-4-12 GUID>` 才算（本转储实测全部 .txt 均为分区，
含 DataVersion.txt；保留严格判定作为防御，不假设任何 .txt 天然是分区）。RegistryContainer
只收列 0 的实例定义行，缩进的引用行不算（与 EBX 文本转储的实例/引用缩进约定一致）。

用法:
    python tools\\build_guid_index.py --out "<索引输出目录>"
    python tools\\build_guid_index.py --ebx "<Venice-EBX根>" --out "<目录>" [--no-bundles] [--no-cache]
    python tools\\build_guid_index.py --out "<目录>" --verify 40      # 生成后抽样往返核对

--ebx 省略时读 EBX 根缓存 ~/.bundles-guid/ebx-path（兼容读取旧版检索工具的缓存位置）。
bundles.md 来源：--bundles 显式指定 > 脚本同目录 > ~/.bundles-guid/bundles.md；
都找不到则跳过 bundle 交叉表并提示（不影响其余四件套）。
索引目录路径缓存到 ~/.vu-guid-index/index-path，供 guid_lookup.py 默认读取。
隐私约定：产物只存转储内相对路径，不写任何本机绝对路径。
"""
import argparse
import json
import os
import random
import re
import sys
import time

GUID_RE = re.compile(rb'^Partition\s+([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})[ \t\r]*$')
RC_RE = re.compile(rb'^RegistryContainer\s+([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})', re.M)
# EntityRegistry 成员行（缩进）：member(N) 路径/实例GUID —— 实测"路径/GUID"是一个斜杠直连的
# 整 token（如 Weapons/UMP45/UMP45/88F1C300-…），中间无空格；整 token 捕获后在代码里切尾段
MEMBER_RE = re.compile(rb'^\t+member\(\d+\)\s+(\S+)[ \t\r]*$')
GUID_TAIL_RE = re.compile(rb'^([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})$')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLE_CANDIDATES = [
    os.path.join(SCRIPT_DIR, 'bundles.md'),
    os.path.join(os.path.expanduser('~'), '.bundles-guid', 'bundles.md'),
]
CACHE_DIR = os.path.join(os.path.expanduser('~'), '.vu-guid-index')
EBX_CACHE_CANDIDATES = [
    os.path.join(os.path.expanduser('~'), '.bundles-guid', 'ebx-path'),
]


def read_cache_ebx():
    """按候选顺序读 EBX 根缓存；都没有就返回 None（用 --ebx 显式指定）。"""
    for p in EBX_CACHE_CANDIDATES:
        try:
            with open(p, encoding='utf-8-sig') as f:
                v = f.read().strip()
            if v:
                return v
        except OSError:
            continue
    return None


def resolve_bundles_md(explicit):
    """bundles.md 解析顺序：显式参数 > 同目录 > 技能 references（存在才用）。"""
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    for cand in BUNDLE_CANDIDATES:
        if os.path.isfile(cand):
            return cand
    return None


def read_data_version(ebx_root):
    """解析 DataVersion.txt 里 VersionData 实例的字段，拼成版本戳。

    实测格式：该文件本身是个分区（首行 Partition），字段行有缩进：
    `Version <构建号>` / `DateTime <构建日期>` / `BranchId <分支>`。
    产出形如 "Version=…; DateTime=…; BranchId=…"，解析不到返回 None。
    """
    p = os.path.join(ebx_root, 'DataVersion.txt')
    fields = {}
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                s = line.strip()
                for key in ('Version', 'DateTime', 'BranchId'):
                    # 注意 "VersionData ..." 不算：要求 key 后紧跟空白
                    if key not in fields and s.startswith(key + ' '):
                        fields[key] = s[len(key) + 1:].strip()
    except OSError:
        return None
    if not fields:
        return None
    return '; '.join('%s=%s' % (k, fields[k]) for k in ('Version', 'DateTime', 'BranchId') if k in fields)


def extract_registry_entries(body):
    """从分区全文提取每个 RegistryContainer 的 EntityRegistry 成员清单。

    口径：以列 0 行为实例块边界；块内 RC 定义行开启收集，缩进的 member(N) 路径/GUID 行入库，
    遇到下一个列 0 行即结束当前 RC 块。返回 [{rc_guid, entries: [{path, guid}]}]。
    """
    result = []
    cur = None
    for line in body.split(b'\n'):
        if line[:1] in (b' ', b'\t'):
            if cur is not None:
                m = MEMBER_RE.match(line)
                if m:
                    token = m.group(1)
                    gm = GUID_TAIL_RE.match(token)
                    if gm:
                        # 裸 GUID（无路径）= 同分区引用（MP_001 实测 14/2234 条），path 记空串
                        cur['entries'].append({'path': '', 'guid': gm.group(1).decode('ascii').upper()})
                    elif b'/' in token:
                        path_part, _, guid_part = token.rpartition(b'/')
                        gm = GUID_TAIL_RE.match(guid_part)
                        if gm:
                            cur['entries'].append({
                                'path': path_part.decode('latin-1'),
                                'guid': gm.group(1).decode('ascii').upper(),
                            })
            continue
        # 列 0 行 = 下一实例定义，当前 RC 块结束
        if cur is not None:
            result.append(cur)
            cur = None
        m = RC_RE.match(line)
        if m:
            cur = {'rc_guid': m.group(1).decode('ascii').upper(), 'entries': []}
    if cur is not None:
        result.append(cur)
    return result


def scan_dump(ebx_root, collect_members):
    """全库扫描。返回 (rows, reg_rows, total_txt, non_partition)。

    rows:    按 path 排序的 [{path, guid, registry_containers}]，path 用 / 分隔的相对路径。
    reg_rows: 注册表展开（仅 collect_members=True 时收集）：
             [{partition_path, partition_guid, rc_guid, entries}]。
    """
    rows = []
    reg_rows = []
    total_txt = 0
    non_partition = 0
    for dirpath, _dirnames, filenames in os.walk(ebx_root):
        for name in filenames:
            if not name.lower().endswith('.txt'):
                continue
            total_txt += 1
            full = os.path.join(dirpath, name)
            try:
                with open(full, 'rb') as f:
                    head = f.read(160)
                    m = GUID_RE.match(head.split(b'\n', 1)[0] + b'\n')
                    if m:
                        # 分区文件：全文收 RegistryContainer 实例定义（列 0）+ EntityRegistry 展开
                        f.seek(0)
                        body = f.read()
                        rcs = []
                        for rm in RC_RE.finditer(body):
                            g = rm.group(1).decode('ascii').upper()
                            if g not in rcs:
                                rcs.append(g)
                        row = {
                            'path': os.path.relpath(full, ebx_root).replace(os.sep, '/'),
                            'guid': m.group(1).decode('ascii').upper(),
                            'registry_containers': rcs,
                        }
                        rows.append(row)
                        if rcs and collect_members:
                            rel = row['path']
                            for ent in extract_registry_entries(body):
                                reg_rows.append({
                                    'partition_path': rel,
                                    'partition_guid': row['guid'],
                                    'rc_guid': ent['rc_guid'],
                                    'entries': ent['entries'],
                                })
                    else:
                        non_partition += 1
            except OSError as e:
                print('[WARN] 读取失败，跳过: %s (%s)' % (full, e))
            if total_txt % 10000 == 0:
                print('  ... 已扫 %d 个 .txt' % total_txt)
    rows.sort(key=lambda r: r['path'])
    reg_rows.sort(key=lambda r: (r['partition_path'], r['rc_guid']))
    return rows, reg_rows, total_txt, non_partition


def build_levels_view(rows, bundle_names=None):
    """地图级视图：Levels/<地图>/ 下的分区按地图分组；主分区 = Levels/<地图>/<地图>.txt。

    bundle_names 提供时，为每图附 official_bundles（官方 bundles.md 里 levels/<图>/ 下的
    bundle 数）：0 = 官方清单没有该图的 bundle——实测多为被砍未出货内容或共享资源目录（如 SHARED）。
    """
    lv_counts = {}
    if bundle_names:
        for b in bundle_names:
            parts = b.split('/')
            if len(parts) >= 2 and parts[0] == 'levels':
                k = parts[1].lower()
                lv_counts[k] = lv_counts.get(k, 0) + 1
    maps = {}
    for r in rows:
        parts = r['path'].split('/')
        if len(parts) < 2 or parts[0] != 'Levels':
            continue
        mp = parts[1]
        ent = maps.setdefault(mp, {'main_partition': None, 'main_guid': None,
                                   'official_bundles': lv_counts.get(mp.lower(), 0) if bundle_names else None,
                                   'partitions': []})
        if len(parts) == 3 and parts[2] == mp + '.txt':
            ent['main_partition'] = r['path']
            ent['main_guid'] = r['guid']
        ent['partitions'].append(r)
    return {'maps': dict(sorted(maps.items()))}


def parse_bundles_md(md_path):
    """解析 bundles.md：superbundle(##) + Contained bundles 表行 -> {bundle: [superbundle,...]}。

    注意：bundles.md 里 bundle 名一律包在反引号里（如 ## `levels/x/y`），必须剥掉再入库。
    """
    bundle_map = {}
    current = None
    try:
        with open(md_path, encoding='utf-8', errors='replace') as f:
            for line in f:
                s = line.strip()
                if s.startswith('## ') and not s.startswith('###'):
                    current = s[3:].strip().strip('`').strip()
                    bundle_map.setdefault(current, [])
                elif s.startswith('|') and current and not s.startswith('| ---') and 'Bundle name' not in s:
                    cells = [c.strip().strip('`').strip() for c in s.strip('|').split('|')]
                    if cells and cells[0]:
                        lst = bundle_map.setdefault(cells[0], [])
                        if current not in lst:
                            lst.append(current)
    except OSError as e:
        print('[WARN] bundles.md 读取失败，跳过 bundle 交叉: %s' % e)
        return None
    return bundle_map


def build_crossref(rows, bundle_map, source_label):
    """bundle <-> 分区近似交叉：bundle 名 == 相对路径（去 .txt，大小写不敏感）才算 exact。"""
    if bundle_map is None:
        return None
    by_lower = {}
    for r in rows:
        key = r['path'][:-4].lower() if r['path'].lower().endswith('.txt') else r['path'].lower()
        by_lower.setdefault(key, []).append(r['path'])
    bundles = []
    matched = 0
    for name in sorted(bundle_map):
        hits = by_lower.get(name.lower(), [])
        if hits:
            matched += 1
        bundles.append({
            'bundle': name,
            'superbundles': bundle_map[name],
            'partitions': hits,
            'match': 'exact' if hits else 'none',
        })
    total = len(bundles)
    return {
        'note': 'bundle 与分区按路径同构近似匹配（bundle 名 == 分区相对路径去 .txt）；'
                '文本转储不含精确归属，match=none 不代表该 bundle 为空',
        'source': source_label,
        'total_bundles': total,
        'matched': matched,
        'coverage_pct': round(matched * 100.0 / total, 1) if total else 0.0,
        'bundles': bundles,
    }


def verify_sample(rows, ebx_root, n):
    """抽样往返核对：随机抽 n 个分区，重开文件重导 GUID/RC，与索引逐字比对。"""
    sample = random.Random(20261117).sample(rows, min(n, len(rows)))
    bad = 0
    for r in sample:
        full = os.path.join(ebx_root, r['path'].replace('/', os.sep))
        with open(full, 'rb') as f:
            head = f.read(160)
            m = GUID_RE.match(head.split(b'\n', 1)[0] + b'\n')
            f.seek(0)
            body = f.read()
        rcs = []
        for rm in RC_RE.finditer(body):
            g = rm.group(1).decode('ascii').upper()
            if g not in rcs:
                rcs.append(g)
        if not m or m.group(1).decode('ascii').upper() != r['guid'] or rcs != r['registry_containers']:
            bad += 1
            print('  [MISMATCH] %s' % r['path'])
    print('[verify] 抽样 %d / 不一致 %d -> %s' % (len(sample), bad, 'PASS' if bad == 0 else 'FAIL'))
    return bad == 0


def main():
    ap = argparse.ArgumentParser(description='EBX bundles 口径索引生成器（独立工具）')
    ap.add_argument('--ebx', default=None, help='Venice-EBX 根（省略按候选顺序读 EBX 根缓存）')
    ap.add_argument('--out', required=True, help='索引输出目录')
    ap.add_argument('--scope', choices=('bundles', 'all'), default='bundles',
                    help='bundles=只收带 RegistryContainer 的模式分区（默认，bundles 工作流口径）；'
                         'all=全库并展开注册表成员')
    ap.add_argument('--bundles', default=None, help='bundles.md 路径（省略按候选位置自动找；找不到跳过交叉表）')
    ap.add_argument('--no-bundles', action='store_true', help='跳过 bundle 交叉表')
    ap.add_argument('--no-cache', action='store_true', help='不写 ~/.vu-guid-index/index-path 缓存')
    ap.add_argument('--verify', type=int, default=25, metavar='N', help='生成后抽样往返核对的分区数（0 关闭）')
    a = ap.parse_args()

    ebx_root = a.ebx or read_cache_ebx()
    if not ebx_root or not os.path.isdir(ebx_root):
        print('[FAIL] 找不到 EBX 根：用 --ebx 指定，或先跑 Detect-EBX.ps1 建缓存')
        return 2
    print('[ebx] %s' % ebx_root)
    print('[scope] %s' % a.scope)

    t0 = time.time()
    rows, reg_rows, total_txt, non_partition = scan_dump(ebx_root, collect_members=(a.scope == 'all'))
    rc_total_full = sum(len(r['registry_containers']) for r in rows)
    # 双口径互校：分区行 + 非分区文件 必须等于扫描到的 .txt 总数，否则扫描有漏（先互校后过滤）
    if len(rows) + non_partition != total_txt:
        print('[FAIL] 双口径互校失败：分区 %d + 非分区 %d != 总数 %d' % (len(rows), non_partition, total_txt))
        return 1
    scanned_total = len(rows)
    if a.scope == 'bundles':
        # bundles 口径：只留带 RegistryContainer 的模式分区（bundle 链条的主体）
        rows = [r for r in rows if r['registry_containers']]
    rc_total = sum(len(r['registry_containers']) for r in rows)
    entry_total = sum(len(x['entries']) for x in reg_rows)
    print('[scan] .txt 共 %d：扫描到分区 %d；口径 %s 保留 %d 个；RegistryContainer %d 个%s，用时 %.1fs'
          % (total_txt, scanned_total, a.scope, len(rows), rc_total,
             ('，EntityRegistry 成员 %d 条' % entry_total) if a.scope == 'all' else '',
             time.time() - t0))

    # bundle 解析提前：地图视图的 official_bundles 计数依赖它
    bundle_map = None
    bundle_src = None
    if not a.no_bundles:
        md_path = resolve_bundles_md(a.bundles)
        if md_path is None:
            print('[bundle] 未找到 bundles.md（--bundles 可显式指定），跳过交叉表与官方计数')
        else:
            bundle_map = parse_bundles_md(md_path)
            bundle_src = os.path.basename(md_path)

    data_version = read_data_version(ebx_root)
    os.makedirs(a.out, exist_ok=True)

    meta = {
        'tool': 'bundles-guid/tools/build_guid_index.py',
        'generated_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'ebx_data_version': data_version,
        'scope': a.scope,
        'partition_rule': '首行 Partition <GUID> 才算分区；RegistryContainer 只收列 0 实例定义行',
        'total_txt': total_txt,
        'scanned_partition_total': scanned_total,
        'partition_count': len(rows),
        'registry_container_count': rc_total,
    }
    if a.scope == 'all':
        meta['non_partition_txt'] = non_partition
        meta['registry_partition_count'] = len(reg_rows)
        meta['registry_entry_count'] = entry_total
    with open(os.path.join(a.out, 'meta.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write('\n')
    with open(os.path.join(a.out, 'ebx_guid_index.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n')
    with open(os.path.join(a.out, 'ebx_levels_by_map.json'), 'w', encoding='utf-8', newline='\n') as f:
        # 缩进排版（用户要求 VS Code 可直读）；体积约 3 倍换可读性
        json.dump(build_levels_view(rows, set(bundle_map) if bundle_map else None), f,
                  ensure_ascii=False, indent=1)
    if a.scope == 'all':
        # 注册表展开（guid_lookup.py --registered / --rc-content 的数据源；约 69MB）
        with open(os.path.join(a.out, 'ebx_registry_entries.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
            for r in reg_rows:
                f.write(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n')
        print('[registry] %d 个 RC 块 / %d 条成员写入 ebx_registry_entries.jsonl'
              % (len(reg_rows), entry_total))
        # 扁平配对文件（一行一对：分区GUID|目标路径|目标GUID）——查询只 grep 两个分区，秒回
        with open(os.path.join(a.out, 'registry_pairs.txt'), 'w', encoding='utf-8', newline='\n') as f:
            n = 0
            for r in reg_rows:
                pg = r['partition_guid']
                for e in r['entries']:
                    f.write('%s|%s|%s\n' % (pg, e['path'], e['guid']))
                    n += 1
            print('[pairs] %d 对写入 registry_pairs.txt' % n)

    if bundle_map is not None:
        cross = build_crossref(rows, bundle_map, bundle_src)
        if cross and a.scope == 'bundles':
            # bundles 口径：只保留命中保留分区的 bundle 及其 superbundle 归属，none 行不进数据
            cross['bundles'] = [b for b in cross['bundles'] if b['match'] == 'exact']
            cross['total_bundles'] = len(cross['bundles'])
            cross['matched'] = len(cross['bundles'])
            cross['coverage_pct'] = 100.0
            cross['note'] = ('bundles 口径：只收录与带 RC 模式分区同构命中的 bundle 及其 superbundle 归属；'
                             '全量 bundle 清单见官方 bundles.md')
        if cross:
            with open(os.path.join(a.out, 'ebx_bundle_crossref.json'), 'w', encoding='utf-8', newline='\n') as f:
                json.dump(cross, f, ensure_ascii=False, indent=1)
            print('[bundle] 收录 %d 个 bundle（含 superbundle 归属；来源 %s）'
                  % (cross['total_bundles'], cross['source']))

    if a.verify > 0 and not verify_sample(rows, ebx_root, a.verify):
        print('[FAIL] 抽样往返核对未过，索引不可信，禁止交付')
        return 1

    if not a.no_cache:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(os.path.join(CACHE_DIR, 'index-path'), 'w', encoding='utf-8') as f:
            f.write(os.path.abspath(a.out))
    print('[done] 索引写入 %s' % os.path.abspath(a.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
