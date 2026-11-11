'use strict';

const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const source = readFileSync(path.join(__dirname, 'verify-order.cjs'), 'utf8');
const publisher = 'const publishResult = await publisher.publish(\n' +
  'publishResult.outcome === rabbit.OutcomeState.ACCEPTED\n' +
  'throw new Error(`message not accepted by RabbitMQ';
const route = 'await fastify.sendMessage(Buffer.from(JSON.stringify(msg)))\nreply.code(201)';
const broker = {
  queue: 'checkout queue', vhost: '/tenant/blue', management_url: 'http://queue.internal:15673/manage/',
  health_url: 'http://checkout.internal:3001/ready', order_url: 'http://checkout.internal:3001/orders',
  publisher_path: '/srv/broker.cjs', route_path: '/srv/checkout.cjs',
  username_env: 'CHECKOUT_USER', password_env: 'CHECKOUT_PASSWORD',
  test_order: { items: [{ productId: 42, quantity: 2, price: 7 }], region: 'blue' },
};
const timing = { request: '7s', stability: 12 };

async function exercise(options = {}) {
  const messages = [];
  const process = {
    argv: ['node', '-', JSON.stringify(broker), JSON.stringify(timing)],
    env: options.env ?? { CHECKOUT_USER: 'test-user', CHECKOUT_PASSWORD: 'test-password' },
  };
  const calls = [];
  const files = [];
  const waits = [];
  const timeouts = [];
  const sandbox = {
    process, Buffer, URL, Date,
    AbortSignal: { timeout: milliseconds => { timeouts.push(milliseconds); return AbortSignal.timeout(milliseconds); } },
    console: { log: message => messages.push(message), error: message => messages.push(message) },
    require: name => {
      if (name === 'node:fs') return {
        readFileSync: file => {
          files.push(file);
          return file === broker.publisher_path ? (options.publisher ?? publisher) : route;
        },
      };
      if (name === 'node:timers/promises') return { setTimeout: async milliseconds => waits.push(milliseconds) };
      return require(name);
    },
    fetch: async (url, request = {}) => {
      calls.push({ url, request });
      const queue = url.includes('/manage/queues/');
      const post = request.method === 'POST';
      const status = queue ? (options.queueStatus ?? 200) : post ? (options.postStatus ?? 201) : 200;
      return {
        ok: status >= 200 && status < 300,
        status,
        json: async () => queue
          ? { name: options.queueName ?? broker.queue, vhost: options.vhost ?? broker.vhost, state: options.queueState ?? 'running' }
          : { status: options.health ?? 'ok' },
      };
    },
  };
  vm.createContext(sandbox);
  await vm.runInContext(source, sandbox);
  return { exitCode: process.exitCode ?? 0, calls, messages, files, waits, timeouts };
}

test('healthy broker-confirmed order succeeds and checks queue twice', async () => {
  const result = await exercise();
  assert.equal(result.exitCode, 0);
  const queueCalls = result.calls.filter(call => call.url.includes('/manage/queues/'));
  assert.equal(queueCalls.length, 2);
  assert(queueCalls.every(call => call.url === 'http://queue.internal:15673/manage/queues/%2Ftenant%2Fblue/checkout%20queue'));
  assert.equal(queueCalls[0].request.headers.authorization,
    'Basic ' + Buffer.from('test-user:test-password').toString('base64'));
  assert.deepEqual(result.files, [broker.publisher_path, broker.route_path]);
  assert(result.timeouts.every(value => value === 7000));
  assert.equal(result.waits.length, 1);
  assert(result.waits[0] > 10000 && result.waits[0] <= 12000);
  assert.equal(result.calls.filter(call => call.url === broker.health_url).length, 2);
  assert.equal(result.calls.find(call => call.request.method === 'POST').url, broker.order_url);
  const order = JSON.parse(result.calls.find(call => call.request.method === 'POST').request.body);
  assert.match(order.customerId, /^scenario01-/);
  assert.deepEqual(order.items, broker.test_order.items);
  assert.equal(order.region, 'blue');
});

for (const [name, options] of [
  ['HTTP 500 despite healthy probes', { postStatus: 500 }],
  ['HTTP 200 without publication contract', { postStatus: 200 }],
  ['bad broker credentials', { queueStatus: 401 }],
  ['queue not running', { queueState: 'down' }],
  ['changed publisher code', { publisher: 'return without publishing' }],
  ['unhealthy service', { health: 'error' }],
  ['wrong queue', { queueName: 'other-queue' }],
  ['wrong vhost', { vhost: '/' }],
  ['missing configured credentials', { env: {} }],
]) {
  test(`rejects ${name}`, async () => {
    assert.equal((await exercise(options)).exitCode, 1);
  });
}