# Fumadocs Component Syntax Reference

Examples of Fumadocs document-structure components, separate from docs-kit learning components. Check the installed Fumadocs version and actual host registry before using any tag or prop. API references: https://www.fumadocs.dev/docs/markdown and https://www.fumadocs.dev/docs/ui/components.

Prefer the host's existing global MDX registration. Add per-page imports only when its MD/MDX compiler supports them and that is the site's convention; ordinary `.md` and generated Markdown do not universally support JSX/imports. Do not assume a component is registered just because Fumadocs is installed.

## Contents

- [Frontmatter](#frontmatter)
- [Callout](#callout)
- [Diagrams and learning components](#diagrams-and-learning-components)
- [Cards](#cards)
- [Steps](#steps)
- [Tabs](#tabs)
- [TypeTable](#typetable)
- [Files](#files-directory-tree)
- [Accordion](#accordion)
- [Standard Markdown](#standard-markdown--gfm-no-import-needed)
- [Includes](#include-fumadocs-mdx-only)

---

## Frontmatter

```mdx
---
title: Page Title
description: Shown in search results and page header subtitle.
---
```
`title` renders as the page's H1 automatically — don't duplicate it with `# Heading`.

---

## Callout

Built-in, no import needed in most setups.

```mdx
<Callout>Plain note, default styling.</Callout>

<Callout title="Title" type="info">
  Informational note.
</Callout>

<Callout title="Watch out" type="warn">
  Something the reader should be careful about.
</Callout>

<Callout title="Breaking" type="error">
  A hard failure mode / breaking change.
</Callout>

<Callout title="Tip" type="idea">
  A helpful shortcut or best practice.
</Callout>
```
Types: `info` (default), `warn`, `error`, `idea`.

---

## Diagrams and learning components

Use docs-kit D2 for diagrams and the matching docs-kit component for code walkthroughs, diffs, terminal procedures, HTTP messages, timed spans or source exploration. Read [`docs-kit-components.md`](docs-kit-components.md) only for the selected feature. Do not use Mermaid, hand-drawn ASCII/Unicode diagrams or removed package APIs as fallback.

Ordinary language-labelled code, JSON, CLI output and file listings remain appropriate text artifacts. Fumadocs Files below is a document-structure component, not a docs-kit export.

---

## Cards

```mdx
<Cards>
  <Card title="Getting Started" href="/docs/getting-started" description="Set up your first project." />
  <Card title="API Reference" href="/docs/api" />
</Cards>
```

---

## Steps

````mdx
import { Step, Steps } from 'fumadocs-ui/components/steps';

<Steps>
<Step>

### Install dependencies
```npm
npm install my-package
```

</Step>
<Step>

### Configure
Edit `config.ts` with your settings.

</Step>
<Step>

### Run
```bash
npm run dev
```

</Step>
</Steps>
````

Alternative lightweight syntax (needs `remark-steps` enabled): append `[step]` after a heading inside consecutive headings — but prefer the explicit `<Steps>/<Step>` component form above, it's more portable.

---

## Tabs

````mdx
import { Tab, Tabs } from 'fumadocs-ui/components/tabs';

<Tabs items={['npm', 'pnpm', 'yarn', 'bun']}>
  <Tab value="npm">
    ```bash
    npm install my-package
    ```
  </Tab>
  <Tab value="pnpm">
    ```bash
    pnpm add my-package
    ```
  </Tab>
  <Tab value="yarn">
    ```bash
    yarn add my-package
    ```
  </Tab>
  <Tab value="bun">
    ```bash
    bun add my-package
    ```
  </Tab>
</Tabs>
````

For simple package-manager install commands specifically, there's also a shorthand codeblock-group syntax:
````mdx
```npm
npm i next -D
```
````
Fumadocs auto-expands this into an npm/pnpm/yarn/bun tab group via `remark-npm`.

---

## TypeTable

For documenting props, config options, or API parameters with types:

```mdx
import { TypeTable } from 'fumadocs-ui/components/type-table';

<TypeTable
  type={{
    name: {
      description: 'The user display name',
      type: 'string',
      required: true,
    },
    email: {
      description: 'Email address',
      type: 'string',
    },
    role: {
      description: 'User role',
      type: "'admin' | 'user'",
      default: "'user'",
    },
  }}
/>
```

---

## Files (directory tree)

```mdx
import { File, Folder, Files } from 'fumadocs-ui/components/files';

<Files>
  <Folder name="app" defaultOpen>
    <File name="layout.tsx" />
    <File name="page.tsx" />
  </Folder>
  <Folder name="components">
    <File name="button.tsx" />
  </Folder>
  <File name="package.json" />
</Files>
```

---

## Accordion

For optional/advanced/FAQ-style content that shouldn't clutter the main flow:

```mdx
import { Accordion, Accordions } from 'fumadocs-ui/components/accordion';

<Accordions type="single">
  <Accordion title="What if the request times out?">
    Explain the edge case here.
  </Accordion>
  <Accordion title="Can I use this in production?">
    Explain here.
  </Accordion>
</Accordions>
```

---

## Standard Markdown / GFM (no import needed)

- Tables: standard `| a | b |` pipe tables.
- Task lists: `- [ ] todo`, `- [x] done`.
- Images: `![alt text](/path/to/image.png)` — use for real screenshots/photos only, not for diagrams.
- Internal links: use the target host's real route map and URL prefix; generated Markdown links may be rewritten by preparation hooks. Verify page/anchor targets.
- Code blocks: standard triple-backtick with language tag for syntax highlighting (powered by Shiki), e.g. ` ```ts `, ` ```python `, ` ```json `.
- Headings: `##`/`###` etc. get automatic anchors and feed the auto-generated table of contents. Don't use `#` (h1) — that's reserved for the frontmatter `title`.
- Heading TOC control: append `[!toc]` to hide a heading from the TOC, or `[toc]` to force-include a non-heading TOC entry.

---

## include (Fumadocs MDX only)

Reuse content from another file:
```mdx
<include>./shared-section.mdx</include>
```
