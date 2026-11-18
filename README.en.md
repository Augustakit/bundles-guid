# bundles-guid

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![smoke](https://github.com/Augustakit/bundles-guid/actions/workflows/smoke.yml/badge.svg)](https://github.com/Augustakit/bundles-guid/actions/workflows/smoke.yml)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/deps-stdlib%20only-brightgreen.svg)](#requirements)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#requirements)
[![EBX](https://img.shields.io/badge/EBX-73%2C475%20partitions-informational.svg)](BUNDLES-GUIDE.md)

[中文](README.md) | **English**

A small local lookup tool for the Venice-EBX (Battlefield 3) text dump. **Default scope is the
bundles workflow**: it scans the whole dump but only indexes the GUID chain you actually touch when
mounting bundles — the 608 game-mode partitions that carry a RegistryContainer. One chain reads
*"bundle name → mode partition GUID → RegistryContainer GUID"*.

It solves two everyday annoyances:

1. **GUID → file.** The official repo only ships the bundle list; partition GUIDs otherwise mean
   grepping 1.4 GB. Build the index once, then locate any partition in ~0.3 s.
2. **Bundles workflow cheat sheet.** For injecting bundles, `AddRegistry`, or per-instance hooks,
   every GUID you need is already listed per map in [BUNDLES-GUIDE.md](BUNDLES-GUIDE.md)
   (`--scope all` widens the index to the full dump).

**The dump itself is always the single source of truth** — the index is a derived artifact you can
rebuild at will.

## What's in here

| Path | What it is | For |
|---|---|---|
| `BUNDLES-GUIDE.md` | **Flagship doc**: bundle → partition → RC chains grouped by map, with usage notes | Humans |
| `REGISTRY-PATHS.md` | Aggregated summary of registry target paths (39,846 entries) | Humans |
| `FINDINGS.md` | Known findings and blind spots (7 entries) — worth reading before you trust a result | Humans |
| `对比报告\` | Mode-vs-mode diff output, **generated on demand and never committed** (`tools\run_compare_batch.py`, ~2 min to rebuild) | Humans |
| `data\` | The index, shipped with the repo (~85 MB; usable right after clone) | Programs |
| `tools\` | Eight scripts: index builder, lookup, registry diff, doc generator, batch runner, target aggregator, cleanup, self-check | Both |
| `meta.json` and the other JSON/JL files in `data\` | Version stamp, partition ledger, map view, bundle cross-reference | Programs (humans should read BUNDLES-GUIDE) |
| `registry_targets.jsonl` | Aggregated table of 39,846 registered targets (written by `gen_registry_targets.py`) | Programs |

## Requirements

- Python 3.7+ (standard library only — no pip install)
- **No dump needed to query** — the index ships in `data\`, so a clone works immediately
- The [Venice-EBX text dump](https://github.com/VeniceUnleashed/Venice-EBX) (~1.4 GB) is only
  needed to rebuild the index, resolve `--open` paths, or run `--verify` against the source

## Quick start

```text
:: 0) No build needed — data\ ships with the repo, so a clone can query immediately

:: 1) Look up a GUID (which file in the dump?)
python tools\guid_lookup.py --guid 8F5E0383-52A4-11DF-AC80-BC6EA2597601
::  -> Levels/MP_001/MP_001.txt  guid=8F5E0383-…  RC=EEBC7D5F-…

:: 2) Which partitions does a map have?
python tools\guid_lookup.py --map MP_001 --rc

:: 3) Index metadata (version stamp / scope / counts)
python tools\guid_lookup.py --stats
::   The reverse lookup `--registered` needs the 69 MB registry expansion generated
::   locally first (see "Data files") — it does not work out of the box

