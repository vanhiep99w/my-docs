# Pipeline noi dung va routing

## Pham vi va ownership

Mỗi site sở hữu curriculum, metadata, MDX registry, layout và build riêng; không có content service dùng chung ở root. `docs-kit` cung cấp khả năng render/compile, không quản lý thứ tự bài hoặc URL của host. Danh sách repo, route prefix và output: [bản đồ repository](repositories.md#danh-muc-site).

Trạng thái bài rỗng/placeholder và phương pháp đếm nằm tại [kiểm kê nội dung](content-status.md#tieu-chi-phan-loai); build/metadata hợp lệ không chứng nhận bài đã viết xong. Hai skill biên soạn hiện dùng chung từ root, xem [shared skills](landing-and-authoring-tools.md#skill-dung-chung-tai-root).

Nguồn kiểm chứng: các `source.config.*`, `lib/source.ts`/`src/lib/source.ts`, App Router page/search handlers; preparer ở AWS/Redis/Microservices/System Design; tests ở Kafka, Jenkins, Redis, SQL và Micro-frontend.

## Nguon noi dung

**Chọn đúng nơi sửa trước khi chạy dev/build.** Tất cả site đều đọc collection `content/docs`, nhưng không phải ở đâu đó cũng là nguồn biên soạn.

| Kiểu | Nguồn tác giả sửa | Cơ chế / dữ liệu đầu ra |
|---|---|---|
| AWS | `.md` ở root + mục checklist trong `aws-learn/README.md` | `scripts/prepare-content.mjs` chọn mục `- [x] [Title](file.md) - Description` dưới section được map; sinh frontmatter, bỏ TOC/H1, đổi link, ghi `content/docs/<category>/*.md` và metadata |
| Redis | `.md` ở root + checklist `redis-learn/README.md` | Tương tự AWS, nhưng metadata category có `pages` theo thứ tự README; copy diagram assets nếu input tồn tại, đổi URL Redis icon trong fence D2 thành asset local |
| Microservices | `.md` root + các thư mục pattern và table trong `microservice-learn/README.md` | Parser table dựng route map; tách/group pattern, rewrite link và aggregate anchors; sinh metadata, gọi source generator |
| System Design Practice | Năm `.md` root được liệt kê trong `DESIGNS` | Sinh `content/docs/*.md`, title/description và rebasing icon trong D2; chỉ tạo root `meta.json` nếu chưa tồn tại |
| JWT | `jwt-learn/content/docs/` | `prepare-content.mjs` là no-op giữ tên lifecycle cũ, không copy root Markdown |
| Multi-Tenant | `multi-tenant/content/docs/` | Preparer chỉ tạo metadata khi thiếu; sau đó `build-source-examples.mjs` sinh source assets |
| Các site còn lại | `content/docs/*.md` hoặc `*.mdx` và `meta.json` trong từng repo | Không thấy hook chuyển root Markdown sang collection; Java, SQL, Interview, Micro-frontend vẫn có bước sinh source assets từ nội dung |

Redis preparer có nhánh kiểm tra input `redis-learn/docs/diagrams` trước khi thay `redis-learn/public/diagrams`; input này **hiện không có** trong checkout, nên không coi nhánh copy đó là bước luôn chạy.

Các file sinh không nên được sửa để thay thế nguồn upstream. Với preparer AWS/Redis, tên section/checklist sai hoặc file chưa tick sẽ không vào mapping. File được map nhưng không tồn tại chỉ warning/skip; build thành công không chứng minh curriculum đã đủ. Hai script này không dọn toàn bộ trang cũ sau rename/delete: rà generated collection và URL cũ.

Microservices chặt hơn: thiếu file trong README, output trùng hoặc `.md` link nội bộ không resolve sẽ throw; path nguồn không được thoát repo. Nó xóa/sinh lại **riêng** `content/docs/patterns`, không toàn bộ collection. Aggregate pattern links được map sang extracted page; anchor đã tách không được giữ như thể còn trên trang aggregate. Số pattern khác kỳ vọng hiện chỉ warning, không phải một schema bảo đảm.

System Design giữ nguyên `meta.json` có sẵn, nên thêm `DESIGNS` chưa đủ để sidebar có mục mới. Ngược lại AWS/Redis/Microservices ghi lại metadata theo script; sửa generated `meta.json` thủ công có thể mất ở lần build sau. Không áp một quy tắc “mọi preparer đều không ghi đè metadata” cho cả hệ thống.

## Compile va hien thi

Luồng đại diện:

```text
authored Markdown/MDX + meta.json + assets
  → npm predev/prebuild (nếu có)
  → Fumadocs MDX collection + remark/rehype plugins
  → generated source hoặc macro → loader(baseUrl)
  → generateStaticParams / metadata / page tree / search index
  → page.data.body(MDX components)
  → HTML + CSS + client islands trong dist hoặc out
  → Cloudflare Pages
```

- `defineDocs({dir: 'content/docs'})` thường ở `source.config.ts`. MongoDB định nghĩa collection bằng `fumadocs-mdx/macro` ngay trong `src/lib/source.ts`; RxJS dùng macro tại `lib/source.ts` và không có `source.config.*` checked-in.
- Generated import khác nhau: AWS `@/.source`, nhiều site `collections/server` (alias TypeScript vào `.source/*`), một số `@/.source/server`. Không sửa `.source` để thay config; kiểm tra `tsconfig.json` và version Fumadocs khi nâng dependency.
- `loader` tạo page tree và lookup theo slug. `baseUrl` là `/` hoặc `/docs`, **không phải** cấu hình Next `basePath`. Copy prefix từ repo khác có thể làm sidebar/search sai URL.
- Route lấy `source.getPage`, trả `notFound()` nếu không có, render title/description/TOC và `page.data.body`. `generateStaticParams` liệt kê đường dẫn để export; nhiều catch-all thêm explicit root slug để redirect.
- Layout giữ Fumadocs `RootProvider`, docs layout/page tree và CSS. Component registry thường ở `src/mdx-components.tsx`, `mdx-components.tsx` hoặc `src/components/mdx.tsx`; một số repo truyền map ngay trong page.

Ví dụ tích hợp hoàn chỉnh: `kafka-learn/source.config.ts` đăng ký D2 và learning-fence plugins; `src/mdx-components.tsx` map component tương ứng; `src/app/globals.css` import CSS; page gọi `getMDXComponents()`. **Cả ba lớp plugin → component → stylesheet phải khớp**. Chỉ thêm npm dependency không đủ.

## Metadata va navigation

Frontmatter cung cấp title/description; schema từng host quyết định field nào được giữ. Ví dụ Interview mở rộng `frontmatterSchema` cho `d2Layout`; Java dùng `src/lib/docs-schema.mjs`. Thêm layout frontmatter mà không thêm schema phù hợp có thể mất override trước khi remark chạy.

`meta.json` là input page tree: `pages` quy định ordering của file/folder. Đổi một file thành parent `folder/index.md[x]` cần cập nhật folder metadata, parent ordering, links/anchors và route đã phát hành. Giữ URL ổn định khi có thể, không mặc định ordering alphabet đúng lộ trình học.

**TOC không có một quy ước chung được máy cưỡng chế:** AWS/Redis preparer loại manual TOC; `micro-frontend-learn/scripts/check-docs.mjs` lại bắt buộc `## Mục lục`, title/description, không H1 lặp và kiểm tra link/anchor/meta targets. Dùng checker của repo đang sửa, không chuẩn hóa theo cảm tính.

Markdown và MDX cũng không tương đương về JSX. Java/SQL/Microservices/Multi-Tenant có remark chuyển SourceRef từ nội dung Markdown sang component; plugin/registry phải hoạt động cùng nhau. Không copy JSX từ `.mdx` sang `.md` mà không kiểm tra compile. Canonical source contract: [Source Explorer](source-explorer.md#hop-dong-du-lieu).

## Search va noi dung cho agent

Các search route là **index sinh khi build**, không phải backend search chạy Node trên Cloudflare:

- Thông thường `/api/search`, `createFromSource(source)` và `staticGET`, kết hợp `force-static` hoặc `revalidate = false`.
- Kafka guard collection rỗng, trả `{}` thay vì tạo search API.
- Micro-frontend dùng `/api/search.json`; `app/layout.tsx` cấu hình đúng `api` đó trong static search provider.
- Không thấy search handler local ở ELK, GraphQL, RxJS, React, Multi-Tenant hoặc System Design. Không giả định có endpoint chỉ vì UI dựa trên Fumadocs.

Docker, GitHub Actions, Jenkins và OpenTelemetry có `/llms.txt`, `/llms-full.txt` và `/llms.mdx/docs/[[...slug]]` để xuất Markdown đã xử lý; Docker/Jenkins/OpenTelemetry còn có OG route. `getLLMText` và URL helpers ở `src/lib/source.ts` sở hữu contract, per-page handler bỏ segment `content.md` cuối để lookup page. Đây là bề mặt cho crawler/agent, không phải raw source API hoặc khả năng chung của mọi site.

Nếu thay slug/processed Markdown/plugin, kiểm tra cả page HTML, search links và LLM output. Nội dung export cùng public assets đều có thể được tải công khai: không đưa credentials, env thật hoặc dữ liệu riêng tư vào ví dụ.

## Redirect va lifecycle URL

Next `redirect()` cho trang gốc và `public/_redirects` của Cloudflare là hai cơ chế khác nhau. Thử cả dev lẫn static preview; static server đơn giản không nhất thiết thực thi `_redirects`.

Ví dụ Interview giữ route cũ trong `src/lib/doc-redirects.ts`, thêm nó vào static params, đồng thời khai báo trong `public/_redirects`. `tests/site-routing.spec.ts` kiểm tra nội dung/route. Đổi slug chỉ trong filesystem sẽ không tự tạo redirect.

State nội dung nằm trong Git; search/HTML/manifest là snapshot theo build. Thay nguồn mà chưa rebuild/deploy không cập nhật website. Nếu bị sai generated output, sửa source/config, chạy lại hook đúng repo và kiểm tra diff; không xóa tùy tiện authored `content/docs` ở các repo direct-authoring.

## Kiem thu tap trung

| Thay đổi | Bằng chứng và cách kiểm tra |
|---|---|
| Learning fences / component wiring | Kafka `tests/docs-kit.test.mjs`: compile fences + registry/styles; Jenkins test cùng tên kiểm tra **export sau build** và không ship D2/WASM |
| D2 icons/System Design | `system-design-practice/tests/docs-kit.test.mjs`: chỉ rebase icon đúng fence, compile năm blueprint, descriptor lỗi phải fail, giữ nguyên numeric IDs |
| Diagram policy Redis | `tests/diagram-audit.test.mjs` + `scripts/audit-diagrams.mjs`; prebuild gọi audit trước prepare |
| Pattern routing/Microservices | `scripts/check-diagrams.test.mjs`, source/learning/diagram tests trong `scripts/*.test.mjs`; diagram checker đọc canonical sources thay vì generated copies |
| Metadata/links Micro-frontend | `npm run check:docs`, `check:export`, `check:source` và tests source/watch |
| SourceRef trong Markdown | SQL `tests/docs-content.test.mjs`, Java `tests/source-examples.test.mjs`; xem [source validation](source-explorer.md#kiem-thu-va-mo-rong) |

Các test đã được đọc để hiểu hợp đồng, **không được chạy trong run chỉ tạo Wiki này**. [Vận hành](development-and-deployment.md#validation-theo-repo) liệt kê lệnh và điều kiện setup. Không có một test command ở root chứng nhận tất cả repo.
