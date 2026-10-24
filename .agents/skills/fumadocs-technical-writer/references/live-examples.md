# Executable examples: Example Explorer and LiveDemo

Choose **Example Explorer for new lessons** that need a real app or multiple behavior variants. Keep **LiveDemo** for existing inline embeds or an explicit requirement to show the app within the article. Use Source Explorer to read implementation, not to run an app. Use D2 flow for authored route playback, not as a substitute for an executable example.

## Contents

- [Verify the host and the app](#verify-the-host-and-the-app)
- [Integrate Example Explorer](#integrate-example-explorer)
- [Author references and versions](#author-references-and-versions)
- [Retain LiveDemo when appropriate](#retain-livedemo-when-appropriate)
- [Respect lifecycle and trust boundaries](#respect-lifecycle-and-trust-boundaries)
- [Validate publication](#validate-publication)

## Verify the host and the app

Inspect actual package exports, the MDX map, provider wrapper, global CSS and the independently built/deployed example. The checked-out manifest currently says `0.11.0`, but local code and an npm range do not prove a host has a feature or that a demo URL is live.

Use a real app URL and matching source artifact. Do not invent versions, claim deployment from a configured URL, or create an `example-explorer`/`live-demo` YAML fence. Both features use JSX and require **no remark plugin**. Do not rewrite the site's existing provider tree or scaffold/deploy an app merely to finish prose without approval.

Canonical contracts are collection-root `docs-kit/docs/{example-explorer,live-demo}.md`, `docs-kit/src/components/example-explorer/{index.ts,provider.tsx,dialog.tsx}`, `docs-kit/src/example-explorer/index.ts`, and `docs-kit/src/components/live-demo.tsx`.

## Integrate Example Explorer

Keep the registry host-owned and stable. This integration sketch uses **placeholder root-relative app paths**, not verified deployments. Replace them with actual deployed artifacts before publishing; prefer a separate trusted demo origin where available.

```tsx
'use client';

import type { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { ExampleExplorerProvider } from '@vanhiep99w/docs-kit/components/example-explorer';
import type { ExampleDefinition } from '@vanhiep99w/docs-kit/example-explorer';

const examples: readonly ExampleDefinition[] = [{
  id: 'cart',
  title: 'Giỏ hàng và đồng bộ state',
  defaultVersion: 'snapshot',
  versions: [
    { id: 'snapshot', title: 'Snapshot + subscription', src: '/examples/cart/snapshot/' },
    { id: 'events', title: 'Event-only để đối chiếu', src: '/examples/cart/events/' },
  ],
}];

export function DocsExamples({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return <ExampleExplorerProvider examples={examples} navigationKey={pathname}>
    {children}
  </ExampleExplorerProvider>;
}
```

Use the existing client wrapper in the real host instead of creating a parallel one. Pass pathname, **not source/example search parameters**, as `navigationKey`. The Next import belongs to the host; docs-kit itself is framework-independent.

Register the author-facing reference in the existing MDX map:

```tsx
import { ExampleRef } from '@vanhiep99w/docs-kit/components/example-explorer';
// Merge ExampleRef into the host's existing MDX components.
```

Import CSS once in the global stylesheet:

```css
@import '@vanhiep99w/docs-kit/styles/example-explorer.css';
```

## Author references and versions

Introduce what to try and what to observe before linking the example. Explain the result afterward; the modal must not be the only source of essential knowledge.

```mdx
Thêm sản phẩm trước khi mở Cart, rồi so sánh hai cách đồng bộ state.

<ExampleRef example="cart">Example: thử giỏ hàng</ExampleRef>

<ExampleRef example="cart" version="events" variant="inline">
  Mở bản event-only để đối chiếu
</ExampleRef>
```

- Match `example` and optional `version` to the registry. Give each definition a unique `id`, `title`, valid `defaultVersion` and nonempty `versions`; each version has a unique `id`, `title`, `src` and optional real `sourceUrl`.
- Use `variant="inline"` for a reference in a sentence; the default is a small button-style anchor. Do not add a large placeholder iframe between paragraphs.
- Treat versions as actual deployed snapshots or behavior variants. Do not label the same app as v1/v2 without a meaningful difference, or call a teaching failure variant a release.
- Let the provider resolve the fallback URL. Without a provider, supply a valid `href`; this becomes an ordinary app link, not a working modal.
- Keep the default launcher unless the host intentionally sets `launcher={false}`. The picker lists references on the current page plus an open deep link; it is not a global lesson catalog.
- Link SourceRef separately when full implementation is needed. Example Explorer does not provide a code editor, source snapshots or source validation.

## Retain LiveDemo when appropriate

Do not migrate an existing inline embed solely because the newer modal exists. If inline display is intended, register `LiveDemo` from `components/live-demo` and import `styles/live-demo.css`; no provider or parser is required.

```mdx
<LiveDemo
  src="/examples/cart/snapshot/"
  title="Thử giỏ hàng"
  height={640}
/>
```

Replace the illustrative URL with an actual artifact. Add `sourceUrl` only when a verified source link exists. The required props are `src` and `title`; height defaults to 620 and accepts 200–1600 px. Do not invent auto-height, theme synchronization or an editor API.

## Respect lifecycle and trust boundaries

- **Example Explorer:** SSR emits small links, not an iframe. Opening the dialog (including a valid deep link) mounts one app; closing, reloading, changing example/version resets/unmounts it. Do not promise retained background app state. Query keys are `example` and `exampleVersion`; preserve Source Explorer queries, unrelated query keys and hashes. Let provider helpers manage push/replace/Back rather than constructing a second URL protocol.
- **LiveDemo:** SSR has no iframe; the reader starts it with Chạy thử. Reload resets the app; changing `src` returns to the unstarted state. No-JS and modified-click paths remain ordinary external app links.
- Publish only trusted apps, preferably on another origin. The iframe sandbox grants `allow-scripts allow-same-origin`; that combination is **not** protection against malicious same-origin code. Do not weaken the sandbox or pass credentials/secrets in URLs.
- Keep URLs HTTP(S) or approved root-relative paths. Registry IDs, not arbitrary URL query values, select Example Explorer apps. URL syntax validation is not an origin allowlist or an availability check.
- Check host CSP `frame-src` and the app's `frame-ancestors`/X-Frame-Options. Use HTTPS in production. Do not claim iframe `onLoad` proves HTTP 200, successful rendering or that all browser frame failures are detectable.
- Preserve Reload/Open in new tab recovery. Do not assume the app inherits the documentation theme or supports automatic height/postMessage synchronization.
- Distinguish native dialog keyboard handling from iframe behavior: **cross-origin iframe key events do not bubble to the parent**. Escape works from the parent toolbar; keep the external close button available and do not promise Escape from every focused app.

## Validate publication

Validate registry/default IDs and render/compile the real ExampleRef or LiveDemo MDX against the host. Verify the referenced app and source version actually exist; distinguish URL/schema checks from real availability checks.

For Example Explorer, test opening, version switching/reset, reload, close, deep links, Back/Forward, route changes and reference registration. Confirm ordinary links work without JavaScript and no app is fetched before opening. For LiveDemo, test lazy start, changing src and reload reset. Check narrow layouts, focus/keyboard controls, blocked-frame recovery and standalone app links. Record any unverified deployment/CSP/iframe behavior instead of calling it working from the docs build alone.