:: 4) Rebuild only to refresh or change scope (~7 min)
python tools\build_guid_index.py --ebx "D:\Venice-EBX" --out "data" --scope all --verify 30
```

Index resolution order: `--index-dir`, then the `~/.vu-guid-index/index-path` cache, then the
**bundled `data\`**. A fresh clone needs neither the cache nor any flag.

**Just want the answers?** Open [BUNDLES-GUIDE.md](BUNDLES-GUIDE.md) directly — the per-map
"bundle name → mode partition GUID → RegistryContainer GUID" table (608 registries across 49 maps).
No index required.

## What you can query

| Query | Notes |
|---|---|
| Partition GUID → file | 608 mode partitions in bundles scope (the scan still covers all 73,475 files; only bundle chains are indexed). Duplicate GUIDs are all listed; `--scope all` widens to the full dump |
| RegistryContainer layer | 608 containers (all under `Levels/` in practice); reverse lookup "which partition owns this RC" |
| Registry expansion (EntityRegistry) | Requires an `--scope all` rebuild: 690,562 member rows across 608 RCs. `--registered <instance GUID>` → which maps register it; `--rc-content <RC or partition>` → everything a map registers |
| Map view | Grouped per map: mode partition + RC + `official_bundles` count (0 usually means cut/unshipped content — 21 of 70 maps in practice) |
| Bundle cross-reference | Bundles scope only records bundles that structurally match a mode partition, plus their superbundle; the full list lives in the official `bundles.md` |

Instance-level GUIDs are deliberately **not** indexed — that is the job of a per-partition parser or a
full-text grep. Keeping the index lightweight (hundreds of KB) is the point.

## All commands

| Command | Purpose |
|---|---|
| `build_guid_index.py --out <dir> [--ebx <root>] [--scope bundles\|all] [--verify N]` | Build / rebuild the index. Defaults to bundles scope; `--verify N` samples partitions back against the dump as a self-check |
| `gen_registry_targets.py [--index-dir <dir>]` | Aggregate `registry_targets.jsonl` from `ebx_registry_entries.jsonl` (target → map count / partition count / map list) |
| `clean_generated.py [--data] [--force] [--dry-run]` | Remove regenerable output (`对比报告\`, `data\对比样例\`, `__pycache__`); `--data` also clears the index but **refuses tracked files** unless `--force`; `--dry-run` lists without deleting |
| `selfcheck.py [--json]` | **One-command self-check**: compile, data integrity, lookups, actionable hint on the missing file, clean no-op, doc section parity; exit 0/1, `--json` for machine consumption |
| `guid_lookup.py --guid <GUID>` | GUID → partition path (RegistryContainer GUIDs are resolved automatically; duplicates all listed) |
| `guid_lookup.py --path <relative path>` | Path → GUID + RC (case-insensitive) |
| `guid_lookup.py --map <map name> [--rc]` | Map → mode partition + RC (`official_bundles=0` = no official bundle for that map) |
| `guid_lookup.py --bundle <bundle name>` | Bundle → structurally matching partitions |
| `guid_lookup.py --registered <instance GUID>` | Which maps register this instance (needs the `all` index) |
| `guid_lookup.py --rc-content <RC or partition>` | Everything a map registers (needs the `all` index; `--limit N` truncates) |
| `compare_registry.py --a <partition A> --b <partition B>` | **Registry diff**: A-only / B-only / shared. Missing detail triggers an automatic `--scope all` rebuild (~150–210 s), cleaned up afterwards; `--keep` preserves it. `--stdout` prints without writing a file |
| `guid_lookup.py --stats` | Index metadata + version stamp (warns when the dump is newer) |
| `guid_lookup.py --verify N` | Sample-check the index back against the dump (audit self-test) |
| `guid_lookup.py … --open` | Resolve hits to absolute paths |

All path queries are case-insensitive, matching the Windows filesystem.

**After any change, one command proves the repo is still sound:** `python tools\selfcheck.py` — eight
assertions, one exit code (0/1). CI runs exactly this, and an external reviewer reads the same output
(`--json`).

## Comparing two modes (worked example)

```text
python tools\compare_registry.py --a "Levels/XP3_Alborz/ConquestLarge01.txt" --b "Levels/XP3_Alborz/RushLarge0.txt"
```

Real output: both mode registries hold roughly 3,200 entries — **2,975 shared** (the map-wide
weapons/unlock pool), **301 Conquest-only** (helicopter pilot kit and friends), **212 Rush-only**
(`Gameplay/GameModes/Rush` logic instances and similar). The full three-section table is written as
a Markdown report.

## Data files (shipped with the repo)

The EBX dump is a frozen 2013 snapshot (`Version=1147186; DateTime=2013-02-14`) that has not
changed in over a decade, so the generated index is **committed directly** — a clone can query
immediately, without downloading 1.4 GB and waiting 7 minutes to rebuild.

| File | Size | Contents |
|---|---|---|
| `meta.json` | 469 B | Version stamp, counts, scope |
| `ebx_guid_index.jsonl` | 92 KB | 608 bundle chains |
| `ebx_levels_by_map.json` | 126 KB | Map view |
| `ebx_bundle_crossref.json` | 117 KB | Bundle cross-reference |
| `registry_pairs.txt` | 78 MB | Flat pairs, the data source for `compare_registry.py` |
| `registry_targets.jsonl` | 6.6 MB | Aggregated table of 39,846 targets |

The only file left out is `ebx_registry_entries.jsonl` (69 MB) — it serves just two commands
(`--registered` / `--rc-content`) but would double the repository. Generate it locally if needed
(~7 min):

```text
python tools\build_guid_index.py --out "data" --scope all
```

### Regenerating

```text
python tools\build_guid_index.py --out "data" --scope all      :: ~7 min
python tools\gen_registry_targets.py --index-dir "data"        :: seconds
```

`registry_targets.jsonl` is keyed by **(target path, target GUID)** rather than the GUID alone —
12 GUIDs carry two path spellings (the regular name and its `*_nongroupable_autogen` variant), so
merging by GUID alone would drop 12 rows. Rows are sorted by `partition_count` descending with
first-seen order preserved inside ties, so a re-run yields a diff showing only real changes.

## Cleaning up generated files

After running comparisons or building an index, the tree accumulates files that can always be
regenerated. One command clears them:

```text
python tools\clean_generated.py --dry-run         :: show what would go, delete nothing
python tools\clean_generated.py                   :: clear temporary output
python tools\clean_generated.py --data            :: also clear the data\ index (tracked files are refused)
python tools\clean_generated.py --data --force    :: only if you really want the data out of the repo
```

By default only these are removed (none are committed, deleting them costs nothing):

| Path | What it is | How to get it back |
|---|---|---|
| `对比报告\` | Batch comparison output, up to ~242 MB | `run_compare_batch.py`, ~2 min |
| `data\对比样例\` | Hand-saved comparison reports | `compare_registry.py`, 1 second |
| `__pycache__\`, `*.pyc` | Python bytecode cache | Rebuilt automatically on the next run |

`--data` also clears the index under `data\` (~84 MB). **Those files are shipped with the repo**, so
deleting them removes the repository's data:

- Git-tracked files are **refused by default** — the script lists them and asks you to confirm intent (exit code 2)
- Deleted by accident: `git checkout -- data\` (instant, no rebuild)
- Really want them out of the repo: add `--force`, then `git add -A` and commit — **a clone will no longer have an index**

Or rebuild from scratch (~7 min, scans the 1.4 GB dump):

```text
python tools\build_guid_index.py --out "data" --scope all
python tools\gen_registry_targets.py --index-dir "data"
```

The script only touches paths inside the repository that are not under `.git` — source files and
commit history are never affected.

## Known findings and blind spots

See [FINDINGS.md](FINDINGS.md): duplicated partition GUIDs, the list of cut/unshipped maps, one case
where a file header GUID disagrees with the referencing side, the semantics of bare GUID members, and
more — worth a read before relying on a result.

## Where this sits in the ecosystem

- [VeniceUnleashed/Venice-EBX](https://github.com/VeniceUnleashed/Venice-EBX) — the text dump itself (this tool's data source)
- [VeniceUnleashed/Venice-EBX-JSON](https://github.com/VeniceUnleashed/Venice-EBX-JSON) — the same dump in JSON
  (used here for a full reconciliation: 99.87% GUID-level coverage, all sampled members present)
- wEBX (webx.powback.com) — a browser-based GUID viewer
- This tool fills a different slot: **fast local CLI + RegistryContainer layer + map view + bundle cross-reference**

## Scope and honest limitations

- Bundle cross-referencing is a **path-isomorphism approximation**, not runtime-accurate ownership
- RegistryContainers only collect column-0 instance definitions (indented lines are references — spot-checked)
- EntityRegistry members are a single `path/instanceGUID` slash-joined token; a bare GUID means a
  same-partition reference (verified against the official JSON: 60/60 present in the host partition)
- A static registry entry does not guarantee in-game availability (lazy loading and conditional
  registration are runtime semantics, out of scope here)
- Privacy: index artifacts and scripts store only paths relative to the dump — zero local absolute paths

## LICENSE

[MIT](LICENSE) © 2026 Augustakit

> Battlefield 3 and the Venice-EBX dump belong to EA/DICE and Venice Unleashed respectively. This tool
> only processes a copy of the dump you already own and distributes no game data.
