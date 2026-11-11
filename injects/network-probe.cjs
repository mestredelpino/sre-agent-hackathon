const http = require('node:http');
const https = require('node:https');

function probe(options) {
  return new Promise((resolve, reject) => {
    const url = new URL(options.url);
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) {
      reject(new Error('Expected HTTP(S) URL without credentials'));
      return;
    }
    const transport = url.protocol === 'https:' ? https : http;
    let finished = false;
    const finish = (result, error) => {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      if (error) reject(error);
      else resolve(result);
    };
    const request = transport.get(url, { agent: false }, response => {
      finish({ status: response.statusCode });
      response.destroy();
    });
    const timer = setTimeout(() => {
      finish({ status: 0, error: 'ETIMEDOUT' });
      request.destroy();
    }, options.timeout_seconds * 1000);
    request.on('error', error => {
      if (['ETIMEDOUT', 'ECONNREFUSED', 'ECONNRESET'].includes(error.code)) {
        finish({ status: 0, error: error.code });
      } else finish(null, error);
    });
  });
}

module.exports = { probe };
if (require.main === module || process.argv[1] === '-') {
  probe(JSON.parse(process.argv[2])).then(result => console.log(JSON.stringify(result))).catch(error => {
    console.error(error.message);
    process.exitCode = 1;
  });
}