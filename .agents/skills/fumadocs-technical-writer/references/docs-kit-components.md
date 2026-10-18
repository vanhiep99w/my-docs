# Docs-kit authoring reference

Use this guide after selecting a feature in the skill's decision table. Read only the relevant section. Schemas here match the inspected docs-kit source snapshot, not every installed consumer version. Paths starting with `docs-kit/` below are relative to the **collection root**; verify the host's installed exports and integration before copying examples.

## Contents

- [Integration contract](#integration-contract)
- [D2 diagrams and progressive views](#d2-diagrams-and-progressive-views)
  - [Icons from the D2 catalog](#icons-from-the-d2-catalog)
- [Code walkthrough versus diff](#code-walkthrough-versus-diff)
- [Terminal sessions](#terminal-sessions)
- [HTTP protocol exchanges](#http-protocol-exchanges)
- [Latency waterfalls](#latency-waterfalls)
- [Source Explorer and adapters](#source-explorer-and-adapters)
- [Validation and publication](#validation-and-publication)

## Integration contract

Keep these three layers aligned; preserve existing collections, plugins, registry entries and page-level overrides.

| Fence / feature | Build import from `@vanhiep99w/docs-kit/…` | Component import subpath | CSS subpath |
| --- | --- | --- | --- |
| `d2` | `d2`: `remarkD2` | `components/d2`: `D2Diagram`; `components/d2-interactive`: `D2InteractiveDiagram` for opt-in modes | `styles/d2.css` |
| `code-walkthrough` | `code-walkthrough`: `remarkCodeWalkthrough` | `components/code-walkthrough`: `CodeWalkthrough` | `styles/code-walkthrough.css` |
| `code-diff` | `code-diff`: `remarkCodeDiff` | `components/code-diff`: `CodeDiff` | `styles/code-diff.css` |
| `terminal-session` | `terminal-session`: `remarkTerminalSession` | `components/terminal-session`: `TerminalSession` | `styles/terminal-session.css` |
| `protocol-exchange` | `protocol-exchange`: `remarkProtocolExchange` | `components/protocol-exchange`: `ProtocolExchange` | `styles/protocol-exchange.css` |
| `span-waterfall` | `span-waterfall`: `remarkSpanWaterfall` | `components/span-waterfall`: `SpanWaterfall` | `styles/span-waterfall.css` |
| Source references | Host-owned asset generator; types/helpers in `source-explorer` | `components/source-explorer`: `SourceExplorerProvider`, `SourceRef`, optional `D2SourceLinks` | `styles/source-explorer.css`; optional `styles/source-explorer-fumadocs.css` |

For one feature, wire only what is missing. Example for a code walkthrough:

```ts
import { remarkCodeWalkthrough } from '@vanhiep99w/docs-kit/code-walkthrough';
// Append to the host's existing remarkPlugins array.
```

```tsx
import { CodeWalkthrough } from '@vanhiep99w/docs-kit/components/code-walkthrough';
// Add CodeWalkthrough to the host's existing MDX component map.
```

```css
@import '@vanhiep99w/docs-kit/styles/code-walkthrough.css';
```

Build helpers/parsers must stay in Node/build code, not client components. Prefer descriptor fences over constructing prepared JSX props manually. A fence renders only if its plugin and resulting component registration exist; having the npm dependency alone is insufficient.

Current exports do **not** include MarbleDiagram, ConcurrencyLanes, AnnotatedExample, DataInspector or StateTransitionExplorer. Do not revive those APIs or translate a task into a nonexistent component. Plain JSON, tables, ordinary code and truthful D2 views remain appropriate where no specialized current component fits.

## D2 diagrams and progressive views

Use `d2` for architecture, dependencies, decision/control flow, entity relationships, message ordering and state transitions. Start with the static default: a caption, readable labels, a small number of meaningful nodes and arrows whose semantics the prose explains.

````mdx
```d2 title="Cache-aside request path"
direction: right
client: Client
api: API
cache: Cache
database: Database {shape: cylinder}
client -> api: Request
api -> cache: Lookup
api -> database: Read on miss
api -> cache: Fill after read
```
````

The picture is a logical flow, not a measured trace. Explain conditions, ordering and failures in surrounding prose; use SpanWaterfall only when timing is actually the teaching point.

Choose opt-in behavior intentionally:

- `interactive`: zoom/pan/fit/expand for a diagram that benefits from exploration; do not enable just because it is available.
- `mode=steps`: successive **inherited** system states. Use CodeWalkthrough instead when the object being stepped through is source code.
- `mode=tabs`: alternative scenarios, each inheriting the base independently, not the preceding scenario.
- `mode=explorer`: layers/drill-down when one flat diagram would hide ownership or overload the reader.
- `mode=animation`: only when changing state over time is informative; require accessible static views and respect reduced motion. Do not use animation to imply live execution.

A minimal inherited-state example:

````mdx
```d2 mode=steps title="A cache entry is populated, then invalidated"
entry: Empty
steps: {
  populated: {entry: Present}
  invalidated: {entry: Empty}
}
```
````

Non-static modes emit `D2InteractiveDiagram`; register it alongside `D2Diagram` and keep the shared D2 CSS. The compiler/WASM runs at build time, never in the browser. Defaults use ELK; layout resolution is fence `layout` > page `d2Layout` > plugin option > ELK. If using page overrides, the host schema must retain `d2Layout`. Local images/imports/fonts and asset roots are host build configuration, not arbitrary paths for document authors to guess.

Canonical details: `docs-kit/docs/d2.md`, `docs-kit/README.md`, `docs-kit/examples/d2/`. Do not hide a large unreadable graph by shrinking the font; split it or choose purposeful layers/scenarios.

### Icons from the D2 catalog

Use https://icons.d2lang.com/ whenever an accurate icon helps the reader recognize a technology or service. Browse/search the catalog and verify the exact asset exists; do not construct a likely-looking path. Keep generic concepts unbranded and preserve text labels. For example, use the Redis icon for an actual Redis cache, not for every cache or database:

````mdx
```d2 title="API reads from a Redis cache"
direction: right
api: API
cache: Redis cache {
  icon: https://icons.d2lang.com/dev/redis.svg
}
api -> cache: Lookup
```
````

The URL above identifies the catalog asset; it does **not** prove the host embeds it. Before publishing:

1. Reuse an existing vetted copy/mapping where available. Otherwise verify the SVG/image, applicable license/attribution and the host's asset policy. Do not inline unreviewed SVG with scripts, event handlers or unexpected external resources.
2. Follow the host's vendoring convention, recording the source URL and checksum where required. Use its existing URL-rewrite plugin if authored catalog URLs are mapped to local assets.
3. For direct local D2 icons, configure an approved `assetsRoot` and use a path relative to the authored MD/MDX file, not the collection root or this skill. Keep roots small, inside the host cwd and free of symlinks. Verify options against the installed package and `docs-kit/docs/d2.md`.
4. Do not assume remote URLs are fetched, cached or embedded: docs-kit leaves them remote unless the host handles them. Prefer build-time embedding so exported pages do not require the catalog at reading time. Add missing integration only when in scope; otherwise report the external dependency or blocker.
5. Inspect exported light/dark diagrams, narrow screens and no-JavaScript views. When embedding is intended, confirm the resulting SVG contains the asset and does not fetch it remotely. Do not change renderer defaults or force icons onto every node just to add a logo.

## Code walkthrough versus diff

Choose **CodeWalkthrough** to guide attention through source/config snapshots. Steps name a snapshot and highlight one-based inclusive ranges in that snapshot; revisits are allowed. Every snapshot must be referenced by a step. Do not put prepared `tokens` in authored YAML.

````mdx
```code-walkthrough
title: Guard nullable input before trimming
language: typescript
snapshots:
  - id: guarded
    title: greet.ts
    code: |-
      function greet(name: string | null) {
        if (name === null) return 'guest';
        return name.trim();
      }
steps:
  - id: guard
    snapshot: guarded
    title: Handle null first
    description: Return before calling trim on a nullable value.
    ranges: [[1, 2]]
  - id: string
    snapshot: guarded
    title: Trim the remaining string
    description: This branch follows the guard; the viewer does not execute it.
    ranges: [[3, 3]]
```
````

General description metadata is not the explanation surface in the compact UI. Introduce context in prose and put step-specific reasoning in `steps[].description`.

Choose **CodeDiff** when the question is specifically what changed between two exact versions. Explain why the change is appropriate and its trade-off outside the viewer; the comparison itself is not a recommendation or a benchmark.

````mdx
```code-diff
title: Increase a hypothetical timeout budget
language: javascript
view: split
before:
  label: Before
  code: |-
    const timeoutMs = 100;
after:
  label: After
  code: |-
    const timeoutMs = 500;
```
````

These numbers are illustrative, not safe production defaults. A longer timeout can hold resources longer; explain the actual budget and evidence in the article. `wordDiff: true` is optional when token-level replacements matter, not a semantic-code analysis mode.

If adding annotations, ranges belong to the original `before` or `after` file, not the rendered diff row. Current CodeDiff does not display caption/annotation descriptions, so do not hide required reasoning there. `|-` preserves an intentionally missing final newline; choose YAML chomping deliberately instead of trimming code. Copy returns the entire original side, not a Git patch.

Canonical schemas/examples: `docs-kit/docs/code-walkthrough.md`, `docs-kit/docs/code-diff.md`, `docs-kit/examples/code-walkthrough/`, `docs-kit/examples/code-diff/`.

## Terminal sessions

Use **TerminalSession** for a procedure whose command context, output, warning or expected result matters. For a single self-explanatory install command, a normal language-labelled code block is enough.

````mdx
```terminal-session
title: Verify the local Node executable
context:
  kind: local
steps:
  - id: version
    command: node --version
    expected: The major version meets this repository's package.json engines requirement.
```
````

`context.kind` is local/container/pod/remote; labels and cwd describe the execution environment. A step context override replaces the whole context, not just one field. `command` is raw copyable input without the prompt; use a separate `prompt` when useful.

Add observed or explicitly labelled illustrative `outputs` as an ordered array of `{stream: stdout|stderr, text}`, optional `collapsed`, and optional step `exitCode`. Do not invent an observed exit code/output or imply that an empty expected-result statement verifies execution. ANSI/control sequences are not supported: use readable plain text, not encoded terminal colors. Put destructive-command scope and recovery before the command, even if a warning is also present inside the descriptor.

Canonical contract/examples: `docs-kit/docs/terminal-session.md`, `docs-kit/examples/terminal-session/`.

## HTTP protocol exchanges

Use **ProtocolExchange** for actual HTTP message structure and independent success/error variants. Use D2 separately for participants and ordering across services when that is a different question. Non-HTTP messages stay ordinary code/JSON or D2; do not pretend Kafka/SQL is HTTP.

````mdx
```protocol-exchange
title: Profile lookup outcomes
variants:
  - id: ok
    title: Found
    request:
      method: GET
      url: /profiles/demo
    response:
      status: 200
      headers:
        - id: content-type
          name: Content-Type
          value: application/json
      body:
        kind: json
        json: '{"id":9007199254740993,"name":"Demo"}'
  - id: missing
    title: Not found
    request: {method: GET, url: /profiles/missing}
    response: {status: 404}
```
````

Headers are ordered `{id, name, value}` arrays; repeated names are allowed with separate IDs. JSON body input is a strict JSON string; do not convert large numeric lexemes through JavaScript Number. Omit body for HEAD and no-content statuses such as 204/304. Missing body and empty body mean different things.

Descriptions/annotations retained for compatibility are not rendered by the compact UI. Place authentication assumptions, idempotency semantics, redirect behavior and error interpretation in nearby prose. This is a static transcript viewer, not an HTTP client, cURL runner or credential store. Use fake credentials and `example.invalid` for illustrative external URLs.

Canonical contract/examples: `docs-kit/docs/protocol-exchange.md`, `docs-kit/examples/protocol-exchange/`.

## Latency waterfalls

Use **SpanWaterfall** for start/duration, overlap, service attribution and parent relationships on a shared time origin. Do not repurpose it for untimed concurrency/state lanes or fabricate measurements to make a component fit.

````mdx
```span-waterfall
title: A hypothetical cache lookup inside a request
unit: ms
provenance:
  kind: illustrative
  description: Synthetic values for teaching; not a measured trace or benchmark.
spans:
  - id: request
    name: GET /profiles/demo
    service: api
    start: 0
    duration: 40
    status: ok
  - id: cache
    parent: request
    name: Cache lookup
    service: redis
    start: 5
    duration: 8
    status: ok
    attributes: '{"cache.hit":true}'
```
````

`unit` is ms/us/s; all starts share one origin. `provenance` is required and says illustrative/measured plus a description. Times must be finite and nonnegative; IDs/parents must resolve without cycles. Attributes are strict JSON strings. Parent/child timing and visual row order do not prove causality or a critical path. Never sum overlapping durations to claim total request latency. Preserve clock-skew/asynchronous caveats rather than silently altering timestamps.

Canonical contract/examples: `docs-kit/docs/span-waterfall.md`, `docs-kit/examples/span-waterfall/`.

## Source Explorer and adapters

Use **SourceRef** when readers need surrounding implementation, multiple files, an alternate snapshot or named region beyond the inline example. Reuse the host's manifest generator rather than creating a second copy of the project as a teaching artifact.

```mdx
<SourceRef project="demo" snapshot="main" file="src/greet.ts" lines="1-4">
  Open the full implementation
</SourceRef>
```

This reference is schematic: replace project/snapshot/file/range with real generator-validated assets before publishing. `region` and `lines` are mutually exclusive; lines are one-based inclusive. Do not invent a manifest entry to make a broken reference appear valid.

The host needs `SourceExplorerProvider`, `SourceRef` in its MDX map, CSS and generated JSON assets. With Next routing, pass pathname as `navigationKey`, not the changing source query. The package does not generate the manifest, read arbitrary source files or guarantee that inline code matches a snapshot; the host pipeline must check those contracts.

Optional `components/code-diff-source` and `components/code-walkthrough-source` adapters open the proper side/snapshot; register the emitted adapter if the installed plugin selects it. D2 source links need the host's `D2SourceLinks` bridge/provider. Do not attach a drawer dependency to every base learning component. Source HTML is trusted build-time highlighted output, not a sanitizer; publish only reviewed non-secret code.

Canonical integration/data contract: Source Explorer sections of `docs-kit/README.md`; inspect the selected host's source generator and focused reference/navigation tests.

## Validation and publication

1. Check the installed feature's actual parser/export, MDX registry and CSS; use existing repository tests where present.
2. Compile the touched docs/fences. Unknown YAML fields, duplicate IDs, invalid ranges or missing references should fail with file/fence context; do not suppress failures by turning descriptors into raw code.
3. Verify prose plus component still make sense with no JavaScript. Inspect dark/light and narrow layouts; preserve readable font size and intentional horizontal scrolling.
4. Check copy targets, disclosure, step selection, source/deep links and keyboard controls for the chosen features. All folded/unselected data remains public.
5. Report what was actually run versus hypothetical or blocked. Rendering does not prove commands, HTTP semantics, code correctness or performance claims.
