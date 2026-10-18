# AWS Questions: Pages Functions va D1

## Pham vi va ownership

`AWS Questions` trên landing là một phần của repo `aws-learn/`, không phải repo riêng. Phần này khác site Fumadocs tĩnh:

```text
docs/index.html → AWS /practice/
 → aws-learn/public/practice/index.html (browser JS)
 → /api/questions + /api/practice-history (Cloudflare Pages Functions)
 → env.DB (Cloudflare D1)
```

Source: `aws-learn/public/practice/index.html`, `functions/api/{questions,practice-history}.js`, `schema.sql`, `scripts/migrate-question-numbers.mjs`, `wrangler.toml`, phần Practice Q&A trong README. `src/app/api/search` là search index tài liệu, **không** xử lý quiz API.

README nói push `main` auto-deploy; setting Git integration, binding/DB thật và tình trạng production chưa được kiểm chứng. Static export đơn thuần không chứng minh Functions + D1 đã triển khai đúng.

## State va lifecycle client

Trang practice là HTML/CSS/JS độc lập, không chạy trong React/Fumadocs component tree. Nó gọi API cùng origin và tải thư viện `marked` từ CDN.

- Danh sách câu hỏi và labels giữ trong memory; `PAGE_SIZE=20`, tải `mode=list`, hydrate detail theo ID khi cần description/notes. ID hoặc question number dùng để jump trực tiếp.
- Practice cho chọn rồi submit; Review hiển thị đáp án/giải thích ngay. `parseQuestion` đọc `Options:`, option dạng `#<number> — text`, `Answer:` và đặc biệt `metadata.answer` để xác định option đúng.
- Client tự tính correctness rồi POST `isCorrect`; không có chấm điểm tin cậy ở backend. API trả cả đáp án/metadata cho client, nên đây không phải hệ thống thi chống gian lận.
- Username được người dùng nhập và lưu localStorage; progress và starred/noted IDs lấy từ D1 theo tên đó. Đây là namespace tiện dụng, không phải tài khoản đăng nhập.
- LocalStorage còn giữ view mode, sort, theme và split width. Chọn đáp án chưa submit chỉ ở memory; submitted answers/notes được gửi backend.
- Auto-refresh mặc định tắt, khi bật poll câu hỏi mỗi 60 giây. Filters có thể yêu cầu tối đa 500 rows rồi lọc phía client; không phải server-side search/pagination đầy đủ cho mọi tập dữ liệu lớn.
- Note toggle có rollback local nếu POST fail; submit/retry-answer bắt lỗi rồi ghi console nhưng vẫn đổi UI. UI có thể trông như đã lưu dù D1 chưa nhận: kiểm tra reload/history, không coi UI feedback là persistence acknowledgment.

## Hop dong questions API

`functions/api/questions.js` export `onRequest`, trả JSON và CORS `*`, cho GET/POST/PATCH/OPTIONS. Không có DELETE. OPTIONS trả 204; method không hỗ trợ trả 405.

### GET

| Chế độ | Input | Output / lưu ý |
|---|---|---|
| Detail | `id` hoặc `number` | ID được ưu tiên nếu có cả hai; query không lọc status. Trả `{row, labels: string[]}` hoặc 404 |
| List | `limit` (default 50, tối đa 500), `offset` (default 0), `sort` | Chỉ `status='open'`; sort `created-asc`, `created-desc`, mặc định updated descending |
| Payload tối giản | `mode=list` | Không có `description`, `notes`; client cần hydrate |
| Optional phần phụ | `labels=0`, `count=1` | Tắt labels hoặc thêm total; labels list có shape `{issue_id, label}` khác detail |

List trả `{rows, labels, total?, hasMore}`; `hasMore` chỉ là `rows.length === limit`, không phải chứng minh có trang tiếp. Labels được query từng batch 90 question IDs để tránh quá nhiều D1 bind variables. `limit/offset/number` hiện parse thô, không validate đầy đủ NaN/âm/range; không mô tả chúng như input contract đã harden.

### POST va PATCH

POST cần title truthy; sinh ID `aws-learn-<8 chars>` bằng random đơn giản, lấy `question_sequence.number` rồi insert question mặc định `open`, priority `3`, issue type `decision`. Metadata có thể là string hoặc object serialize; description/notes mặc định rỗng. Labels array được insert ignore qua batch. Thành công 201 trả `{id, question_number, success}`.

PATCH cần `?id`, parse JSON rồi tìm question (404 nếu thiếu); các field không có trong body giữ nguyên. Cho cập nhật title/status/priority/issue_type/description/notes/metadata; question number giữ nguyên. Có `labels` nghĩa là thay toàn bộ tập labels, `[]` là xóa hết. Thành công trả `{id, success, updated_at}`.

Không có transaction bao toàn bộ sequence/question/labels. Đặc biệt PATCH thực hiện UPDATE question **trước** khi kiểm tra `labels` có phải array: request có thể trả 400 sau khi đã đổi các field khác. Recovery phải đọc lại dữ liệu để xác định phần đã thành công, không retry blind như thao tác atomic/idempotent. POST chưa có idempotency key; retry có thể tạo câu hỏi mới.

