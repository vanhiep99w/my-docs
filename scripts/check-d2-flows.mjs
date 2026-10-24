#!/usr/bin/env node
/** Compile every flow fence with its host's installed package and production remark plugins.
 * Run preparation hooks first for sites whose content/docs is generated. No root npm install.
 */
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { assertFlowTopology } from './d2-flow-policy.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const worker = args[0] === '--host';

async function files(dir) {
  const result = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) result.push(...await files(file));
    else if (/\.mdx?$/.test(entry.name)) result.push(file);
  }
  return result.sort();
}
function collect(node, predicate) {
  return [ ...(predicate(node) ? [node] : []), ...(node.children ?? []).flatMap(child => collect(child, predicate)) ];
}
function props(node) {
  return Object.fromEntries(node.attributes.map(({ name, value }) => {
    if (!value || typeof value !== 'object') return [name, value];
    const expression = value.data.estree.body[0].expression;
    return [name, expression.type === 'Literal' ? expression.value : JSON.parse(expression.arguments[0].value)];
  }));
}

if (worker) {
  const host = path.resolve(root, args[1]);
  assert.equal(path.dirname(host), root, 'host must be an immediate child repository');
  process.chdir(host);
  const require = createRequire(path.join(host, 'package.json'));
  const load = specifier => import(pathToFileURL(require.resolve(specifier)).href);
  const [{ unified }, { default: remarkParse }, { default: remarkFrontmatter }, { default: config }] = await Promise.all([
    load('unified'), load('remark-parse'), load('remark-frontmatter'), import(pathToFileURL(path.join(host, 'source.config.ts')).href),
  ]);
  const configured = config.mdxOptions.remarkPlugins;
  const plugins = typeof configured === 'function' ? configured([]) : configured;
  const processor = unified().use(remarkParse).use(remarkFrontmatter, ['yaml']).use(plugins);
  const [{ createElement }, { renderToStaticMarkup }, { D2InteractiveDiagram }] = await Promise.all([
    load('react'), load('react-dom/server'), load('@vanhiep99w/docs-kit/components/d2-interactive'),
  ]);
  let pages = 0, diagrams = 0, scenarios = 0, steps = 0;
  // Aggregates are also maintained sources in Microservices, although its preparer
  // publishes the standalone pattern lessons instead of some aggregate sections.
  const paths = args[1] === 'microservice-learn'
    ? (await import(pathToFileURL(path.join(host, 'scripts/diagram-inventory.mjs')).href)).sourceDocuments(host).then(names => names.map(name => path.join(host, name)))
    : files(path.join(host, 'content/docs'));
  for (const file of await paths) {
    const value = await readFile(file, 'utf8');
    if (!value.includes('mode=flow')) continue;
    const tree = processor.parse(value);
    const expected = collect(tree, node => node.type === 'code' && node.lang === 'd2' && /\bmode=flow\b/.test(node.meta ?? ''));
    if (!expected.length) continue;
    for (const node of expected) assertFlowTopology(node.value, `${file}:${node.position.start.line}`);
    // Preserve page frontmatter/layout, but do not recompile unrelated learning examples.
    tree.children = [...tree.children.filter(node => node.type === 'yaml'), ...expected];
    const output = await processor.run(tree, { path: file, value });
    const nodes = collect(output, node => node.type === 'mdxJsxFlowElement' && node.name === 'D2InteractiveDiagram');
    assert.equal(nodes.length, expected.length, `${file}: every flow needs the interactive viewer`);
    for (const node of nodes) {
      const p = props(node);
      assert.equal(p.mode, 'flow', file);
      assert.ok(p.flow?.scenarios.length, `${file}: missing prepared scenarios`);
      const html = renderToStaticMarkup(createElement(D2InteractiveDiagram, p));
      for (const svg of [p.lightSvg, p.darkSvg]) {
        assert.match(svg, /data-d2-flow-edge=/, `${file}: mapped edges in both themes`);
        assert.match(svg, /data-d2-flow-node=/, `${file}: mapped nodes in both themes`);
      }
      // Essential explanations must exist in server output, not only in hydrated controls.
      for (const scenario of p.flow.scenarios) {
        const escape = text => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#x27;');
        assert.ok(html.includes(escape(scenario.label)), `${file}: no-JS scenario label`);
        for (const step of scenario.steps) assert.ok(html.includes(escape(step.description)), `${file}: no-JS step ${step.edge}`);
        scenarios++;
        steps += scenario.steps.length;
      }
      diagrams++;
    }
    pages++;
  }
  // Zero flows is valid: this host may contain only ordinary sequence diagrams.
  console.log(JSON.stringify({ repo: args[1], pages, diagrams, scenarios, steps }));
} else {
  const requested = [];
  for (let i = 0; i < args.length; i++) {
    assert.equal(args[i], '--repo', 'usage: node scripts/check-d2-flows.mjs [--repo NAME ...]');
    assert.ok(args[i + 1], '--repo needs a name');
    requested.push(args[++i]);
  }
  const repos = requested.length ? requested : ['angular-learn', 'graphql-learn', 'interview-question', 'java-learn', 'jenkins-learn', 'k8s-learn', 'kafka-learn', 'micro-frontend-learn', 'microservice-learn', 'multi-tenant', 'react-learn', 'redis-learn', 'sql', 'system-design-practice'];
  let failures = 0;
  for (const repo of repos) {
    const result = spawnSync(process.execPath, [fileURLToPath(import.meta.url), '--host', repo], { cwd: root, stdio: 'inherit', timeout: 300_000 });
    if (result.status !== 0) { failures++; console.error(`${repo}: flow validation failed`, result.error?.message ?? ''); }
  }
  if (failures) process.exitCode = 1;
}
