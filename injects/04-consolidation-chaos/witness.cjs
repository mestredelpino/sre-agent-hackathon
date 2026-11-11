'use strict';
const assert = require('node:assert/strict');
const action = process.argv[2];
const broker = JSON.parse(process.argv[3]);
const settings = JSON.parse(process.argv[4]);
const duration = /^(\d+(?:\.\d+)?)(ms|s|m|h)$/.exec(settings.timing.request);
assert(duration, 'Configure timing.request as a positive duration with ms, s, m or h units');
const timeout = Number(duration[1]) * { ms: 1, s: 1000, m: 60000, h: 3600000 }[duration[2]];
assert(timeout > 0 && Number.isSafeInteger(timeout), 'timing.request must resolve to positive integer milliseconds');
assert(process.env[broker.username_env] && process.env[broker.password_env], 'Configured broker credentials are missing');
const authorization = 'Basic ' + Buffer.from(
  `${process.env[broker.username_env]}:${process.env[broker.password_env]}`
).toString('base64');
const root = broker.management_url.replace(/\/$/, '');
const queue = settings.scenario.witness_queue;
const vhost = encodeURIComponent(broker.vhost);
async function request(path, method = 'GET', body) {
  return fetch(root + path, { method, headers: { authorization, 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(timeout) });
}
async function main() {
  const queuePath = '/queues/' + vhost + '/' + encodeURIComponent(queue);
  if (action === 'seed') {
    assert((await request(queuePath, 'PUT', { durable: true, auto_delete: false, arguments: {} })).ok);
    const response = await request('/exchanges/' + vhost + '/amq.default/publish', 'POST', {
      properties: { delivery_mode: 2 }, routing_key: queue,
      payload: 'scenario04-order-durability-witness', payload_encoding: 'string',
    });
    assert(response.ok);
    assert.equal((await response.json()).routed, true);
    console.log('Durable witness message routed to isolated queue');
  } else if (action === 'lost') {
    const response = await request(queuePath);
    assert.equal(response.status, 404, 'Witness queue still exists; data loss not demonstrated');
    console.log('Witness queue and message lost after broker replacement');
  } else if (action === 'delete') {
    const response = await request(queuePath, 'DELETE');
    assert(response.ok || response.status === 404);
  } else {
    throw new Error('Unknown witness action');
  }
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });