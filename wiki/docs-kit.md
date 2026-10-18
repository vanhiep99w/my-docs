# Docs-kit: component va build integrations

## Pham vi va ownership

`docs-kit/` là Git repo/package npm độc lập `@vanhiep99w/docs-kit`, version checked-in `0.9.0`, ESM, Node `>=22`, peer React `^18.3.0 || ^19.0.0`. Nó không phải Next app, Cloudflare Worker hay root workspace dependency. Không có peer dependency Next/Fumadocs: host tự tích hợp remark, MDX registry và CSS.

Bằng chứng chính: `docs-kit/package.json`, `src/d2/*`, `src/components/*`, các module learning fences, tests và `.github/workflows/ci.yml`. Tài liệu API chi tiết có sẵn trong `docs-kit/README.md`, `docs-kit/docs/{d2,terminal-session,code-diff,code-walkthrough,protocol-exchange,span-waterfall,compact-ui}.md`; Wiki này giữ hợp đồng liên repo và ranh giới thay đổi, không sao chép mọi option.

## Public entrypoints va tich hop

Package dùng **subpath exports**, không có root barrel gom build code và UI. Import theo trách nhiệm:

| Lớp | Entry point (`@vanhiep99w/docs-kit/…`) | Trách nhiệm |
|---|---|---|
| Node build | `d2`, `terminal-session`, `code-diff`, `code-walkthrough`, `protocol-exchange`, `span-waterfall` | Parse/validate/prepare descriptor, remark transform; D2 gọi renderer WASM |
| React UI | `components/<tên tính năng>` | Hiển thị dữ liệu đã chuẩn bị; không kéo parser/compiler vào browser |
| Client tùy chọn | `components/d2-interactive`, `components/source-explorer`, `components/code-diff-source`, `components/code-walkthrough-source` | Viewer/drawer/adapters; load tùy chức năng |
| Data helpers | `source-explorer`, các `<learning-feature>/data` đã export | Types, validation, URL/line helpers không phụ thuộc host framework |
| CSS | `styles/<tên tính năng>.css` | Host phải import; `source-explorer-fumadocs.css` là layout adapter tùy chọn |

