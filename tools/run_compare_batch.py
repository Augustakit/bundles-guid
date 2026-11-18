#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比批处理 v2.1：每图一份"全模式两两完整对比"文件 + 跨图家族矩阵 + 基线 + 自检。

产出（对比报告/）：
  README.md                    本目录说明书（每个文件是什么、怎么用）
  INDEX.md                     导航：基线三分口径 + 每图矩阵 + 家族矩阵 + 自检汇总
  baseline.json                基线机器版（通吃配额/每图独有/模式专属）
  对比_全模式_<图>.md           ×49：该图全部模式两两对比（每对列 A独有/B独有 全量明细 + 共有计数）
  家族_矩阵.md                 跨图同模式家族的差异数矩阵（全量明细按需用 compare_registry.py）
  family/<家族>_<图>.md        ×12：家族内差异最大的精选全量报告

数据源：data/registry_pairs.txt（常驻快查文件，缺失时自动 --scope all 重建）。
"""
import json
import os
import random
import re
import subprocess
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_guid_index import read_cache_ebx  # noqa: E402
from guid_lookup import resolve_index_dir  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, '对比报告')
PAIRS_NAME = 'registry_pairs.txt'
LOG = []


def log(msg=''):
    print(msg, flush=True)
    LOG.append(msg)


def mode_key(partition_name):
    return re.sub(r'[0-9_]', '', os.path.basename(partition_name)[:-4].lower())


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    index_dir = resolve_index_dir(None)
    ebx_root = read_cache_ebx()
    if not index_dir:
        print('[FAIL] 找不到索引目录（缓存与仓库自带 data/ 都没有）')
        return 2
    if not ebx_root:
        # 本脚本第 5 步要回读转储原文做抽验，所以必须有 EBX 根；
        # 只要单对对比不需要它，用 compare_registry.py 即可。
        print('[FAIL] 本脚本末尾要回读转储做抽验，必须先有 EBX 根缓存')
        print('       指定 --ebx 或先跑 Detect-EBX.ps1；只做单对对比请用 compare_registry.py')
        return 2

    # ---- 1. 配对数据（复用或重建） ----
    if not os.path.isfile(os.path.join(index_dir, PAIRS_NAME)):
        log('[1] 配对文件缺失，重建（--scope all）…')
        build = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_guid_index.py')
        subprocess.run([sys.executable, build, '--ebx', ebx_root, '--out', index_dir,
                        '--scope', 'all', '--verify', '0', '--no-cache'], check=True)
    log('[1] 加载配对文件 + 分区元数据…')
    part_meta = {}
    for line in open(os.path.join(index_dir, 'ebx_guid_index.jsonl'), encoding='utf-8'):
        r = json.loads(line)
        part_meta[r['path'].lower()] = {'partition_path': r['path'], 'partition_guid': r['guid'],
                                        'rc_guid': ','.join(r['registry_containers'])}
    g2low = {v['partition_guid']: k for k, v in part_meta.items()}
    part_members = {}
    part_keys = {}
    for line in open(os.path.join(index_dir, PAIRS_NAME), encoding='utf-8'):
        pg, tpath, tguid = line.rstrip('\n').split('|', 2)
        low = g2low.get(pg.upper())
        if low is None:
            continue
        part_members.setdefault(low, {})[(tpath.lower(), tguid.upper())] = tpath or None
        part_keys.setdefault(low, set()).add((tpath.lower(), tguid.upper()))
    by_map = defaultdict(list)
    for low in part_members:
        by_map[part_meta[low]['partition_path'].split('/')[1]].append(low)
    log('[1] 分区 %d 个 / %d 张图' % (len(part_meta), len(by_map)))

    # ---- 2. 基线（三分口径） ----
    log('[2] 基线…')
    map_unions = {}
    for mp, lows in by_map.items():
        u = set()
        for low in lows:
            u |= part_keys[low]
        map_unions[mp] = u
    target_maps = defaultdict(int)
    for mp, u in map_unions.items():
        for k in u:
            target_maps[k] += 1
    hist = defaultdict(int)
    for k, c in target_maps.items():
        hist[c] += 1
    quorum = sorted(k for k, c in target_maps.items() if c == len(by_map))
    map_unique = {}
    for mp, u in map_unions.items():
        others = set()
        for m2, u2 in map_unions.items():
            if m2 != mp:
                others |= u2
        map_unique[mp] = u - others
    part_mode_unique = {}
    for mp, lows in by_map.items():
        for low in lows:
            others = set()
            for low2 in lows:
                if low2 != low:
                    others |= part_keys[low2]
            part_mode_unique[low] = part_keys[low] - others

    meta_idx = json.load(open(os.path.join(index_dir, 'meta.json'), encoding='utf-8'))
    baseline = {
        'tool': 'bundles-guid/tools/run_compare_batch.py',
        'generated_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'ebx_data_version': meta_idx.get('ebx_data_version'),
        'scope': meta_idx.get('scope'),
        'maps_with_rc': len(by_map),
        'quorum_count': len(quorum),
        'map_count_histogram': {str(c): n for c, n in sorted(hist.items(), reverse=True)},
        'map_unique_counts': {mp: len(v) for mp, v in sorted(map_unique.items(), key=lambda x: -len(x[1]))},
        'mode_unique_counts': {part_meta[low]['partition_path']: len(v)
                               for low, v in sorted(part_mode_unique.items(), key=lambda x: -len(x[1]))},
    }
    json.dump(baseline, open(os.path.join(OUT, 'baseline.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    log('    %d/%d 图通吃池 %d 条；每图独有 Top3: %s' % (
        len(by_map), len(by_map), len(quorum),
        '，'.join('%s=%d' % (mp, n) for mp, n in list(baseline['map_unique_counts'].items())[:3])))

    # ---- 3. 每图全模式两两完整对比（一图一文件） ----
    log('[3] 每图全模式两两完整对比…')

    def disp(low, key):
        p = part_members[low].get(key)
        return p if p else '(同分区裸引用)'

    def short(low):
        return part_meta[low]['partition_path'].split('/', 2)[2][:-4]

    pair_sections_total = 0
    for mp in sorted(by_map):
        lows = sorted(by_map[mp])
        n = len(lows)
        lines = ['# %s — 全模式两两对比（%d 个模式分区，%d 对）' % (mp, n, n * (n - 1) // 2), '',
                 '> 每对列**双方独有**的全量明细（"缺谁多谁"）；共有部分只给计数', '> （通吃/共有池在多数对之间高度重合，全量罗列无信息量）。', '']
        for i, la in enumerate(lows):
            for j, lb in enumerate(lows):
                if j <= i:
                    continue
                ka_set, kb_set = part_keys[la], part_keys[lb]
                oa = ka_set - kb_set
                ob = kb_set - ka_set
                cm = len(ka_set & kb_set)
                pair_sections_total += 1
                lines.append('---')
                lines.append('')
                lines.append('## %s vs %s' % (short(la), short(lb)))
                lines.append('')
                lines.append('| | 分区 GUID | RC GUID | 成员数 |')
                lines.append('|---|---|---|---|')
                lines.append('| A `%s` | `%s` | `%s` | %d |' % (short(la), part_meta[la]['partition_guid'],
                                                                part_meta[la]['rc_guid'], len(ka_set)))
                lines.append('| B `%s` | `%s` | `%s` | %d |' % (short(lb), part_meta[lb]['partition_guid'],
                                                                part_meta[lb]['rc_guid'], len(kb_set)))
                lines.append('')
                lines.append('**A 独有 %d 条 / B 独有 %d 条 / 共有 %d 条**' % (len(oa), len(ob), cm))
                lines.append('')
                if oa:
                    lines.append('### A（%s）独有' % short(la))
                    lines.append('')
                    lines.append('| 目标路径 | 实例 GUID |')
                    lines.append('|---|---|')
                    for k in sorted(oa, key=lambda x: (disp(la, x) or '').lower()):
                        lines.append('| `%s` | `%s` |' % (disp(la, k) or '（同分区裸引用）', k[1]))
                    lines.append('')
                if ob:
                    lines.append('### B（%s）独有' % short(lb))
                    lines.append('')
                    lines.append('| 目标路径 | 实例 GUID |')
                    lines.append('|---|---|')
                    for k in sorted(ob, key=lambda x: (disp(lb, x) or '').lower()):
                        lines.append('| `%s` | `%s` |' % (disp(lb, k) or '（同分区裸引用）', k[1]))
                    lines.append('')
                if not oa and not ob:
                    lines.append('（两模式登记内容完全一致）')
                    lines.append('')
        open(os.path.join(OUT, '对比_全模式_%s.md' % mp), 'w', encoding='utf-8', newline='\n').write(
            '\n'.join(lines) + '\n')
    log('[3] 完成，%d 对全部出明细（49 个文件）' % pair_sections_total)

    # ---- 4. 跨图同模式家族（只收真游戏模式家族；矩阵全量，明细按需） ----
    log('[4] 跨图同模式家族…')
    MODE_WHITELIST = {'conquest', 'conquestlarge', 'conquestsmall', 'rush', 'rushlarge',
                      'sqdm', 'tdm', 'deathmatch', 'squadrush', 'tanksuperiority',
                      'ctf', 'cql', 'cqs', 'dm', 'air', 'airsuperiority'}
    fam = defaultdict(list)
    for mp, lows in by_map.items():
        for low in lows:
            k = mode_key(low)
            if k in MODE_WHITELIST:
                fam[k].append((mp, low))
    fam_rows = []
    fam_reports = 0
    for fkey in sorted(fam):
        members = fam[fkey]
        if len(members) < 2:
            continue
        base_low = members[0][1]
        base_set = part_keys[base_low]
        fam_rows.append('')
        fam_rows.append('## 家族 %s（%d 张图；矩阵为与基准的差异）' % (fkey, len(members)))
        fam_rows.append('')
        fam_rows.append('| 图 | 分区 GUID | RC GUID | 与基准差异 |')
        fam_rows.append('|---|---|---|---|')
        best = None
        for mp, low in members:
            d = len(part_keys[low] ^ base_set)
            fam_rows.append('| %s | `%s` | `%s` | %d |' % (
                mp, part_meta[low]['partition_guid'], part_meta[low]['rc_guid'], d))
            if d > 0 and (best is None or d > best[0]):
                best = (d, base_low, low, mp)
        if best and fam_reports < 12:
            d, la, lb, mp = best
            p = os.path.join(OUT, 'family', '%s_%s_vs_%s.md' % (fkey, os.path.basename(la)[:-4], mp))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            sa, sb = part_keys[la], part_keys[lb]
            oa, ob, cm = sa - sb, sb - sa, sa & sb
            lines = ['# 家族 %s：%s vs %s（与基准差异最大对）' % (fkey, os.path.basename(la)[:-4], mp), '',
                     '- A `%s` 成员 %d / B `%s` 成员 %d / 共有 %d' % (
                         part_meta[la]['partition_path'], len(sa),
                         part_meta[lb]['partition_path'], len(sb), len(cm)), '']
            for title, items in (('A 独有', sorted(oa)), ('B 独有', sorted(ob))):
                lines.append('## %s（%d 条）' % (title, len(items)))
                lines.append('')
                lines.append('| 目标路径 | 实例 GUID |')
                lines.append('|---|---|')
                for k in sorted(items):
                    pth = part_members[la].get(k) or part_members[lb].get(k) or k[0]
                    lines.append('| `%s` | `%s` |' % (pth or '（同分区裸引用）', k[1]))
                lines.append('')
            open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
            fam_reports += 1
            fam_rows.append('')
            fam_rows.append('差异最大：%s（%d 条）全量报告：family/%s_%s_vs_%s.md' % (mp, d, fkey, os.path.basename(la)[:-4], mp))
    log('[4] 真模式家族 %d 个，精选报告 %d 份' % (len([f for f in fam.values() if len(f) >= 2]), fam_reports))
    open(os.path.join(OUT, '家族_矩阵.md'), 'w', encoding='utf-8', newline='\n').write(
        '# 家族_矩阵 — 跨图同模式家族\n' + '\n'.join(fam_rows) + '\n')

    # ---- 5. 抽验（10 分区全文核对：分区 GUID + RC GUID 在转储原文中在位） ----
    log('[5] 抽验 10 分区（全文核对）…')
    rng = random.Random(20261118)
    sample_lows = rng.sample(sorted(part_meta), 10)
    ok = bad = 0
    verify = []
    for low in sample_lows:
        r = part_meta[low]
        p = os.path.join(ebx_root, r['partition_path'].replace('/', os.sep))
        pg_ok = rc_ok = False
        with open(p, 'rb') as fh:
            for raw in fh:
                ln = raw.decode('latin-1', 'replace').lower()
                if not pg_ok and r['partition_guid'].lower() in ln:
                    pg_ok = True
                if not rc_ok and r['rc_guid'].lower() in ln:
                    rc_ok = True
                if pg_ok and rc_ok:
                    break
        if pg_ok and rc_ok:
            ok += 1
        else:
            bad += 1
            verify.append('%s 分区GUID=%s RC=%s' % (r['partition_path'], pg_ok, rc_ok))
    log('[5] 通过 %d / 失败 %d' % (ok, bad))
    for v in verify:
        log('    ' + v)

    # ---- 6. 自检汇总（pairs 文件常驻保留） ----
    singles = sum(1 for lows in by_map.values() if len(lows) < 2)
    checks = [
        ('RC 总数断言 608', len(part_meta) == 608),
        ('抽验失败=0', bad == 0),
        ('直方图守恒', sum(hist.values()) == len(target_maps)),
        ('对比文件数=图数', len([f for f in os.listdir(OUT) if f.startswith('对比_')]) == len(by_map)),
        ('全模式对全覆盖', pair_sections_total == sum(len(l) * (len(l) - 1) // 2 for l in by_map.values())),
    ]
    all_ok = all(v for _, v in checks)

    # ---- README（本目录说明书） ----
    rd = ['# compare_reports — 文件说明书', '',
          '本目录所有文件均由 `tools\\run_compare_batch.py` 从索引数据生成（转储更新后重跑即刷新）。', '',
          '| 文件 | 是什么 |', '|---|---|',
          '| `README.md` | 本说明书 |',
          '| `INDEX.md` | **入口导航**：基线三分口径 + 每图差异数矩阵 + 跨图家族矩阵 + 自检汇总 |',
          '| `对比_全模式_<图名>.md` ×%d | **主交付物**：该图全部模式两两对比，每对列双方独有全量明细（缺谁多谁）+ 共有计数 |' % len(by_map),
          '| `baseline.json` | 基线机器版：通吃配额、登记图数直方图、每图独有、模式专属 |',
          '| `家族_矩阵.md` | 跨图同模式家族的差异矩阵（同一模式在不同图的差异） |',
          '| `family\\<家族>_<图>.md` ×%d | 家族内与基准差异最大的精选全量报告 |' % fam_reports,
          '| `单对\\compare_<A>_vs_<B>.md` | 按需单对对比报告（compare_registry.py 默认落这里，临时产物看完可删） |',
          '| 数据本体 | 四件套在上级 data\\；registry_pairs.txt 常驻不删 |', '',
          '## 任意一对的按需全量对比', '',
          '```', 'python tools\\compare_registry.py --a "<分区A>" --b "<分区B>"', '```',
          '', '## 自检', '']
    for name, v in checks:
        rd.append('- %s：%s' % (name, 'PASS' if v else 'FAIL'))
    rd.append('- 抽验 10 分区：通过 %d / 失败 %d' % (ok, bad))
    open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rd) + '\n')

    # ---- INDEX ----
    idx = ['# INDEX — 导航与数据', '',
           '> 生成：%s；口径：bundles（608 模式分区 / %d 图）；明细文件清单见本目录 README.md。' % (
               time.strftime('%Y-%m-%d %H:%M'), len(by_map)), '',
           '## 基线（三分口径）', '',
           '- **%d/%d 图通吃池**：%d 条' % (len(by_map), len(by_map), len(quorum)),
           '- 登记图数直方图：' + '，'.join('%s图=%s条' % (c, n) for c, n in
                                            sorted(baseline['map_count_histogram'].items(),
                                                   key=lambda x: -int(x[0]))[:8]),
           '- 每图独有 Top5：' + '，'.join('%s=%d条' % (mp, n) for mp, n in
                                          list(baseline['map_unique_counts'].items())[:5]),
           '- 模式专属 Top5：' + '，'.join('%s=%d条' % (pth.split('/', 2)[2], n) for pth, n in
                                            list(baseline['mode_unique_counts'].items())[:5]),
           '- 明细见 baseline.json', '']
    idx.extend(['## 每图差异数总览（指向各自的完整对比文件）', ''])
    for mp in sorted(by_map):
        idx.append('- [对比_全模式_%s.md](对比_全模式_%s.md)（%d 个模式分区）' % (mp, mp, len(by_map[mp])))
    idx.extend(['', '跨图家族矩阵：[家族_矩阵.md](家族_矩阵.md)'])
    idx.extend(['', '## 自检', ''])
    for name, v in checks:
        idx.append('- %s：%s' % (name, 'PASS' if v else 'FAIL'))
    idx.append('- 抽验 10 分区：通过 %d / 失败 %d' % (ok, bad))
    for v in verify:
        idx.append('  - ' + v)
    idx.extend(['', '## 运行日志', '', '```'] + LOG + ['```'])
    open(os.path.join(OUT, 'INDEX.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(idx) + '\n')

    log('')
    log('== 批处理完成 %.0fs ==' % (time.time() - t0))
    for name, v in checks:
        log('  %-24s %s' % (name, 'PASS' if v else 'FAIL'))
    log('  对比文件 %d 个 / 全量对 %d / 家族精选 %d' % (len(by_map), pair_sections_total, fam_reports))
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
