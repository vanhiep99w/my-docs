# Ban do repository va ranh gioi he thong

## Pham vi va ownership

Root `my-docs/` hiện là repo Git `vanhiep99w/my-docs` tập hợp checkout qua submodule tracking `main`; không có `package.json` hoặc npm workspace manifest. Khi khởi tạo Wiki, root chưa có Git; cấu trúc đã thay đổi khi thiết lập commit/push và sync. Có **26 repo con** có `.git` riêng: 24 site học tập, landing `docs` và package `docs-kit`. Mỗi site có package/lockfile/config và lifecycle riêng; đây không phải một Next app chứa 24 modules.

Theo mô hình tác giả cung cấp, mỗi doc tương ứng một GitHub repository và các site dùng Cloudflare. Bằng chứng local xác nhận checkout độc lập, static-export configs và URLs trong landing; không xác minh quyền sở hữu remote, trạng thái GitHub hoặc dashboard Cloudflare. Code repo con commit/push trong repo đó trước; root commit Wiki/shared skills và pointer submodule, không thay thế commit code repo con.

## Ranh gioi va quan he

```text
Người đọc
 └─ docs/index.html (landing HTML tĩnh)
     ├─ outbound links → 24 site docs độc lập
     └─ AWS Questions → aws-learn /practice/ → Pages Functions → D1

Tác giả / build từng site
 ├─ authored MD/MDX + metadata/assets → Fumadocs/Next static export
 └─ subset consumers → npm @vanhiep99w/docs-kit
                          ├─ Node compile-time plugins/D2 workers
                          └─ React components + optional client viewer + CSS
```

Không thấy shared backend hay DB chung của tất cả site. Tên Kafka/Redis/MongoDB/ELK mô tả **nội dung học**, không chứng minh các database/broker đó đang được website sử dụng. Ngoại lệ persistence được trace là AWS D1. Labs Node/WebSocket trong Interview là môi trường minh họa riêng, không tự trở thành backend Cloudflare của trang docs.

## Danh-muc-site

