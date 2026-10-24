# Áp dụng D2 request flow

## Phạm vi đã thực hiện

Đã áp dụng `mode=flow` cho **205 diagram trong 133 tài liệu nguồn thuộc 14 repo**, gồm **238 scenario / 1.519 bước**. Dùng package `docs-kit 0.12.0` đã cài trong từng host; không nâng dependency, thay renderer mặc định hoặc bật autoplay toàn site.

Static export có **198 flow trong 128 trang**. Chênh lệch là 7 diagram trong 5 bài tổng hợp Microservices: đây vẫn là nguồn được quản lý, nhưng preparer hiện xuất bản các bài pattern độc lập thay cho một số section tổng hợp. Không sửa trực tiếp output `content/docs/` của Redis, Microservices và System Design.

| Repo | Tài liệu nguồn | Flow | Ví dụ đã áp dụng |
| --- | ---: | ---: | --- |
| `angular-learn` | 5 | 9 | Authentication, cookie session, ETag, reconnect, SSR |
| `graphql-learn` | 15 | 19 | Request pipeline, JWT/401, validation/coercion, resolver, pagination |
| `interview-question` | 3 | 4 | Resume upload, SharedWorker/WebSocket ticket, Module Federation |
| `java-learn` | 19 | 32 | Spring MVC/Security/AOP, JPA flush/rollback, saga, OAuth2 |
| `jenkins-learn` | 2 | 2 | Build qua controller/agent, shared library invocation |
| `k8s-learn` | 20 | 21 | API request, runtime/CNI, DNS, Ingress, Service traffic, CSI |
| `kafka-learn` | 7 | 14 | Produce/fetch, retry, idempotency, offset/transaction failure windows |
| `micro-frontend-learn` | 5 | 5 | BFF auth/refresh, dynamic remote, compatibility/fallback, cache, bootstrap |
| `microservice-learn` | 36 | 64 | Discovery, request/reply, saga/outbox, retry, auth, tracing, event processing |
| `multi-tenant` | 2 | 3 | Authentication, tenant selection/switch, context qua message queue |
| `react-learn` | 2 | 2 | Portal event propagation, update/render/commit path |
| `redis-learn` | 11 | 21 | Cache hit/miss, write patterns, session, rate limit, routing, command lifecycle |
| `sql` | 2 | 4 | Connection/query, transaction giữ connection, outbox, N+1 |
| `system-design-practice` | 4 | 5 | Chat history, create paste, rate limit, create/redirect short URL |
| **Tổng** | **133** | **205** | |

## Quyết định khi chuyển đổi

- Tách các nhánh loại trừ nhau thành scenario: hit/miss, ALLOW/429, commit/rollback, return/exception, hợp lệ/401/403, tương thích/fallback, replay/snapshot.
- Tách các giai đoạn không nên giả vờ chạy nối tiếp: submit/worker/polling, tạo/dọn CNI sandbox, cache sync/local read, CLOSED/OPEN/HALF-OPEN.
- Thay các sequence nhiều nhánh của cache/session/rate limiter và URL Shortener bằng topology D2 cố định; giữ label, icon, request, response và publish event. Các sequence còn lại giữ notes, ordering và fragment có ý nghĩa, đồng thời thêm playback.
- Timeout/mất ACK là quan sát tại caller, không phải một response được nhận thành công: sửa các cạnh liên quan trong Kafka và Microservices thành bước local.
- Không bật autoplay/loop. Tốc độ trình chiếu không phải latency; không ngụ ý viewer chạy HTTP, code, timer hay mô phỏng fork/join.
- Giữ page identity, frontmatter, sidebar ordering, code snippets và source references. Chỉ cập nhật hash diagram trong các ledger GraphQL/React; không thay hash/provenance của code artifacts.
- Sửa structural checker của Micro-frontend để `# @flow` trong code fence không bị nhận nhầm là H1, kèm regression test. Test System Design vẫn kiểm tra message/response counts và nhánh song song cũ; bổ sung assertions hit bỏ qua DB, miss nạp cache, ALLOW/429 và custom alias/sinh ID.

