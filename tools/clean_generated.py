#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理可重生产物（只删派生物，绝不碰源码和 git 历史）。

默认清三类"删了没有任何损失"的临时垃圾：
  对比报告/          run_compare_batch.py 的批量对比产出（最多约 242MB，重跑约 2 分钟）
  data/对比样例/     手动留存的对比报告样例（compare_registry.py 1 秒可重建）
  __pycache__/       Python 字节码缓存（下次运行自动重新生成）
  *.pyc              Python 字节码

--data 额外清索引本体（约 84MB；若已生成 69MB 的 ebx_registry_entries.jsonl 则约 154MB）：
  data/*.json / data/*.jsonl / data/*.txt
  ⚠ 这些文件**已经随仓库发布**，删掉等于把仓库的数据移除：
     被 git 跟踪的文件默认**拒绝删除**——要删必须显式加 --force。
     误删想恢复 -> git checkout -- data/          （秒回，不必重建）
     确实要从仓库移除 -> --force，然后 git add -A 并提交（clone 的人将失去索引）
     也可以重建（约 7 分钟，扫 1.4GB 转储）：
       python tools\\build_guid_index.py --out "data" --scope all
       python tools\\gen_registry_targets.py --index-dir "data"

--dry-run 只列出将删除的路径和体积，不动手。

安全边界：只删仓库根目录之内、且不在 .git 里的路径；仓库根本身永不被删。

用法:
    python tools\\clean_generated.py --dry-run     # 先看看要删什么
    python tools\\clean_generated.py               # 清临时产物
    python tools\\clean_generated.py --data        # 连索引一起清（已入库文件会被拒绝）
    python tools\\clean_generated.py --data --force  # 真的要从仓库移除索引才这么用

退出码：全部成功 0；有删除失败 1；拒绝删除已跟踪文件 2。
"""
import argparse
import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(SCRIPT_DIR)
GIT_DIR = os.path.join(REPO, '.git')

# 默认清理的目录（相对仓库根）
TEMP_DIRS = [
    '对比报告',
    os.path.join('data', '对比样例'),
]
# --data 时清理的索引文件后缀
DATA_SUFFIXES = ('.json', '.jsonl', '.txt')


def human(n):
    """字节数转可读。"""
    if n < 1024:
        return '%d B' % n
    for unit in ('KB', 'MB', 'GB'):
        n /= 1024.0
        if n < 1024 or unit == 'GB':
            return '%.1f %s' % (n, unit)
    return '%d B' % n


def path_size(p):
    """目录或文件的体积。"""
    if os.path.isfile(p):
        try:
            return os.path.getsize(p)
        except OSError:
            return 0
    total = 0
    for dirpath, _dirnames, filenames in os.walk(p):
        for name in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, name))
            except OSError:
                pass
    return total


def walk_repo():
    """遍历仓库（跳过 .git），yield (dirpath, dirnames, filenames)。"""
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if os.path.join(dirpath, d) != GIT_DIR]
        yield dirpath, dirnames, filenames


def tracked_paths():
    """返回 git 跟踪的文件（realpath 小写集合）。git 不可用/非仓库时返回 None。"""
    try:
        r = subprocess.run(['git', '-C', REPO, 'ls-files', '-z'],
                           capture_output=True, check=False)
    except OSError:
        return None
    if r.returncode != 0:
        return None
    out = set()
    for raw in r.stdout.split(b'\x00'):
        if not raw:
            continue
        rel = raw.decode('utf-8', errors='replace')
        out.add(os.path.realpath(os.path.join(REPO, rel)).lower())
    return out


def collect(include_data):
    """收集待删路径。全部经 realpath 校验，确保在仓库内且不是 .git。"""
    found = []
    for rel in TEMP_DIRS:
        p = os.path.join(REPO, rel)
        if os.path.isdir(p):
            found.append(p)

    for dirpath, dirnames, filenames in walk_repo():
        for d in list(dirnames):
            if d == '__pycache__':
                found.append(os.path.join(dirpath, d))
                dirnames.remove(d)
        for name in filenames:
            if name.endswith('.pyc'):
                found.append(os.path.join(dirpath, name))

    if include_data:
        data_dir = os.path.join(REPO, 'data')
        if os.path.isdir(data_dir):
            for name in sorted(os.listdir(data_dir)):
                p = os.path.join(data_dir, name)
                if os.path.isfile(p) and name.lower().endswith(DATA_SUFFIXES):
                    found.append(p)

    # 安全过滤 + 去重
    repo_real = os.path.realpath(REPO)
    git_real = os.path.realpath(GIT_DIR)
    out = []
    seen = set()
    for p in found:
        rp = os.path.realpath(p)
        if rp == repo_real or rp == git_real:
            continue
        if not rp.startswith(repo_real + os.sep):
            continue
        if rp.startswith(git_real + os.sep):
            continue
        if rp in seen:
            continue
        seen.add(rp)
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser(description='清理可重生产物（只删派生物，不碰源码）')
    ap.add_argument('--data', action='store_true',
                    help='额外清 data/ 下的索引本体（约 84MB）；其中已入库的文件默认拒绝删除')
    ap.add_argument('--force', action='store_true',
                    help='配合 --data：连 git 已跟踪的索引文件一起删（会让仓库失去数据，慎用）')
    ap.add_argument('--dry-run', action='store_true',
                    help='只列出将删除的路径与体积，不实际删除')
    a = ap.parse_args()

    targets = collect(a.data)
    if not targets:
        print('[clean] 没有可清理的产物，已经是干净的')
        return 0

    # 已入库（git 跟踪）的文件是仓库的数据本体，默认拒绝删除
    tracked = tracked_paths()
    if a.data and tracked is not None:
        protected = [p for p in targets
                     if os.path.realpath(p).lower() in tracked]
        if protected:
            print('[WARN] 下列 %d 个文件已被 git 跟踪，删掉等于把仓库的数据移除：' % len(protected))
            for p in protected:
                print('  %s' % os.path.relpath(p, REPO))
            if not a.force:
                print()
                if a.dry_run:
                    print('  （dry-run 不删任何东西；真跑时这些会被拒绝——要用 --force 才删）')
                else:
                    print('  只想清临时产物     -> 去掉 --data 再跑')
                    print('  误删了想恢复       -> git checkout -- data/')
                    print('  确实要从仓库移除   -> 加 --force，然后 git add -A 并提交')
                    return 2
            else:
                print('  --force：这些文件将被删除')
            print()
        if not a.force:
            targets = [p for p in targets
                       if os.path.realpath(p).lower() not in tracked]

    total = 0
    for p in targets:
        sz = path_size(p)
        total += sz
        print('  %s  (%s)' % (os.path.relpath(p, REPO), human(sz)))
    print('[clean] %d 项，合计 %s' % (len(targets), human(total)))

    if a.dry_run:
        print('[dry-run] 什么都没删。去掉 --dry-run 才真删')
        return 0

    failed = 0
    for p in targets:
        try:
            if os.path.isdir(p):
                shutil.rmtree(p)
            elif os.path.exists(p):
                os.remove(p)
        except OSError as e:
            failed += 1
            print('[WARN] 删除失败 %s (%s)' % (os.path.relpath(p, REPO), e))
    print('[done] 已删除 %d 项%s' % (len(targets) - failed,
                                     '' if not failed else '，失败 %d 项' % failed))
    if a.data:
        print('       索引已删。误删想恢复：git checkout -- data/')
        print('       要重建：python tools\\build_guid_index.py --out "data" --scope all')
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
