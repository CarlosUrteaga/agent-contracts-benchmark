import data from "../data/canonical_results.json";

export const siteData = data;

export function metric(value, digits = 6) {
  if (value === null || value === undefined) {
    return "NA";
  }
  const text = Number(value).toFixed(digits);
  return text.replace(/\.?0+$/, "");
}

export function withBase(path) {
  const base = import.meta.env.BASE_URL || "/";
  const normalizedBase = base.endsWith("/") ? base.slice(0, -1) : base;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return normalizedBase ? `${normalizedBase}${normalizedPath}` : normalizedPath;
}

export function artifactByLabel(label) {
  return siteData.artifacts.find((artifact) => artifact.label === label);
}
