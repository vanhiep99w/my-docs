---
name: fumadocs-technical-writer
description: Write, revise or restructure Vietnamese or English technical documentation for Fumadocs sites using docs-kit components. Use for architecture/design docs, API references, runbooks, tutorials and MD/MDX lessons; choose D2 diagrams/request-flow playback, CodeWalkthrough, CodeDiff, TerminalSession, ProtocolExchange, SpanWaterfall, Source Explorer, Example Explorer (ExampleRef) and LiveDemo according to the reader's question. Also use when replacing legacy Mermaid or ASCII diagrams with docs-kit. Do not use for marketing copy or Word/PDF/PPTX deliverables.
---

# Fumadocs Technical Writer

Write clear, evidence-based technical documentation with **docs-kit for diagrams and technical learning examples**, plus Fumadocs components for document structure. Choose the smallest component that helps the reader answer a concrete question; do not decorate every paragraph with a viewer.

## Shared skill and host preflight

Use this single skill from the collection root's `.agents/skills/`; do not recreate per-repository copies. Resolve `references/...` relative to this skill directory. Confirm the target repository and page before editing; do not write curriculum pages into the collection root or the landing repo `docs/`. Keep all skills under `aws-learn/` unchanged.

Read applicable rules, adjacent lessons, metadata, `package.json`/lockfile, preparation hooks, `source.config.*`, the actual MDX registry and global styles. Follow the host's authoring source and conventions: some sites generate `content/docs` from root Markdown, others author there directly; frontmatter, H1 and manual TOC handling differ. Use `../../../wiki/content-pipeline.md` as an authority map, then verify source when necessary.

Inspect `../../../docs-kit/package.json`, its README and the host's **installed** package exports/version before using a component. Local source or a manifest range does not prove that API is installed or published; a new D2 mode may exist locally before consumers receive it. Check actual capabilities instead of prescribing a stale version or inventing a minimum release. Do not upgrade every repository as part of a writing task.

## Workflow

1. **Locate the canonical source and doc type.** Identify the reader's problem, prerequisites and desired outcome. Read only the relevant template in `references/doc-structures.md`.
2. **Plan explanations and visuals together.** For each visual, name the question it answers and select from the decision table below. Use matching icons from https://icons.d2lang.com/ whenever they accurately identify a depicted technology/service and make the diagram easier to understand. Introduce the visual in prose, then explain the decisive behavior afterward.
3. **Verify integration before authoring.** Read the selected section of [docs-kit components](references/docs-kit-components.md). Fences need their remark plugin, emitted MDX component and CSS; Source Explorer also needs provider/generated assets/reference checks. For request playback, read [D2 flow](references/d2-flow.md). For real apps, read [live examples](references/live-examples.md): Example Explorer needs a host registry/provider, ExampleRef and CSS, while LiveDemo needs JSX registration/CSS only. Neither iframe feature needs a remark plugin. Do not guess schemas, imports or deployment URLs.
4. **Write the actual file.** Match `.md`/`.mdx` and the host's frontmatter/heading conventions; preserve page identity, links and `meta.json` ordering. Keep technical names/code accurate and follow the voice/readability rules below.
5. **Validate the selected features.** Run focused descriptor/MDX checks, the host's build when permitted, and inspect export/browser behavior relevant to the change. Check light/dark, narrow screens, no-JavaScript readability and copy/source links where applicable. Report checks actually run and remaining limitations; never deploy merely to validate prose.

If docs-kit or the selected feature is missing, identify the minimum dependency/plugin/component/CSS work. Make that integration only when it is in scope; otherwise ask for approval or clearly report the blocker and provide prose/tables without claiming a working diagram. **Never fall back to a Mermaid fence, Mermaid JSX component, hand-drawn ASCII/Unicode box-and-arrow diagram or screenshot of a diagram.** When migrating a legacy diagram, preserve its semantics and meaningful labels in D2 rather than copying syntax mechanically. Do not remove a renderer/dependency still used by unrelated pages.

## Choose components by the reader's question

