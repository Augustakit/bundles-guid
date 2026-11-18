#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""注册表对比器：两个模式分区登记内容的差集（秒级——直接读扁平配对文件）。

输出三段式 Markdown（A 独有 / B 独有 / 共有）+ 控制台摘要。
配对文件缺失时自动 --scope all 重建（约 150-210 秒，重建后即秒查）。

用法:
    python tools\\compare_registry.py --a "Levels/XP3_Alborz/ConquestLarge01.txt" --b "Levels/XP3_Alborz/RushLarge0.txt"
口径：目标键 = (路径小写, GUID大写)——成员路径大小写混用是转储原生现象，必须归一后再差集。
退出码：成功 0；参数/环境问题 2。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_guid_index import read_cache_ebx  # noqa: E402
from guid_lookup import resolve_index_dir  # noqa: E402

PAIR_NAME = 'registry_pairs.txt'
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm_path(p):
    p = p.replace('\\', '/').strip('/')
    return p if p.lower().endswith('.txt') else p + '.txt'


def load_pair_buckets(index_dir, guids):
    """流式扫配对文件，只留目标分区的成员。返回 {guid: {(路径小写, GUID大写): 原始路径}}。"""
    want = set(g.upper() for g in guids)
    buckets = {g: {} for g in want}
    with open(os.path.join(index_dir, PAIR_NAME), encoding='utf-8') as f:
        for line in f:
            pg, tpath, tguid = line.rstrip('\n').split('|', 2)
            if pg in want:
                buckets[pg][(tpath.lower(), tguid.upper())] = tpath or None
    return buckets