## Những gì không chuyển hàng loạt

Flow chỉ phù hợp với đường đi/bước xử lý được biên soạn rõ ràng. Giữ static/steps/tabs cho ER/schema, dependency/ownership, memory layout, state snapshots, concurrency, fan-out/fan-in hoặc timing cần ngữ nghĩa riêng. Không biến mọi mũi tên thành một thứ tự thực thi.

- `jmm` và `js-learn`: không chọn các hình memory ordering, contention hoặc event-loop concurrency để giả làm request traversal trong đợt này.
- `elk-learn`: có dependency nhưng `source.config.ts` vẫn chỉ đăng ký Mermaid, chưa có đủ D2 plugin/component/CSS. Chưa đổi diagram thành flow không hoạt động.
- `aws-learn`, `docker-learn`, `github-actions-learn`, `jwt-learn`, `mongodb-learn`, `otel-learn`, `rxjs-learn`: chưa tích hợp docs-kit; không tự rollout package/runtime mới chỉ để sửa bài.

Đây là đợt áp dụng trên các ví dụ đã chọn và kiểm chứng, không phải cam kết mọi diagram còn lại đều đã được audit đầy đủ về technical accuracy. Không thay các skill AWS.

## Kiểm tra lại

Từ root, dùng Node hỗ trợ native TypeScript (đã kiểm tra trên Node 26.9.0), với dependencies của các host đã cài. Chuẩn bị các collection generated trước:

```bash
(cd redis-learn && npm run prepare-content)
(cd microservice-learn && npm run prepare-content)
(cd system-design-practice && npm run prepare-content)
node scripts/check-d2-flows.mjs
# Hoặc giới hạn repo:
node scripts/check-d2-flows.mjs --repo redis-learn --repo system-design-practice
```

Checker dùng **package đã cài và production remark plugins của từng host**, giữ page frontmatter/layout và icon transforms, compile mọi flow, kiểm tra edge/node mapping ở light/dark và server-render tất cả scenario/step explanations. Với Microservices, checker đọc cả canonical aggregates; build riêng xác minh collection được xuất bản. Checker không build/deploy site và không thay thế việc review ngữ nghĩa scenario.

### Kết quả kiểm tra đợt này

- Checker flow: **205/205 diagram**, 238 scenario, 1.519 bước; SVG hai theme và toàn bộ lời giải thích no-JS đều hợp lệ.
- **14/14 production builds** thành công. Focused tests/content checks của các repo có suite và typechecks đã chạy đều qua sau khi cập nhật các contract liên quan đến flow; Kubernetes dùng build làm check của repo.
- Browser smoke trên một trang có flow của mỗi site: chọn scenario, Next tới cuối, Reset, Play/Pause, giữ bước khi mở/đóng fullscreen, mobile dark + reduced motion, không tràn trang, no-JS fallback; **14/14 qua, không có hydration error**. Đây là smoke theo host, không phải browser test mọi diagram/scenario.
- Redis: **11/11 browser tests**; Multi-Tenant: browser integration test qua.
- `python3 scripts/check-stack.py`: qua; không đổi manifest/lockfile.

### Hạn chế còn lại của Java layout audit

`npm test`, `docs:check`, build và typecheck Java đều qua. Chạy thêm `docs:audit` thấy **9/31 layout budget không đạt**; cả 9 caption này thuộc diagram không sửa trong đợt flow. `docs:check-export` cũng báo dimension mismatch giữa report đo lại và export, kể cả các trang không thay đổi. Không sửa budget, scale hoặc renderer để che lỗi; cần một đợt đối chiếu audit/export riêng. Không coi hai extra check này là đã qua.

Chỉ build/serve local để xác minh; không chạy lệnh deploy và không xác minh website production.
