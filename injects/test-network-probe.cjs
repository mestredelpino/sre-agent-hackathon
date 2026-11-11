const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { EventEmitter } = require('node:events');
const { test } = require('node:test');
const { probe } = require('./network-probe.cjs');

test('probe reads actual HTTP codes without following redirects', async () => {
  const server = http.createServer((request, response) => {
    response.writeHead(Number(request.url.slice(1)), { Location: '/200' });
    response.end();
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    for (const status of [200, 302, 503]) {
      const result = await probe({ url: `http://127.0.0.1:${server.address().port}/${status}`, timeout_seconds: 2 });
      assert.equal(result.status, status);
    }
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
});

test('probe distinguishes allowed transport errors from DNS/TLS failures', async context => {
  for (const code of ['ECONNREFUSED', 'ECONNRESET', 'ENOTFOUND', 'CERT_HAS_EXPIRED']) {
    context.mock.method(http, 'get', () => {
      const request = new EventEmitter();
      process.nextTick(() => request.emit('error', Object.assign(new Error(code), { code })));
      return request;
    });
    if (['ECONNREFUSED', 'ECONNRESET'].includes(code)) {
      assert.deepEqual(await probe({ url: 'http://lab.test/', timeout_seconds: 2 }), { status: 0, error: code });
    } else await assert.rejects(probe({ url: 'http://lab.test/', timeout_seconds: 2 }), new RegExp(code));
    context.mock.restoreAll();
  }
});

test('probe has a bounded timeout for a nonresponding server', async context => {
  context.mock.method(http, 'get', () => {
    const request = new EventEmitter();
    request.destroy = () => {};
    return request;
  });
  assert.deepEqual(await probe({ url: 'http://lab.test/', timeout_seconds: 0.01 }), { status: 0, error: 'ETIMEDOUT' });
});

test('probe rejects credentials and non-HTTP protocols', async () => {
  for (const url of ['file:///tmp/example', 'https://user:password@lab.test/']) {
    await assert.rejects(probe({ url, timeout_seconds: 1 }), /without credentials/);
  }
});

test('probe executes when supplied through node stdin as kubectl does', () => {
  const result = spawnSync(process.execPath, ['-', JSON.stringify({ url: 'file:///tmp/example', timeout_seconds: 1 })],
    { input: fs.readFileSync(path.join(__dirname, 'network-probe.cjs')), encoding: 'utf8' });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /without credentials/);
});