Mỗi dòng dựa trên `<repo>/package.json`, `next.config.*`, loader tại `lib/source.ts` hoặc `src/lib/source.ts`, cây `content/docs` và link literal trong `docs/index.html`. Output tính từ root repo con. “Route” là `loader.baseUrl`, không phải Next `basePath` hay redirect root. “Nguồn” tóm tắt authority, chi tiết tại [pipeline nội dung](content-pipeline.md#nguon-noi-dung).

| Repo | Phạm vi curriculum hiện có | Route | Nguồn | Output | URL trong landing |
|---|---|---|---|---|---|
| `aws-learn` | AWS services, architecture, exam practice | `/` | Root MD + README; quiz riêng | `dist` | <https://aws-learn.pages.dev> |
| `k8s-learn` | Kubernetes, workloads/network/storage, labs/production | `/` | `content/docs` | `dist` | <https://k8s-learn-2tg.pages.dev/> |
| `docker-learn` | Docker/BuildKit/Compose/Swarm, operations/labs | `/docs` | `content/docs` | `out` | <https://docker-learn.pages.dev/> |
| `github-actions-learn` | Workflows/runners/actions, CI/CD/security | `/docs` | `content/docs` | `out` | <https://github-actions-learn.pages.dev/> |
| `jenkins-learn` | Jobs/pipelines/agents, integrations/delivery | `/docs` | `content/docs` | `out` | <https://jenkins-learn.pages.dev/> |
| `multi-tenant` | Isolation, identity/data/lifecycle, operations | `/` | `content/docs` | `dist` | <https://multi-tenant-8ax.pages.dev> |
| `otel-learn` | Signals/instrumentation/collector, backends/labs | `/` | `content/docs` | `dist` | <https://otel-learn.pages.dev/> |
| `microservice-learn` | Architecture/patterns, resilience/data/deploy/AWS | `/` | Root/nested MD + README | `dist` | <https://microservice-learn.pages.dev> |
| `graphql-learn` | Schema/queries, Spring integration, production | `/docs` | `content/docs` | `dist` | <https://graphql-learn.pages.dev/> |
| `sql` | SQL, MySQL/PostgreSQL/Oracle, optimization | `/` | `content/docs` | `dist` | <https://sql-by4.pages.dev> |
| `mongodb-learn` | CRUD/schema/index/aggregation, sharding/operations | `/docs` | `content/docs` | `dist` | <https://mongodb-learn.pages.dev/> |
| `elk-learn` | Elasticsearch/Kibana, ingestion/search/production | `/docs` | `content/docs` | `dist` | <https://elk-learn.pages.dev/> |
| `kafka-learn` | Producers/consumers, Streams/Connect, operations | `/` | `content/docs` | `dist` | <https://kafka-learn.pages.dev> |
| `redis-learn` | Data structures, persistence/HA, patterns/operations | `/` | Root MD + README | `dist` | <https://redis-learn.pages.dev/> |
| `java-learn` | Java/JVM/concurrency, Spring/JPA/design patterns | `/` | `content/docs` | `dist` | <https://java-learn.pages.dev> |
| `jmm` | Java Memory Model | `/` | `content/docs/jmm` | `dist` | <https://jmm-ahk.pages.dev> |
| `jwt-learn` | JWT/auth/crypto, security/lifecycle/case studies | `/` | `content/docs` | `dist` | <https://jwt-learn.pages.dev/> |
| `react-learn` | React internals, rerender optimization/patterns | `/` | `content/docs` | `dist` | <https://react-learn-awm.pages.dev/> |
| `js-learn` | JS/TS, closures/prototypes, async/modules | `/` | `content/docs` | `dist` | <https://js-learn.pages.dev/> |
| `angular-learn` | Angular components/reactivity/routing/testing | `/docs` | `content/docs` | `dist` | <https://angular-learn.pages.dev/> |
| `rxjs-learn` | Observables/operators/schedulers/testing | `/docs` | `content/docs` | `out` | <https://rxjs-learn.pages.dev/docs/> |
| `micro-frontend-learn` | Composition/Federation, lifecycle/contracts/deploy | `/docs` | `content/docs` | `out` | <https://micro-frontend-learn.pages.dev/docs> |
| `interview-question` | Behavioral/Java/web/database/security/system design | `/` | `content/docs` + source labs | `dist` | <https://interview-question.pages.dev> |
| `system-design-practice` | URL shortener, pastebin, chat, feed, rate limiter | `/` | Năm MD root | `dist` | <https://system-design-practice.pages.dev> |

Mục thứ 25 trên landing là <https://aws-learn.pages.dev/practice/> cùng repo AWS. `github-actions-learn`, `mongodb-learn`, `elk-learn` **đã có** ở checkout hiện tại; không dùng kết luận “thiếu ba folder” của lần so sánh trước khi chúng xuất hiện.

Tên folder, tên package, Wrangler project và hostname không luôn trùng: `jmm` có package/Wrangler `jmm-learn`, `sql` có Wrangler `sql-learn`; các hostname có suffix như `-2tg`/`-by4` là dữ liệu cấu hình portal. Không tự tái tạo URL từ folder name.

## Phien-ban-va-consumers

Ý định stack chung là Fumadocs + Next.js + React hiện đại. **Manifest chưa đồng nhất và “mới nhất” không phải một invariant đã được kiểm tra.** Bảng là declaration trong package.json, không phải version resolved trong lockfile/node_modules, cũng không xác nhận npm latest hoặc website live.

| Repo | Next | React | Fumadocs core / MDX | docs-kit |
|---|---|---|---|---|
| `angular-learn` | `^16.3.4` | `^19.3.0` | `^16.15.9` / `^15.4.0` | — |
| `aws-learn` | `^15.2.4` | `^19.0.0` | `^14.5.6` / `^11.1.3` | — |
| `docker-learn` | `16.2.10` | `^19.2.7` | `16.11.5` / `15.2.0` | — |
| `elk-learn` | `^16.3.0` | `^19.2.0` | `^16.14.0` / `^15.2.2` | — |
| `github-actions-learn` | `16.2.11` | `19.2.8` | `16.11.5` / `15.2.0` | — |
| `graphql-learn` | `16.3.3` | `19.2.8` | `16.15.4` / `15.4.0` | — |
| `interview-question` | `^16.2.11` | `^19.2.8` | `^16.12.1` / `^15.2.0` | `^0.9.0` |
| `java-learn` | `^16.2.11` | `^19.2.8` | `^16.12.0` / `^15.2.0` | `^0.5.0` |
| `jenkins-learn` | `16.2.11` | `19.2.8` | `16.11.5` / `15.2.0` | `0.9.0` |
| `jmm` | `^16.2.11` | `^19.2.8` | `^16.12.1` / `^15.2.0` | `^0.9.0` |
| `js-learn` | `^16.2.12` | `^19.2.8` | `^16.12.1` / `^15.2.0` | — |
| `jwt-learn` | `^16.2.11` | `^19.2.8` | `^16.12.1` / `^15.2.0` | — |
| `k8s-learn` | `^16.2.10` | `^19.2.7` | `^16.11.5` / `^15.2.0` | `^0.9.0` |
| `kafka-learn` | `^16.2.12` | `^19.2.8` | `^16.12.1` / `^15.2.0` | `^0.9.0` |
| `micro-frontend-learn` | `^16.4.0` | `^19.2.0` | `16.17.1` / `15.4.7` | `0.5.0` |
| `microservice-learn` | `16.3.0` | `19.2.8` | `16.14.0` / `15.2.2` | `^0.9.0` |
| `mongodb-learn` | `16.3.0` | `^19.2.8` | `16.14.3` / `15.2.3` | — |
| `multi-tenant` | `^16.2.12` | `^19.2.8` | `^16.12.1` / `^15.2.0` | `^0.9.0` |
| `otel-learn` | `16.2.12` | `19.2.8` | `16.13.0` / `15.2.0` | — |
| `react-learn` | `^16.2.11` | `^19.2.8` | `^16.12.1` / `^15.2.0` | — |
| `redis-learn` | `^16.2.11` | `^19.2.8` | `^16.12.1` / `^15.2.0` | `^0.9.0` |
| `rxjs-learn` | `16.3.8` | `19.3.0` | `16.16.0` / `15.4.6` | — |
| `sql` | `^16.2.11` | `^19.2.8` | `^16.12.1` / `^15.2.0` | `0.5.0` |
| `system-design-practice` | `^16.2.12` | `^19.2.8` | `^16.12.1` / `^15.2.0` | `^0.9.0` |

`fumadocs-ui` là npm alias sang `@fumadocs/base-ui` tại Docker, GitHub Actions, Jenkins, MongoDB và OpenTelemetry; các site khác khai báo `fumadocs-ui` trực tiếp. Cùng import string không có nghĩa cùng implementation/version. Thay registry/components/layout cần đọc API của version consumer, không copy nguyên setup từ site khác.

Hai skill Fumadocs dùng chung nằm ở root `.agents/skills/`, không còn cài riêng trong mỗi repo; skill của AWS được giữ nguyên. Marketplace skill cũ trong `docs/` đã gỡ. [Ownership và cách dùng](landing-and-authoring-tools.md#skill-dung-chung-tai-root).

Tình trạng body/placeholder được quản lý riêng tại [kiểm kê curriculum](content-status.md#tong-hop-24-repo); số trang không phải số bài đã hoàn thiện.

Không có manifest consumer dùng `file:../docs-kit` hiện tại; các dependency docs-kit được khai báo theo npm version. Phát triển local bằng packed install vẫn có thể thực hiện có chủ đích, nhưng deploy repo độc lập phải tránh phụ thuộc checkout bên cạnh. [Package contract và rollout](docs-kit.md#mo-rong-va-phat-hanh).

## Bien-the-ung-dung

- `/docs` sites có App Router tại `app/docs/[[...slug]]` hoặc `src/app/docs/[[...slug]]`; root có homepage/redirect riêng. Root-route sites dùng `src/app/[[...slug]]`. App sống ở root `app/` tại Angular, ELK, GraphQL, RxJS và Micro-frontend; không ép tất cả về `src/app`.
- Collection/import alias và macro khác nhau: xem [compile/render](content-pipeline.md#compile-va-hien-thi).
- Direct authoring, root-generated collection và source labs có authority khác nhau; xem [nguồn nội dung](content-pipeline.md#nguon-noi-dung).
- Agent-facing LLM/OG output chỉ có ở một số template; [search và agent surfaces](content-pipeline.md#search-va-noi-dung-cho-agent).
- Một số repo có Wiki con: `docs/wiki/quickstart.md`, `docker-learn/wiki/quickstart.md`, `k8s-learn/wiki/quickstart.md`. Chúng bổ sung chi tiết repo; kiểm chứng source nếu mâu thuẫn, nhất là Wiki landing cũ.

## Thanh-cong-loi-va-pham-vi-thay-doi

Site build/publish độc lập: lỗi một site không rollback site khác; landing vẫn có thể trỏ sang URL lỗi. Package release chưa làm consumer nào đổi nếu dependency/lockfile chưa nâng và site chưa build. Search index, source manifests và HTML cần cùng snapshot export; cập nhật một public file riêng lẻ có thể gây stale refs.

Root có `scripts/sync-repos.py` và workflow đồng bộ gitlinks theo `main` mỗi 30 phút/manual/dispatch; không có orchestration deploy/upgrade/test ứng dụng đồng loạt, tự đếm số bài portal hoặc hợp đồng version thống nhất. Bảng phiên bản và counts trong Wiki là snapshot trước sync, cần kiểm tra manifest mới khi quyết định thay đổi. Khi thêm repo, cần chốt Node/dependencies, authority nội dung, route, output, validation và Pages project trước khi thêm link landing. Quy trình: [vận hành và deploy](development-and-deployment.md#them-hoac-nang-cap-mot-site).

Unknowns: consumer package/API bên ngoài các checkout, setting auth/branch/cache/dashboard, lịch sử migrations/DB thực và độ đồng bộ source local với các website live. Không suy ra các điều đó từ việc folder tồn tại hoặc có `deploy` script.
