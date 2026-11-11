'use strict';
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const test = require('node:test');
const vm = require('node:vm');
const source = readFileSync(`${__dirname}/witness.cjs`, 'utf8');

async function run(action, overrides = {}) {
  const requests = [];
  const errors = [];
  const broker = { management_url: 'https://broker.invalid/custom/api/', vhost: 'team / one',
    username_env: 'CUSTOM_USER', password_env: 'CUSTOM_PASSWORD', ...overrides };
  const settings = { scenario: { witness_queue: 'proof / queue' }, timing: { request: '2s' } };
  const process = { argv: ['node', '-', action, JSON.stringify(broker), JSON.stringify(settings)],
    env: { CUSTOM_USER: 'offline-user', CUSTOM_PASSWORD: 'offline-password' } };
  const context = vm.createContext({ require, process, Buffer, AbortSignal: { timeout(milliseconds) {
    assert.equal(milliseconds, 2000);
    return 'offline-signal';
  } }, console: { log() {}, error(message) { errors.push(message); } },
  fetch: async (url, options) => {
    requests.push({ url, ...options });
    return { ok: action !== 'lost', status: action === 'lost' ? 404 : 200,
      json: async () => ({ routed: true }) };
  } });
  await vm.runInContext(source, context);
  assert.deepEqual(errors, []);
  assert.equal(process.exitCode, undefined);
  return requests;
}

test('seed uses configured URL, credentials, encoded vhost and isolated queue', async () => {
  const requests = await run('seed');
  assert.equal(requests.length, 2);
  assert.equal(requests[0].url, 'https://broker.invalid/custom/api/queues/team%20%2F%20one/proof%20%2F%20queue');
  assert.equal(requests[0].method, 'PUT');
  assert.equal(requests[0].headers.authorization,
    'Basic ' + Buffer.from('offline-user:offline-password').toString('base64'));
  assert.equal(requests[1].url, 'https://broker.invalid/custom/api/exchanges/team%20%2F%20one/amq.default/publish');
  assert.equal(JSON.parse(requests[1].body).routing_key, 'proof / queue');
});

test('lost and delete address the same configured queue', async () => {
  for (const action of ['lost', 'delete']) {
    const requests = await run(action, { vhost: '/' });
    assert.equal(requests.length, 1);
    assert.equal(requests[0].url, 'https://broker.invalid/custom/api/queues/%2F/proof%20%2F%20queue');
    assert.equal(requests[0].method, action === 'lost' ? 'GET' : 'DELETE');
  }
});

test('missing configured credentials fail before any request', async () => {
  await assert.rejects(run('seed', { username_env: 'MISSING_USER' }), /credentials are missing/);
});