#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EBX 分区索引查询器（独立工具，只读；索引由同目录 build_guid_index.py 生成）。

四向查询 + 注册表展开 + 抽样核对：
    --guid  <GUID>    GUID -> 分区路径（同时查分区 GUID 和 RegistryContainer GUID；
                        转储存在同 GUID 多文件时全部列出——实测 7 对，MP_BandarDesert/XP3_Desert 共用地形分区）
    --path  <相对路径>  分区路径 -> GUID + RegistryContainer（路径 / 或 \\ 均可，可不带 .txt）
    --map   <地图名>   地图 -> 主分区 + 全部分区 + 注册表容器（含子目录；official_bundles=0
                        表示官方 bundles.md 没有该图的 bundle，多为被砍未出货内容或共享目录）
    --bundle <bundle>  bundle -> 近似同构分区（exact/none，见交叉表 note）
    --registered <GUID> 反查注册表展开：哪些分区/RC 登记了这个实例（"某武器/配件在哪些图可用"）
    --rc-content <值>   按 RC GUID 或分区路径列出其 EntityRegistry 成员（--limit N 截断，默认 30，0=全部）
    --stats           打印索引元信息（版本戳/计数/覆盖率）
    --verify N        从索引抽 N 个分区回读转储核对（默认 0 不做）

公共开关：
    --index-dir <目录>  索引目录（省略依次读 ~/.vu-guid-index/index-path 缓存、仓库自带 data/）
    --ebx <根>          转储根（省略读 ~/.bundles-guid/ebx-path 缓存；--open / --verify / 版本核对用）
    --open              把命中的分区路径拼成绝对路径输出（需要 EBX 根）
    --rc                只看带 RegistryContainer 的分区（配合 --map / --path 前缀过滤）