| Reader needs to understand | Use | Avoid |
| --- | --- | --- |
| Components, ownership, dependencies, request flow, decisions or state transitions | D2 through `remarkD2`; static `D2Diagram` for a small view | Mermaid/ASCII diagrams, or inventing a state-machine viewer API |
| A large diagram, evolving system state, alternative scenarios or drill-down | `D2InteractiveDiagram`: current D2 fences use the viewer by default; choose `mode=steps`, `tabs` or `explorer` intentionally, `interactive=false` for server-only | Assuming old static defaults; treating inherited steps and independent scenarios as equivalent |
| A request traversing a fixed topology under different authored scenarios | D2 `mode=flow`, with leading comment-YAML scenarios and exact edge IDs; see `references/d2-flow.md` | A separate RequestFlow API, inferring runtime branches, or presenting playback speed as measured latency |
| Why particular lines of code/config matter, one step at a time | `CodeWalkthrough` / `code-walkthrough` with snapshots and ordered steps | A walkthrough for a single self-explanatory snippet; confusing code snapshots with runtime state |
| What changed between two versions and which side/lines changed | `CodeDiff` / `code-diff` | Manually drawing +/− tables; using a diff to teach a many-step control flow |
| Which command to run in which environment, expected stdout/stderr, warnings and exit code | `TerminalSession` / `terminal-session` | A terminal-shaped architecture diagram; claiming displayed output was executed |
| HTTP request/response method, status, ordered headers, bodies and error variants | `ProtocolExchange` / `protocol-exchange` | A generic sequence diagram instead of the actual HTTP messages; assuming the viewer sends requests |
| Durations, overlap, service spans and parent/child timing | `SpanWaterfall` / `span-waterfall`, with explicit illustrative/measured provenance | Fabricated measurements, automatic critical-path claims or using spans as generic state/concurrency lanes |
| Full related files, snapshots, regions or cross-file implementation behind a snippet/diagram | `SourceRef` + `SourceExplorerProvider`; optional Diff/Walkthrough adapters and D2 source links | Copying an entire project inline, or assuming the package generates the host manifest |
| Trying a real app, comparing deployed behavior variants or returning to examples without shrinking the article | `ExampleRef` + `ExampleExplorerProvider` and host-owned registry; prefer this modal for new lessons | Treating Source Explorer as an app runner, fabricated versions, or arbitrary iframe URLs from query parameters |
| An existing inline app viewport, or an explicit inline-embed requirement | `LiveDemo` with verified `src`/`title`; retain compatibility rather than migrating unrelated embeds | Adding a remark fence, implying the component builds/hosts the app, or promising an untrusted-code sandbox |
| A short snippet, raw log/output, standalone JSON, a directory listing, schema/options or a comparison | Normal code/text fences, a Markdown table, or registered Fumadocs `Files`/`TypeTable` | Forcing everything into docs-kit; recreating removed DataInspector/MarbleDiagram/ConcurrencyLanes APIs |

Use two components only for different questions: D2 for the service interaction and ProtocolExchange for its HTTP details; CodeDiff for the change and TerminalSession for verifying it; D2 for the logical flow and SpanWaterfall for a genuinely timed trace; ExampleRef for trying behavior and SourceRef for reading its real implementation. Do not repeat the same explanation in multiple viewers.

For RxJS timing/lifecycle lessons, use truthful D2 flow/step views for subscription and cancellation relationships, plus a frame/event table and executable `TestScheduler` examples when exact timing matters. Do not fabricate a docs-kit marble renderer, draw hand-aligned marble diagrams or pretend a latency waterfall reproduces operator semantics.

## D2 icons: use whenever appropriate

- Use the catalog at https://icons.d2lang.com/ when writing or revising D2 diagrams. Choose recognizable product/service icons whenever they clarify component identity; do not restrict this to a particular vendor or repository.
- Match the icon to the actual component, not just a related ecosystem. Do not assign a vendor logo to a generic API, database or abstract concept, or imply a dependency the article does not have. Omit an icon when no accurate, useful match exists.
- Keep explicit text labels and meaningful arrows; icons supplement the explanation, never replace it. Use consistent treatment for repeated components and check light/dark and small-screen readability.
- Verify the exact catalog asset URL instead of guessing filenames. Reuse the host's trusted local assets, URL-rewrite, checksum/attribution and build-time embedding conventions; do not assume docs-kit downloads remote icons automatically. Read the icon guidance in `references/docs-kit-components.md` before adding a new asset or changing asset configuration.

