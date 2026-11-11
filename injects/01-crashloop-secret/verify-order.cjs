'use strict';

const assert = require('node:assert/strict');
const { randomUUID } = require('node:crypto');
const { readFileSync } = require('node:fs');
const { setTimeout: wait } = require('node:timers/promises');

const broker = JSON.parse(process.argv[2]);
const timing = JSON.parse(process.argv[3]);
const timeoutMatch = /^(\d+(?:\.\d+)?)(ms|s|m|h)?$/.exec(String(timing.request));
assert(timeoutMatch, 'Invalid request timeout');
const requestTimeout = Number(timeoutMatch[1]) * ({ ms: 1, s: 1000, m: 60000, h: 3600000 }[timeoutMatch[2] || 's']);

async function request(url, options = {}) {
  const response = await fetch(url, { ...options, signal: AbortSignal.timeout(requestTimeout) });
  assert(response.ok, `HTTP ${response.status} from ${new URL(url).pathname}`);
  return response;
}

async function main() {
  const start = Date.now();
  const publisher = readFileSync(broker.publisher_path, 'utf8');
  const route = readFileSync(broker.route_path, 'utf8');
  assert(publisher.includes('const publishResult = await publisher.publish(') &&
    publisher.includes('publishResult.outcome === rabbit.OutcomeState.ACCEPTED') &&
    publisher.includes('throw new Error(`message not accepted by RabbitMQ'),
  'Broker acknowledgement contract changed; inspect the running publisher');
  assert(/await fastify\.sendMessage\([\s\S]*?reply\.code\(201\)/.test(route),
    'Order response contract changed; inspect the running route');
  const queue = broker.queue;
  assert(process.env[broker.username_env] && process.env[broker.password_env], 'Missing broker credentials');
  const authorization = 'Basic ' + Buffer.from(
    `${process.env[broker.username_env]}:${process.env[broker.password_env]}`
  ).toString('base64');
  const queueURL = `${broker.management_url.replace(/\/$/, '')}/queues/${encodeURIComponent(broker.vhost)}/${encodeURIComponent(queue)}`;
  async function checkQueue() {
    const data = await (await request(queueURL, { headers: { authorization } })).json();
    assert.equal(data.name, queue);
    assert.equal(data.state, 'running');
    assert.equal(data.vhost, broker.vhost);
  }
  const health = await (await request(broker.health_url)).json();
  assert.equal(health.status, 'ok');
  await checkQueue();
  const customerId = `scenario01-${randomUUID()}`;
  const response = await request(broker.order_url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...broker.test_order, customerId }),
  });
  assert.equal(response.status, 201, 'Expected RabbitMQ ACCEPTED response path');
  await checkQueue();
  console.log(`Order ${customerId}: HTTP 201 after RabbitMQ ACCEPTED; ${queue} queue running`);
  await wait(Math.max(0, Number(timing.stability) * 1000 - (Date.now() - start)));
  assert.equal((await (await request(broker.health_url)).json()).status, 'ok');
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });