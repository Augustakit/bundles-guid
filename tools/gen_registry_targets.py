#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""注册表目标聚合表生成器（只读索引；索引由同目录 build_guid_index.py --scope all 生成）。

把注册表展开 ebx_registry_entries.jsonl 聚合成"某个目标被哪些地图、多少个分区登记"：

    registry_targets.jsonl   每行 {path, guid, map_count, partition_count, maps[]}

聚合键是 (目标路径, 目标GUID)，**不是单独 GUID**——实测 12 个 GUID 存在两种路径写法
（常规名与 `*_nongroupable_autogen` 变体），按 GUID 归并会少 12 条。

maps 取自分区路径的第二段（`Levels/<地图>/...`）；不在这棵树下的分区记为 `(non-level)`。
partition_count 统计的是**不同分区 GUID**（不是不同 RC：同一分区可有多个注册表容器）。

排序：partition_count 降序，同分区数内保持首次出现顺序（Python 稳定排序，不额外排键），
与历史产物逐字节一致——这样重新生成时 git diff 只会显示真实变化。

用法:
    python tools\\gen_registry_targets.py                      # 索引目录取缓存，产物写回同目录
    python tools\\gen_registry_targets.py --index-dir "<目录>"
    python tools\\gen_registry_targets.py --entries "<目录>\\ebx_registry_entries.jsonl" --out "<文件>"

前置：先跑一次
    python tools\\build_guid_index.py --out "<目录>" --scope all
（bundles 口径不产出 ebx_registry_entries.jsonl，本脚本会明确报缺失）

退出码：成功 0；索引/输入缺失 2。
"""
import argparse
import json
import os
import sys

CACHE_FILES = [
    os.path.join(os.path.expanduser('~'), '.vu-guid-index', 'index-path'),
]
REPO_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
ENTRIES_NAME = 'ebx_registry_entries.jsonl'
OUT_NAME = 'registry_targets.jsonl'
NON_LEVEL = '(non-level)'


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


def map_of(partition_path):
    """分区路径 -> 地图名：Levels/<地图>/... 取第二段。"""
    parts = partition_path.split('/')
    if len(parts) >= 2 and parts[0] == 'Levels':
        return parts[1]
    return NON_LEVEL


def build(entries_path):
    """聚合 ebx_registry_entries.jsonl。返回 (rows, 块数, 成员数)。"""
    agg = {}  # 插入有序：(目标路径, 目标GUID) -> {parts:set, maps:set}
    n_blocks = 0
    n_entries = 0
    with open(entries_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            n_blocks += 1
            pp = r['partition_path']
            mp = map_of(pp)
            # 老产物可能没有 partition_guid，退回按路径计数，行为不变（实测 1:1）
            pg = r.get('partition_guid') or pp
            for e in r['entries']:
                n_entries += 1
                k = (e.get('path', ''), e['guid'])
                v = agg.get(k)
                if v is None:
                    v = agg[k] = {'parts': set(), 'maps': set()}
                v['parts'].add(pg)
                v['maps'].add(mp)

    rows = []
    for (pth, tg), v in agg.items():
        maps = sorted(v['maps'])
        rows.append({
            'path': pth,
            'guid': tg,
            'map_count': len(maps),
            'partition_count': len(v['parts']),
            'maps': maps,
        })
    # 稳定排序：只按 (-partition_count, path)，组内保留首次出现顺序
    rows.sort(key=lambda r: (-r['partition_count'], r['path']))
    return rows, n_blocks, n_entries


def main():
    ap = argparse.ArgumentParser(description='注册表目标聚合表生成器（registry_targets.jsonl）')
    ap.add_argument('--index-dir', default=None, help='索引目录（省略读 ~/.vu-guid-index/index-path 缓存）')
    ap.add_argument('--entries', default=None, help='直接指定 ebx_registry_entries.jsonl（覆盖 --index-dir）')
    ap.add_argument('--out', default=None, help='输出文件（省略写 <索引目录>/registry_targets.jsonl）')
    a = ap.parse_args()

    if a.entries:
        entries_path = a.entries
        index_dir = a.index_dir or os.path.dirname(os.path.abspath(entries_path))
    else:
        index_dir = a.index_dir or read_cache(CACHE_FILES)
        if not index_dir and os.path.isfile(os.path.join(REPO_DATA, 'meta.json')):
            index_dir = REPO_DATA  # 仓库自带的 data/
        if not index_dir:
            print('[FAIL] 找不到索引目录：用 --index-dir 指定，或先跑 build_guid_index.py')
            return 2
        entries_path = os.path.join(index_dir, ENTRIES_NAME)

    if not os.path.isfile(entries_path):
        print('[FAIL] 缺 %s（%s）' % (ENTRIES_NAME, os.path.dirname(os.path.abspath(entries_path))))
        print('       它只在 --scope all 口径产出，先跑:')
        print('       python tools\\build_guid_index.py --out "<目录>" --scope all')
        return 2

    out_path = a.out or os.path.join(index_dir, OUT_NAME)

    rows, n_blocks, n_entries = build(entries_path)
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n')

    top = rows[0] if rows else None
    print('[in]  %d 个注册表块 / %d 条成员' % (n_blocks, n_entries))
    print('[out] %d 个目标 -> %s' % (len(rows), os.path.abspath(out_path)))
    if top:
        print('[top] %s（%d 个分区 / %d 张图）'
              % (top['path'] or '<裸GUID>', top['partition_count'], top['map_count']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
