import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const directory = dirname(fileURLToPath(import.meta.url));
const root = resolve(directory, '../..');
const read = path => readFileSync(join(root, path), 'utf8').replace(/\r\n/g, '\n');
assert.ok(existsSync(join(root, 'examples/README.md')), 'Attendee example catalog exists');
for (const legacy of ['agents', 'skills']) {
  assert.ok(!existsSync(join(root, legacy)), `Old top-level folder must not remain: ${legacy}`);
}
const ids = ['evidence-led-investigation', 'network-troubleshooting', 'vm-troubleshooting',
  'kubernetes-troubleshooting', 'evidence-packet', 'mermaid-diagram', 'drawio-diagram'];
const sections = ['Scope and Inputs', 'Capability Discovery', 'Procedure', 'Stop and Routing',
  'Handoff Contract', 'Repair and Verification', 'Acceptance Cases'];
const sources = new Map();
for (const filename of readdirSync(directory).filter(name => name.endsWith('.md'))) {
  const text = read(`examples/skills/${filename}`);
  if (!text.startsWith('---\n')) continue;
  const metadata = text.match(/^---\nname: ([a-z0-9-]+)\ndescription: "([^"\n]+)"\n---\n/);
  assert.ok(metadata, `${filename}: expected source name and quoted description`);
  const [, id, description] = metadata;
  assert.equal(filename, `${id}.md`);
  assert.ok(!sources.has(id), `Duplicate source ID: ${id}`);
  assert.ok(description.startsWith('Use when ') && description.length > 80, `${id}: discovery trigger`);
  sources.set(id, text);
  if (id === 'drawio-diagram') {
    for (const contract of [/original workshop/, /mxGraphModel/, /mxGeometry/,
      /source\/target/, /untrusted evidence/, /UNKNOWN/, /save and reopen/,
      /Rendering and visual validation unverified/, /does not\ninstall/]) {
      assert.match(text, contract, `${id}: editable diagram contract`);
    }
    continue;
  }
  if (id === 'mermaid-diagram') {
    for (const contract of [/original workshop procedure/, /sequenceDiagram/, /flowchart/, /xychart-beta/,
      /missing samples as gaps/, /denominator/, /p95\/p99/, /Rendering and visual validation unverified/]) {
      assert.match(text, contract, `${id}: incident visualization contract`);
    }
    continue;
  }
  for (const section of sections) assert.ok(text.includes(`## ${section}\n`), `${id}: ${section}`);
  for (const token of ['<INCIDENT_ID>', '<AUTHORIZED_SCOPE>', '<UTC_WINDOW>']) {
    assert.ok(text.includes(token), `${id}: external input ${token}`);
  }
  assert.doesNotMatch(text, /sre-web|opponent|disposable|facilitator|last 15 minutes|TEAM_RESOURCE_GROUP|LAB-CHAIN/i,
    `${id}: scenario coupling`);
  for (const contract of [/untrusted evidence/i, /denied/i, /collection/i, /fresh/i,
    /hypotheses/i, /discriminating/i, /approval owner/i, /rollback/i, /no automatic fix/i]) {
    assert.match(text, contract, `${id}: missing contract ${contract}`);
  }
}
assert.deepEqual([...sources.keys()].sort(), [...ids].sort(), 'Seven supplied example skill sources, not runtime requirements');
for (const id of ids.slice(0, 4)) {
  const text = sources.get(id);
  for (const target of ids.slice(1, 4).filter(target => target !== id)) {
    assert.ok(text.includes(target), `${id}: missing routing target ${target}`);
  }
  assert.match(text, /at most one transfer to each domain/);
  assert.match(text, /predicted/i);
  assert.match(text, /actual/i);
}
const network = sources.get('network-troubleshooting');
for (const contract of [/subnet and NIC NSGs/, /effective routes/, /DNS/, /return paths/,
  /If the path contains a Load Balancer/, /If it contains Application Gateway/,
  /control-plane configuration from data-plane evidence/, /private network reachability/]) {
  assert.match(network, contract);
}
const vm = sources.get('vm-troubleshooting');
for (const contract of [/Resource Health/, /provisioning and power/, /Memory and filesystem capacity/,
  /CPU, memory, disk latency/, /Boot screenshots/, /Do not attach Run Command/, /Missing telemetry is not healthy/]) {
  assert.match(vm, contract);
}
const kubernetes = sources.get('kubernetes-troubleshooting');
for (const contract of [/Azure Reader is not Kubernetes API permission/, /EndpointSlices/,
  /readiness\/liveness\/startup/, /DNS symptoms/, /No secrets reads/, /no approved data-plane test/,
  /Expired or missing events/, /deployment revision/]) assert.match(kubernetes, contract);

