import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { formatScore, latestCampaigns, selectCampaigns } from '../src/utils/dashboard.js';
const { dashboard_campaigns: campaigns } = JSON.parse(readFileSync(new URL('../src/data/canonical_results.json', import.meta.url)));
const defaults = { scope: 'featured', mode: 'guarded', metric: 'successful_safe_completion_rate', provider: 'all', status: 'checked', sort: 'recent', search: '' };
test('featured comparison includes three requested models with exact recorded identities', () => {
  assert.deepEqual(selectCampaigns(campaigns, defaults).map(c => c.model_id), ['claude-opus-5','claude-opus-4-8','gpt-5.5-2026-04-23']);
});
test('latest uses closure dates and excludes admission issues', () => {
  assert.deepEqual(latestCampaigns(campaigns).map(c => c.model_id), ['claude-opus-5','claude-sonnet-5','claude-haiku-4-5-20251001']);
});
test('all, checked, issue and text filters are consistent', () => {
  assert.equal(selectCampaigns(campaigns, { ...defaults, scope: 'all', status: 'all' }).length, 26);
  assert.equal(selectCampaigns(campaigns, { ...defaults, scope: 'all' }).length, 23);
  assert.equal(selectCampaigns(campaigns, { ...defaults, scope: 'all', status: 'issues' }).length, 3);
  assert.equal(selectCampaigns(campaigns, { ...defaults, scope: 'all', status: 'all', search: 'ASTRA' })[0].admission_issue, true);
  assert.equal(selectCampaigns(campaigns, { ...defaults, search: 'does-not-exist' }).length, 0);
  assert.equal(selectCampaigns(campaigns, { ...defaults, provider: 'OpenAI' }).length, 1);
});
test('metric sorting respects direction and puts excluded campaigns last', () => {
  const rows = selectCampaigns(campaigns, { ...defaults, scope: 'all', status: 'all', sort: 'score' });
  assert.ok(rows.slice(-3).every(c => c.admission_issue));
  const latency = selectCampaigns(campaigns, { ...defaults, metric: 'mean_latency_ms', sort: 'score' });
  assert.ok(latency[0].statistics.guarded.mean_latency_ms.estimate <= latency[1].statistics.guarded.mean_latency_ms.estimate);
});
test('undefined values never turn into zero, units are explicit', () => {
  assert.equal(formatScore(null, defaults.metric), 'N/A');
  assert.equal(formatScore(0, defaults.metric), '0.0%');
  assert.equal(formatScore(0.746032, defaults.metric), '74.6%');
  assert.equal(formatScore(1500, 'mean_latency_ms'), '1.5 s');
});
test('explicit multi-selection supports different models, empty selection and flagged records', () => {
  const ids = ['campaign-openai-xhigh-r3', 'campaign-anthropic-claude-opus-5-sol-r3'];
  const selected = selectCampaigns(campaigns, { ...defaults, scope: 'all', status: 'all', evaluationIds: ids });
  assert.equal(selected.length, 2);
  assert.deepEqual(new Set(selected.map(c => c.campaign_id)), new Set(ids));
  assert.equal(selectCampaigns(campaigns, { ...defaults, scope: 'all', evaluationIds: [] }).length, 0);
  const flagged = selectCampaigns(campaigns, { ...defaults, scope: 'all', status: 'all', evaluationIds: ['campaign-openai-gpt6-astra-max-r3'] });
  assert.equal(flagged.length, 1);
  assert.equal(flagged[0].admission_issue, true);
});
