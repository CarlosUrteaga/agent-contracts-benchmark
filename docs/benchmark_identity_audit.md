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

## Same experiment across model conditions

The benchmark is designed to evaluate the **same 21 scenarios under the same rules** across different LLMs. Model profiles are execution conditions, and new models may require additional entries in `approved_agent_configurations` so pre-execution fingerprint checks admit them. Commit `9ec0b1ff` deliberately split the contract hash to allow this without redefining the benchmark.

A direct comparison of `49770f82` with `e67da475` shows that all four contract files differ **only** in `approved_agent_configurations` and the derived `contract_fingerprint`. Each list grew from 2 to 26 entries. Their normalized semantic content is identical in every mode. The 21 scenario files, evaluator, and diagnosis files are byte-identical across those revisions. Therefore the later GPT, Claude, and other model additions explain expected **compatibility-hash drift**, not a changed scenario set or contract methodology. They do not, by themselves, require a new benchmark version or rerun of earlier models.

The separate problem is that the v2 manifest's stored compatibility digest (`ee480a55…`) did not match even the committed contract tree at `9ec0b1ff`. The model-admission change explains why raw bytes drift over time; it does not establish where that particular stored digest came from. The stored semantic digest (`0aed568f…`) is likewise inconsistent with the unchanged semantic content. These are manifest bookkeeping discrepancies, not evidence that adding models changed the experimental rules.

The complete stored values are in the unchanged manifest. `python3 -m tools.enforcement.freeze_manifest --out /tmp/benchmark-manifest-audit.json` produces the complete current values without writing to the freeze path. The generated file's `freeze_commit` and `generated_at` describe this audit run, so compare only `frozen_artifacts`.

## Provenance by commit

| Revision | Evidence |
| --- | --- |
| `ebaa836c` | Pre-freeze methodology commit. The manifest still names this as `freeze_commit`, but **none** of the five v1 artifact hashes stored by the subsequent freeze commit matches this tree. The field is a stale commit reference, not a reproducible frozen snapshot. |
| `49770f82` | `Freeze benchmark v1.0 (#6)`. Its v1 manifest's `scenarios_hash`, `contracts_hash`, `oracle_hash`, `evaluator_hash`, and `diagnose_f1_hash` all match the artifacts in this commit. This is the committed v1.0 snapshot to use when reconstructing the original freeze. |
| `1e893e6a` | `Formalize oracle catalog and validation`. It expands `scenario_catalog.json` from 12 to 630 lines, changes `docs/oracle_spec.md`, and changes the oracle digest from `ccfa17d1…` to `cc904937…`. The new catalog declares `benchmark-v1.1`. The scenario and evaluator files did not change, so the hash change alone does not prove a different scoring behavior. Nevertheless, `docs/benchmark_freeze_statement.md` explicitly classifies oracle artifact changes as requiring a new version and a full rerun if adopted as an official release. |
| `9ec0b1ff` | `Separate freeze identity from contract compatibility`. This is the intentional adjustment that permits additional model fingerprints without changing the benchmark methodology. It introduces v2 hash fields without changing the contracts or oracle in that commit. Recomputing its committed tree with the generator introduced in the same commit gives semantic `9e8ee81c…`, compatibility `e8a3a985…`, and oracle `cc904937…`; the v2 manifest instead stores `0aed568f…`, `ee480a55…`, and `ccfa17d1…`. Thus all three discrepancies already existed when v2 was committed. The exact source of the two stored contract digests is not established by the committed history. |
| `e67da475` | Current audited `main`. Contract semantic digest is still `9e8ee81c…`, the same as at `ebaa836c` and `49770f82`. Post-freeze model admissions changed only approved configuration lists and derived fingerprints, reaching compatibility digest `8a1e42aa…`; the oracle remains `cc904937…`. |

The contract semantic digest was constant across every contract-changing commit from `ebaa836c` through `e67da475` under the current generator. None of those committed trees produced either stored v2 contract digest. This establishes a manifest conversion discrepancy, but it does not establish whether the values came from an uncommitted working tree or another calculation. Do not infer a source without further evidence.

## Classification for new runs

The present checkout is a **post-freeze working revision** of the same 21-scenario experimental design. Adding models did not redefine that design. It is not byte-identical to the frozen `benchmark-v1.0` artifact set because the oracle specification and catalog were formalized later, and the manifest contains stale or unexplained values. This is an artifact-identity qualification, not a claim that the scientific question or measured rules necessarily changed. An execution manifest copying `benchmark-v1.0` does not by itself resolve this qualification. `validate_execution_manifest.py` compares campaign metadata derived from the stored manifest; it does not compare the frozen artifact digests against the checkout.

The `84/84` mock parity result from the vogtcon integration tests runner behavior on this working revision. It does not establish historical freeze identity. Before claiming exact frozen-artifact identity for an official replicated campaign, choose and review one of these separate paths:

1. Reconstruct `benchmark-v1.0` from `49770f82` in an isolated checkout, retaining its v1 manifest and original oracle; or
2. Release the current oracle as a new benchmark revision, with a reviewed manifest whose recorded hashes match the committed artifacts, then rerun the full experiment as required by the freeze policy.

A version increment would identify a new artifact set under the existing freeze policy; it need not mean changing the experiment's research question or scenarios. The current oracle's `benchmark-v1.1` string is evidence of intended evolution, not proof that a complete v1.1 release and rerun happened. This audit does not choose or enact a release. Any pilot run before that decision should be labeled exploratory and pinned to its benchmark commit, contract digest, oracle digest, model profile, and vogtcon version.

## Disposition for the 26-campaign publication

This investigation is closed as a **documented provenance discrepancy**; it does not rewrite the historical manifest. The 26 closed campaigns use the same 21 scenario files, evaluator, diagnosis rules, and normalized contract semantics across model conditions. The later model fingerprints change operational compatibility metadata and do not require a new benchmark version or rerun by themselves. The campaigns predate the `vogtcon` runner integration and must be attributed to the historical runner.

For a report of these existing results, use `benchmark-v1.0` as the **label recorded in their execution manifests**, identify the actual campaign artifacts and repository revision separately, and cite this audit. Do not claim that the current checkout or the v2 manifest is byte-identical to the original freeze. The original frozen artifact snapshot is recoverable at `49770f82`; the two stored v2 contract digests have no matching committed contract tree under the generator; and the oracle digest identifies the pre-formalization oracle.

The oracle formalization preserved the scenario and evaluator files, so an altered scoring outcome has not been demonstrated by these hashes. The written freeze policy nevertheless treats changes to oracle documentation and catalog as requiring a new benchmark version and full rerun for an **official new release**. This audit records that policy boundary explicitly. It does not silently grant an exception, declare a completed v1.1 release, or require rerunning campaigns solely because new LLMs were admitted.

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