const catalog = read('examples/skills/README.md');
const rows = [...catalog.matchAll(/^\| (network|vm|kubernetes) \| ([a-z-]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$/gm)];
assert.equal(rows.length, 15, 'Five explicit acceptance cases per domain');
for (const domain of ['network', 'vm', 'kubernetes']) {
  const cases = rows.filter(row => row[1] === domain);
  assert.deepEqual(cases.map(row => row[2]), ['healthy', 'fault', 'missing-access', 'injected-instructions', 'out-of-scope']);
  for (const [, , kind, condition, outcome, evidence] of cases) {
    assert.ok(condition.trim().length > 30 && evidence.trim().length > 30, `${domain}/${kind}: concrete fixture and evidence`);
    assert.ok(outcome.trim().startsWith(kind === 'missing-access' ? 'BLOCKED:' : kind === 'out-of-scope' ? 'STOP:' : 'PASS:'),
      `${domain}/${kind}: explicit expected outcome`);
  }
}
const migrations = new Map([
  ['lab-vm-network-triage', ['network-troubleshooting', 'vm-troubleshooting']],
  ['lab-k8s-triage', ['kubernetes-troubleshooting']],
  ['lab-evidence-packet', ['evidence-packet']],
]);
for (const [legacy, replacements] of migrations) {
  const text = read(`examples/skills/${legacy}.md`);
  assert.match(text, /Deprecated/);
  assert.ok(!text.startsWith('---'), `${legacy}: must not remain an installable duplicate`);
  for (const id of replacements) assert.ok(text.includes(`${id}.md`));
}
const roleSkills = new Map([
  ['lab-triage.md', ['evidence-led-investigation', 'evidence-packet']],
  ['lab-network-specialist.md', ['network-troubleshooting', 'azure-network-watcher', 'azure-application-gateway', 'azure-diagnostics', 'evidence-packet']],
  ['lab-vm-specialist.md', ['vm-troubleshooting', 'azure-virtual-machines', 'azure-diagnostics', 'evidence-packet']],
  ['lab-k8s-specialist.md', ['kubernetes-troubleshooting', 'azure-kubernetes-service', 'azure-diagnostics', 'evidence-packet']],
  ['lab-incident-analyst.md', ['evidence-packet', 'incident_postmortem_generator', 'mermaid-diagram']],
]);
const upstreamSkills = new Set(['azure-network-watcher', 'azure-application-gateway', 'azure-diagnostics',
  'azure-virtual-machines', 'azure-kubernetes-service', 'incident_postmortem_generator']);
for (const filename of readdirSync(join(root, 'examples/agents')).filter(name => name.endsWith('.md'))) {
  const text = read(`examples/agents/${filename}`);
  if (filename === 'lab-incident-recorder.md') {
    assert.match(text, /^# Deprecated:/);
    assert.match(text, /lab-incident-analyst\.md/);
    assert.doesNotMatch(text, /\*\*Choose Skills:/);
    continue;
  }
  for (const legacy of migrations.keys()) assert.ok(!text.includes(legacy), `${filename}: stale skill ${legacy}`);
  const selection = text.match(/\*\*Choose Skills:\*\* (.+)/);
  assert.ok(selection, `${filename}: explicit selection`);
  const selected = [...selection[1].matchAll(/`([^`]+)`/g)].map(match => match[1]);
  assert.deepEqual(selected, roleSkills.get(filename), `${filename}: exact domain skill selection`);
  assert.ok(selected.length <= 5, `${filename}: active skill limit`);
  for (const id of selected) assert.ok(sources.has(id) || upstreamSkills.has(id), `${filename}: unknown skill ${id}`);
  if (filename !== 'lab-triage.md') assert.match(text, /\*\*Handoff Agents:\*\* none;/);
}
const configuration = read('AGENT-CONFIGURATION.md');
assert.match(configuration, /Publish and Prove Selected Skills/);
for (const legacy of migrations.keys()) assert.ok(!configuration.includes(legacy), `Configuration: stale skill ${legacy}`);
const setup = read('SRE-AGENT-SETUP.md');
for (const boundary of [/no cloud commands were run/, /Markdown body after the frontmatter/,
  /downstream permissions/, /actual skill retrieval\/load evidence separately/,
  /MANUAL HANDOVER/, /No Azure tenant access/, /Review/]) assert.match(setup, boundary);
const guidance = read('examples/README.md');
for (const contract of [/optional guides/, /create your own/, /unrelated domain skills need not/,
  /Examples grant no permissions/, /at least one relevant skill procedure/, /same observable behavior/,
  /verified manual chain/, /stale evidence/]) assert.match(guidance, contract);
const documents = [...readdirSync(directory).filter(name => name.endsWith('.md')).map(name => `examples/skills/${name}`),
  'examples/README.md', 'SRE-AGENT-SETUP.md', 'AGENT-CONFIGURATION.md',
  ...readdirSync(join(root, 'examples/agents')).map(name => `examples/agents/${name}`)];
let links = 0;
for (const document of documents) {
  const text = read(document).replace(/```[\s\S]*?```/g, '');
  for (const [, target] of text.matchAll(/\[[^\]\n]+\]\(([^)\s]+)\)/g)) {
    if (/^(?:[a-z]+:|#)/i.test(target)) continue;
    const [path, anchor] = target.split('#');
    const resolved = resolve(dirname(join(root, document)), decodeURIComponent(path));
    assert.ok(existsSync(resolved), `${document}: broken link ${target}`);
    if (anchor && resolved.endsWith('.md')) {
      const headings = [...readFileSync(resolved, 'utf8').matchAll(/^#+ (.+)$/gm)]
        .map(match => match[1].trim().toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s/g, '-'));
      assert.ok(headings.includes(anchor), `${document}: broken anchor ${target}`);
    }
    links += 1;
  }
}
console.log(`PASS: seven unique skill sources; domain contracts and bounded routing; 15 acceptance cases; migration and role IDs; ${links} local links.`);
console.log('Structural/document validation only: no Azure skill loading, reasoning, permissions, queries or deployment proved.');