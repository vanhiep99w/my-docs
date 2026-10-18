# Source Explorer va source labs

## Pham vi va ownership

Source Explorer là drawer xem code minh họa cạnh bài viết, không phải IDE, filesystem browser, runtime sandbox hay GitHub fetcher. `docs-kit` sở hữu types/helpers/UI chung; **từng host sở hữu generator, registry, highlight HTML và việc kiểm chứng references**. Interview hiện còn UI/types local trong `interview-question/src/components/source-explorer/`, dù cũng dùng docs-kit cho learning fences; sửa package không tự sửa implementation local đó.

Nguồn chính: `docs-kit/src/source-explorer/index.ts`, `src/components/source-explorer/{provider,explorer}.tsx`, generators/tests của Java/SQL/Interview/Micro-frontend/Microservices/Multi-Tenant. Ví dụ runtime thực ở `interview-question/examples/` là repo-local labs, không phải backend của các site tài liệu.

## Hop dong du lieu

`@vanhiep99w/docs-kit/source-explorer` export:

```ts
SourceRequest = { project; snapshot?; file?; region?; lines? }
SourceManifest = { id; title; defaultSnapshot; snapshots: { id; title; asset }[] }
SourceSnapshot = { project; snapshot; defaultFile; files: SourceFile[] }
SourceFile = { path; displayPath?; language; code; html; regions: Record<string, [number, number]> }
```

Đây là sơ đồ field, không phải đoạn TypeScript để copy compile. Manifest endpoint chứa **array** các manifest. Host mặc định phục vụ `/source-examples/manifest.json`; asset của snapshot được resolve relative với URL manifest. `code` là bản copy, `html` là Shiki HTML đã escape/highlight lúc build, `regions` dùng số dòng 1-based inclusive sau khi bỏ marker theo generator. Viewer không tự tính token hay lấy file từ path trên server.

`validateSourceRequest` yêu cầu project không rỗng; region và lines loại trừ nhau; lines là một dòng hoặc inclusive range số nguyên an toàn, dương, có thứ tự. Kiểm tra **project/snapshot/file/region có thật và line bounds** thuộc generator host. Không coi helper validation là schema validation toàn bộ JSON tải từ mạng.

Deep-link query dùng `source`, `snapshot`, `file`, `region`, `lines`. `readSourceURL` đọc request nếu có `source`; `writeSourceURL` chỉ xóa/thay năm key đó trên bản sao URL, giữ query khác và hash. Slug bài viết và source project ID là hai namespace khác nhau: rename bài không được vô tình đổi identity source đã chia sẻ.

## Producers trong tung host

| Host / entrypoint | Nguồn chuẩn và quy tắc riêng |
|---|---|
| Interview `scripts/build-source-examples.mjs` | `examples/registry.json` liệt kê project/snapshot/root/defaultFile/files. Đọc file chỉ dưới `examples/`, cho phép stable display path map sang file capture có hash. `//#region`/`//#endregion` bị bỏ khỏi code hiển thị; kiểm tra duplicate/nested/mismatched/unclosed markers. Kiểm tra SourceRef trong bài và hash capture so với source gốc; snapshot asset mang content hash |
| Java `scripts/build-source-examples.mjs` | Code fence metadata `source="project/file"` trong `content/docs` là authority; project thuộc một document, snapshot `main`. Validate static SourceRef, region/lines/defaults và duplicate files; sinh HTML và manifest trong staging trước thay output |
| SQL `scripts/docs-content.mjs` + `build-source-examples.mjs` | Snippet trong bài là authority; project từ relative path bài, file tách theo heading/ngôn ngữ/ordinal, snapshot `article`. Không ghép SQL thay thế cho nhiều DB, ví dụ intentionally failing và destructive cleanup thành một runnable project. Chỉ publish target cần thiết sau validation; snapshot có hash |
| Micro-frontend `source-examples/registry.json` + `scripts/source-examples.mjs` | Registry chỉ rõ bài, default file và optional snapshots; code opted-in trong MDX. `sourceSnapshot` bị thiếu chỉ thuộc default, không tự nhân sang mọi variant. Kiểm tra safe relative paths, registry/defaults/regions/references |
| Microservices `scripts/source-examples.mjs` | Đọc generated collection sau prepare; original opted-in code fences thành file riêng, snapshot `article`, project từ basename. Validate SourceRef/D2 source links và refs trong learning descriptors; từ chối duplicate project/path, stale refs và một số fence đã bị loại khỏi API. Label manifest nói rõ snippets không phải project chạy độc lập |
| Multi-Tenant `scripts/lib/source-examples.mjs` + `build-source-examples.mjs` | Opted-in regular fences, code-diff/walkthrough có source request và D2/MDX references. Nhóm project/snapshot/file, validate static refs và inclusive ranges. Default ưu tiên `guide` nếu có, không áp cho các host khác |

