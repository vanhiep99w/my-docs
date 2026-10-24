# D2 request-flow authoring

Use `mode=flow` to explain **which route an authored request takes through one fixed topology**: cache hit/miss, retry, response or fallback. Use `steps` for evolving inherited boards, `tabs` for independent board variants, `animation` for D2 board animation, and SpanWaterfall for timing. Do not present playback as HTTP execution, a tracing backend or a general simulation engine.

## Contents

- [Check availability and integration](#check-availability-and-integration)
- [Author a complete scenario](#author-a-complete-scenario)
- [Preserve edge and scenario semantics](#preserve-edge-and-scenario-semantics)
- [Choose playback deliberately](#choose-playback-deliberately)
- [Validate the lesson](#validate-the-lesson)

## Check availability and integration

Inspect the host's installed `d2` plugin/types and component exports, not only the collection checkout. The local package version alone does not establish a published minimum version for `flow`; the feature can exist as local work before a consumer receives it. Do not claim that every `0.11.0` installation supports it or silently upgrade all sites.

Reuse `remarkD2`, the existing `d2` fence, `D2InteractiveDiagram` registration and `styles/d2.css`. Keep `D2Diagram` registered for explicit server-only diagrams. Do not invent a separate `request-flow` fence, `RequestFlow` component, React Flow dependency or new stylesheet.

Check canonical contracts in collection-root `docs-kit/src/d2/{index.ts,flow.ts}`, `docs-kit/docs/d2.md`, and `docs-kit/examples/d2/request-flow.d2`. Read them when an installed schema differs or a reference fails. If unsupported, report the integration blocker; use an ordinary D2 view plus prose only if that still answers the reader's question, never pretend it animates.

## Author a complete scenario

Place YAML metadata in a **leading D2 comment block**, before the topology. Keep every metadata line commented, delimit it with `# @flow` and `# @endflow`, and preserve YAML indentation.

This example teaches lookup routes only; it intentionally does not model cache population. Explain that scope in the lesson. Add populate and acknowledgement edges if teaching a full cache-fill cycle.

````mdx
```d2 mode=flow layout=dagre autoplay=true loop=true loopDelay=2000 interval=1600 title="Hai đường đọc dữ liệu"
# @flow
# scenarios:
#   - id: hit
#     label: Cache hit
#     steps:
#       - edge: "(client -> api)[0]"
#         description: API nhận request.
#       - edge: "(api -> cache)[0]"
#         description: API tra cache trước.
#       - edge: "(cache -> api)[0]"
#         description: Cache trả dữ liệu có sẵn.
#       - edge: "(api -> client)[0]"
#         description: API trả kết quả, không đọc database.
#   - id: miss
#     label: Cache miss
#     steps:
#       - edge: "(client -> api)[0]"
#         description: API nhận request.
#       - edge: "(api -> cache)[0]"
#         description: API kiểm tra cache.
#       - edge: "(cache -> api)[0]"
#         description: Cache báo chưa có dữ liệu.
#       - edge: "(api -> database)[0]"
#         description: API đọc database.
#       - edge: "(database -> api)[0]"
#         description: Database trả kết quả về API.
#       - edge: "(api -> client)[0]"
#         description: API trả kết quả cho client.
# @endflow
direction: right
client: Client
api: API
cache: Cache
database: Database {shape: cylinder}
client -> api: Request
api -> cache: Lookup
cache -> api: Hit / miss
api -> database: Query
database -> api: Result
api -> client: Response
```
````

Keep the decisive explanation in surrounding prose and each step's `description`; do not rely on a dot, color or hidden UI status to carry the lesson. Treat `layout=dagre` here as a deliberate choice for a cyclic request/response graph, not a new global default.

## Preserve edge and scenario semantics

- Give each scenario a unique `id`, a reader-facing `label` and ordered `steps`. Each step requires `edge` and `description`; optional `duration` overrides the default presentation interval.
- Reference the **normalized compiled D2 edge ID**, including its zero-based index. `api -> cache: Lookup` and a later `api -> cache: Populate` are `(api -> cache)[0]` and `(api -> cache)[1]`, not interchangeable labels. Do not reference a nonexistent reverse edge; declare responses/acks explicitly.
- Use `service.(api -> cache)[0]` for nested edges. Prefer simple node IDs; quoted IDs can be normalized by D2. Verify actual compiler IDs rather than guessing quoting or matching SVG order.
- Repeat an edge explicitly for a retry. Do not infer execution order or branch conditions from topology, edge labels or D2 `scenarios` boards. Flow scenarios are the YAML playback descriptor, not inherited D2 boards.
- Keep references in the selected `target` board. Current limits are 1–16 scenarios, 1–128 steps per scenario, 512 steps total and 64 KiB metadata; recheck source before relying on limits.
- Greyed-out nodes/edges are absent from **all steps of the selected scenario**, not merely waiting for their turn. Future steps stay part of the route; containers of used nodes stay enabled. This is visual exclusion, not disabled source links or proof of runtime unreachability.
- Describe one traversed edge at a time. Do not imply fork/join concurrency, automatic routing, payload mutation or executing service state. The point stays on lines and fades between ports; it does not animate an invented path through node interiors.

## Choose playback deliberately

- Leave `autoplay` and `loop` off unless motion helps the explanation. Both default to `false`; the example opts in explicitly.
- Use `interval` for default travel presentation time, `duration` for an individual step, and `loopDelay` for the pause between runs. Default interval is 1500 ms; default loop delay is 2000 ms. Bounds are 250–60000 ms; `interval` and `loopDelay` must be integers, while step `duration` must be finite. These are **not latency measurements**.
- Expect a short arrival hold and fades in addition to travel time. Speed changes playback, not the wall-clock replay delay.
- With autoplay enabled, selecting another scenario starts it from the beginning when visible and motion is allowed. Pause/Reset cancel pending replay; reduced motion and hidden tabs prevent automatic motion.
- Preserve the current implementation's fullscreen contract: same scenario, step, speed, point position, Play/Pause and remaining replay delay. Do not tell readers they must press Play again merely because they opened fullscreen.
- Keep labels/tooltips accessible. Current UI uses a compact header and icon controls inside the canvas; All steps and source open dismissable panels. Do not add article instructions tied to obsolete text buttons, a visible status row or fixed color meanings.

## Validate the lesson

Compile the actual MDX fence through the installed host integration; invalid metadata or edge references must fail with file/fence context. Never hand-author prepared flow props or SVG paths.

Test both scenarios, response direction, duplicate edges, excluded components, playback to every endpoint and manual Next/Previous. If opting into autoplay/loop, test scenario switches, Pause during the replay delay and fullscreen enter/exit. Check light/dark, narrow layouts and reduced motion. Verify the static SVG and all scenario explanations remain readable without JavaScript; downloaded SVG is static, not an exported running simulation.
