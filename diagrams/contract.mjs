import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { views } from './views.mjs';

export const diagramDirectory = dirname(fileURLToPath(import.meta.url));
const decodeXml = value => value.replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

export function checkSreAgentArchitecture(definition = views.find(view => view.id === 'sre-agent-architecture')) {
  assert.ok(definition, 'Dedicated SRE Agent architecture exists');
  const nodes = new Map(definition.nodes.map(node => [node.id, node]));
  assert.equal(nodes.size, definition.nodes.length, 'Unique architecture node IDs');
  for (const node of nodes.values()) {
    assert.ok(node.x >= 0 && node.y >= 0 && node.x + node.w <= definition.width && node.y + node.h <= definition.height, `${node.id}: page bounds`);
  }
  for (const edge of definition.edges) assert.ok(nodes.has(edge.from) && nodes.has(edge.to), 'Valid route terminals');
  for (const [from, to, kind] of [
    ['human', 'main'], ['main', 'invoke'], ['invoke', 'triage'],
    ['incident', 'plan', 'control'], ['plan', 'triage', 'control'],
    ['schedule', 'triage', 'control'], ['triage', 'k8s'], ['k8s', 'triage'],
    ['triage', 'analyst'], ['analyst', 'triage'], ['triage', 'optional', 'control'],
    ['k8s', 'skills', 'control'], ['analyst', 'skills', 'control'],
    ['optional', 'knowledge', 'control'], ['tools', 'checks'],
    ...['resources', 'law', 'prometheus', 'grafana', 'repository'].map(target => ['checks', target, 'control']),
  ]) {
    assert.ok(definition.edges.some(edge => edge.from === from && edge.to === to && edge.kind === kind), `Required architecture route ${from} -> ${to} (${kind || 'solid'})`);
  }
  for (const [id, terms] of [
    ['invoke', ['/agent lab-triage', 'Not a default replacement']],
    ['plan', ['Off (paused)', 'Review', 'lab-triage']],
    ['intake', ['Conditional', 'correlated alert/thread/tool trace']],
    ['schedule', ['Optional', 'Separate trigger', 'Review']],
    ['skills', ['Description-led retrieval', 'not permission grants']],
    ['knowledge', ['Separate reference retrieval', 'source revision']],
    ['checks', ['execution UAMI', 'effective RBAC', 'Connector consent', 'Network route', 'Review is not a universal gate']],
    ['tools', ['Available/configured is not guaranteed', 'Read-only tool policy']],
    ['author', ['configuration user', 'Not proof of execution permissions']],
    ['uami', ['Actual execution UAMI', 'inherited roles']],
    ['grafanaIdentity', ['Grafana managed identity', 'Does not grant agent access']],
    ['operator', ['Separate authorized operator', 'No agent recovery credentials']],
    ['manual', ['MANUAL HANDOVER']],
  ]) for (const term of terms) assert.ok(nodes.get(id)?.label.includes(term), `${id}: ${term}`);
  assert.match(definition.description, /not Azure backend internals/);
  assert.equal(nodes.get('main').icon, undefined, 'No substitute SRE Agent product logo');
  assert.ok(!definition.edges.some(edge => edge.from === 'k8s' && edge.to === 'analyst'), 'Specialist returns to triage before synthesis');
}

export function checkSreAgentPresentation() {
  const focused = views.find(view => view.id === '07-sre-agent-architecture');
  const full = views.find(view => view.id === 'sre-agent-architecture');
  assert.ok(focused && full, 'Full and presentation SRE Agent views exist');
  assert.equal(focused.width, 1152);
  assert.equal(focused.height, 408);
  const nodes = new Map(focused.nodes.map(node => [node.id, node]));
  assert.equal(nodes.size, focused.nodes.length, 'Unique presentation node IDs');
  for (const node of nodes.values()) {
    assert.ok(node.font >= 20, `${node.id}: presentation label size`);
    assert.ok(node.x >= 0 && node.y >= 0 && node.x + node.w <= focused.width && node.y + node.h <= focused.height, `${node.id}: presentation bounds`);
  }
  for (const [from, to] of [['human', 'main'], ['triage', 'k8s'], ['k8s', 'triage'], ['triage', 'analyst'], ['analyst', 'triage']]) {
    assert.ok(focused.edges.some(edge => edge.from === from && edge.to === to), `Presentation route ${from} -> ${to}`);
  }
  for (const edge of focused.edges) {
    assert.ok(nodes.has(edge.from) && nodes.has(edge.to), 'Presentation route terminals');
    assert.ok(full.edges.some(original => original.from === edge.from && original.to === edge.to), 'Derived route agrees with full architecture');
  }
  for (const [id, term] of [['invoke', 'not the default chat route'], ['skills', 'Selected skills'], ['knowledge', 'Reference sources'], ['tools', 'Own approved tools'], ['bounds', 'connector authorization'], ['review', 'universal gate'], ['proof', 'Lab 5 proof']]) assert.ok(nodes.get(id)?.label.includes(term), `${id}: ${term}`);
  assert.match(focused.description, /derived from sre-agent-architecture/);
}