Không có một cú pháp metadata extraction dùng chung cho mọi generator. Trước copy ví dụ giữa repo, kiểm tra parser/source tests của nơi nhận; code hiện trên trang và code trong drawer phải cùng authority. Giữ snippets/metadata ở nguồn tác giả, không sửa public JSON để chữa stale refs.

## Publish va cap nhat source assets

Build lifecycle của các host gọi source generator qua `predev`/`prebuild`, hoặc từ `prepare-content`. Luồng thành công là validate mọi project/reference → highlight code tại build → ghi snapshot assets → ghi manifest → build/export public files → drawer fetch khi mở.

Không phải mọi host có mức atomicity giống nhau. Micro-frontend có cơ chế rõ nhất: `scripts/build-source-examples.mjs` validate/render toàn bộ trước ghi; atomic write từng immutable hashed asset, manifest kế tiếp và `revision.json` cuối. Trong dev, `scripts/watch-source-examples.mjs`:

- Watch MDX + registry bằng chokidar; debounce và serialize rebuild, ghi nhận dirty khi thay đổi xảy ra trong build.
- Lần initial build lỗi thì không khởi động dev thành công; lần rebuild lỗi giữ assets tốt trước đó và cho phép recovery ở lượt sau.
- Watch mode không prune hashed assets cũ; build thường có prune.
- `scripts/dev.mjs` khởi watcher trước Next và đóng watcher khi child exit/signal.
- `app/source-provider.tsx` poll revision trong development, đổi manifest query để tránh cache Promise stale; polling lỗi giữ revision tốt trước đó. Production không poll.

Các host khác cần chạy lại generator/dev hook khi sửa nguồn; không suy ra chúng cũng có watcher hoặc revision protocol. Snapshot cũ bị prune có thể làm tab đang mở dùng manifest cũ tải asset 404; retry/reload và kiểm tra export consistency trước khi thêm cache workaround.

## Consumer va lifecycle drawer

Provider chung mặc định dùng manifest URL trên, nhận `navigationKey` (host thường truyền `usePathname`) và `scrollAnchorSelector` tùy chọn. Host chịu trách nhiệm đặt provider quanh bài và import CSS, layout adapter nếu cần.

1. `SourceRef` tạo anchor query có thể mở tab mới; click bình thường trong provider bị chặn navigation và mở drawer. Ctrl/Cmd/middle-click vẫn giữ semantics anchor. Không provider vẫn có anchor, nhưng không có drawer tự nhiên từ package.
2. Provider ghi request vào history: mở lần đầu push, đang mở thì replace; đổi file/snapshot replace. Đóng entry do provider sở hữu gọi Back; mở từ deep link thì clear source params bằng replace. `popstate` và navigation key đồng bộ request.
3. Drawer lazy-load. Nó fetch manifest, lookup project/default snapshot rồi fetch asset. Promise cache theo URL giữ trong module; fetch thất bại bị bỏ khỏi cache. Effect có active flag để response cũ không cập nhật selection mới.
4. File mặc định từ snapshot, optional region/lines dùng để highlight/scroll. Chọn file khác bỏ range/region cũ. Snapshot switch dùng default file snapshot mới.
5. Non-modal dialog cho phép tiếp tục đọc bài, mobile có file picker; Escape ưu tiên modal dialog đang mở. Khi đóng có phục hồi focus/layout; copy file lấy `code`, copy link normalize file/snapshot hiện tại.

D2 node links được bridge qua `components/source-explorer/d2-source-links.tsx`; Diff/Walkthrough có adapter mở source theo đúng side/snapshot. Chúng không được làm toàn bộ SVG/UI thành link reload trang hoặc gắn provider vào mọi base component.

## Loi va ranh gioi bao mat

- Manifest/project/snapshot không tồn tại hoặc request HTTP fail: drawer hiển thị lỗi và nút retry (clear cache rồi load lại).
- File không còn: hiển thị hướng dẫn chọn file khác; region/range sai có warning riêng, không crash toàn bộ bài.
- Clipboard không có quyền/không khả dụng: báo người đọc chọn code hoặc dùng URL bar.
- Reference sai trong authored content nên fail **lúc build**, không dựa vào fallback runtime để che lỗi.
- Manifest/HTML phải do repository kiểm soát: viewer nhúng `file.html` bằng `dangerouslySetInnerHTML`, không sanitize arbitrary external payload. Không trỏ `manifestUrl` tới nguồn không tin cậy. Không có browser runtime schema validator bảo vệ toàn bộ asset.
- Public snapshot chứa code/capture được publish; không đưa env/auth/credential hoặc private source. Line/region ID và snapshot là hợp đồng đã chia sẻ, không chỉ chi tiết CSS.

