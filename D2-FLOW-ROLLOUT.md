# Áp dụng D2 request flow

## Phạm vi hiện tại

Theo phản hồi của người dùng, **sequence diagram có lifeline không dùng flow playback**. Thứ tự tương tác đã thể hiện sẵn từ trên xuống; giữ viewer D2 thông thường với zoom, fullscreen, source và SVG download, không thêm Scenario/Play/Next.

Đã gỡ playback khỏi **174 sequence diagram trong 109 tài liệu nguồn thuộc 12 repo**. Giữ diagram, labels, notes, icons, message ordering và các fragment; chỉ bỏ metadata/controls flow cùng prose chỉ dành cho playback. Các sửa lỗi timeout/mất ACK thành quan sát local tại caller vẫn được giữ.

Sau điều chỉnh còn **31 flow topology trong 26 trang thuộc 4 repo**, gồm **45 scenario / 242 bước**:

| Repo | Trang còn flow | Diagram còn flow | Nội dung |
| --- | ---: | ---: | --- |
| `graphql-learn` | 15 | 19 | Request pipeline, JWT/401, validation/coercion, resolver, pagination |
| `micro-frontend-learn` | 5 | 5 | BFF auth/refresh, dynamic remote, compatibility/fallback, cache, bootstrap |
| `redis-learn` | 3 | 3 | Cache hit/miss, session hợp lệ/hết hạn, rate-limit allow/deny |
| `system-design-practice` | 3 | 4 | Chat history, rate limit, create/redirect short URL |
| **Tổng** | **26** | **31** | |

Không còn flow trong `angular-learn`, `interview-question`, `java-learn`, `jenkins-learn`, `k8s-learn`, `kafka-learn`, `microservice-learn`, `multi-tenant`, `react-learn` và `sql`. Các sequence ở Redis và System Design cũng trở lại viewer thông thường. Ví dụ trong phản hồi là `redis-learn/lua-scripting.md` → `/advanced/lua-scripting/`.

Đợt đầu từng có 205 flow trong 133 tài liệu nguồn (198 flow/128 trang được xuất bản). Đây là số liệu lịch sử, **không phải phạm vi flow hiện tại**. Năm bài tổng hợp Microservices không có route riêng nay cũng không còn flow.

## Quyết định authoring

- Chỉ dùng `mode=flow` cho topology cố định, khi việc theo dõi đường đi hoặc chọn nhánh thực sự giúp đọc bài.
- Không dùng flow trên `shape: sequence_diagram`, kể cả sequence nhiều actor hoặc có nhiều nhánh. Giữ ordering, notes và fragment của sequence thay vì chồng thêm playback.
- Giữ static/steps/tabs cho ER/schema, dependency/ownership, memory layout, state snapshots, concurrency, fan-out/fan-in hoặc timing cần semantics riêng.
- Các topology còn flow tách nhánh loại trừ nhau: hit/miss, ALLOW/429, credential hợp lệ/401, compatibility/fallback. Không suy ra branch runtime từ topology.
- Không bật autoplay/loop toàn site. Tốc độ trình chiếu không phải latency; viewer không chạy HTTP, code, timer hay fork/join.
- Giữ page identity, frontmatter, navigation, code snippets và source references. React diagram ledger được cập nhật lại theo source sequence không có flow; không đổi hash/provenance của code artifacts.
- Không nâng dependency, sửa renderer mặc định, thay skill AWS hoặc sửa generated collection thay nguồn gốc.

Các site chưa đủ tích hợp D2/docs-kit (`elk-learn`, AWS, Docker, GitHub Actions, JWT, MongoDB, OTel, RxJS) không được tự thêm runtime/package chỉ để thay diagram. Các hình memory ordering/concurrency trong `jmm` và `js-learn` vẫn giữ cách trình bày cũ.

## Kiểm tra lại

Từ root, dùng Node hỗ trợ native TypeScript (đã kiểm tra trên Node 26.9.0), với dependencies của các host đã cài. Chuẩn bị collection generated trước:

```bash
(cd redis-learn && npm run prepare-content)
(cd microservice-learn && npm run prepare-content)
(cd system-design-practice && npm run prepare-content)
node --test tests/d2-flow-policy.test.mjs
node scripts/check-d2-flows.mjs
# Hoặc giới hạn repo:
node scripts/check-d2-flows.mjs --repo redis-learn --repo system-design-practice
```

Checker dùng **package đã cài và production remark plugins của từng host**, giữ frontmatter/layout và icon transforms, compile mọi flow, kiểm tra mapping light/dark và server-render toàn bộ lời giải thích. Nó **reject sequence/lifeline dùng `mode=flow`** trước compile. Repo có 0 flow là hợp lệ. Với Microservices, checker đọc cả canonical aggregates; preparation/build riêng xác minh collection xuất bản.

Checker không build/deploy site và không thay thế việc review ngữ nghĩa hoặc browser checks. Root có regression tests riêng cho policy sequence/topology.

## Validation

- Policy regression tests: qua; sequence/lifeline bị từ chối, topology và comment/label hợp lệ không bị nhận nhầm.
- Checker toàn bộ 14 host: còn đúng **31 diagram / 45 scenario / 242 bước**, không có sequence flow; SVG hai theme và toàn bộ lời giải thích no-JS hợp lệ.
- Kiểm tra source: cả **174 sequence diagram** giữ nguyên body D2 (labels, notes, icons, message ordering), chỉ bỏ descriptor và mode flow.
- Focused tests/content checks và **12/12 production builds** của các repo sửa trong đợt này qua; các typechecks/lint áp dụng cũng qua. Kubernetes dùng build làm check của repo.
- Browser smoke: **16/16 trang mẫu thuộc 14 host** qua. 12 trang sequence không còn Scenario/Play hay flow SVG attributes; 4 trang topology vẫn chọn scenario và chuyển bước được. Zoom/Fit, fullscreen, mobile dark/reduced motion và no-JS fallback hoạt động, không có hydration error. Đây là smoke theo host/loại diagram, không phải browser test mọi trang.
- Redis: **11/11 browser tests**; Multi-Tenant: browser integration test qua. Root: **2 policy tests + 39 Python unit tests** qua.
- Không suy ra deployment production từ build local.

### Hạn chế Java layout audit đã ghi nhận trước đó

Đợt đầu, `npm test`, `docs:check`, build và typecheck Java qua, nhưng extra `docs:audit` báo **9/31 layout budget không đạt**, đều ở caption không sửa trong đợt flow; `docs:check-export` cũng báo dimension mismatch giữa report đo lại và export. Không sửa budget, scale hoặc renderer để che lỗi, và không coi các extra check này là đã được khắc phục bởi việc bỏ playback.

Chỉ build/serve local để xác minh; không chạy lệnh deploy và không xác minh website production.
