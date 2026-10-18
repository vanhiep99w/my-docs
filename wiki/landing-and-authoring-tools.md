# Landing và công cụ biên soạn

## Phạm vi và ownership

Repo `docs/` sở hữu landing page `docs/index.html`. Marketplace `write-docs`, installer và archive skill cũ đã được gỡ; hai skill Fumadocs dùng chung hiện nằm tại root `.agents/skills/`, không trong repo landing. Landing chỉ dẫn người đọc đến site khác, không tổng hợp MDX hay gọi `docs-kit` khi chạy. Không có npm manifest/build/test runner ở repo này.

Nguồn chính: `docs/index.html`, `docs/README.md` và hai shared `SKILL.md` ở root. Wiki cũ trong `docs/wiki/` còn mô tả bento cards, particle/sky animation và 18 links; đó **không phải** UI hiện tại. Không dùng hướng dẫn `.card`/`.bento` đó cho directory hiện nay.

## Entrypoint và directory

Cloudflare phục vụ `index.html`; theo `docs/README.md`, build command để trống và output `/` tính từ repo `docs`, không phải từ thư mục cha `my-docs`. Không có cấu hình Cloudflare checked-in xác nhận dashboard đang dùng đúng setting.

HTML/CSS/JS inline chứa:

- Header, search `#track-search`, hero, learning graph SVG và thư viện `#track-directory`.
- Ba nhóm `infrastructure`, `backend`, `web`: hiện có 25 `.track-item`, tương ứng 24 site và một link AWS Questions trong AWS site.
- Mỗi item có `data-category`, từ khóa `data-search`, anchor `.track-link`, `.track-name` và `.track-meta`; các mục luyện tập thêm `data-practice`.
- Font Google được tải ngoài site; favicon và icons là SVG inline. Trang không có database, session hay API.

Danh sách URL và quan hệ repo nằm ở [bản đồ repository](repositories.md#danh-muc-site). URL là dữ liệu biên tập trong HTML, không suy ra từ tên folder hay `wrangler.name`.

## Cơ chế lọc và state

IIFE cuối `index.html` giữ `activeFilter` và `practiceOnly` trong bộ nhớ tab. Không ghi localStorage, không đồng bộ query string hoặc chia sẻ state giữa các site.

`updateDirectory()` chuẩn hóa tiếng Việt (lowercase, NFD, bỏ dấu và đổi `đ` thành `d`), rồi kiểm tra đồng thời category, practice và substring trên `data-search + textContent`. Kết quả điều khiển `hidden` của item/section và empty-state `role=status`.

- Nút filter đặt category, tắt practice-only và cập nhật `aria-pressed`; không xóa search.
- Gõ search tắt practice-only, giữ category.
- CTA Luyện tập đặt category `all`, bật practice-only và xóa search.
- Ctrl/Cmd+K focus/select search. Escape khi search đang focus xóa search, tắt practice-only, blur nhưng **giữ category**.
- Không JavaScript: anchor vẫn dùng được và toàn bộ mục hiện, nhưng search/filter không chạy. CSS có responsive layout và reduced-motion cho graph; cần kiểm tra browser khi sửa.

## Thay doi portal

1. Sửa/copy một `.track-item` trong nhóm phù hợp; category item phải khớp section và filter.
2. Điền URL đã kiểm tra, tên, metadata và keyword tìm kiếm; thêm `data-practice` nếu thực sự là mục luyện tập.
3. Nếu dùng icon mới, định nghĩa SVG symbol và kiểm tra `use href`.
4. Rà tất cả số liệu lặp ở head description, hero, graph, library và footer. `25`/`718+` cùng các số bài hiện là literal, **không được đếm tự động** từ repo hoặc website con.
5. Khi đổi URL site, kiểm tra đường dẫn gốc và `/docs`/redirect thật; không đổi hostname chỉ để khớp display name.

Validation từ repo `docs/`: `git diff --check`; dùng `python3 -m http.server 8000` để kiểm tra desktop/mobile, bàn phím, search có/không dấu, filter + search, practice, empty-state, reduced motion và links. Không có test tự động cho các tương tác này. Một site con lỗi không phá landing, nhưng link của người đọc sẽ hỏng; recovery là sửa anchor hoặc sửa deploy tại repo sở hữu site.

## Skill dung chung tai root

Chỉ giữ hai skill chung dưới root tập hợp:

- `.agents/skills/fumadocs-project-init/SKILL.md`: scaffold repo mới và curriculum placeholder; references gồm project templates, layout, outline và favicon.
- `.agents/skills/fumadocs-technical-writer/SKILL.md`: viết/chỉnh sửa bài theo nguồn chuẩn; chọn component docs-kit phù hợp cho D2, walkthrough/diff, terminal, HTTP, timed spans và source exploration. References gồm cấu trúc bài, docs-kit, component Fumadocs và writing voice.

Mỗi skill resolve references tương đối với **thư mục skill**, không phải working directory của repo đang viết bài. Chọn target repo trước sửa; root `my-docs`, landing `docs` và package `docs-kit` không phải chỗ scaffold một site mới đè lên dữ liệu hiện có. Template là ví dụ theo version, không bảo đảm npm latest; registry/component/CSS phải khớp host.

Các bản trùng và skill khác trong `.agents/skills` của repo con đã được xóa; không dùng symlink để lắp lại từng repo. Marketplace `write-docs`, manifest, installer và `.skill` distributions ngoài AWS cũng đã bị xóa theo yêu cầu. Các skill AWS còn lại trong `aws-learn/.agents/skills` và `aws-learn/.claude/skills` được giữ như ngoại lệ; riêng checkout Excalidraw bên thứ ba ở AWS đã bị xóa theo yêu cầu tiếp theo của tác giả.

`AGENTS.md` ở root định tuyến tới hai skill chung. Khi mở riêng một checkout repo con, thư mục parent này không tự đi theo Git clone; cần cho agent truy cập/configure shared skills rõ ràng. Không khẳng định mọi công cụ sẽ tự discover skill ở thư mục cha, và không cài/xóa bản global trong HOME trong thay đổi này.

Các tài liệu con cũ còn nhắc marketplace hoặc đường dẫn local đã xóa chỉ là tham chiếu lịch sử, không phải nguồn cài đặt hiện hành. Writer hiện không sinh Mermaid hoặc sơ đồ ASCII/Unicode, cũng không dùng API đã bị docs-kit loại bỏ như MarbleDiagram. Giữ log/output/payload/file listing dưới dạng text khi hợp lý; thiếu tích hợp docs-kit thì báo blocker hoặc xin phép bổ sung, không quay lại renderer cũ. Favicon và writing voice/readability vẫn được giữ trong các skill tương ứng.

## Ranh gioi thay doi

- Landing thay đổi và deploy từ Git repo `docs/`; shared skills thay đổi tại root `.agents/skills`, không tự đi cùng deploy landing.
- Viết bài học mới thuộc site sở hữu nội dung; xem [pipeline nội dung](content-pipeline.md#nguon-noi-dung).
- Component mới thuộc `docs-kit/`, sau đó từng consumer phải nâng package và build/deploy lại; landing không tự cập nhật theo npm release.
- Source local không xác nhận availability hay bài-count trên site đang live; cần kiểm tra môi trường khi quyết định cập nhật metadata.