export function checkAsset(id, width, height) {
  const source = readFileSync(join(diagramDirectory, `${id}.drawio`), 'utf8').trim();
  const svg = readFileSync(join(diagramDirectory, `${id}.svg`), 'utf8');
  assert.match(source, /<mxfile\b/);
  assert.match(source, /<mxGraphModel\b/);
  assert.ok((source.match(/vertex="1"/g) || []).length >= 5, `${id}: editable vertices`);
  assert.ok((source.match(/edge="1"/g) || []).length >= 3, `${id}: connected editable edges`);
  assert.match(svg, new RegExp(`viewBox="0 0 ${width} ${height}"`));
  assert.match(svg, /role="img"/);
  assert.match(svg, /aria-labelledby="[^"]+"/);
  assert.match(svg, /<title\b[^>]*>[^<]+<\/title>/);
  assert.match(svg, /<desc\b[^>]*>.{80,}?<\/desc>/);
  assert.doesNotMatch(svg, /<script|<foreignObject|(?:href|src)="(?:https?:|file:)/i);
  assert.equal(decodeXml(svg.match(/\bcontent="([^"]+)"/)[1]), source, `${id}: embedded editable source parity`);
  const images = [...svg.matchAll(/<image\b[^>]*?(?:xlink:href|href)="([^"]+)"/g)];
  assert.ok(images.length > 0, `${id}: real icon images`);
  for (const [, reference] of images) {
    assert.match(reference, /^data:image\/svg\+xml;base64,/);
    assert.match(Buffer.from(reference.split(',')[1], 'base64').toString('utf8'), /<svg/);
  }
  const modelIds = new Set([...source.matchAll(/<mxCell\b[^>]*\bid="([^"]+)"/g)].map(match => match[1]));
  for (const [, terminal] of source.matchAll(/\b(?:source|target)="([^"]+)"/g)) assert.ok(modelIds.has(terminal), `${id}: dangling edge ${terminal}`);
  return svg;
}

export function checkAllAssets() {
  checkSreAgentArchitecture();
  checkSreAgentPresentation();
  const provenance = JSON.parse(readFileSync(join(diagramDirectory, 'icons/provenance.json'), 'utf8'));
  for (const [key, icon] of Object.entries(provenance.icons)) {
    const bytes = readFileSync(join(diagramDirectory, 'icons', `${key}.svg`));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), icon.sha256, `${key}: original icon bytes`);
    assert.ok(icon.source.startsWith('img/lib/azure2/'));
  }
  assert.match(readFileSync(join(diagramDirectory, 'icons/LICENSE-drawio.txt'), 'utf8'), /Apache License/);
  assert.match(readFileSync(join(diagramDirectory, 'icons/NOTICE-drawio.txt'), 'utf8'), /does not apply to end-user diagram output/);
  for (const view of views) checkAsset(view.id, view.width, view.height);
  const routes = {
    platform: [['browser', 'gateway'], ['gateway', 'front'], ['front', 'pods'], ['cert', 'secret'], ['secret', 'agic'], ['agic', 'gateway'], ['system', 'agic'], ['keda', 'pods'], ['nap', 'pool'], ['pool', 'pods'], ['acr', 'pods']],
    application: [['entry', 'front'], ['front', 'product'], ['front', 'order'], ['order', 'queue'], ['queue', 'makeline'], ['makeline', 'db'], ['admin', 'product'], ['admin', 'makeline'], ['customer', 'order'], ['worker', 'makeline']],
    observability: [['aks', 'amw'], ['aks', 'law'], ['amw', 'grafana'], ['law', 'grafana'], ['law', 'alert'], ['gateway', 'alert'], ['alert', 'receiver'], ['agent', 'law'], ['agent', 'resources'], ['alert', 'agent']],
    'sre-agent-architecture': views.find(view => view.id === 'sre-agent-architecture').edges.map(edge => [edge.from, edge.to]),
  };
  for (const [id, connections] of Object.entries(routes)) {
    const source = readFileSync(join(diagramDirectory, `${id}.drawio`), 'utf8');
    const cells = [...source.matchAll(/<mxCell\b[^>]+edge="1"[^>]*>/g)].map(match => match[0]);
    for (const [from, to] of connections) assert.ok(cells.some(cell => cell.includes(`source="${from}"`) && cell.includes(`target="${to}"`)), `${id}: required route ${from} -> ${to}`);
  }
}

export function checkSlideAssets(text, directory, count, height) {
  const images = [...text.matchAll(/<img class="diagram"[^>]+>/g)].map(match => match[0]);
  assert.equal(images.length, count, 'Diagram asset count');
  for (const image of images) {
    assert.match(image, /alt="[^"]{80,}"/);
    assert.match(image, /width="1152"/);
    assert.match(image, new RegExp(`height="${height}"`));
    const reference = image.match(/src="([^"]+)"/)[1];
    const path = resolve(directory, reference);
    assert.ok(existsSync(path), reference);
    checkAsset(reference.split('/').at(-1).replace(/\.svg$/, ''), 1152, height);
  }
  return images;
}