## Authoring and safety invariants

- Keep diagram source in `d2` fences and technical examples in the matching docs-kit descriptor fence. Keep screenshots/photos/logos as images only when they are genuinely images, not a workaround for the diagram policy.
- Keep logs, payloads, CLI output, literal file/directory listings and position-sensitive syntax as text. The ban is on hand-drawn **diagrams**, not on text characters appearing in real artifacts. Use Fumadocs `Files` when registered, otherwise an indented path list/table; do not invent a docs-kit file-tree component.
- Place essential explanation in surrounding MDX prose. Current compact UI deliberately does not render some legacy metadata: CodeDiff caption/annotation descriptions and ProtocolExchange descriptions/annotations; CodeWalkthrough shows active step explanations rather than its general description.
- YAML descriptors have strict schemas: unique IDs, valid references and 1-based inclusive ranges in the correct snapshot/side. Preserve code/newline semantics with deliberate `|-`/`|` usage. Do not hand-author prepared tokens, SVG props, diff rows or lossless-JSON offsets when the build plugin can create them.
- Keep ProtocolExchange JSON bodies and SpanWaterfall attributes as strict JSON **strings**. Preserve numeric lexemes; do not round-trip through JavaScript Number. Standalone payloads can remain `json` fences.
- Treat every example as published data, including folded output, unselected snapshots and closed variants. Remove credentials/private data; use explicit demo values. D2 SVG and Source Explorer HTML are trusted build outputs, not input sanitizers.
- State what was measured versus hypothetical. Descriptor viewers and D2 flow do not execute commands/code, make real requests, fetch traces or prove performance. Example Explorer/LiveDemo instead load an independently hosted app in an iframe when opened/started; validate that app separately and do not promise successful loading, malicious-code isolation or parent keyboard/theme control.

## Multi-part technical series

This skill is commonly used to generate one part/section at a time within a larger technical topic (e.g. a Redis series, a Java series, microservices, interview-question collections, Kafka, Kubernetes, etc.). Keep this in mind:

- Treat each generated doc as one page in a series, not a one-off. Write it so it stands alone (a reader landing directly on this page can still follow it), but keep tone/depth/heading style consistent with a typical multi-part technical series so parts feel like they belong together.
- If the user gives context about earlier/later parts (or you can see other files in the series), keep terminology, naming conventions, and depth consistent with them.
- End-of-doc `<Cards>` linking to sibling parts in the series is a good default when a series structure is evident (see Core structure pattern).

## Table of contents (mục lục) — required at the top of every doc

In addition to Fumadocs' auto-generated sidebar TOC, every doc this skill produces must include a **manual, hand-written table of contents right after the frontmatter/intro callout, before the first content section**. Use a heading + a bullet list of Markdown anchor links to each `##`/`###` section in the doc, e.g.:

```mdx
## Mục lục

- [Tổng quan](#tổng-quan)
- [Kiến trúc](#kiến-trúc)
  - [Thành phần chính](#thành-phần-chính)
- [Ví dụ](#ví-dụ)
- [Câu hỏi thường gặp](#câu-hỏi-thường-gặp)
```

Rules for building it correctly:
- Anchor slugs are the heading text lowercased, spaces replaced with `-`, punctuation stripped — Fumadocs auto-generates anchors this way, so the manual TOC must match exactly or the links break. Vietnamese diacritics are kept in the slug (Fumadocs sanitizes spaces/punctuation, not accented characters), e.g. `## Ví dụ` → `#ví-dụ`.
- Nest sub-bullets for `###` under their parent `##` entry, matching the doc's actual heading hierarchy.
- Build the TOC *after* you've written the doc's headings (or at least finalized them), so links don't drift out of sync — if you revise headings later, update the TOC to match.
- This manual TOC is written in whichever language the doc body is in (Vietnamese docs get a Vietnamese "Mục lục" heading, English docs get "Table of Contents").

## Frontmatter (always include)

Every Fumadocs page needs YAML frontmatter. `title` becomes the page's H1 — do not also add a `# Heading` at the top of the body.

