---
name: fumadocs-project-init
description: Scaffold a new Next.js + React + Fumadocs documentation repository for a technical topic, plan its curriculum and create valid placeholder pages with ordered metadata, a topic favicon and a wider docs layout for Cloudflare static hosting. Use for requests such as tạo project docs cho Redis, khởi tạo site Fumadocs or init a Kubernetes docs site. Verify compatible package versions for the target environment. Do not use to write detailed lesson content; use fumadocs-technical-writer for that.
---

# Fumadocs Project Init

Scaffold a complete Next.js + Fumadocs documentation project from an empty folder, for a given technical topic (Redis, Kafka, Java, Kubernetes, microservices, interview-question collections, etc.). This skill produces the **project skeleton and every page as a placeholder** — not the detailed content. Detailed content for each page is written later, one page at a time, using the `fumadocs-technical-writer` skill.

## Shared skill and target repository

This skill lives once at the collection root under `.agents/skills/`, alongside `fumadocs-technical-writer`. Do not copy or install it into each documentation repository.

Resolve every `references/...` path relative to this skill directory, not the target repository's working directory. Confirm the target topic and destination repository before creating files. Never scaffold over the collection root, an existing site, `docs/` (the static landing page), or `docs-kit/` (the shared package).

Read the target's applicable rules and existing configuration if it is not empty. Treat templates as versioned examples, not proof of the latest package API. Inspect `../../../docs-kit/README.md` when integrating shared components; match plugin, component registration and CSS to the selected package version. Keep all skills in `aws-learn/` unchanged.

## Relationship to `fumadocs-technical-writer`

These two skills are a pair, used in sequence:
1. **`fumadocs-project-init`** (this skill) — run once per topic. Creates the project, decides the full page/category structure, writes every page as a lightweight placeholder.
2. **`fumadocs-technical-writer`** — run once per page afterward, whenever the user says "viết chi tiết phần X" / "fill in the Redis persistence page". It replaces one placeholder's body with full content, following the same frontmatter/TOC/component conventions this skill already set up.

Mention this handoff to the user at the end: which page to tackle first, and that they can ask you to write it in detail next.

## Network access varies by environment — check, don't assume

Check the actual environment rather than assuming network access or a particular agent's tool names. `npm --version` checks the local executable, not registry connectivity. When network use is permitted, a bounded registry query such as `npm view next version --fetch-retries=0 --fetch-timeout=10000` can establish connectivity.

- **No registry access:** create project files directly from the inspected templates, report that dependency versions/API compatibility remain unverified, and do not repeatedly retry installation. Existing local dependencies may still allow validation; only report checks actually run.
- **Registry access available:** verify current compatible versions/import paths, install in the target repository and run its focused checks/build when permitted. Never deploy merely to validate scaffolding.

## Workflow

### 1. Confirm the topic and scope
If the user already named a clear topic (as in the trigger examples), proceed without asking. Only ask a clarifying question if the topic is genuinely ambiguous (e.g. "docs" with no subject) or if language (Vietnamese vs English docs) isn't clear from context — default to matching the language the user is writing in.

### 2. Plan the full doc outline
Before writing any files, design the complete page tree for the topic: top-level categories (folders) and the pages inside each. Read `references/topic-outline-guide.md` for the planning pattern and worked examples (Redis, Kafka, Kubernetes, Java, microservices, interview questions) — follow that pattern's shape: a learning-roadmap style structure with foundational categories first, topic-core categories in the middle, and operational/troubleshooting categories at the end, mirroring the reference screenshot's structure (Nền tảng → Bắt đầu → topic-specific groups → Instrumentation/framework-specific → Deployment/Production → Troubleshooting).

Write this plan out as a simple nested list before generating files, so structure is decided once and applied consistently (folder names, ordering, page slugs).

### 3. Source the topic's favicon
Before scaffolding, find the topic's **real, standard icon — in its correct official color(s), never black/monochrome** — read `references/favicon-guide.md` for the full workflow. Short version: prefer genuine multi-color official artwork if the brand's real logo isn't single-tone (brand-assets page, Wikipedia SVG), otherwise use Simple Icons' colored CDN endpoint with a verified official hex (never the bare monochrome default). Save as `app/icon.svg`/`app/icon.png`. Never invent a made-up logo-style icon for a topic that has a real one. If the topic genuinely has no standard/recognizable icon (a generic collection, an internal system, an abstract pattern-name topic), generate a simple non-branded icon instead and say so in the wrap-up — don't fabricate something that looks like a real brand mark for a topic that doesn't have one.

### 4. Scaffold the Next.js + Fumadocs project files

