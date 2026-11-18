#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自证：一条命令跑完全部可机械验证的断言。

设计目的（交付契约）：
  项目自己处理、自己证明；外部（CI、审核方、skill）只读**同一份输出**判定
  PASS/FAIL，不必知道内部细节，也不必各自实现一套检查。

用法:
    python tools\\selfcheck.py            # 人类可读
    python tools\\selfcheck.py --json     # 机器可读（供 CI / skill 消费）

退出码：0 = 全通过；1 = 有失败。
"""
import argparse
import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = sys.executable

CHECKS = []


def record(name, ok, detail):
    CHECKS.append({'name': name, 'ok': bool(ok), 'detail': detail})
    return ok


def run(args, env=None, cwd=REPO, timeout=180):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run([PY] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace',
                       env=e, cwd=cwd, timeout=timeout)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def check_compile():
    files = sorted(f for f in os.listdir(HERE) if f.endswith('.py'))
    bad = []
    for f in files:
        try:
            py_compile.compile(os.path.join(HERE, f), doraise=True)
        except py_compile.PyCompileError as e:
            bad.append('%s: %s' % (f, str(e).splitlines()[0]))
    return record('compile', not bad, '%d files%s' % (
        len(files), '' if not bad else '; ' + '; '.join(bad)))


def check_data():
    want = ['meta.json', 'ebx_guid_index.jsonl', 'ebx_levels_by_map.json',
            'ebx_bundle_crossref.json', 'registry_pairs.txt', 'registry_targets.jsonl']
    d = os.path.join(REPO, 'data')
    missing = [f for f in want if not os.path.isfile(os.path.join(d, f))]
    if missing:
        return record('data-present', False, 'missing: ' + ', '.join(missing))
    total = sum(os.path.getsize(os.path.join(d, f)) for f in want)
    return record('data-present', True, '%d files / %.1f MB' % (len(want), total / 1048576.0))


def check_meta():
    p = os.path.join(REPO, 'data', 'meta.json')
    try:
        with open(p, encoding='utf-8') as f:
            m = json.load(f)
    except Exception as e:
        return record('meta-json', False, 'unreadable: %s' % e)
    ok = bool(m.get('ebx_data_version')) and bool(m.get('scope'))
    return record('meta-json', ok, 'scope=%s version=%s' % (
        m.get('scope'), str(m.get('ebx_data_version'))[:38]))


def check_lookup():
    rc, out = run(['tools/guid_lookup.py', '--guid', '8F5E0383-52A4-11DF-AC80-BC6EA2597601'])
    ok = rc == 0 and 'Levels/MP_001/MP_001.txt' in out
    return record('lookup-guid', ok, out.strip().splitlines()[0][:70] if out.strip() else 'no output')


def check_map():
    rc, out = run(['tools/guid_lookup.py', '--map', 'MP_001', '--rc'])
    n = sum(1 for l in out.splitlines() if l.startswith('Levels/'))
    ok = rc == 0 and n >= 5
    return record('map-view', ok, '%d partitions listed' % n)


def check_entries_hint():
    """缺 ebx_registry_entries.jsonl 时，提示必须给出能照做的命令、退出码必须是 2。"""
    tmp = tempfile.mkdtemp(prefix='selfcheck_home_')
    try:
        env = {'HOME': tmp, 'USERPROFILE': tmp}
        rc, out = run(['tools/guid_lookup.py', '--registered',
                       '88F1C300-D6E4-4AB0-CB95-F424ADBA8271'], env=env)
        ok = rc == 2 and '--scope all' in out and 'ebx_registry_entries.jsonl' in out
        return record('entries-hint', ok, 'exit=%d, hint=%s' % (
            rc, 'ok' if '--scope all' in out else 'MISSING --scope all'))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_clean_noop():
    rc, out = run(['tools/clean_generated.py', '--dry-run'])
    ok = rc == 0 and '什么都没删' in out
    return record('clean-dry-run', ok, 'exit=%d' % rc)


def check_docs_parity():
    def heads(p):
        with open(os.path.join(REPO, p), encoding='utf-8') as f:
            return sum(1 for l in f if l.startswith('## '))
    try:
        a, b = heads('README.md'), heads('README.en.md')
    except OSError as e:
        return record('docs-parity', False, 'unreadable: %s' % e)
    return record('docs-parity', a == b, 'zh=%d en=%d sections' % (a, b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true', help='输出 JSON（供 CI / skill 消费）')
    a = ap.parse_args()

    check_compile()
    check_data()
    check_meta()
    check_lookup()
    check_map()
    check_entries_hint()
    check_clean_noop()
    check_docs_parity()

    passed = sum(1 for c in CHECKS if c['ok'])
    total = len(CHECKS)
    ok = passed == total

    if a.json:
        print(json.dumps({'selfcheck': 'PASS' if ok else 'FAIL',
                          'passed': passed, 'total': total,
                          'checks': CHECKS}, ensure_ascii=False, indent=2))
    else:
        for c in CHECKS:
            print('[%s] %-14s %s' % ('PASS' if c['ok'] else 'FAIL', c['name'], c['detail']))
        print('SELFCHECK %s (%d/%d)' % ('PASS' if ok else 'FAIL', passed, total))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
