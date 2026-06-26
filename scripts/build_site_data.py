#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import shutil
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATS = REPO_ROOT / "results/enforcement/statistics/final-nineteen-campaigns.json"
DEFAULT_OUT = REPO_ROOT / "site"
FREEZE_DATE = "2026-06-14"
CANONICAL_CUT_DATE = "2026-06-25"
MODES = ["no_contract", "advisory", "guarded", "strict"]
MODE_DESCRIPTIONS = {
    "no_contract": "No online contract checks; actions execute and are only scored offline.",
    "advisory": "Violations are detected and logged, but actions still execute.",
    "guarded": "Invalid actions are blocked and the agent can replan after denial.",
    "strict": "Blocking violations abort the run and protected side effects commit only on success.",
}
ARTIFACTS = [
    ("benchmark/enforcement/benchmark_manifest.json", "benchmark_manifest.json"),
    ("docs/benchmark_freeze_statement.md", "benchmark_freeze_statement.md"),
    ("docs/calibration_log.md", "calibration_log.md"),
    ("docs/contract_audit_matrix.md", "contract_audit_matrix.md"),
    ("docs/contract_enforcement_benchmark.md", "contract_enforcement_benchmark.md"),
    ("docs/contract_experiment.md", "contract_experiment.md"),
    ("docs/EXECUTIVE_SUMMARY.md", "executive_summary.md"),
    ("docs/execution_plan.md", "execution_plan.md"),
    ("docs/future_platform_roadmap.md", "future_platform_roadmap.md"),
    ("docs/oracle_spec.md", "oracle_spec.md"),
    ("docs/oracle_traceability_matrix.md", "oracle_traceability_matrix.md"),
    ("docs/pilot_calibration_statement.md", "pilot_calibration_statement.md"),
    ("docs/pre_freeze_audit.md", "pre_freeze_audit.md"),
    ("docs/resultados_experimento.md", "results.md"),
    ("docs/scenario_audit_matrix.md", "scenario_audit_matrix.md"),
    ("results/enforcement/statistics/final-nineteen-campaigns.json", "final-nineteen-campaigns.json"),
]
GUARDED_BACKEND_CAMPAIGNS = [
    "campaign-claude-opus-48-r3",
    "campaign-openai-direct-r3",
    "campaign-openai-xhigh-r3",
    "campaign-gpt-oss-120b-r3",
    "campaign-qwen35-397b-r3",
]
OVERHEAD_CAMPAIGNS = [
    "campaign-base-r5",
    "campaign-deepseek-v4-pro-r5",
    "campaign-gpt-oss-120b-r5",
    "campaign-kimi-k26-r3",
    "campaign-kimi-k26-r5",
    "campaign-kimi-k27-code-r3",
    "campaign-kimi-k27-code-r5",
    "campaign-nemotron-3-ultra-r3",
]


def metric_payload(metric: dict[str, Any] | None) -> dict[str, Any]:
    if not metric:
        return {"estimate": None, "ci_95": None, "defined": False}
    return {
        "estimate": metric.get("estimate"),
        "ci_95": metric.get("ci_95"),
        "defined": bool(metric.get("defined")),
    }


def fmt(value: float | int | None, digits: int = 6) -> str:
    if value is None:
        return "NA"
    text = f"{value:.{digits}f}"
    return text.rstrip("0").rstrip(".")


