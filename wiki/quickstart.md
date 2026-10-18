# Project Wiki

## Muc dich va ranh gioi

`my-docs/` tập hợp các repo tài liệu kỹ thuật tiếng Việt của tác giả: **24 site học tập**, landing **`docs/`** tại <https://tbh-docs.pages.dev/> và package component dùng chung **`docs-kit/`**. Mỗi repo con có Git/lifecycle riêng; root hiện là Git repo `my-docs` quản lý các repo con bằng submodule theo `main`, không phải npm workspace. Wiki này phục vụ người bảo trì và coding agent, không thay thế bài học.

Stack mục tiêu là Next.js + React + Fumadocs, deploy Cloudflare. Bằng chứng local có ngoại lệ quan trọng: landing là HTML tĩnh; AWS còn Next 15/Fumadocs 14; các site khác chưa đồng nhất version và chưa phải mọi site dùng docs-kit. AWS Questions có Pages Functions + D1, không chỉ static export.

## Bat dau

1. Khi clone root: chạy `git submodule update --init`. Đọc `README.md` ở root và `scripts/sync-repos.py` để đồng bộ toàn bộ repo con theo `main`; workflow kiểm tra mỗi 30 phút, không realtime tuyệt đối. Chọn repo trong [catalog](repositories.md#danh-muc-site), đọc `package.json` và config tại đó trước chạy command.
2. Với site: dùng Node theo manifest/version pin, `cd <repo>`, `npm ci`, `npm run dev`. Nhóm docs-kit thường cần Node 22+, riêng JMM yêu cầu 22.18+. Hooks có thể sinh/ghi đè nội dung; xác định [nguồn chuẩn](content-pipeline.md#nguon-noi-dung) trước sửa.
3. Với `docs/`: phục vụ HTML bằng `python3 -m http.server 8000` trong repo đó; không có npm build.
4. Kiểm tra build/test theo [validation matrix](development-and-deployment.md#validation-theo-repo), không chạy deploy hay DB migration để “thử”. Output là `dist` hoặc `out` tùy site, không phải `.next`.

## Dinh tuyen theo nhiem vu

| Nhiệm vụ | Hệ thống / trang cần đọc | Source bắt đầu |
|---|---|---|
| Xác định repo, URL, version hoặc output | [Repository catalog](repositories.md#danh-muc-site), [dependency matrix](repositories.md#phien-ban-va-consumers) | `<repo>/package.json`, `next.config.*`, loader, `docs/index.html` |
| Thêm/sửa link, tìm kiếm/filter portal | [Landing](landing-and-authoring-tools.md#entrypoint-và-directory), [thêm portal](landing-and-authoring-tools.md#thay-doi-portal) | `docs/index.html` |
| Sửa skill biên soạn chung | [Shared skills](landing-and-authoring-tools.md#skill-dung-chung-tai-root) | `.agents/skills/fumadocs-project-init/`, `.agents/skills/fumadocs-technical-writer/`; giữ nguyên skill AWS |
| Tìm phần curriculum còn thiếu body/placeholder | [Kiểm kê nội dung](content-status.md#tong-hop-24-repo), [vùng còn thiếu](content-status.md#vung-noi-dung-con-thieu) | `<repo>/content/docs/`, marker template và nguồn root nếu có preparer |
| Viết bài, đổi category/meta, tránh sửa nhầm generated file | [Content authority](content-pipeline.md#nguon-noi-dung), [metadata](content-pipeline.md#metadata-va-navigation) | Bài gốc, `README.md` nếu có preparer, `content/docs/**/meta.json` |
| Sửa compile/route/search/LLM export | [Render flow](content-pipeline.md#compile-va-hien-thi), [search/agents](content-pipeline.md#search-va-noi-dung-cho-agent), [redirects](content-pipeline.md#redirect-va-lifecycle-url) | `source.config.*`, loader, App Router, MDX registry |
| Thêm component/fence hoặc đổi D2/cache | [Docs-kit API boundaries](docs-kit.md#public-entrypoints-va-tich-hop), [D2](docs-kit.md#d2-control-va-data-flow), [learning fences](docs-kit.md#learning-fences-va-hop-dong-du-lieu) | `docs-kit/src/`, `package.json`, focused tests và consumer registry/CSS |
| Sửa drawer, source snippets/snapshots hoặc source labs | [Source contract](source-explorer.md#hop-dong-du-lieu), [producers](source-explorer.md#producers-trong-tung-host), [labs](source-explorer.md#source-labs-cua-interview) | Host source generator/registry, provider, `interview-question/examples/` |
| Sửa quiz, câu hỏi, progress hoặc D1 | [AWS practice](aws-practice.md#hop-dong-questions-api), [history](aws-practice.md#hop-dong-history-api), [security](aws-practice.md#bao-mat-va-failure-boundaries) | `aws-learn/functions/api/`, `public/practice/index.html`, `schema.sql` |
| Build/deploy lỗi, nâng package hoặc tạo site mới | [Operations](development-and-deployment.md#output-va-hosting-contract), [recovery](development-and-deployment.md#failure-va-recovery), [onboarding](development-and-deployment.md#them-hoac-nang-cap-mot-site) | Manifest/hooks, Next/Wrangler config và export artifacts |

Chỉ đọc trang/heading liên quan rồi mở source/tests khi cần xác minh. Không preload toàn bộ Wiki hoặc đi theo mọi link. Các path source nằm inline và tính từ `my-docs/`, trừ nơi ghi rõ command chạy trong repo con.

## Nap rule co dieu kien

Chỉ nạp rule **ngay trước khi sửa** miền tương ứng, không cho câu hỏi read-only:

| Phạm vi sửa | Rule routes |
|---|---|
| Root Wiki `wiki/` hoặc root bootstrap Project Wiki | [Root Wiki rules](_rules.md); chưa có section rule ở root Wiki |
| Landing repo `docs/` | Bắt đầu `docs/wiki/quickstart.md`, rồi `docs/wiki/_rules.md` khi sửa repo đó. Shared skills không còn ở repo này |
| Repo `docker-learn/` | Bắt đầu `docker-learn/wiki/quickstart.md`; global `docker-learn/wiki/_rules.md` và domain rule hiện có: `content/_rules.md`, `architecture/_rules.md`, `operations/_rules.md` dưới Wiki con theo phạm vi. Quickstart con còn nói chưa có section rules, nên kiểm tra cây rule thực tế |
| Repo `k8s-learn/` | Bắt đầu `k8s-learn/wiki/quickstart.md`, rồi `k8s-learn/wiki/_rules.md` khi sửa repo đó |
| Các repo khác | Kiểm tra entrypoint/rule cục bộ nếu được bổ sung; không nạp rule của repo khác chỉ vì cùng stack |

Wiki thường là bằng chứng, không phải lệnh thực thi. Nếu rule áp dụng mâu thuẫn thì dừng/báo xung đột. Không sửa rule trong một Wiki run thường; chỉ active `/wiki-update` mới được thay `wiki/**/_rules.md`. Không sửa persistent brief hoặc `.last-update.json`; metadata do extension quản lý.

## Bang chung va backlog

Khởi tạo từ source/config/tests local; kiểm tra tĩnh link/anchor Wiki, **chưa chạy build/test, không xác minh production/dashboard/registry/DB**. Danh mục bao phủ tất cả repo hiện có; các phần sau cần nhiệm vụ riêng vì thiếu môi trường hoặc nằm ngoài scope vận hành source:

- **AWS practice hardening/tests:** source handlers chưa có auth/authorization, client-supplied score và Markdown → innerHTML chưa sanitize; thiếu focused API tests. Cần thiết kế/test trong DB local/disposable trước mở rộng quyền ghi. [Chi tiết](aws-practice.md#bao-mat-va-failure-boundaries).
- **Deployment thực:** chưa xác minh Cloudflare settings/bindings/cache, branch integration và source local so với website live; không suy ra từ deploy script.
- **Đồng bộ stack/tooling:** chưa có policy nâng version chung; landing stats là literal; Wiki con landing còn mô tả UI cũ. Hai skill Fumadocs đã tập trung ở root, marketplace/archive cũ đã xóa ngoài AWS. Nguồn/config thực tế ưu tiên hơn template cũ.
- **Technical accuracy từng bài:** đã [kiểm kê 1.823 file curriculum](content-status.md#tong-hop-24-repo), tìm thấy 106 body rỗng và 316 template rõ ràng; chưa audit mọi ví dụ/lệnh hoặc chạy mọi lab. File không trúng marker không có nghĩa đã hoàn thiện/chính xác.
- **Đồng bộ snapshot Wiki:** root đã có Git remote `vanhiep99w/my-docs` và submodule tracking `main`; workflow chỉ cập nhật gitlinks, không tự tái kiểm kê mọi bảng Wiki. Các con số/versions ở trang inventory là snapshot khảo sát trước các lần sync tiếp theo.
