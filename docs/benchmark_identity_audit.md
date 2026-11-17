# Benchmark identity audit (2026-11-17)

This audit explains the three differences between `benchmark/enforcement/benchmark_manifest.json` and the current checkout. It is a provenance record, not a new benchmark release. The manifest and all frozen artifacts remain unchanged.

## What the hashes identify

`tools/enforcement/freeze_manifest.py` hashes each relative path, a newline, its bytes, and another newline. For `contracts_semantics_hash`, it hashes a sorted JSON representation after removing `approved_agent_configurations` and `contract_fingerprint`. The algorithm has not changed since commit `9ec0b1ff` introduced the v2 manifest.

At `e67da475` (the benchmark `main` revision audited here), the comparison is:

| Field | Stored in v2 manifest | Recomputed at `e67da475` | Interpretation |
| --- | --- | --- | --- |
| `scenarios_hash` | `f605406c…` | `f605406c…` | Match |
| `contracts_semantics_hash` | `0aed568f…` | `9e8ee81c…` | The stored value did not match the committed contract tree when v2 was introduced. |
| `contract_compatibility_hash` | `ee480a55…` | `8a1e42aa…` | The stored value did not match the committed contract tree when v2 was introduced; approved configuration lists changed again later. |
| `oracle_hash` | `ccfa17d1…` | `cc904937…` | The stored value identifies the earlier oracle, before its formalization. |
| `evaluator_hash` | `159e3c53…` | `159e3c53…` | Match |
| `diagnose_f1_hash` | `e2c255b5…` | `e2c255b5…` | Match |

The complete stored values are in the unchanged manifest. `python3 -m tools.enforcement.freeze_manifest --out /tmp/benchmark-manifest-audit.json` produces the complete current values without writing to the freeze path. The generated file's `freeze_commit` and `generated_at` describe this audit run, so compare only `frozen_artifacts`.

## Provenance by commit

| Revision | Evidence |
| --- | --- |
| `ebaa836c` | Pre-freeze methodology commit. The manifest still names this as `freeze_commit`, but **none** of the five v1 artifact hashes stored by the subsequent freeze commit matches this tree. The field is a stale commit reference, not a reproducible frozen snapshot. |
| `49770f82` | `Freeze benchmark v1.0 (#6)`. Its v1 manifest's `scenarios_hash`, `contracts_hash`, `oracle_hash`, `evaluator_hash`, and `diagnose_f1_hash` all match the artifacts in this commit. This is the committed v1.0 snapshot to use when reconstructing the original freeze. |
| `1e893e6a` | `Formalize oracle catalog and validation`. It expands `scenario_catalog.json` from 12 to 630 lines, changes `docs/oracle_spec.md`, and changes the oracle digest from `ccfa17d1…` to `cc904937…`. The new catalog declares `benchmark-v1.1`. This is an oracle change under `docs/benchmark_freeze_statement.md`, which calls for a new version and a full rerun if adopted as an official benchmark. |
| `9ec0b1ff` | `Separate freeze identity from contract compatibility`. This commit introduces v2 hash fields without changing the contracts or oracle in that commit. Recomputing its committed tree with the generator introduced in the same commit gives semantic `9e8ee81c…`, compatibility `e8a3a985…`, and oracle `cc904937…`; the v2 manifest instead stores `0aed568f…`, `ee480a55…`, and `ccfa17d1…`. Thus all three discrepancies already existed when v2 was committed. The exact source of the two stored contract digests is not established by the committed history. |
| `e67da475` | Current audited `main`. Contract semantic digest is still `9e8ee81c…`, the same as at `ebaa836c` and `49770f82`. Post-freeze edits to contract files changed approved configuration lists and derived fingerprints, reaching compatibility digest `8a1e42aa…`; the oracle remains `cc904937…`. |

The contract semantic digest was constant across every contract-changing commit from `ebaa836c` through `e67da475` under the current generator. None of those committed trees produced either stored v2 contract digest. This establishes a manifest conversion discrepancy, but it does not establish whether the values came from an uncommitted working tree or another calculation. Do not infer a source without further evidence.

## Classification for new runs

The present checkout is a **post-freeze working revision**, identified by its Git commit and the recomputed artifact digests. It must not be described as an exact run of the frozen `benchmark-v1.0` artifact set merely because the current manifest still says `benchmark-v1.0` or because an execution manifest copies that label. `validate_execution_manifest.py` compares campaign metadata derived from the stored manifest; it does not compare the frozen artifact digests against the checkout.

The `84/84` mock parity result from the vogtcon integration tests runner behavior on this working revision. It does not establish historical freeze identity. Before an official replicated campaign, choose and review one of these separate paths:

1. Reconstruct `benchmark-v1.0` from `49770f82` in an isolated checkout, retaining its v1 manifest and original oracle; or
2. Release the current oracle as a new benchmark revision, with a reviewed manifest whose recorded hashes match the committed artifacts, then rerun the full experiment as required by the freeze policy.

The current oracle's `benchmark-v1.1` string is evidence of intended evolution, not proof that a complete v1.1 release and rerun happened. This audit does not choose or enact a release. Any pilot run before that decision should be labeled exploratory and pinned to its benchmark commit, contract digest, oracle digest, model profile, and vogtcon version.

## Read-only reproduction

From the benchmark repository root:

```sh
python3 -m tools.enforcement.freeze_manifest --out /tmp/benchmark-manifest-audit.json
python3 -m tools.enforcement.validate_oracle
git show 49770f82:benchmark/enforcement/benchmark_manifest.json
git show 9ec0b1ff:benchmark/enforcement/benchmark_manifest.json
git diff 49770f82 1e893e6a -- docs/oracle_spec.md benchmark/enforcement/oracle/scenario_catalog.json
git diff 9ec0b1ff HEAD -- tools/enforcement/freeze_manifest.py tools/enforcement/common.py
```

To reproduce the historical contract digests without editing a checkout, run this from the repository root:

```sh
python3 - <<'PY'
import hashlib
import json
import subprocess
from tools.enforcement.common import normalize_contract_for_semantic_identity

paths = subprocess.check_output(
    ['git', 'ls-tree', '-r', '--name-only', 'HEAD', '--', 'contracts/enforcement'], text=True
).splitlines()
paths = sorted(path for path in paths if path.endswith('.yaml'))
for revision in ('ebaa836c', '49770f82', '9ec0b1ff', 'HEAD'):
    semantic, compatibility = hashlib.sha256(), hashlib.sha256()
    for path in paths:
        raw = subprocess.check_output(['git', 'show', f'{revision}:{path}'])
        compatibility.update(path.encode() + b'\n' + raw + b'\n')
        normalized = normalize_contract_for_semantic_identity(json.loads(raw))
        payload = json.dumps(normalized, sort_keys=True).encode()
        semantic.update(path.encode() + b'\n' + payload + b'\n')
    print(revision, 'semantic', semantic.hexdigest(), 'compatibility', compatibility.hexdigest())
PY
```