## Source labs cua Interview

Các labs là source minh họa có `package.json` riêng; xem `interview-question/examples/registry.json`. Site chỉ publish/read code của chúng, không tự chạy backend Node khi lên Cloudflare Pages.

### Webpack va Vite

`examples/webpack-react-demo/{basic,async-bootstrap}` có build/typecheck riêng. `scripts/capture-webpack-output.mjs` tạo bộ capture để giải thích emitted bundles/runtime/source maps; generator kiểm tra SHA-256 source snapshot với report, buộc refresh capture đã review khi source đổi. Không đánh đồng artifact capture với bundle site docs.

`examples/frontend-build-lab` minh họa Vite + React, dynamic admin import và tree shaking. `scripts/test-source-labs.mjs` kiểm tra dynamic chunk chỉ fetch sau click, unused sentinel không có trong runtime, type errors làm typecheck/build fail và HMR giữ UI state. Lệnh đó cài/build/chạy browser các lab; không phải một read-only check.

### React shell va Vue remote

Trong `examples/module-federation-react-vue`, shell React tải `vueSub/mount` lazily qua `shell/src/remote.ts`, kiểm tra `protocolVersion === 1` và API `mountVueSub`. Promise cache bị reset khi load fail. `VueHost.tsx` sở hữu browser history, chỉ nhận navigation thuộc `/catalog`, đồng bộ path/query/hash sang remote và cleanup mount bị cancel/unmount.

Remote `vue-sub/src/mount.ts` tạo Vue app với memory history, nhận initial location, trả `updateLocation`/`unmount`; counter host-updates ngăn loop echo navigation. Remote có bootstrap standalone riêng. `scripts/test-module-federation.mjs` kiểm tra lazy load, deep links/back-forward, state reset khi remount, remote unavailable và missing JS trả 404 thay vì SPA HTML. Đây là contract local version 1, không phải Federation orchestration chung của tất cả docs.

### SharedWorker va WebSocket

`examples/shared-worker-websocket/src/realtime-client.ts` ưu tiên SharedWorker (một connection manager chia sẻ nhiều tab cùng context), fallback dedicated worker theo tab. Tabs register protocol v1, heartbeat, subscribe/unsubscribe và giữ cursor riêng. Client resync snapshot cho tab mới/frozen; event sequence cũ bị bỏ, không suy ra exactly-once delivery.

`src/connection-manager.ts` giữ client/topic leases, socket/connect promise, reconnect state và auth generation; lấy ticket qua POST rồi mở WebSocket. Auth change hủy socket/ticket identity cũ; 401/4401 báo cần auth thay vì reconnect vô hạn. Mỗi tab có listener/cursor riêng, worker giữ routing subscriptions.

`server.mjs` là **LOCAL LAB ONLY**: fixed demo identity, ticket single-use 30 giây, origin checks local, topics allowlist, payload/backpressure limits; state/history/idempotency trong memory, mất khi restart. Nó có API snapshot/metrics/disconnect phục vụ demo/test. Không dùng làm authentication, authorization hoặc durable replay production. Test lab có multi-tab isolation, late subscriber snapshot, reconnect, dedicated fallback, command dedup và business socket không bị HMR can thiệp.

## Kiem-thu-va-mo-rong

- Package contract: `docs-kit/tests/source-explorer.test.mjs` kiểm tra URL round-trip/query/hash, SSR không phụ thuộc Next và lazy/client/CSS artifacts.
- Host extraction/reference: Java `tests/source-examples.test.mjs`; SQL `tests/docs-content.test.mjs`; Microservices `scripts/source-examples.test.mjs`; Multi-Tenant `scripts/tests/source-examples.test.mjs`.
- Micro-frontend `tests/source-examples.test.mjs` bảo vệ variant/default/region; `tests/source-watch.test.mjs` bảo vệ atomic save, serialization và recovery.
- Interview `tests/source-build.spec.ts`, `source-explorer.spec.ts`, `source-drawer-navigation.spec.ts`, `source-lab-docs.spec.ts`, `webpack-output.spec.ts` và federation doc test.

Thêm source project: chọn authority đúng host, khai báo defaults/files/snapshots, gắn refs tĩnh, chạy generator + focused tests, build static rồi thử deep link/reload/copy và lỗi missing asset. Đừng chỉ sửa registry và kiểm tra drawer bằng dev output cũ. Các test kể trên được đọc, chưa chạy trong run Wiki này.
