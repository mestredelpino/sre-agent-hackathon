import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { checkAllAssets, checkSreAgentArchitecture, checkSreAgentPresentation, diagramDirectory } from './contract.mjs';
import { withRenderer } from './render.mjs';
import { views } from './views.mjs';

checkSreAgentArchitecture();
checkSreAgentPresentation();
if (process.argv.includes('--source-only')) {
  console.log('PASS: SRE Agent architecture source routes, trigger states, retrieval and identity boundaries');
  process.exit(0);
}
checkAllAssets();
console.log(`PASS: ${views.length} editable draw.io/SVG pairs, exact embedded source, connected technical routes, icon hashes, notices and accessible self-contained exports`);

if (process.argv.includes('--browser')) {
  await withRenderer(async page => {
    const screenshots = mkdtempSync(join(tmpdir(), 'sre-drawio-review-'));
    for (const view of views) {
      await page.setViewport({ width: view.width, height: view.height });
      await page.goto(pathToFileURL(join(diagramDirectory, `${view.id}.svg`)).href);
      await page.evaluate(() => document.fonts.ready);
      const failures = await page.evaluate(async () => {
        const failures = [];
        const svg = document.documentElement;
        const width = Number(svg.getAttribute('width'));
        const height = Number(svg.getAttribute('height'));
        const labels = [...svg.querySelectorAll('text')];
        for (const [index, label] of labels.entries()) {
          const box = label.getBoundingClientRect();
          if (box.x < -1 || box.y < -1 || box.x + box.width > width + 1 || box.y + box.height > height + 1) failures.push(`Clipped label: ${label.textContent}`);
          const owner = label.closest('[data-box]');
          if (owner?.getAttribute('data-kind') === 'node') {
            const [horizontal, vertical, nodeWidth, nodeHeight] = owner.getAttribute('data-box').split(' ').map(Number);
            if (box.x < horizontal - 1 || box.y < vertical - 1 || box.x + box.width > horizontal + nodeWidth + 1 || box.y + box.height > vertical + nodeHeight + 1) failures.push(`Label outside node: ${label.textContent}`);
          }
          for (const other of labels.slice(index + 1)) {
            const neighbor = other.getBoundingClientRect();
            if (Math.min(box.x + box.width, neighbor.x + neighbor.width) - Math.max(box.x, neighbor.x) > 1 && Math.min(box.y + box.height, neighbor.y + neighbor.height) - Math.max(box.y, neighbor.y) > 1) failures.push(`Labels overlap: ${label.textContent} / ${other.textContent}`);
          }
        }
        if (svg.querySelector('#sre-agent-architecture-title')) {
          for (const path of svg.querySelectorAll('[data-cell-id^="edge-"] path[fill="none"]')) {
            const length = path.getTotalLength();
            for (const label of labels) {
              const box = label.getBBox();
              for (let distance = 0; distance <= length; distance += 3) {
                const point = path.getPointAtLength(distance);
                if (point.x > box.x && point.x < box.x + box.width && point.y > box.y && point.y < box.y + box.height) {
                  failures.push(`Route crosses label: ${label.textContent}`);
                  break;
                }
              }
            }
          }
        }
        for (const image of svg.querySelectorAll('image')) {
          const reference = image.getAttribute('href') || image.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
          const bitmap = new Image();
          bitmap.src = reference;
          await bitmap.decode();
          const canvas = document.createElementNS('http://www.w3.org/1999/xhtml', 'canvas');
          canvas.width = canvas.height = 40;
          const context = canvas.getContext('2d');
          context.drawImage(bitmap, 0, 0, 40, 40);
          const pixels = context.getImageData(0, 0, 40, 40).data;
          if (!pixels.some((value, index) => index % 4 === 3 && value > 0)) failures.push('Blank icon');
          const imageBox = image.getBoundingClientRect();
          for (const text of image.closest('[data-cell-id]').querySelectorAll('text')) {
            const textBox = text.getBoundingClientRect();
            if (Math.min(imageBox.x + imageBox.width, textBox.x + textBox.width) - Math.max(imageBox.x, textBox.x) > 1 && Math.min(imageBox.y + imageBox.height, textBox.y + textBox.height) - Math.max(imageBox.y, textBox.y) > 1) failures.push(`Icon overlaps label: ${text.textContent}`);
          }
        }
        return failures;
      });
      await page.screenshot({ path: join(screenshots, `${view.id}.png`) });
      assert.deepEqual(failures, [], `${view.id}: SVG label, node and icon bounds`);
      const source = readFileSync(join(diagramDirectory, `${view.id}.drawio`), 'utf8');
      const decoded = await page.evaluate(source => {
        const documentXml = new DOMParser().parseFromString(source, 'application/xml');
        return { errors: documentXml.querySelectorAll('parsererror').length, edges: [...documentXml.querySelectorAll('mxCell[edge="1"]')].every(cell => cell.hasAttribute('source') && cell.hasAttribute('target')) };
      }, source);
      assert.deepEqual(decoded, { errors: 0, edges: true });
      console.log(`PASS: ${view.id}: XML, label/node bounds, no text/icon overlap, rendered nonblank icons`);
    }
    console.log(`Visual review screenshots: ${screenshots}`);
  });
}