import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { withRenderer, renderDiagram } from './render.mjs';
import { views } from './views.mjs';

const directory = dirname(fileURLToPath(import.meta.url));
const selectedId = process.argv.find(argument => argument.startsWith('--view='))?.slice('--view='.length);
assert.ok(!selectedId || views.some(view => view.id === selectedId), `Unknown view: ${selectedId}`);
const paths = {
  gateway: 'networking/Application_Gateways.svg', aks: 'compute/Kubernetes_Services.svg',
  law: 'analytics/Log_Analytics_Workspaces.svg', grafana: 'other/Grafana.svg',
  prometheus: 'other/Prometheus.svg', monitor: 'management_governance/Monitor.svg',
  acr: 'containers/Container_Registries.svg', vault: 'security/Key_Vaults.svg', storage: 'storage/Storage_Accounts.svg',
};

await withRenderer(async (page, webapp) => {
  const icons = {};
  const provenance = {};
  mkdirSync(join(directory, 'icons'), { recursive: true });
  for (const [key, relative] of Object.entries(paths)) {
    const bytes = readFileSync(join(webapp, 'img/lib/azure2', relative));
    const text = bytes.toString('utf8');
    assert.match(text, /<svg/);
    assert.doesNotMatch(text, /<script|https?:[^"']*\.(png|svg)/);
    icons[key] = `data:image/svg+xml,${encodeURIComponent(text)}`;
    writeFileSync(join(directory, 'icons', `${key}.svg`), bytes);
    provenance[key] = { source: `img/lib/azure2/${relative}`, sha256: createHash('sha256').update(bytes).digest('hex') };
  }
  writeFileSync(join(directory, 'icons/NOTICE-drawio.txt'), readFileSync(join(webapp, 'img/LICENSE')));
  writeFileSync(join(directory, 'icons/LICENSE-drawio.txt'), readFileSync(join(webapp, '../../../LICENSE')));
  writeFileSync(join(directory, 'icons/provenance.json'), `${JSON.stringify({ package: 'hediet.vscode-drawio', version: '1.19.0', icons: provenance }, null, 2)}\n`);
  for (const definition of views.filter(view => (!selectedId || view.id === selectedId) && (!process.argv.includes('--one') || view.id === '06-entry'))) {
    const result = await renderDiagram(page, definition, icons);
    assert.match(result.source, /<mxfile/);
    assert.match(result.svg, /data:image\/svg\+xml;base64,/);
    assert.ok(result.edges > 0);
    writeFileSync(join(directory, `${definition.id}.drawio`), `${result.source}\n`);
    writeFileSync(join(directory, `${definition.id}.svg`), `${result.svg}\n`);
    console.log(`PASS: ${definition.id}: ${result.vertices} editable nodes, ${result.edges} connected edges; bundled mxGraph SVG export`);
  }
});