export const metricOptions = {
  successful_safe_completion_rate: { label: "Safe completion", percent: true, lower: false, description: "Share of runs that satisfy an acceptable outcome without a forbidden outcome. Higher is better." },
  unsafe_side_effect_rate: { label: "Unsafe side effects", percent: true, lower: true, description: "Committed unsafe effects per observed unsafe-action opportunity. Lower is better. No opportunity means N/A, not zero." },
  governance_effectiveness: { label: "Governance effectiveness", percent: true, lower: false, description: "Prevention relative to the no-contract unsafe-effect baseline, where that contrast is defined. Higher is better." },
  f1: { label: "Runtime detection F1", percent: false, lower: false, description: "Runtime precision–recall balance on the benchmark's detection targets. Read alongside intervention opportunities; this is not an overall model score." },
  mean_latency_ms: { label: "Mean run latency", seconds: true, lower: true, description: "Mean end-to-end run time, including model calls and governance. Lower is faster; failures and early stops also affect this metric." },
};
export function formatScore(value, metric) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return "N/A";
  const spec = metricOptions[metric];
  const number = spec.percent ? value * 100 : spec.seconds ? value / 1000 : value;
  return `${number.toFixed(spec.percent || spec.seconds ? 1 : 3)}${spec.percent ? "%" : spec.seconds ? " s" : ""}`;
}
export function latestCampaigns(campaigns) {
  return campaigns.filter((c) => !c.admission_issue).sort((a, b) => b.closed_at.localeCompare(a.closed_at)).slice(0, 3);
}
export function selectCampaigns(campaigns, filters) {
  const latest = new Set(latestCampaigns(campaigns).map((c) => c.campaign_id));
  const query = (filters.search || "").trim().toLowerCase();
  return campaigns.filter((c) => {
    if (Array.isArray(filters.evaluationIds) && !filters.evaluationIds.includes(c.campaign_id)) return false;
    if (filters.scope === "featured" && !c.featured) return false;
    if (filters.scope === "latest" && !latest.has(c.campaign_id)) return false;
    if (filters.provider !== "all" && c.provider !== filters.provider) return false;
    if (filters.status === "checked" && c.admission_issue) return false;
    if (filters.status === "issues" && !c.admission_issue) return false;
    return `${c.label} ${c.model_id} ${c.profile_id} ${c.campaign_id}`.toLowerCase().includes(query);
  }).sort((a, b) => {
    if (filters.sort === "name") return a.label.localeCompare(b.label) || b.closed_at.localeCompare(a.closed_at);
    if (filters.sort === "score") {
      const value = (c) => c.admission_issue ? null : c.statistics[filters.mode][filters.metric]?.estimate;
      const av = value(a), bv = value(b);
      if (av == null && bv != null) return 1;
      if (bv == null && av != null) return -1;
      if (av != null && bv != null && av !== bv) return metricOptions[filters.metric].lower ? av - bv : bv - av;
    }
    return b.closed_at.localeCompare(a.closed_at);
  });
}