def load_reports(stats_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(stats_path.read_text())
    return payload["campaign_reports"]


def load_campaign_summary(report: dict[str, Any]) -> dict[str, Any]:
    summary_path = REPO_ROOT / report["runs_root"] / "summary.json"
    return json.loads(summary_path.read_text())


def report_index(reports: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {report["campaign_id"]: report for report in reports}


def flatten_reports(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    metrics = [
        "successful_safe_completion_rate",
        "governance_effectiveness",
        "precision",
        "recall",
        "f1",
        "unsafe_side_effect_rate",
        "recovery_rate_after_block",
        "mean_replans_per_run",
        "mean_latency_ms",
        "mean_token_usage",
        "mean_estimated_cost",
        "mean_iterations_per_run",
    ]
    for report in reports:
        for mode in MODES:
            mode_stats = report["per_mode_statistics"][mode]
            row: dict[str, Any] = {
                "campaign_id": report["campaign_id"],
                "provider": report["provider"],
                "model_id": report["model_id"],
                "declared_model_version": report["declared_model_version"],
                "replications": report["replications"],
                "mode": mode,
            }
            for metric in metrics:
                row[metric] = metric_payload(mode_stats.get(metric))
            rows.append(row)
    return rows


def build_headline_metrics(base_r5: dict[str, Any]) -> dict[str, Any]:
    stats = base_r5["per_mode_statistics"]
    guarded = stats["guarded"]
    strict = stats["strict"]
    advisory = stats["advisory"]
    no_contract = stats["no_contract"]
    return {
        "unsafe_side_effect_rate": {
            "no_contract": metric_payload(no_contract["unsafe_side_effect_rate"]),
            "advisory": metric_payload(advisory["unsafe_side_effect_rate"]),
            "guarded": metric_payload(guarded["unsafe_side_effect_rate"]),
            "strict": metric_payload(strict["unsafe_side_effect_rate"]),
        },
        "successful_safe_completion_rate": {
            "guarded": metric_payload(guarded["successful_safe_completion_rate"]),
            "strict": metric_payload(strict["successful_safe_completion_rate"]),
            "delta_guarded_minus_strict": round(
                guarded["successful_safe_completion_rate"]["estimate"]
                - strict["successful_safe_completion_rate"]["estimate"],
                6,
            ),
        },
        "operational_overhead": {
            "mean_latency_ms_delta_guarded_minus_strict": round(
                guarded["mean_latency_ms"]["estimate"] - strict["mean_latency_ms"]["estimate"], 6
            ),
            "mean_token_usage_delta_guarded_minus_strict": round(
                guarded["mean_token_usage"]["estimate"] - strict["mean_token_usage"]["estimate"], 6
            ),
            "mean_iterations_delta_guarded_minus_strict": round(
                guarded["mean_iterations_per_run"]["estimate"] - strict["mean_iterations_per_run"]["estimate"],
                6,
            ),
        },
        "recovery_rate_after_block": metric_payload(guarded["recovery_rate_after_block"]),
    }


def build_site_data(stats_path: Path) -> dict[str, Any]:
    raw = json.loads(stats_path.read_text())
    reports = raw["campaign_reports"]
    report_by_id = report_index(reports)
    base_r5 = report_by_id["campaign-base-r5"]
    data = {
        "benchmark_version": base_r5["benchmark_version"],
        "freeze_date": FREEZE_DATE,
        "canonical_cut_date": CANONICAL_CUT_DATE,
        "generated_at": raw["generated_at"],
        "analysis_stage": raw["analysis_stage"],
        "bootstrap_schema_version": raw["bootstrap_schema_version"],
        "bootstrap_samples": raw["bootstrap_samples"],
        "campaign_count": len(reports),
        "modes": [
            {"id": mode, "description": MODE_DESCRIPTIONS[mode]}
            for mode in MODES
        ],
        "headline_metrics": build_headline_metrics(base_r5),
        "campaign_rows": flatten_reports(reports),
        "base_r5_table": {
            mode: {
                "unsafe_side_effect_rate": metric_payload(
                    base_r5["per_mode_statistics"][mode]["unsafe_side_effect_rate"]
                ),
                "governance_effectiveness": metric_payload(
                    base_r5["per_mode_statistics"][mode]["governance_effectiveness"]
                ),
                "successful_safe_completion_rate": metric_payload(
                    base_r5["per_mode_statistics"][mode]["successful_safe_completion_rate"]
                ),
                "precision": metric_payload(base_r5["per_mode_statistics"][mode]["precision"]),
                "recall": metric_payload(base_r5["per_mode_statistics"][mode]["recall"]),
                "f1": metric_payload(base_r5["per_mode_statistics"][mode]["f1"]),
            }
            for mode in MODES
        },
        "guarded_backend_rows": [],
        "overhead_rows": [],
        "artifacts": [],
    }
    for campaign_id in GUARDED_BACKEND_CAMPAIGNS:
        report = report_by_id[campaign_id]
        guarded = report["per_mode_statistics"]["guarded"]
        summary = load_campaign_summary(report)
        guarded_summary = summary["per_mode"]["guarded"]
        data["guarded_backend_rows"].append(
            {
                "campaign_id": campaign_id,
                "successful_safe_completion_rate": metric_payload(
                    guarded["successful_safe_completion_rate"]
                ),
                "unsafe_action_opportunity_rate": {
                    "estimate": guarded_summary.get("unsafe_action_opportunity_rate"),
                    "ci_95": None,
                    "defined": guarded_summary.get("unsafe_action_opportunity_rate") is not None,
                },
                "blocked_unsafe_actions": {
                    "estimate": guarded_summary.get("blocked_unsafe_actions"),
                    "ci_95": None,
                    "defined": guarded_summary.get("blocked_unsafe_actions") is not None,
                },
                "recall": metric_payload(guarded["recall"]),
                "f1": metric_payload(guarded["f1"]),
            }
        )
    for campaign_id in OVERHEAD_CAMPAIGNS:
        report = report_by_id[campaign_id]
        guarded = report["per_mode_statistics"]["guarded"]
        strict = report["per_mode_statistics"]["strict"]
        data["overhead_rows"].append(
            {
                "campaign_id": campaign_id,
                "guarded_mean_latency_ms": metric_payload(guarded["mean_latency_ms"]),
                "strict_mean_latency_ms": metric_payload(strict["mean_latency_ms"]),
                "guarded_mean_token_usage": metric_payload(guarded["mean_token_usage"]),
                "strict_mean_token_usage": metric_payload(strict["mean_token_usage"]),
                "guarded_mean_iterations_per_run": metric_payload(guarded["mean_iterations_per_run"]),
                "strict_mean_iterations_per_run": metric_payload(strict["mean_iterations_per_run"]),
                "successful_safe_completion_rate_delta": round(
                    guarded["successful_safe_completion_rate"]["estimate"]
                    - strict["successful_safe_completion_rate"]["estimate"],
                    6,
                ),
            }
        )
    return data


def write_json(data: dict[str, Any], out_dir: Path) -> None:
    path = out_dir / "src/data/canonical_results.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def copy_public_artifacts(out_dir: Path) -> list[dict[str, str]]:
    artifact_root = out_dir / "public/assets/artifacts"
    artifact_root.mkdir(parents=True, exist_ok=True)
    copied: list[dict[str, str]] = []
    for source, target_name in ARTIFACTS:
        source_path = REPO_ROOT / source
        target_path = artifact_root / target_name
        shutil.copy2(source_path, target_path)
        copied.append(
            {
                "label": target_name,
                "source": source,
                "site_path": f"assets/artifacts/{target_name}",
            }
        )
    return copied


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_markdown_fragments(data: dict[str, Any], out_dir: Path) -> None:
    include_root = out_dir / "_generated/legacy_markdown"
    include_root.mkdir(parents=True, exist_ok=True)

    headline = data["headline_metrics"]
    guarded_success = headline["successful_safe_completion_rate"]["guarded"]["estimate"]
    strict_success = headline["successful_safe_completion_rate"]["strict"]["estimate"]
    safe_delta = headline["successful_safe_completion_rate"]["delta_guarded_minus_strict"]
    latency_delta = headline["operational_overhead"]["mean_latency_ms_delta_guarded_minus_strict"]
    token_delta = headline["operational_overhead"]["mean_token_usage_delta_guarded_minus_strict"]
    campaign_count = data["campaign_count"]
    overview = f"""
<div class="metric-grid">
  <div class="metric-card">
    <span class="metric-label">Benchmark freeze</span>
    <strong>{data["benchmark_version"]}</strong>
    <span class="metric-subtle">Frozen on {data["freeze_date"]}</span>
  </div>
  <div class="metric-card">
    <span class="metric-label">Canonical cut</span>
    <strong>{campaign_count} campaigns</strong>
    <span class="metric-subtle">Closed on {data["canonical_cut_date"]}</span>
  </div>
  <div class="metric-card">
    <span class="metric-label">Safety-utility lead</span>
    <strong>{fmt(safe_delta)} uplift</strong>
    <span class="metric-subtle">`guarded - strict` successful safe completion on `campaign-base-r5`</span>
  </div>
  <div class="metric-card">
    <span class="metric-label">Operational cost</span>
    <strong>{fmt(latency_delta, 3)} ms</strong>
    <span class="metric-subtle">Latency delta with +{fmt(token_delta, 3)} mean tokens</span>
  </div>
</div>

The benchmark asks whether Agent Contracts plus an Agent Governor can govern a tool-using LLM agent during execution under a frozen scenario set and oracle.

On the base five-replication campaign, `guarded` reaches `successful_safe_completion_rate = {fmt(guarded_success)}` versus `{fmt(strict_success)}` for `strict`, while both blocking modes keep `unsafe_side_effect_rate = 0.0`.
""".strip()
    (include_root / "overview_metrics.md").write_text(overview + "\n")

    mode_rows = [
        [f"`{entry['id']}`", entry["description"]]
        for entry in data["modes"]
    ]
    (include_root / "mode_cards.md").write_text(
        md_table(["Mode", "Runtime behavior"], mode_rows) + "\n"
    )

    base_rows = []
    for mode in MODES:
        stats = data["base_r5_table"][mode]
        base_rows.append(
            [
                f"`{mode}`",
                fmt(stats["unsafe_side_effect_rate"]["estimate"]),
                fmt(stats["governance_effectiveness"]["estimate"]),
                fmt(stats["successful_safe_completion_rate"]["estimate"]),
                fmt(stats["precision"]["estimate"]),
                fmt(stats["recall"]["estimate"]),
                fmt(stats["f1"]["estimate"]),
            ]
        )
    (include_root / "table_base_r5.md").write_text(
        md_table(
            [
                "Mode",
                "`unsafe_side_effect_rate`",
                "`governance_effectiveness`",
                "`successful_safe_completion_rate`",
                "`precision`",
                "`recall`",
                "`f1`",
            ],
            base_rows,
        )
        + "\n"
    )

    backend_rows = [
        [
            f"`{row['campaign_id'].replace('campaign-', '')}`",
            fmt(row["successful_safe_completion_rate"]["estimate"]),
            fmt(row["unsafe_action_opportunity_rate"]["estimate"]),
            fmt(row["blocked_unsafe_actions"]["estimate"]),
            fmt(row["recall"]["estimate"]),
            fmt(row["f1"]["estimate"]),
        ]
        for row in data["guarded_backend_rows"]
    ]
    (include_root / "table_guarded_backends.md").write_text(
        md_table(
            [
                "Backend",
                "`guarded successful_safe_completion_rate`",
                "`guarded unsafe_action_opportunity_rate`",
                "`guarded blocked_unsafe_actions`",
                "`guarded recall`",
                "`guarded f1`",
            ],
            backend_rows,
        )
        + "\n"
    )

    overhead_rows = [
        [
            f"`{row['campaign_id']}`",
            fmt(row["guarded_mean_latency_ms"]["estimate"], 3),
            fmt(row["strict_mean_latency_ms"]["estimate"], 3),
            fmt(row["guarded_mean_token_usage"]["estimate"], 3),
            fmt(row["strict_mean_token_usage"]["estimate"], 3),
            fmt(row["guarded_mean_iterations_per_run"]["estimate"], 3),
            fmt(row["strict_mean_iterations_per_run"]["estimate"], 3),
            fmt(row["successful_safe_completion_rate_delta"]),
        ]
        for row in data["overhead_rows"]
    ]
    (include_root / "table_overhead.md").write_text(
        md_table(
            [
                "Campaign",
                "`guarded mean_latency_ms`",
                "`strict mean_latency_ms`",
                "`guarded mean_token_usage`",
                "`strict mean_token_usage`",
                "`guarded mean_iterations_per_run`",
                "`strict mean_iterations_per_run`",
                "`guarded - strict successful_safe_completion_rate`",
            ],
            overhead_rows,
        )
        + "\n"
    )

    artifact_rows = [
        [f"[`{artifact['label']}`](" + artifact["site_path"] + ")", f"`{artifact['source']}`"]
        for artifact in data["artifacts"]
    ]
    (include_root / "artifact_links.md").write_text(
        md_table(["Public artifact", "Repo source"], artifact_rows) + "\n"
    )

    artifact_groups = {
        "Core benchmark": [
            "benchmark_manifest.json",
            "benchmark_freeze_statement.md",
            "contract_enforcement_benchmark.md",
            "contract_experiment.md",
            "oracle_spec.md",
        ],
        "Results and validation": [
            "executive_summary.md",
            "results.md",
            "pre_freeze_audit.md",
            "calibration_log.md",
            "pilot_calibration_statement.md",
        ],
        "Matrices and traceability": [
            "contract_audit_matrix.md",
            "oracle_traceability_matrix.md",
            "scenario_audit_matrix.md",
        ],
        "Operational planning": [
            "execution_plan.md",
            "future_platform_roadmap.md",
            "final-nineteen-campaigns.json",
        ],
    }
    artifact_lookup = {artifact["label"]: artifact for artifact in data["artifacts"]}
    reference_sections: list[str] = []
    for heading, labels in artifact_groups.items():
        reference_sections.append(f"### {heading}")
        rows = []
        for label in labels:
            artifact = artifact_lookup[label]
            rows.append([f"[`{label}`]({artifact['site_path']})", f"`{artifact['source']}`"])
        reference_sections.append(md_table(["Document", "Repo source"], rows))
        reference_sections.append("")
    (include_root / "reference_sections.md").write_text("\n".join(reference_sections).rstrip() + "\n")


def chart_svg(title: str, groups: list[dict[str, Any]], palette: list[str], max_value: float, lower_better: set[str] | None = None) -> str:
    lower_better = lower_better or set()
    width = 1180
    height = 560
    left = 180
    top = 90
    chart_width = 920
    chart_height = 360
    group_gap = 28
    group_count = len(groups)
    series_count = len(groups[0]["values"])
    group_width = (chart_width - group_gap * (group_count - 1)) / group_count
    bar_gap = 10
    bar_width = (group_width - bar_gap * (series_count - 1)) / series_count
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        ".bg{fill:#f6f2e8}.frame{fill:#fffdf8;stroke:#d8cdb4;stroke-width:2}.grid{stroke:#d8cdb4;stroke-dasharray:4 6}.axis{stroke:#5b5243;stroke-width:2}.title{font:700 28px Georgia, serif;fill:#1f1c18}.label{font:600 15px 'Avenir Next', 'Segoe UI', sans-serif;fill:#3d372d}.small{font:500 13px 'Avenir Next', 'Segoe UI', sans-serif;fill:#6c6456}.value{font:600 12px 'Avenir Next', 'Segoe UI', sans-serif;fill:#241f19}.hint{font:500 13px 'Avenir Next', 'Segoe UI', sans-serif;fill:#6c6456}",
        "</style>",
        '<rect class="bg" width="100%" height="100%"/>',
        '<rect class="frame" x="24" y="24" width="1132" height="512" rx="24"/>',
        f'<text class="title" x="48" y="62">{title}</text>',
    ]
    for i in range(6):
        y = top + chart_height - chart_height * (i / 5)
        lines.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + chart_width}" y2="{y:.2f}"/>')
        lines.append(f'<text class="small" x="{left - 20}" y="{y + 5:.2f}" text-anchor="end">{fmt(max_value * (i / 5), 1)}</text>')
    lines.append(f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_height}"/>')
    lines.append(f'<line class="axis" x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}"/>')
    for group_index, group in enumerate(groups):
        start_x = left + group_index * (group_width + group_gap)
        lines.append(
            f'<text class="label" x="{start_x + group_width / 2:.2f}" y="{top + chart_height + 38}" text-anchor="middle">{group["label"]}</text>'
        )
        if group["label"] in lower_better:
            lines.append(
                f'<text class="hint" x="{start_x + group_width / 2:.2f}" y="{top + chart_height + 58}" text-anchor="middle">lower is better</text>'
            )
        for value_index, value in enumerate(group["values"]):
            bar_x = start_x + value_index * (bar_width + bar_gap)
            bar_height = 0 if value["estimate"] is None else chart_height * (value["estimate"] / max_value)
            bar_y = top + chart_height - bar_height
            lines.append(
                f'<rect x="{bar_x:.2f}" y="{bar_y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" rx="8" fill="{palette[value_index % len(palette)]}"/>'
            )
            lines.append(
                f'<text class="small" x="{bar_x + bar_width / 2:.2f}" y="{top + chart_height + 80 + (value_index % 2) * 18}" text-anchor="middle">{value["label"]}</text>'
            )
            lines.append(
                f'<text class="value" x="{bar_x + bar_width / 2:.2f}" y="{bar_y - 8:.2f}" text-anchor="middle">{fmt(value["estimate"], 3)}</text>'
            )
    lines.append("</svg>")
    return "\n".join(lines)


def clamp_zero(value: float | None) -> float:
    if value is None:
        return 0.0
    return max(value, 0.0)


def write_svgs(data: dict[str, Any], out_dir: Path) -> None:
    svg_root = out_dir / "public/assets/generated"
    svg_root.mkdir(parents=True, exist_ok=True)
    palette = ["#8c6c3f", "#c58e39", "#3e6b63", "#1f3f39"]
    base_groups = []
    for metric in [
        "unsafe_side_effect_rate",
        "governance_effectiveness",
        "successful_safe_completion_rate",
    ]:
        base_groups.append(
            {
                "label": metric,
                "values": [
                    {
                        "label": mode,
                        "estimate": data["base_r5_table"][mode][metric]["estimate"],
                    }
                    for mode in MODES
                ],
            }
        )
    (svg_root / "base-r5-modes.svg").write_text(
        chart_svg(
            "Base model comparison on campaign-base-r5",
            base_groups,
            palette,
            1.0,
            lower_better={"unsafe_side_effect_rate"},
        )
        + "\n"
    )

    backend_groups = []
    for metric in [
        "successful_safe_completion_rate",
        "unsafe_action_opportunity_rate",
        "f1",
    ]:
        backend_groups.append(
            {
                "label": metric,
                "values": [
                    {
                        "label": row["campaign_id"].replace("campaign-", "").replace("-r3", ""),
                        "estimate": clamp_zero(row[metric]["estimate"]),
                    }
                    for row in data["guarded_backend_rows"]
                ],
            }
        )
    (svg_root / "guarded-backends.svg").write_text(
        chart_svg(
            "Guarded mode across selected backends",
            backend_groups,
            ["#355c7d", "#6c5b7b", "#c06c84", "#f67280", "#f8b195"],
            1.0,
        )
        + "\n"
    )

    overhead_groups = []
    for metric in [
        "successful_safe_completion_rate_delta",
        "guarded_mean_iterations_per_run",
        "strict_mean_iterations_per_run",
    ]:
        overhead_groups.append(
            {
                "label": metric,
                "values": [
                    {
                        "label": row["campaign_id"].replace("campaign-", ""),
                        "estimate": clamp_zero(
                            row[metric]["estimate"]
                            if isinstance(row[metric], dict)
                            else row[metric]
                        ),
                    }
                    for row in data["overhead_rows"]
                ],
            }
        )
    (svg_root / "guarded-vs-strict.svg").write_text(
        chart_svg(
            "Guarded recovery utility and iteration overhead",
            overhead_groups,
            ["#2f4858", "#4f6d7a", "#a7c5bd", "#e0a458", "#d1495b", "#edae49", "#66a182", "#9b5de5"],
            max(
                1.0,
                max(
                    clamp_zero(
                        row["guarded_mean_iterations_per_run"]["estimate"]
                    )
                    for row in data["overhead_rows"]
                ),
            ),
        )
        + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    data = build_site_data(args.stats)
    data["artifacts"] = copy_public_artifacts(out_dir)
    write_json(data, out_dir)
    write_markdown_fragments(data, out_dir)
    write_svgs(data, out_dir)


if __name__ == "__main__":
    main()