```mdx
---
title: Short Page Title
description: One-sentence summary shown in search results and page headers.
---
```

## Core structure pattern

For most technical docs, follow this shape (adapt per doc type):

````mdx
---
title: <Title>
description: <One-line summary>
---

<Callout type="info">
  Optional: audience/prereqs/scope note.
</Callout>

## Mục lục
- [Overview](#overview)
- [Request flow](#request-flow)
- [Details](#details)
- [Next steps](#next-steps)

## Overview
Start from the reader's problem, then explain this example's scope.

## Request flow
The API owns request processing; persistence belongs to the database.

```d2 title="Request ownership"
direction: right
client: Client
api: API
database: Database {shape: cylinder}
client -> api: Request
api -> database: Read or write
```

Explain which boundary can fail and where the response/error is handled.

## Details
### Subsection
...

<Callout type="warn" title="Gotcha">
  Anything that could bite the reader.
</Callout>

## Next steps
<Cards>
  <Card title="Related doc" href="/docs/related" />
</Cards>
````

Reach for these components as the content calls for them (full syntax in the reference file):
- **`<Callout>`** — notes, warnings, errors, tips. Use liberally in place of "Note:" prose.
- **`<Steps>` / `<Step>`** — any sequential procedure (install → configure → deploy).
- **`<Tabs>`** — content that varies by variant (package manager, OS, language, environment).
- **`<TypeTable>`** — documenting props/parameters/config options with types.
- **`<Files>`** — showing a project/directory file tree.
- **`<Accordion>`** — optional/advanced detail that would clutter the main flow (FAQs, edge cases).
- **`<Cards>`** — linking out to related pages at the end of a doc.
- Tabbed code blocks (` ```npm ` style) — install commands across package managers.

Don't over-componentize a short doc — a two-paragraph doc doesn't need Steps/Tabs/Accordion just because they exist. Match component density to doc complexity.

## Voice: write like a colleague, not a manual

Accurate-but-flat docs get skimmed and dropped. Write the way a good senior engineer explains something to a teammate: same precision, human delivery. The full guide, with before/after examples, is in `references/writing-voice.md`. The core habits:

- **Open with the reader's problem or a question they already have**, then introduce the concept as the answer. Don't open with a dictionary definition.
- **Talk to one reader.** Default to *mình – bạn* in Vietnamese docs (match the user's existing docs if they use *chúng ta* / *tôi*), and keep the choice consistent across the doc and the series.
- **Explain choices in connected prose**, not a sequence of bullets or isolated configs. Lead from the reader's problem to the chosen approach, show the decisive snippet, then explain why it fits, what it costs and when to choose differently. Keep bullets/tables for parallel facts, steps and lookup material; keep complete configs in validated source references when available.
- **Take a stance**: say which option you'd pick by default and when you wouldn't use the thing at all. Name the common misunderstanding or trap.
- **Prefer concrete over abstract**: a scenario, a command and its output, a worked example. Use one everyday analogy per hard concept, and say where it stops being true.
- **Keep English technical terms as English** (cache, thread, failover, consumer group), the way Vietnamese engineers actually say them.
- **Cut machine-sounding filler** ("Trong thế giới công nghệ ngày nay…", "đóng vai trò quan trọng", "Hãy cùng khám phá…", nominalised verbs like "thực hiện việc lưu trữ").

Make the voice natural through clear reasoning, concrete examples and varied sentence rhythm — not by adding personal-experience stories ("mình từng làm ở…", "theo kinh nghiệm của mình…"). Do not invent anecdotes, credentials, benchmarks or incident metrics. Use clearly hypothetical scenarios instead; preserve the user's own experience only when supplied and relevant to the requested edit. Follow the examples and final self-check in `references/writing-voice.md`.

Dial the voice to the doc type: fullest in explainers and design docs, lean in API reference tables (voice lives in the intro and gotcha callouts), and calm, short and joke-free in runbooks.

## Length: no cap, optimize for clarity and flow

There is no target length and no ceiling — never cut content, explanation, or examples short just to keep the doc "concise." The only thing that matters is that a reader can follow it easily:

- Explain *why*, not just *what*, wherever it helps understanding — don't compress reasoning into a single dense sentence if it needs two.
- Prefer more sections with clear headings over fewer sections crammed with unrelated content. Long is fine; confusing is not.
- Keep a logical, linear flow: overview before details, context before specifics, simple case before edge cases. Reorder content if the natural writing order isn't the natural reading order.
- Use transitions between sections so the doc reads as one connected explanation, not a bullet dump — but bullets/tables are still the right call for enumerable facts (params, steps, comparisons).
- It's fine (encouraged) to add extra examples, an extra diagram, or a worked walkthrough if it makes a concept click — don't hold back because it adds length.
- The only trims that are ever appropriate: removing genuinely redundant restatements, or removing content that's flat-out irrelevant to the doc's purpose. Never trim for length's own sake.

## Sentence & paragraph-level readability (required)

Length has no cap, but *density* does — a long doc made of clear sentences is good; a long doc made of dense, jargon-packed sentences is not, even if every fact in it is correct. Apply these rules to every doc this skill produces:

**1. Gloss jargon on first use — don't chain undefined terms.**
If a sentence needs multiple technical terms the reader may not already know (e.g. "selectivity", "planner", "heap fetch", "visibility map" in a database-internals doc), don't string them together assuming familiarity. Define each unfamiliar term in plain language the first time it appears, in the same sentence or the one right after — a short parenthetical or a one-clause definition is usually enough. Once a term has been defined, it's fine to use it freely afterward.
- Weak: "Vì selectivity thấp, planner có thể chọn seq scan thay vì index scan để tránh heap fetch dư thừa."
- Better: "Selectivity — tỷ lệ rows khớp điều kiện — quyết định planner (bộ phận chọn execution plan) có dùng index hay không. Nếu selectivity thấp (đa số rows đều khớp), quét tuần tự cả bảng thường rẻ hơn."

**2. One main idea per sentence — split compound sentences that stack unrelated clauses.**
If a sentence joins three or four separate claims with commas/periods-as-connectors ("X, và Y, ngoài ra Z, tuy nhiên W..."), split it into separate sentences, one claim each. A reader should never have to hold more than one new idea in mind per sentence. This applies especially to lists of consequences/costs/trade-offs — write them as short sentences or an actual bullet list, not one run-on sentence.

**3. Concrete example immediately with (or before) abstract explanation — never several sentences of abstraction first.**
Don't state an abstract rule for multiple sentences and only then reveal the example that makes it concrete — by the time the reader reaches the example, they've already lost the thread. Instead: state the rule in one short sentence, then immediately show the concrete example (code, query, scenario), then (if needed) one closing sentence tying the example back to the rule. Abstraction sandwiched by concreteness reads far easier than abstraction stacked up front.

**4. Every hedge needs a landing — don't stack qualifiers without a takeaway.**
Technical accuracy often requires caveats ("it depends", "not always", "in most cases except when..."), and that's fine — but a paragraph that's nothing but chained qualifiers with no clear bottom line is exhausting to read and teaches the reader nothing they can act on. After hedging, always close with one plain sentence stating what to actually do or conclude (e.g. "Nói ngắn gọn: kiểm tra `EXPLAIN` thay vì đoán."). If a concept genuinely can't be simplified to a clear takeaway, say so explicitly rather than trailing off in qualifiers.

**Self-check before finishing a doc:** re-read a few of the denser paragraphs and ask — could someone unfamiliar with 1-2 of the terms here still follow the sentence? Does any single sentence contain more than one new idea? Is there an example within a sentence or two of every abstract claim? Does every hedge-heavy paragraph end with a clear takeaway? Fix any paragraph that fails these checks before considering the doc done.


## Read before writing

Before producing the file:

- View `references/fumadocs-components.md` for exact import statements and JSX syntax for built-in components — get these right the first time rather than guessing at prop names.
- View `references/writing-voice.md` for the voice rules, the list of machine-sounding phrases to avoid, and the per-doc-type register. Run its short self-check before saving the file.
- For diagrams or technical learning examples, read only the relevant section of `references/docs-kit-components.md`, then verify the selected feature against the installed host package and canonical docs-kit source/examples.