## Hop dong history API

`functions/api/practice-history.js` tạo bảng/index nếu thiếu ở đầu mỗi request trừ OPTIONS, rồi xử lý GET/POST/DELETE. Username được stringify, trim và cắt 80 ký tự; không có xác thực hay kiểm tra quyền sở hữu tên.

- **GET `?username=`**: kết hợp answer history và notes, kể cả note không có answer. Trả `{username, rows}`; row có `question_id`, `selected` array, `submitted`, `isCorrect`, `answeredAt`, `updatedAt`, `noted`, `noteUpdatedAt`.
- **POST answer**: cần username/question_id; normalize selected thành array strings, upsert theo `(username, question_id)`. `submitted` default true, correctness lấy từ body, không xác minh question tồn tại hay đáp án đúng.
- **POST note**: nếu body **có field `noted`**, chạy nhánh note và return, không đồng thời lưu answer. Chỉ boolean `true` là add/upsert, giá trị khác xóa note.
- **DELETE với question_id**: chỉ xóa answer của câu đó, giữ note dù truyền scope khác.
- **DELETE không question_id**: scope `notes`, `all` hoặc mặc định/history để xóa theo username. Hai DELETE của `all` không được bọc transaction.
- Thiếu username/question_id cần thiết hoặc JSON lỗi trả 400; method không hỗ trợ 405. Lỗi D1/parse stored JSON không có catch chuyển thành structured application error.

## Persistence va migration

`schema.sql` định nghĩa `questions`, `question_sequence`, `question_labels`, `practice_answer_history` và indexes. Các quan hệ question_id không có foreign key trong schema được đọc; xóa/sửa question không có cascade contract đã chứng minh.

`practice_question_notes` **không nằm trong schema.sql** hiện tại; history handler tự tạo cùng index. Schema có `CREATE TABLE IF NOT EXISTS`, không tự bổ sung column vào bảng cũ đã tồn tại.

`scripts/migrate-question-numbers.mjs` bổ sung question_number, sequence, backfill theo created_at/id và unique index. Nó gọi Wrangler qua subprocess; `D1_DATABASE` đổi tên DB và flags chọn scope. **Mặc định là `--remote`**, không phải local; nếu cả local/remote có mặt thì remote được ưu tiên. Không chạy chỉ để xem/validate tài liệu. Migration cố ý bỏ qua lỗi ALTER COLUMN đã có, nhưng cũng có thể che lỗi ALTER khác: phải kiểm tra kết quả và schema thực tế trong thay đổi vận hành đã được cho phép.

`wrangler.toml` khai báo Pages output `./dist` và D1 binding `DB`. Không đưa identifier database/account hoặc credential vào ví dụ Wiki. Không truy cập state `.wrangler`, live env hoặc dữ liệu người dùng để khởi tạo docs.

## Bao mat va failure boundaries

Các handler được đọc **không có authentication/authorization/rate limiting**; CORS wildcard không bảo vệ ghi dữ liệu. Người gọi có thể chọn username tùy ý, ghi/sửa questions hoặc xóa history nếu endpoint public đúng như code local. External access controls nếu có ở Cloudflare chưa được biết; không khẳng định site production đang mở hay đã an toàn.

Practice dùng `marked.parse` rồi đưa vào `innerHTML` cho stem/notes, không thấy sanitizer tại các đường render này. Với write API chưa xác thực trong source, đây là bề mặt stored HTML/XSS cần xem xét trước mở rộng người ghi. `esc()` có tồn tại cho một số text, không bảo vệ mọi Markdown-render path.

Các giới hạn khác: JSON body/field validation mỏng, không có atomic multi-step writes, tên người dùng không chứng minh identity, timestamps dạng string UTC không timezone suffix ở server, unknown external API consumers. Không coi progress là audit trail/điểm thi đáng tin cậy.

## Validation va mo rong

Không tìm thấy test suite cho hai Functions và practice client trong repo ở lần khảo sát này. Build Next chỉ kiểm tra/export docs, không kiểm thử D1, endpoints hay quiz correctness.

Khi có nhiệm vụ sửa tính năng này, cần môi trường D1 local/disposable và test tập trung:

1. Schema mới/cũ, backfill numbering và unique sequence; tránh default remote migration.
2. List/detail shapes, pagination bounds, >90 labels, status filtering và hydrate.
3. POST/PATCH validation trước ghi, lỗi giữa các bước và hành vi retry.
4. History upsert/note-only/delete scope; giữ note khi reset answer.
5. Username switching, reload persistence, network failure và feedback chưa lưu.
6. Trust boundary cho Markdown, write auth/authorization và endpoint access.
7. `wrangler pages dev dist` sau build để kiểm tra integration Functions; static `serve dist` không đủ.

Trước thay API/schema cần rà client functions tương ứng trong `public/practice/index.html`; không mặc định chỉ có một consumer bên ngoài. Các khoảng trống trên là backlog có bằng chứng source, không phải hành vi đã được sửa trong run Wiki này.
