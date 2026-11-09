import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const webapp = process.env.DRAWIO_WEBAPP || 'C:/Users/carlosmes/.vscode/extensions/hediet.vscode-drawio-1.19.0/drawio/src/main/webapp';
const marpRoot = process.env.MARP_CLI_ROOT || join(process.env.APPDATA || '', 'npm/node_modules/@marp-team/marp-cli');
const require = createRequire(join(resolve(marpRoot), 'package.json'));
const puppeteer = require('puppeteer-core');

export async function withRenderer(action) {
  const browser = await puppeteer.launch({
    executablePath: process.env.BROWSER_PATH || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true,
  });
  try {
    const page = await browser.newPage();
    await page.setContent('<!doctype html><html><body><div id="graph"></div></body></html>');
    await page.evaluate(() => {
      globalThis.mxLoadResources = false;
      globalThis.mxLoadStylesheets = false;
    });
    await page.addScriptTag({ content: readFileSync(join(webapp, 'mxgraph/mxClient.js'), 'utf8') });
    return await action(page, webapp);
  } finally {
    await browser.close();
  }
}

export async function renderDiagram(page, definition, icons) {
  return page.evaluate(({ definition, icons }) => {
    mxConstants.LINE_HEIGHT = 1.5;
    const graph = new mxGraph(document.getElementById('graph'));
    graph.setHtmlLabels(false);
    const parent = graph.getDefaultParent();
    const cells = {};
    graph.getModel().beginUpdate();
    for (const node of definition.nodes) {
      const base = node.kind === 'note'
        ? 'text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;'
        : node.kind === 'boundary'
          ? 'rounded=0;fillColor=#eef4f8;strokeColor=#d9e2e8;align=left;verticalAlign=top;spacingTop=12;spacingLeft=16;'
          : 'rounded=1;arcSize=6;fillColor=#ffffff;strokeColor=#0078d4;strokeWidth=1.5;align=center;verticalAlign=middle;';
      const image = node.icon ? `shape=label;image=${icons[node.icon]};imageWidth=36;imageHeight=36;imageAlign=left;spacingLeft=48;spacingRight=6;` : '';
      cells[node.id] = graph.insertVertex(parent, node.id, node.label, node.x, node.y, node.w, node.h,
        `${base}fontFamily=Segoe UI;fontSize=${node.font || 22};fontColor=#201f1e;whiteSpace=wrap;html=0;${image}`);
    }
    for (const [index, edge] of definition.edges.entries()) {
      const control = edge.kind === 'control';
      const style = `edgeStyle=none;rounded=0;endArrow=block;endFill=1;strokeWidth=2;strokeColor=${control ? '#107c10' : '#0078d4'};${control ? 'dashed=1;dashPattern=8 5;' : ''}exitX=${edge.exit?.[0] ?? 1};exitY=${edge.exit?.[1] ?? 0.5};entryX=${edge.entry?.[0] ?? 0};entryY=${edge.entry?.[1] ?? 0.5};exitPerimeter=0;entryPerimeter=0;`;
      const cell = graph.insertEdge(parent, `edge-${index}`, '', cells[edge.from], cells[edge.to], style);
      cell.geometry.points = (edge.points || []).map(([horizontal, vertical]) => new mxPoint(horizontal, vertical));
    }
    graph.getModel().endUpdate();
    const documentXml = mxUtils.createXmlDocument();
    const mxfile = documentXml.createElement('mxfile');
    mxfile.setAttribute('host', 'app.diagrams.net');
    mxfile.setAttribute('agent', 'Workshop architecture generator / bundled mxGraph');
    const diagram = documentXml.createElement('diagram');
    diagram.setAttribute('id', definition.id);
    diagram.setAttribute('name', definition.title);
    const model = new mxCodec(documentXml).encode(graph.getModel());
    model.setAttribute('page', '1');
    model.setAttribute('pageScale', '1');
    model.setAttribute('pageWidth', definition.width);
    model.setAttribute('pageHeight', definition.height);
    diagram.appendChild(model);
    mxfile.appendChild(diagram);
    documentXml.appendChild(mxfile);
    const source = mxUtils.getXml(documentXml);
    graph.getModel().clear();
    new mxCodec(mxUtils.parseXml(source)).decode(mxUtils.parseXml(source).querySelector('mxGraphModel'), graph.getModel());
    graph.view.validate();
    const svgDocument = mxUtils.createXmlDocument();
    const namespace = 'http://www.w3.org/2000/svg';
    const svg = svgDocument.createElementNS(namespace, 'svg');
    svg.setAttribute('width', definition.width);
    svg.setAttribute('height', definition.height);
    svg.setAttribute('viewBox', `0 0 ${definition.width} ${definition.height}`);
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-labelledby', `${definition.id}-title ${definition.id}-desc`);
    svg.setAttribute('content', source);
    for (const [tag, value] of [['title', definition.title], ['desc', definition.description]]) {
      const child = svgDocument.createElementNS(namespace, tag);
      child.setAttribute('id', `${definition.id}-${tag}`);
      child.textContent = value;
      svg.appendChild(child);
    }
    const group = svgDocument.createElementNS(namespace, 'g');
    svg.appendChild(group);
    svgDocument.appendChild(svg);
    const canvas = new mxSvgCanvas2D(group);
    canvas.foEnabled = false;
    const exporter = new mxImageExport();
    const drawCellState = exporter.drawCellState;
    exporter.drawCellState = function (state, target) {
      const previous = target.root;
      const cellGroup = svgDocument.createElementNS(namespace, 'g');
      cellGroup.setAttribute('data-cell-id', state.cell.id);
      const definitionNode = definition.nodes.find(node => node.id === state.cell.id);
      if (definitionNode) {
        cellGroup.setAttribute('data-kind', definitionNode.kind || 'node');
        cellGroup.setAttribute('data-box', [definitionNode.x, definitionNode.y, definitionNode.w, definitionNode.h].join(' '));
      }
      previous.appendChild(cellGroup);
      target.root = cellGroup;
      drawCellState.call(this, state, target);
      target.root = previous;
    };
    exporter.drawState(graph.getView().getState(graph.getModel().root), canvas);
    for (const image of svg.querySelectorAll('image')) {
      const reference = image.getAttribute('href') || image.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
      if (!reference?.startsWith('data:image/svg+xml,')) throw new Error(`Non-embedded icon: ${reference}`);
      const embedded = `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(decodeURIComponent(reference.slice('data:image/svg+xml,'.length)))))}`;
      image.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', embedded);
    }
    graph.destroy();
    return { source, svg: mxUtils.getXml(svg), vertices: definition.nodes.length, edges: definition.edges.length };
  }, { definition, icons });
}

if (process.argv.includes('--smoke')) {
  await withRenderer(async page => {
    const result = await page.evaluate(() => {
      const graph = new mxGraph(document.getElementById('graph'));
      graph.insertVertex(graph.getDefaultParent(), 'probe', 'Editable renderer probe', 10, 10, 300, 60);
      const xml = mxUtils.getXml(new mxCodec().encode(graph.getModel()));
      return { xml, vertices: graph.getChildVertices(graph.getDefaultParent()).length, svg: graph.getSvg ? true : false };
    });
    assert.equal(result.vertices, 1);
    assert.match(result.xml, /mxGraphModel/);
    console.log('PASS: bundled mxGraph renderer creates and encodes an editable vertex', result.svg);
  });
}