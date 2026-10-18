# Phat trien, validation va Cloudflare deploy

## Pham vi va ownership

Thao tác npm/Git/build/deploy diễn ra trong **repo con được chọn**, không phải root `my-docs`. Từng site sở hữu package-lock, Node requirement, hooks và Pages output; `docs-kit` sở hữu npm artifact. Root có `scripts/sync-repos.py` để fast-forward/pin Git submodules theo `main` và test an toàn bằng `python3 -m unittest discover -s tests -v`; không có lệnh build/phát hành mọi ứng dụng đồng loạt. Xem `README.md` root cho local commands, cron/manual/dispatch và giới hạn đồng bộ định kỳ.

Bằng chứng: mọi `package.json`, `next.config.*`, `wrangler.toml` có mặt; `.node-version`/`.nvmrc`, hai workflow CI, Playwright configs, static preview scripts và tests được nêu dưới đây. Các command trong trang là hướng dẫn cho thay đổi tương lai; run Wiki này **không cài dependencies, chạy app/test/build hoặc deploy** vì chúng ghi ngoài Wiki và một số test còn tạo thư mục tạm ngoài repo.

## Setup va lifecycle

1. Xác định repo theo [catalog](repositories.md#danh-muc-site); đọc manifest/config trước dùng hướng dẫn template.
2. Chọn Node theo repo: `docs-kit` và nhiều consumer yêu cầu `>=22`; `jmm` cụ thể `>=22.18.0`. Interview/Jenkins có `.node-version=22`, Jenkins/Micro-frontend có `.nvmrc=22`. Node 22.18+ là điểm bắt đầu hợp lý cho nhóm này, không thay yêu cầu manifest hoặc CI.
3. Trong checkout đã có lockfile, dùng `npm ci` để cài đúng graph. Sau khi chủ động đổi dependency, dùng npm install/version command phù hợp rồi review cả manifest + lockfile. Không sao chép `node_modules` giữa site có stack khác nhau.
4. `npm run dev` chạy Next, nhưng hooks có thể sửa collection hoặc source assets. Luồng authority và generated output ở [pipeline nội dung](content-pipeline.md#nguon-noi-dung).
5. `npm run build` là static export; npm tự gọi `prebuild`. Chạy `next build` trực tiếp có thể **bỏ qua prebuild của package**, cho output stale.

Nhóm có preparer: AWS/Redis/Microservices/System Design; JWT preparer no-op; Multi-Tenant còn gọi source builder. Interview/Java/SQL có source predev/prebuild; Micro-frontend dùng dev wrapper watcher và source prebuild. Redis prebuild audit diagrams trước prepare. Các site còn lại có postinstall Fumadocs generation hoặc tích hợp generation khi Next build tùy config/version.

`.source`, build output, source JSON, cache và registry tác giả là các lớp khác nhau. Không sửa generated `.source` để chữa TS import; chạy đúng generator và kiểm tra alias trong `tsconfig`. Đừng xóa `content/docs` ở repo direct-authoring chỉ vì repo khác dùng nó làm generated output.

## Output va hosting contract

Tất cả 24 Next configs khảo sát bật `output: 'export'`. Static HTML/JS/CSS không cần Node runtime khi phục vụ. Không suy ra hỗ trợ SSR, Server Actions, cookies server hoặc Next runtime API chỉ vì có `app/api` trong source.

| Loại deploy | Build / output | Lưu ý |
|---|---|---|
| Landing `docs` | Không build; publish `/` của repo `docs` | HTML inline, setting chỉ được ghi trong README |
| Docker / GitHub Actions / Jenkins / RxJS / Micro-frontend | `npm run build`; publish `out` | Micro-frontend README/CI còn yêu cầu `npm run check:export`; `dist` ở đó không phải site output |
| 19 Next sites còn lại | `npm run build`; publish `dist` | Config từng repo dùng `distDir: 'dist'`; không suy ra theo tên template |
| `docs-kit` | TypeScript + copy assets → npm package `dist` | Không deploy folder này như website |

`wrangler.toml` có ở phần lớn site, nhưng **không thấy ở Angular, ELK, GraphQL, MongoDB, OpenTelemetry và Micro-frontend**. Một số vẫn có deploy script hoặc hướng dẫn dashboard. Không coi thiếu Wrangler file là thiếu Cloudflare site; ngược lại có file cũng không chứng minh binding/branch/dashboard đã đúng.

Khi có `deploy` script, nó thường build rồi `wrangler pages deploy <output>`. Đó là thao tác publish có side effect, **không phải validation**. Credential/account/production branch nằm ngoài bằng chứng local. Không đọc hoặc commit env/auth/token để giải quyết Wiki/setup thông thường.

AWS còn có Pages Functions từ `functions/` và binding D1: [contract riêng](aws-practice.md#persistence-va-migration). Không chạy migration numbering theo default vì script mặc định **remote**.

## Preview va routing

- Dùng script `preview`/`start` phù hợp manifest sau build. Một số preview chạy lại build (Angular, Jenkins, MongoDB), số khác chỉ serve output hiện có.
- Docker/OpenTelemetry dùng `serve`; GraphQL start dùng `npx --yes serve dist`; đa số Wrangler preview dùng `wrangler pages dev dist` hoặc `out`.
- ELK và RxJS còn `start: next start` dù static export: không dùng command đó làm bằng chứng deploy hoạt động; phục vụ output tĩnh theo README hoặc static server đúng kiểu export.
- Micro-frontend `scripts/serve-export.mjs` phục vụ `out`, thử file exact rồi `.html` rồi `/index.html`, hỗ trợ RSC assets và 404. Preview mặc định port 3210. Không thay bằng SPA fallback trả `index.html` cho missing JS.
- `trailingSlash` không đồng nhất; đừng mặc định mọi bài export thành `slug/index.html`. Micro-frontend checker rõ ràng kỳ vọng `.html`.
- `public/_redirects` là contract Cloudflare; static server đơn giản không mô phỏng được nó. Test thêm App Router redirects/dev, deep link/reload, search URL và per-page LLM output nếu có.

## Validation-theo-repo

Chạy sau `npm ci`, với browser/network nếu test yêu cầu. Lệnh tương đối với root **repo tương ứng**; không dùng một vòng `npm test` cho mọi site.

| Repo / loại thay đổi | Lệnh có trong manifest và precondition |
|---|---|
| `docs` | Không npm tests; HTML/filter/link/browser checks ở [landing](landing-and-authoring-tools.md#thay-doi-portal) |
| `elk-learn`, `graphql-learn`, `react-learn`, `jwt-learn` | Build + review output/route/MDX bằng browser |
| `angular-learn` | `npm test`, build; D2/content checks có trong test script |
| `aws-learn` | `npm test` (MDX alerts/Mermaid/SSH highlighting), build + browser smoke. API/D1 cần validation riêng, build chưa đủ |
| `docker-learn` | `npm run types:check`, `npm run lint`, `npm run build`; không test script |
| `github-actions-learn` | `npm run types:check`, `npm run lint`, `npm run build` |
| `mongodb-learn` | `npm run types:check`, `npm run lint`, `npm run build` |
| `otel-learn` | `npm run types:check`, `npm run lint`, `npm run build` |
| `rxjs-learn`, `js-learn` | Build + browser review; không test/typecheck script riêng. JS còn experimental TypeScript CLI trong Next config, không copy config sang site khác |
| `jenkins-learn` | `npm run check`: lint → types:check → build → test:docs. `test:docs` đọc HTML `out/docs`, phải build trước |
| `jmm` | `npm test`, `npm run typecheck`, build. Test script dùng `--experimental-strip-types`, yêu cầu Node đã nêu |
| `k8s-learn` | Build + browser/content review; chưa có npm test script cho docs-kit trong manifest |
| `kafka-learn` | `npm run test:docs`, `npm run typecheck`, build; tests compile fences và kiểm tra registry/CSS |
| `java-learn` | `npm test`, `npm run docs:check`, `npm run typecheck`, build; `docs:audit`, `docs:compare-layouts`, `docs:check-export` khi sửa diagram/layout/export |
| `sql` | `npm test`, `npm run diagrams:check`, `npm run typecheck`, build; source build tự chạy trước dev/build |
| `microservice-learn` | `npm test`, `npm run check-diagrams`, `npm run diagrams:inventory`, `npm run typecheck`, build |
| `multi-tenant` | `npm test`, `npm run typecheck`, build rồi `npm run test:browser` |
| `redis-learn` | `npm run test:docs`, `npm run typecheck`, build rồi `npm run test:browser`; browser server không tự build |
| `system-design-practice` | `npm test`, `npm run typecheck`, build |
| `micro-frontend-learn` | `check:docs`, `check:source`, `npm test`, `typecheck`, build, `check:export`, `test:e2e` theo CI |
| `interview-question` | `npm run source:build`; `npm run test:source` dùng Playwright config có build+test-server; labs là các lệnh opt-in riêng ở [Source Explorer](source-explorer.md#source-labs-cua-interview) |

Các test unit có thể compile D2 hoặc ghi fixture/temp/cache; “unit” không đồng nghĩa read-only hay không cần Node/build dependencies. Đọc focused test trước chạy trong môi trường có write boundaries.

### Browser requirements

`docs-kit`/Multi-Tenant/Redis dùng `CHROME_PATH` để override browser. Interview và Micro-frontend dùng `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`. Nếu không dùng binary sẵn, cài Chromium theo Playwright; không đọc user browser cookies/profile để test tài liệu.

Micro-frontend Playwright kiểm tra desktop/mobile trên **export đã build** qua preview server. Interview Playwright tự gọi build khi khởi test webServer, nhưng local reuseExistingServer có thể tái dùng server cũ; khi nghi stale output kiểm tra precondition. Redis Playwright dùng `DOCS_TEST_PORT` mặc định 43219 và static server; cần build trước. Multi-Tenant browser test cũng ghi screenshot artifacts và dùng `playwright-core`/browser cài riêng.

## Docs-kit-va-CI

`docs-kit/.github/workflows/ci.yml` có:

- Unit/package job trên Node 22 và 24: npm ci → typecheck → npm test → test:pack.
- Browser job Node 24: cài Chromium rồi test:browser, upload test-results khi fail.
- Permissions read-only contents, không có npm publish/deploy job.

`test:pack` dựng consumer độc lập để kiểm tra package export/build không dựa nhầm host checkout; cần registry/network. `benchmark` là tác vụ đo tách biệt, không phải performance gate hoặc SLA. Phát hành package và rollout consumer: [docs-kit](docs-kit.md#mo-rong-va-phat-hanh).

`micro-frontend-learn/.github/workflows/docs.yml` là workflow site thứ hai được tìm thấy: Node theo `.nvmrc`, check docs/source/tests/typecheck, build/check-export, Chromium/E2E; push main/PR và concurrency cancel-in-progress. Workflow này verify, không có deploy step. Hai workflow này không kiểm tra mọi repo khác; các project Pages có thể dùng Git integration cấu hình ngoài source.

## Failure va recovery

| Triệu chứng | Kiểm tra và recovery có căn cứ |
|---|---|
| Cloudflare báo output không có | So `next.config`, manifest scripts và output trong catalog; đặc biệt Micro-frontend dùng `out`, không `dist` hay `.next` |
| Sửa bài nhưng website không đổi | Authority đúng chưa? Có bỏ qua prebuild? Generated file bị ghi đè? Source watcher/generator có lỗi? Đã deploy commit/build đó chưa? |
| Không resolve collection import | Postinstall/MDX generation + tsconfig alias + Fumadocs version; không viết `.source` thủ công |
| D2 fail/hang/OOM | Lấy file/fence error, thử diagram/layout/resources nhỏ; cache writable/broker settings; mặc định concurrency 1. Không chữa bằng bỏ compile hoặc ship WASM vào client |
| Component hiện YAML/raw fence hoặc thiếu style | Đối chiếu plugin → registry → CSS và version package consumer |
| Drawer missing/stale source | Rebuild manifest/snapshot cùng export, kiểm tra project/default/file/region và cache revision; [failure contract](source-explorer.md#loi-va-ranh-gioi-bao-mat) |
| Search lỗi trên static host | Có staticGET artifact không, provider API đúng không (`/api/search.json` ở Micro-frontend), page URL theo loader prefix đúng không |
| Root/renamed URL lỗi | So `generateStaticParams`, Next redirect và `_redirects`; preview không đồng nghĩa Cloudflare redirect emulation |
| Font/network build error | Một số layout như Kafka tải `next/font/google`; phân biệt lỗi network setup với compile/content lỗi. Không cam kết build offline hoàn toàn |
| AWS quiz/history không lưu | Static export không kiểm tra Functions/D1; rà binding/schema/request acknowledgment. UI có nhánh chỉ console lỗi, xem [AWS lifecycle](aws-practice.md#state-va-lifecycle-client) |

## Them-hoac-nang-cap-mot-site

1. Chốt repo con và remote sở hữu; tránh scaffold từ folder có content/private artifacts không liên quan.
2. Chọn dependency versions + Node có chủ đích, không “latest” ngầm; giữ lockfile. Với docs-kit, chọn API version mà registry/plugin/CSS host hỗ trợ.
3. Chốt authoring authority, `defineDocs`/macro, loader route, schema và metadata; trace một bài từ nguồn đến HTML/search/drawer.
4. Kiểm thử focused + static export + browser. Nếu URL đã có người dùng, thêm redirect và kiểm tra consumers/anchors.
5. Chốt Pages output/root/branch/cache và bindings nếu có ngoài dashboard. Không thêm runtime server feature vào static export mà không đổi hosting model rõ ràng.
6. Deploy repo con khi được phép, kiểm tra route live rồi sửa portal trong `docs/index.html` và metadata counts nếu có bằng chứng.
7. Nâng Wiki khi hợp đồng thay đổi. Commit/push repo con trước, chạy `python3 scripts/sync-repos.py --commit` rồi push root `main`. Root Wiki/shared skills thuộc repo `my-docs`, không tự được commit vào repos con; workflow chỉ cập nhật gitlinks, không tự viết lại Wiki.

## Pham-vi-kiem-chung-cua-Wiki

Run khởi tạo chỉ đọc source/config/tests/public documentation, không đọc secret/env thật/logs và không truy cập production DB hoặc dashboard. Link/anchor nội bộ Wiki và source-path references được kiểm tra tĩnh trước hoàn tất. Không tuyên bố suite pass, Pages deploy thành công, security control bên ngoài tồn tại hoặc dependency mới nhất trên registry.