**Before writing any file, verify current package versions and import paths if web access is available** (it may not be, in a sandboxed environment — see the network note above). Fumadocs ships very frequently and has broken import paths across versions before (see the warning at the top of `references/project-file-templates.md` for a real example: a stale `fumadocs-ui` version pin caused `'DocsPage' is not exported from 'fumadocs-ui/layouts/docs/page'` at build time). If `web_search`/`web_fetch` are available, check https://www.fumadocs.dev/docs/mdx/next and https://www.fumadocs.dev/docs/ui/manual-installation for the current recommended versions/imports before proceeding; if they're not available (no network), use the reference file's documented versions as the best available snapshot and flag to the user that they should double-check `npm outdated`/the Fumadocs docs if the build fails after `npm install`.

Read `references/project-file-templates.md` for the exact file contents (package.json, next.config.ts, source.config.ts, mdx-components.tsx, components/mdx/mermaid.tsx, lib/source.ts, lib/layout.shared.ts, app/layout.tsx, app/global.css, app/docs/layout.tsx, app/docs/[[...slug]]/page.tsx, app/api/search/route.ts, public/_redirects, tsconfig.json, postcss.config). Write every one of these into the target folder — this is the latest Fumadocs App Router setup (fumadocs-mdx content source + fumadocs-ui layouts, Tailwind v4), configured for **static export to `./dist`** (Cloudflare Pages target) by default. Don't skip `app/api/search/route.ts` or `public/_redirects` — a project missing the search route will have a broken search box, and one missing `_redirects` will 404 at the site root on Cloudflare Pages. **Don't skip `components/mdx/mermaid.tsx` + the `remarkMdxMermaid` plugin in `source.config.ts` + registering `Mermaid` in `mdx-components.tsx`, either** — without all three, ` ```mermaid ` code blocks (used throughout the writer skills' diagrams) render as plain unstyled code instead of an actual diagram. This is a real bug this skill has shipped before — double-check all three pieces are present before considering scaffolding done.

### 5. Generate the content tree with placeholders
For every folder in the plan from step 2:
- Add a `meta.json` (title + page ordering — see reference for exact schema).
- Add an `index.mdx` (or a same-named `.mdx`) **category landing page** styled like the reference screenshot's "trang khung" pattern: frontmatter title/description, a short intro sentence stating this is a placeholder page for the group, a "## Phạm vi dự kiến" (or "## Expected scope" in English) section, and a "## Các bài trong nhóm" (or "## Pages in this group") bullet list linking to each child page with a one-line description of what that page will cover. Include the manual mục lục convention from `fumadocs-technical-writer` here too, for consistency.

For every leaf/detail page in the plan:
- Frontmatter with `title`/`description`.
- A short placeholder body: one or two sentences describing what this page will cover, plus a `<Callout type="info">` noting it's a placeholder to be filled in via the detailed-writing pass.
- Do **not** write full detailed content, diagrams, or long explanations here — that's `fumadocs-technical-writer`'s job later. Keep every leaf placeholder brief and consistent in shape.

Every generated `.mdx` file must still be valid, buildable Fumadocs MDX (correct frontmatter, no broken syntax) even though the content is a placeholder.

### 6. Apply the tightened-padding layout
The user wants: (a) the overall docs layout to extend closer to both screen edges instead of capping out with large empty margins on wide screens, (b) the padding between the sidebar/content/TOC columns reduced so the article content area is wider, and (c) the content area to actually reclaim space and shift left when the sidebar is collapsed/hidden. Read `references/layout-padding-customization.md` and apply its recommended fixes to `app/global.css` and `app/docs/layout.tsx` as part of step 4's files (don't skip this — it's a firm requirement every time this skill runs, not optional polish).

**This has proven to need more than CSS-variable tweaks in real testing** (a scaffolded project still showed a right-edge gap and non-reclaiming collapsed sidebar). Apply the CSS-variable stopgap (Fix 1/2/3) always, but treat CLI eject (Fix 4 in the reference) as the real fix whenever a shell with network access is available — run it, edit the ejected classes per the reference's guidance, and verify visually with `npm run dev` before telling the user this requirement is done. If no network is available to eject and verify, say so explicitly in the wrap-up (step 7) rather than implying the padding is confirmed fixed.

### 7. Wrap up
- Present the project folder to the user (zip it if it's large — see file-sharing guidance).
- Report actual install/build/browser checks and any environment limitations. Give the target repository's remaining commands without claiming network access is unavailable unless verified.
- Point out the doc outline you generated (categories + page count) and suggest which page to write first with `fumadocs-technical-writer`.