def main():
    ap = argparse.ArgumentParser(description='注册表对比器（两分区登记内容差集，秒级）')
    ap.add_argument('--a', required=True, help='分区 A（相对路径，大小写不敏感）')
    ap.add_argument('--b', required=True, help='分区 B')
    ap.add_argument('--out', default=None, help='报告输出路径（默认 compare_<A>_<B>.md）')
    ap.add_argument('--limit', type=int, default=15, metavar='N', help='控制台每段预览条数（默认 15）')
    ap.add_argument('--lower', action='store_true', help='报告/预览的路径全小写输出（模组代码习惯小写路径时用）')
    ap.add_argument('--stdout', action='store_true', help='全量打到控制台、不写报告文件（临时看一眼用）')
    ap.add_argument('--index-dir', default=None)
    ap.add_argument('--ebx', default=None)
    a = ap.parse_args()

    index_dir = resolve_index_dir(a.index_dir)
    if not index_dir or not os.path.isdir(index_dir):
        print('[FAIL] 找不到索引目录：先跑 build_guid_index.py')
        return 2
    by_path = {}
    with open(os.path.join(index_dir, 'ebx_guid_index.jsonl'), encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            by_path[r['path'].lower()] = r

    ka, kb = norm_path(a.a).lower(), norm_path(a.b).lower()
    ra, rb = by_path.get(ka), by_path.get(kb)
    if not ra:
        print('[FAIL] 分区 A 不在索引（bundles 口径只含带 RC 的模式分区）: %s' % a.a)
        return 1
    if not rb:
        print('[FAIL] 分区 B 不在索引: %s' % a.b)
        return 1
    if ka == kb:
        print('[FAIL] 两个分区是同一个')
        return 2

    # 配对文件缺失 -> 自动 --scope all 重建（产出 registry_pairs.txt）
    if not os.path.isfile(os.path.join(index_dir, PAIR_NAME)):
        ebx_root = a.ebx or read_cache_ebx()
        if not ebx_root:
            print('[FAIL] 配对文件缺失且无法自动重建（找不到 EBX 根缓存）——用 --ebx')
            return 2
        print('[rebuild] 配对文件缺失，自动重建（--scope all，约 150-210 秒）…')
        build = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_guid_index.py')
        subprocess.run([sys.executable, build, '--ebx', ebx_root, '--out', index_dir,
                        '--scope', 'all', '--verify', '0', '--no-cache'], check=True)

    buckets = load_pair_buckets(index_dir, [ra['guid'], rb['guid']])
    set_a, set_b = set(buckets[ra['guid']]), set(buckets[rb['guid']])
    only_a, only_b, common = set_a - set_b, set_b - set_a, set_a & set_b

    def disp(bucket, key):
        p = bucket.get(key)
        return p if p else '(同分区裸引用)'

    rc_a = ','.join(ra['registry_containers'])
    rc_b = ','.join(rb['registry_containers'])
    print()
    print('== 对比摘要 ==')
    print('A: %s (分区 %s / RC %s)  成员 %d 条' % (ra['path'], ra['guid'], rc_a, len(set_a)))
    print('B: %s (分区 %s / RC %s)  成员 %d 条' % (rb['path'], rb['guid'], rc_b, len(set_b)))
    print('A 独有 %d | B 独有 %d | 共有 %d' % (len(only_a), len(only_b), len(common)))
    for tag, bucket, items in (('A 独有预览', buckets[ra['guid']], sorted(only_a)),
                               ('B 独有预览', buckets[rb['guid']], sorted(only_b))):
        print('-- %s --' % tag)
        for k in sorted(items, key=lambda x: (disp(bucket, x) or '').lower())[:a.limit]:
            pp = disp(bucket, k) or '(同分区裸引用)'
            pp = pp.lower() if a.lower else pp
            print('    %s  <%s>' % (pp, k[1]))
        if len(items) > a.limit:
            print('    …（其余 %d 条见报告文件）' % (len(items) - a.limit))

    if min(len(set_a), len(set_b)) < 10:
        import re as _re
        mk = lambda p: re.sub(r'[0-9_]', '', os.path.basename(p)[:-4].lower())
        fam = mk(ra['path'])
        cnt = defaultdict(int)
        with open(os.path.join(index_dir, PAIR_NAME), encoding='utf-8') as f:
            for line in f:
                cnt[line.split('|', 1)[0]] += 1
        g2p = {r['guid']: r['path'] for r in by_path.values()}
        alts = sorted(((cnt[g], g2p[g]) for g in cnt if mk(g2p[g]) == fam and cnt[g] >= 50), reverse=True)[:3]
        print('[HINT] 一侧是残桩注册表（<10 条，EntityRegistry 可能为 *nullArray*，见 FINDINGS #8）')
        for c, pth in alts:
            print('       可比对象建议: %s（%d 条成员）' % (pth, c))

    default_dir = os.path.join(BASE, '对比报告', '单对')
    os.makedirs(default_dir, exist_ok=True)
    out_path = a.out or os.path.join(default_dir, 'compare_%s_vs_%s.md' % (
        os.path.basename(ra['path'])[:-4], os.path.basename(rb['path'])[:-4]))
    lines = ['# 注册表对比：%(a)s vs %(b)s' % {'a': ra['path'], 'b': rb['path']}, '',
             '- A 分区 `%s`（GUID `%s`，RC `%s`），成员 %d 条' % (ra['path'], ra['guid'], rc_a, len(set_a)),
             '- B 分区 `%s`（GUID `%s`，RC `%s`），成员 %d 条' % (rb['path'], rb['guid'], rc_b, len(set_b)),
             '- A 独有 **%d** 条 / B 独有 **%d** 条 / 共有 **%d** 条' % (len(only_a), len(only_b), len(common)),
             '', '> 目标键已 casefold 归一（成员路径大小写混用是转储原生现象）。', '']
    for title, items in (('A 独有（%d 条）' % len(only_a), sorted(only_a)),
                         ('B 独有（%d 条）' % len(only_b), sorted(only_b)),
                         ('共有（%d 条）' % len(common), sorted(common))):
        lines.append('## %s' % title)
        lines.append('')
        lines.append('| 目标路径 | 实例 GUID |')
        lines.append('|---|---|')
        for k in sorted(items, key=lambda x: x[0]):
            pp = k[0] or '（同分区裸引用）'
            pp = pp.lower() if a.lower else pp
            lines.append('| `%s` | `%s` |' % (pp, k[1]))
        lines.append('')
    if a.stdout:
        print()
        print('\n'.join(lines))
        print()
        print('[stdout 模式：未写任何文件]')
        return 0
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('[report] %s' % os.path.abspath(out_path))
    print('        （临时产物，看完可删；同一对随时 1 秒重生成）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