Ví dụ host đã kiểm tra: Kafka/Jenkins dùng bộ learning components đầy đủ; Java/SQL/Micro-frontend dùng D2 + Source Explorer theo package `0.5.x`; các consumer chưa tích hợp vẫn dùng Mermaid/component local. [Bản đồ dependency](repositories.md#phien-ban-va-consumers) là snapshot manifest, không phải cam kết mọi site đã dùng bản mới nhất.

Một tính năng mới cần cùng lúc: export trong package, build assets, plugin trong `source.config`, component trong MDX map, CSS ở host và fixture/test. Không import plugin Node vào file `'use client'`. Không giả định cài package mới sẽ tự sửa registry của site.

## D2: control va data flow

```text
fence d2 trong MD/MDX
 → remarkD2: options + frontmatter + local resources
 → cache lookup / shared local broker
 → worker Node giữ D2 WASM → render light/dark + fit labels/boards
 → MDX D2Diagram hoặc D2InteractiveDiagram với SVG props
 → server HTML; optional lazy client viewer khi Explore
```

`src/d2/index.ts` thu các code node `lang=d2`; các fence khác giữ nguyên. Nó phát JSX component với caption/id/SVG; lỗi được `file.fail` gắn vào file/vị trí node, không biến thành hình rỗng.

### Options va invariants

- Defaults hiện tại: `layout=elk`, `sketch=true`, `scale=0.75`, `padding=12`, theme light/dark `0/200`, `mode=static`, caption `Diagram`.
- Layout effective: **fence `layout` → page frontmatter `d2Layout` → plugin option → ELK**. Chỉ `elk`, `dagre`, `tala`; giá trị sai hoặc duplicate recognized fence options báo lỗi. Page schema host phải giữ `d2Layout`.
- Modes: static, steps, tabs, explorer, animation. Non-static tự chọn interactive component; host phải đăng ký component đó. `interactive` cũng có thể opt-in trực tiếp.
- Renderer `src/d2/render.mjs` dùng đo nhãn/font và render hai theme; tests bảo vệ label fit, explicit label placement và sequence semantics. Đừng thu nhỏ chữ để che lỗi layout; điều chỉnh source/caption hoặc layout có kiểm thử.
- `src/components/d2.tsx` là pure React: nhúng SVG trusted bằng `dangerouslySetInnerHTML`, figure có caption và scroll region keyboard-focusable. CSS chọn light/dark; không cần client compiler.
- Interactive launcher lazy-import `d2-viewer.js` sau Explore. Suspense/error boundary giữ static views/source; boards khác có native details fallback. Animation có điều khiển, không phải luồng thực thi hệ thống được vẽ.

### Cache va worker lifecycle

Cache mặc định `.cache/docs-kit/d2`, resolve từ working directory consumer. Nhiều host đổi thành `.next/cache/docs-kit/d2` để phù hợp chiến lược cache build. Cache không phải output deploy.

Key gồm source, salt ID theo **relative document path + fence index**, renderer/SDK fingerprint, effective options và resource bytes. Absolute checkout path không nằm trong key render nên cache có thể dùng lại khi di chuyển checkout. Trong process, pending promise deduplicate cùng cache file; disk cache được validate và ghi temp + rename để tránh entry nửa chừng. JSON hỏng hoặc artifact không hợp lệ được render lại; lỗi filesystem khác vẫn có thể làm build fail.

`pool-client.ts` khởi động broker local qua socket/Windows pipe, lock startup và fingerprint cấu hình. Các process MDX có cùng absolute cache directory/settings chia sẻ broker; render cache portable không có nghĩa mọi checkout chia sẻ cùng broker. Socket/lock/log nằm ở thư mục tạm hệ điều hành, không đưa vào cache CI hay public export.

`pool-server.mjs` xếp hàng và deduplicate job; worker giữ D2 instance để tránh khởi động WASM cho mỗi diagram. Mặc định một worker, option `concurrency` chỉ nhận 1–8; idle mặc định 30 giây và job timeout nội bộ mặc định 60 giây. Worker crash/timeout làm **job đó fail**, worker được thay cho job tiếp theo. Client chỉ retry một lần cho lỗi transport/broker đóng giữa ping và render, không retry lỗi cú pháp. Broker tự shutdown khi idle; queue và short-lived result cache có giới hạn.

Đừng tăng concurrency để chữa mọi timeout: kiểm tra diagram/resource size, renderer options và giới hạn RAM build trước. Kiểm thử lifecycle ở `tests/pool.test.mjs` bao gồm multi-process, crash, timeout, startup failure, stale socket và idle restart.

### Resources va trust boundary

`src/d2/resources.ts` dựng virtual filesystem từ `importsRoot` (`.d2`) và `assetsRoot` (ảnh), relative với working directory host. Các root này phải là directory thực trong `file.cwd`, không symlink; document cũng phải ở trong cwd. Scan từ chối symlink và giới hạn tổng 256 file/8 MiB cho resources được đọc. Icon được nhúng data URL; cache fingerprint theo nội dung. TTF font options được resolve từ host cwd và cùng byte/file budget; không áp nhầm kiểm tra root imports/assets cho mọi font path.

Chỉ compile tài liệu do tác giả đáng tin cậy kiểm soát. Inline SVG **không phải sanitizer**, không có API nhận MDX/D2 từ công chúng. Bounds tài nguyên không biến renderer thành sandbox. Không đưa token, log thật hay private source vào diagram/asset vì chúng có thể xuất hiện trong HTML và source viewer.

## Learning fences va hop dong du lieu

`terminal-session`, `code-diff`, `code-walkthrough`, `protocol-exchange`, `span-waterfall` là YAML descriptor fences, không phải code để chạy. Plugin parse YAML, validate schema/IDs/references/budgets, prepare dữ liệu rồi dùng `src/mdx/data-element.ts` phát structured MDX props. Descriptor lỗi phải fail build kèm vị trí. Các code fences thông thường không được diễn giải như descriptor.

| Feature | Input/output và invariant | Không làm |
|---|---|---|
| Terminal Session | `context` local/container/pod/remote; các step có command, outputs stdout/stderr theo thứ tự, expected/exitCode do tác giả ghi. Context override là thay toàn bộ, không merge. Copy command gốc, native details cho output | Không chạy shell, bắt log hoặc kết nối host; từ chối ANSI/control không hỗ trợ |
| Code Diff | Before/after code, optional side-specific source refs, annotations, inline/split và word diff opt-in; build tính diff + Shiki tokens. Copy giữ original/newline/CRLF | Không patch file thật, không chạy diff engine/Shiki trong client |
| Code Walkthrough | Snapshots code và ordered steps trỏ snapshot/ranges; hỗ trợ quay lại snapshot. Highlight từng snapshot độc lập, token là build output, không được nhập trong YAML | Không execute code hoặc giả lập runtime state |
| Protocol Exchange | Variants request/response, ordered headers với ID riêng cho duplicate names, text/strict JSON body; copy giữ source và số lớn | Không gửi HTTP/follow redirect, không tạo credential store hay cURL wire output |
| Span Waterfall | Unit, provenance illustrative/measured, spans start/duration/parent/service, attributes JSON; validate finite time, parent tồn tại/không cycle, giữ author order giữa siblings | Không gọi tracing backend, sửa clock skew hoặc suy ra critical path |

Annotations/ranges phải hợp lệ trong đúng output/side/snapshot. UI có SSR/native fallback để tài liệu vẫn đọc được không JS; tương tác client không thay đổi source Git. Source adapters cho Diff/Walkthrough chỉ mở drawer theo [Source Explorer contract](source-explorer.md#hop-dong-du-lieu).

JSON trong Protocol/Waterfall được chuẩn bị qua `src/json/prepare.ts` và `json/data.ts`: giữ raw JSON string, offsets và scalar lexemes để không làm tròn số lớn. Parser strict từ chối duplicate keys, JSON không hợp lệ và vượt depth/node budgets. Không parse payload bằng `JSON.parse` rồi stringify lại nếu cần giữ byte/number semantics. Không có tự động redact: tác giả phải lọc dữ liệu trước xuất bản.

## Mo rong va phat hanh

`npm run build` clean `dist`, chạy TypeScript rồi `scripts/copy-assets.mjs` copy worker/render `.mjs` và CSS. `files` trong package manifest kiểm soát artifact npm; các module runtime không thể chỉ tồn tại trong source mà quên copy/export.

Lộ trình thay đổi:

1. Sửa source/types và thêm test parser/validation/SSR/browser tương ứng.
2. Chạy `npm run typecheck`, `npm test`, `npm run test:pack`, `npm run test:browser` theo [vận hành](development-and-deployment.md#docs-kit-va-ci).
3. `prepare` build khi pack/install theo lifecycle; `prepublishOnly` chạy unit + packed consumer. Isolated consumer test cần registry, không chỉ render trong repo package.
4. Theo README, phát hành npm public thủ công, bump version và tag phù hợp; CI không publish. Không commit token hoặc artifact build.
5. Nâng dependency/lockfile ở từng repo consumer, chạy hook/build/test của host rồi deploy lại. Không có rollout đồng loạt ở root. Version `0.5.0` chưa được xem là tương đương API `0.9.0`.

Không biết có consumer ngoài các checkout ở đây hay không; public export phải được coi là hợp đồng tiềm năng bên ngoài. Dùng additive API/default an toàn và packed test trước khi thay export/schema.

## Kiem thu theo failure surface

- D2 output/cache/layout: `tests/d2.test.mjs`, `d2-features.test.mjs`, `layout-overrides.test.mjs`, `label-layout.test.mjs`.
- Pool/concurrency/recovery: `tests/pool.test.mjs`.
- YAML → prepared props → MDX execution/SSR + no build deps trong browser: test theo tên feature.
- Lossless payload và export đã loại bỏ: `tests/json-payload.test.mjs`.
- Viewer, copy, keyboard, dark mode, mobile/compact và source adapters: `tests/browser/*.spec.mjs`.
- Package compatibility ngoài Next/Fumadocs: `scripts/smoke-pack.mjs`.

Run Wiki này chỉ kiểm chứng bằng đọc code/test/config, không chạy suite hoặc benchmark. Số đo performance trong README là kết quả local đã ghi ở đó, không phải SLA Cloudflare và không được tái xác nhận ở đây.