退出码：命中 0；未命中 1；索引/环境问题 2。
"""
import argparse
import json
import os
import random
import sys

CACHE_FILES = [
    os.path.join(os.path.expanduser('~'), '.vu-guid-index', 'index-path'),
]
EBX_CACHE_CANDIDATES = [
    os.path.join(os.path.expanduser('~'), '.bundles-guid', 'ebx-path'),
]


def read_cache(paths):
    """按顺序找第一个存在的缓存文件读其内容。"""
    for p in paths:
        try:
            with open(p, encoding='utf-8-sig') as f:
                v = f.read().strip()
            if v:
                return v
        except OSError:
            continue
    return None


REPO_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def resolve_index_dir(explicit):
    """索引目录解析优先级：显式参数 > 用户缓存 > 仓库自带的 data/。

    仓库自带的 data/ 随 git 一起发布（EBX 转储是 2013 年的冻结快照），
    所以 clone 下来即使没有缓存文件，也能直接查询，不必先重建索引。
    """
    if explicit:
        return explicit
    cached = read_cache(CACHE_FILES)
    if cached:
        return cached
    if os.path.isfile(os.path.join(REPO_DATA, 'meta.json')):
        return REPO_DATA
    return None


def load_index(index_dir):
    """载入 meta + jsonl，建 guid->[row]（同 GUID 多文件全收）与 path->row 两张表。"""
    meta_p = os.path.join(index_dir, 'meta.json')
    jsonl_p = os.path.join(index_dir, 'ebx_guid_index.jsonl')
    if not os.path.isfile(meta_p) or not os.path.isfile(jsonl_p):
        print('[FAIL] 索引不完整：缺 meta.json / ebx_guid_index.jsonl（%s）' % index_dir)
        print('       先跑: python tools\\build_guid_index.py --out "<目录>"')
        return None
    with open(meta_p, encoding='utf-8') as f:
        meta = json.load(f)
    by_guid, by_path = {}, {}
    with open(jsonl_p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            by_guid.setdefault(r['guid'], []).append(r)
            # 路径键统一小写：Windows 文件系统不区分大小写，查询口径对齐（--path/--map 同理）
            by_path[r['path'].lower()] = r
    return meta, by_guid, by_path


def check_stale(meta, ebx_root):
    """索引版本戳 vs 当前转储版本戳；不一致只警告不拦（索引可重生）。

    解析逻辑复用 build_guid_index.read_data_version（DataVersion.txt 本身是分区，
    首行是 Partition 行，Version/DateTime/BranchId 字段缩进在后面），避免口径漂移。
    """
    if not ebx_root:
        return
    try:
        from build_guid_index import read_data_version
    except ImportError:
        return
    cur = read_data_version(ebx_root)
    if cur and meta.get('ebx_data_version') and cur != meta['ebx_data_version']:
        print('[WARN] 索引过期：索引 %s != 当前转储 %s（重跑 build_guid_index.py 重生）'
              % (meta['ebx_data_version'], cur))


def norm_path(p):
    p = p.replace('\\', '/').strip('/')
    if not p.lower().endswith('.txt'):
        p += '.txt'
    return p


def need_entries_hint():
    """缺 ebx_registry_entries.jsonl 时给出**能照做**的三行提示。

    这个文件 69MB、未随仓库发布；只服务 --registered / --rc-content 两条命令。
    默认口径（bundles）不会产出它，必须显式 --scope all 且本地要有 1.4GB 转储。
    """
    print('[FAIL] 缺 ebx_registry_entries.jsonl（69MB，未随仓库发布；只服务本命令与 --rc-content）')
    print('       需要时本地生成（要 1.4GB EBX 转储，约 7 分钟）：')
    print('       python tools\\build_guid_index.py --out "data" --scope all')


def load_registry(index_dir):
    """懒加载注册表展开文件，建 target_guid->[(分区路径, rc_guid)] 与 rc_guid->entries 两张表。

    文件缺失（旧版索引）返回 ({}, {}, False)，调用方给出重建提示。
    """
    p = os.path.join(index_dir, 'ebx_registry_entries.jsonl')
    if not os.path.isfile(p):
        return {}, {}, False
    by_target, by_rc = {}, {}
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            key = (r['partition_path'], r['rc_guid'])
            for e in r['entries']:
                by_target.setdefault(e['guid'], []).append(key)
            by_rc.setdefault(r['rc_guid'], {'rc_guid': r['rc_guid'], 'partition_path': r['partition_path'],
                                            'entries': r['entries']})
    return by_target, by_rc, True


def show(rows, ebx_root, open_flag, lower=False):
    for r in rows:
        # --path/--map/--bundle 查询的目的往往就是拿分区 GUID，所以三种查询都把它打出来
        # --lower：路径全小写输出（模组代码习惯小写路径时用）
        pth = r['path'].lower() if lower else r['path']
        head = pth + '  guid=' + r['guid']
        if r.get('registry_containers'):
            head += '  RC=' + ','.join(r['registry_containers'])
        print(head)
        if open_flag:
            if not ebx_root:
                print('  [WARN] --open 需要 EBX 根（--ebx 或先跑 Detect-EBX.ps1），跳过')
                ebx_root = None
            else:
                print('  -> %s' % os.path.join(ebx_root, r['path'].replace('/', os.sep)))


def main():
    ap = argparse.ArgumentParser(description='EBX 分区索引查询器（独立工具）')
    ap.add_argument('--guid')
    ap.add_argument('--path')
    ap.add_argument('--map')
    ap.add_argument('--bundle')
    ap.add_argument('--registered')
    ap.add_argument('--rc-content')
    ap.add_argument('--limit', type=int, default=30, metavar='N', help='--rc-content 显示条数上限（0=全部，默认 30）')
    ap.add_argument('--stats', action='store_true')
    ap.add_argument('--verify', type=int, default=0, metavar='N')
    ap.add_argument('--index-dir', default=None,
                    help='索引目录（省略读缓存，再退回仓库自带 data/）')
    ap.add_argument('--ebx', default=None)
    ap.add_argument('--open', action='store_true')
    ap.add_argument('--lower', action='store_true', help='路径全小写输出（模组代码习惯小写路径时用）')
    ap.add_argument('--rc', action='store_true', help='只显示带 RegistryContainer 的分区')
    a = ap.parse_args()

    index_dir = resolve_index_dir(a.index_dir)
    if not index_dir or not os.path.isdir(index_dir):
        print('[FAIL] 找不到索引目录：--index-dir 指定，或先跑 build_guid_index.py')
        print('       （仓库自带的 data/ 缺失时才会走到这里）')
        return 2
    loaded = load_index(index_dir)
    if not loaded:
        return 2
    meta, by_guid, by_path = loaded
    ebx_root = a.ebx or read_cache(EBX_CACHE_CANDIDATES)
    check_stale(meta, ebx_root)

    if a.stats:
        print(json.dumps(meta, ensure_ascii=False, indent=2))
        return 0

    if a.guid:
        g = a.guid.strip().upper()
        rows = by_guid.get(g)
        if rows:
            if len(rows) > 1:
                print('[dup] 该 GUID 在转储里有 %d 个同名分区（转储特性，全部列出）：' % len(rows))
            show(rows, ebx_root, a.open, a.lower)
            return 0
        # 分区 GUID 未命中 -> 查 RegistryContainer GUID
        hits = [row for row in by_path.values() if g in row['registry_containers']]
        if hits:
            print('[rc] %s 是以下分区的 RegistryContainer：' % g)
            show(hits, ebx_root, a.open, a.lower)
            return 0
        print('[MISS] %s 不在索引（分区 GUID 与 RegistryContainer 均未命中）' % g)
        return 1

    if a.path:
        r = by_path.get(norm_path(a.path).lower())
        if r and (not a.rc or r['registry_containers']):
            show([r], ebx_root, a.open, a.lower)
            return 0
        print('[MISS] 索引中无此分区路径: %s' % a.path)
        return 1

    if a.map:
        view_p = os.path.join(index_dir, 'ebx_levels_by_map.json')
        try:
            with open(view_p, encoding='utf-8') as f:
                maps = json.load(f)['maps']
        except (OSError, KeyError, ValueError):
            print('[FAIL] 地图视图缺失或损坏: %s' % view_p)
            return 2
        ent = maps.get(a.map)
        if not ent:
            # 地图名大小写不敏感（Windows 目录口径）
            lk = {k.lower(): v for k, v in maps.items()}
            ent = lk.get(a.map.lower())
        if not ent:
            print('[MISS] 索引中无此地图: %s（可用 --map MP_001 / COOP_002 等目录名）' % a.map)
            return 1
        rows = ent['partitions']
        if a.rc:
            rows = [r for r in rows if r['registry_containers']]
        print('[map] %s：主分区 %s；分区 %d 个（显示 %d）'
              % (a.map, ent['main_partition'] or '无', len(ent['partitions']), len(rows)))
        show(rows, ebx_root, a.open, a.lower)
        return 0

    if a.bundle:
        cross_p = os.path.join(index_dir, 'ebx_bundle_crossref.json')
        try:
            with open(cross_p, encoding='utf-8') as f:
                cross = json.load(f)
        except (OSError, ValueError):
            print('[FAIL] bundle 交叉表缺失或损坏（生成时没找到 bundles.md？）: %s' % cross_p)
            return 2
        want = a.bundle.strip().lower()
        for b in cross['bundles']:
            if b['bundle'].lower() == want:
                print('[bundle] %s（superbundle: %s）-> %s'
                      % (b['bundle'], ','.join(b['superbundles']) or '-', b['match']))
                for pth in b['partitions']:
                    print('  ' + pth)
                if not b['partitions']:
                    print('  （无同构分区；%s）' % cross['note'])
                return 0
        print('[MISS] bundles.md 里没有这个 bundle: %s' % a.bundle)
        return 1

    if a.registered:
        by_target, _by_rc, ok = load_registry(index_dir)
        if not ok:
            need_entries_hint()
            return 2
        g = a.registered.strip().upper()
        hits = by_target.get(g)
        if not hits:
            print('[MISS] 没有任何 RegistryContainer 登记实例 %s' % g)
            return 1
        parts = sorted(set(p for p, _rc in hits))
        rcs = sorted(set(rc for _p, rc in hits))
        print('[registered] 实例 %s 被 %d 个注册表登记，涉及 %d 个分区：' % (g, len(hits), len(parts)))
        for p in parts:
            print('  ' + p)
        if len(rcs) <= 8:
            print('  RC: ' + ', '.join(rcs))
        return 0

    if a.rc_content:
        by_target, by_rc, ok = load_registry(index_dir)
        if not ok:
            need_entries_hint()
            return 2
        want = a.rc_content.strip()
        ent = by_rc.get(want.upper())
        if not ent:
            r = by_path.get(norm_path(want).lower())
            if r and r['registry_containers']:
                ent = by_rc.get(r['registry_containers'][0])
        if not ent:
            print('[MISS] 索引中没有这个 RC 或带 RC 的分区: %s' % want)
            return 1
        entries = ent['entries']
        print('[rc-content] RC %s（分区 %s）：EntityRegistry 成员共 %d 条'
              % (ent['rc_guid'], ent['partition_path'], len(entries)))
        shown = entries if a.limit == 0 else entries[:a.limit]
        for e in shown:
            print('  %s  %s' % (e['guid'], e['path']))
        if a.limit != 0 and len(entries) > a.limit:
            print('  ...（其余 %d 条未显示，--limit 0 看全部）' % (len(entries) - a.limit))
        return 0

    if a.verify > 0:
        ebx = ebx_root
        if not ebx or not os.path.isdir(ebx):
            print('[FAIL] --verify 需要 EBX 根（--ebx 或先跑 Detect-EBX.ps1）')
            return 2
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            from build_guid_index import GUID_RE, RC_RE
        except ImportError:
            print('[FAIL] 找不到 build_guid_index.py（需与本脚本同目录）')
            return 2
        rows = sorted(by_path.values(), key=lambda r: r['path'])
        sample = random.Random(20261117).sample(rows, min(a.verify, len(rows)))
        bad = 0
        for r in sample:
            full = os.path.join(ebx, r['path'].replace('/', os.sep))
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
        return 0 if bad == 0 else 1

    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
