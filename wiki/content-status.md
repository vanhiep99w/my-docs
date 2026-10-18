# Kiem ke noi dung va placeholder

## Pham vi va cach doc ket qua

Kiểm kê filesystem của **24 collection `content/docs`**, không phải trạng thái website live. Tổng hiện có **1.823 file Markdown/MDX**, trong đó **106 trang chưa có body** và **316 trang có marker template rõ ràng**. Như vậy có **422 trang cần viết body hoặc thay khung** theo tiêu chí dưới đây.

**1.401 trang còn lại không có nghĩa là đã hoàn thiện.** Nhóm này gồm bài dài, trang index/tổng quan, tài liệu có thể còn thiếu phần, và cả nội dung chưa được audit. Không dùng phép trừ này để công bố tỷ lệ hoàn thành.

Ownership: mỗi repo sở hữu nội dung và metadata; Wiki này chỉ ghi nhận snapshot. `docs-kit/docs`, root Wiki, Wiki con, skill references và source labs không nằm trong mẫu đếm. AWS Questions trong D1 cũng không được đếm như file bài học. Xem [catalog](repositories.md#danh-muc-site) để chọn repo/URL và [nguồn biên soạn](content-pipeline.md#nguon-noi-dung) để chọn đúng file sửa.

## Tieu chi phan loai

Các nhóm loại trừ nhau, theo thứ tự:

1. **Rỗng:** bỏ YAML frontmatter đầu file và whitespace, không còn body. Frontmatter có title/description vẫn chưa phải bài học.
2. **Khung rõ ràng:** body không rỗng; ngoài fenced code có một trong các marker template được kiểm tra ở các file đại diện dưới đây.
3. **Khác:** mọi file còn lại; chưa xác nhận chất lượng, độ chính xác hay độ hoàn thiện.

| Marker | Source đại diện đã đọc |
|---|---|
| `Đây là placeholder page.` | `elk-learn/content/docs/advanced-search/autocomplete.mdx` |
| `Đây là trang placeholder. Nội dung chuyên sâu` | `mongodb-learn/content/docs/aggregation/aggregation-pipeline.mdx` |
| `Đây là trang placeholder trong curriculum Kubernetes.` | `k8s-learn/content/docs/certifications/certification-overview.md` |
| `Trang này là **placeholder** cho chủ đề` | `otel-learn/content/docs/labs/collector-pipeline.mdx` |
| Callout có `title="Trang placeholder"` | `graphql-learn/content/docs/bao-mat-va-quan-sat/logging-va-tracing.mdx` |
| `Placeholder: bổ sung nội dung` | `github-actions-learn/content/docs/cong-thuc/01-basic-ci.md` |
| `TODO: Viết nội dung chi tiết cho doc này.` | `redis-learn/content/docs/operations/backup-restore.md` và nguồn `redis-learn/backup-restore.md` |

Không dùng grep mọi từ `placeholder`, `TODO`, “sẽ được” hoặc “đang được” để phân loại. Ví dụ Angular có placeholder của deferrable views/content projection; Docker có hostname/proxy placeholder; Redis có caching placeholder/generation. Đây là nội dung kỹ thuật thực, không phải trang bỏ trống. Code samples có TODO cũng không tự biến cả trang thành khung.

## Tong hop 24 repo

Các số tính cả index/category pages nếu là `.md`/`.mdx`, không tính `meta.json`. “Khác” chỉ là phần chưa thuộc hai tiêu chí thiếu body/template.

| Repo | Tổng file | Rỗng | Khung rõ ràng | Khác |
|---|---:|---:|---:|---:|
| `angular-learn` | 76 | 0 | 0 | 76 |
| `aws-learn` | 138 | 0 | 0 | 138 |
| `docker-learn` | 258 | 106 | 0 | 152 |
| `elk-learn` | 83 | 0 | 52 | 31 |
| `github-actions-learn` | 105 | 0 | 26 | 79 |
| `graphql-learn` | 84 | 0 | 38 | 46 |
| `interview-question` | 24 | 0 | 0 | 24 |
| `java-learn` | 88 | 0 | 0 | 88 |
| `jenkins-learn` | 89 | 0 | 0 | 89 |
| `jmm` | 25 | 0 | 0 | 25 |
| `js-learn` | 35 | 0 | 0 | 35 |
| `jwt-learn` | 45 | 0 | 0 | 45 |
| `k8s-learn` | 191 | 0 | 105 | 86 |
| `kafka-learn` | 36 | 0 | 0 | 36 |
| `micro-frontend-learn` | 81 | 0 | 0 | 81 |
| `microservice-learn` | 69 | 0 | 0 | 69 |
| `mongodb-learn` | 78 | 0 | 61 | 17 |
| `multi-tenant` | 16 | 0 | 0 | 16 |
| `otel-learn` | 104 | 0 | 30 | 74 |
| `react-learn` | 29 | 0 | 0 | 29 |
| `redis-learn` | 38 | 0 | 4 | 34 |
| `rxjs-learn` | 81 | 0 | 0 | 81 |
| `sql` | 45 | 0 | 0 | 45 |
| `system-design-practice` | 5 | 0 | 0 | 5 |
| **Tổng** | **1.823** | **106** | **316** | **1.401** |

Không thay trực tiếp số `718+` hay count từng portal bằng các số này: count ở landing là literal biên tập, còn mẫu trên gồm cả placeholder/category pages và collection có thể đã cũ. Chưa chạy prepare/build để đồng bộ hoặc so sánh với live site.

## Vung noi dung con thieu

Đường dẫn category trong các bảng sau tương đối với `<repo>/content/docs/`. Con số chỉ là trang thiếu body/khung, không phải tổng số trang category.

### Docker: 106 trang chi co frontmatter

| Category | Rỗng |
|---|---:|
| `development-va-cicd` | 13 |
| `docker-internals` | 13 |
| `docker-swarm` | 11 |
| `he-sinh-thai-va-thay-the` | 8 |
| `kubernetes-va-docker` | 8 |
| `labs-va-case-studies` | 13 |
| `observability-va-troubleshooting` | 14 |
| `production-operations` | 13 |
| `tham-khao` | 13 |

Ví dụ `docker-learn/content/docs/development-va-cicd/ci-builds.mdx` không có body sau frontmatter. Category `development-va-cicd/meta.json` đã có `pages` liệt kê các trang, nên có mục trong curriculum không chứng minh bài đã được viết. Wiki con Docker còn có số liệu kiểm kê trước đây; khi cần tình trạng hiện tại, chạy lại phương pháp dưới đây thay vì dùng count cũ.

### Kubernetes: 105 trang khung

| Category | Khung |
|---|---:|
| `certifications` | 6 |
| `cluster-administration` | 15 |
| `delivery` | 12 |
| `ecosystem` | 12 |
| `labs-projects` | 12 |
| `observability` | 10 |
| `production` | 11 |
| `security` | 16 |
| `troubleshooting` | 11 |

`delivery` có cả 9 file thuộc nhóm “khác”, không phải toàn category đều placeholder. Category `security/meta.json` đã liệt kê đủ 16 mục; cần viết bài, không tạo thêm file cùng chủ đề chỉ để có trang trên sidebar. Root index và Wiki con còn lời mô tả/count từ các đợt curriculum cũ, không dùng làm chứng nhận trạng thái hiện tại.

### MongoDB: 61 trang khung

| Category | Khung |
|---|---:|
| `aggregation` | 6 |
| `bao-mat-va-production` | 8 |
| `bat-dau` | 5 |
| `crud-va-truy-van` | 7 |
| `indexes-va-hieu-nang` | 6 |
| `replication-va-sharding` | 7 |
| `thiet-ke-du-lieu` | 6 |
| `transactions-va-consistency` | 5 |
| `troubleshooting` | 5 |
| `ung-dung-va-cong-cu` | 6 |

17 file “khác” gồm 6 trang trong `nen-tang`, 10 category indexes và root index. Vì vậy không diễn giải “17” thành 17 bài chuyên sâu. `bat-dau/meta.json` đã đăng ký các trang cài đặt/local/Atlas/mongosh/Compass/CRUD đầu tiên còn mang template: đây là khoảng trống đầu lộ trình đáng ưu tiên về mặt trải nghiệm học.

### ELK: 52 trang khung

| Category | Khung |
|---|---:|
| `advanced-search` | 6 |
| `clients-integrations` | 6 |
| `data-ingestion` | 7 |
| `deployment` | 6 |
| `kibana` | 6 |
| `observability-security` | 7 |
| `production` | 8 |
| `troubleshooting` | 6 |

Các category trên đều có một index thuộc nhóm “khác”. Các nhóm `bat-dau`, `elasticsearch-core`, `nen-tang` không trúng marker stub ở snapshot này. Root index vẫn nói các bài hiện là placeholder; đó là copy tổng quát có thể đã cũ, không thay thế kiểm tra body từng file.

### GraphQL: 38 trang khung

| Category | Khung |
|---|---:|
| `bao-mat-va-quan-sat` | 2 |
| `client-va-tich-hop` | 7 |
| `production` | 7 |
| `tich-hop-spring-for-graphql` | 3 |
| `trien-khai` | 6 |
| `truy-cap-du-lieu-va-hieu-nang` | 6 |
| `xu-ly-su-co` | 7 |

Các category hỗn hợp không nên bị đánh dấu “chưa viết cả nhóm”. Ví dụ `bao-mat-va-quan-sat` có 5 file không trúng marker và 2 stub. Body Callout tự nhận “Trang placeholder” là bằng chứng thiếu nội dung mạnh hơn từ `placeholder` trong ví dụ policy/security của bài dài.

### OpenTelemetry: 30 trang khung

| Category | Khung |
|---|---:|
| `labs` | 7 |
| `production` | 9 |
| `reference` | 6 |
| `troubleshooting` | 8 |

Mỗi nhóm này còn một index không thuộc marker. Các marker chỉ hứa bổ sung mental model, cấu hình, kiểm chứng và failure modes, chưa chứa phần hướng dẫn đó.

### GitHub Actions: 26 trang khung

| Category | Khung |
|---|---:|
| `cong-thuc` | 8 |
| `nang-cao` | 9 |
| `tham-chieu` | 9 |

Các trang có H1/TOC/Best Practices/Troubleshooting đầy đủ heading nhưng nội dung vẫn là “Placeholder: bổ sung…”. Kiểm tra có heading/frontmatter và build thành công không đủ để kết luận đây là bài hoàn thiện. `cong-thuc/meta.json` đã có đủ 8 công thức, nên sửa file hiện có theo thứ tự thay vì thêm duplicate recipe.

### Redis: 4 trang operations

Bốn nguồn biên soạn `redis-learn/security.md`, `redis-learn/monitoring.md`, `redis-learn/backup-restore.md`, `redis-learn/troubleshooting.md` đều có marker TODO template; collection `operations/` tương ứng cũng có marker. `redis-learn/content/docs/operations/meta.json` đã liệt kê cả bốn.

Đây là repo dùng root Markdown + README mapping rồi sinh collection: sửa **nguồn root**, không chỉ sửa bản dưới `content/docs`. Trong run này chỉ đối chiếu marker tồn tại hai phía, chưa chạy preparer hoặc chứng minh mọi byte của collection đã đồng bộ.

## Uu tien de xuat va workflow

Đây là đề xuất biên tập, không phải business requirement đã tồn tại trong code:

1. **Đóng khoảng trống đầu lộ trình:** MongoDB `bat-dau` và CRUD giúp người đọc có đường chạy ví dụ trước các phần nâng cao.
2. **Hoàn thiện operations có phạm vi nhỏ:** bốn bài Redis có nguồn/template rõ, thuận tiện làm một đợt nội dung khép kín với lệnh kiểm chứng và recovery.
3. **Nối học với vận hành:** Docker CI/CD/production/troubleshooting, Kubernetes security/cluster-administration và OpenTelemetry labs/production theo thứ tự người học cần.
4. **Viết theo một nhóm coherent:** ELK ingestion → Kibana → production, GraphQL data access/observability → deploy, GitHub Actions recipes theo dependency; không chỉ thay chữ placeholder cho đủ chỉ số.

Mỗi đợt: chọn nguồn chuẩn → đọc category metadata và bài liên quan → thay body khung bằng cơ chế, ví dụ, trade-offs, failure/recovery và kiểm chứng → chạy validation của repo → kiểm tra route/sidebar/export → cập nhật snapshot Wiki khi cần. Xem [validation matrix](development-and-deployment.md#validation-theo-repo).

Nếu còn placeholder được giữ có chủ đích, ghi rõ phạm vi dự kiến thay vì trình bày như tutorial đã kiểm chứng. Không tự xóa mục navigation hoặc đổi URL đã phát hành chỉ vì chưa viết body.

## Lap lai kiem ke

Chạy đoạn Python sau từ root tập hợp. Nó chỉ đọc Markdown/MDX trong các collection và in số liệu; không ghi file, regenerate hoặc kết nối mạng. Parser fence ở đây phục vụ inventory, không thay thế AST/MDX build validation.

```python
from pathlib import Path
from collections import Counter
import re

markers = [
    r'Đây là placeholder page\.',
    r'Đây là trang placeholder\. Nội dung chuyên sâu',
    r'Đây là trang placeholder trong curriculum Kubernetes\.',
    r'Trang này là \*\*placeholder\*\* cho chủ đề',
    r'<Callout\b[^>]*title="Trang placeholder"',
    r'Placeholder: bổ sung nội dung',
    r'TODO: Viết nội dung chi tiết cho doc này\.',
]

def without_code(body):
    lines, fence = [], None
    for line in body.splitlines():
        if fence:
            closing = r'^ {0,3}' + re.escape(fence[0])
            closing += r'{' + str(len(fence)) + r',}\s*$'
            if re.match(closing, line):
                fence = None
            continue
        match = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if match:
            fence = match[1]
        else:
            lines.append(line)
    return '\n'.join(lines)

total = Counter()
for repo in sorted(Path('.').iterdir()):
    base = repo / 'content/docs'
    if not base.is_dir():
        continue
    counts = Counter()
    for page in sorted(base.rglob('*')):
        if page.suffix not in ('.md', '.mdx'):
            continue
        body = re.sub(
            r'\A---\r?\n[\s\S]*?\r?\n---\r?\n?', '',
            page.read_text(encoding='utf-8'),
        ).strip()
        kind = 'empty' if not body else 'other'
        if body and any(re.search(m, without_code(body)) for m in markers):
            kind = 'stub'
        counts[kind] += 1
    counts['total'] = sum(counts.values())
    total.update(counts)
    print(repo.name, dict(counts))
print('TOTAL', dict(total))
```

## Gioi han va validation

- Đếm file hiện diện, **chưa chứng minh tất cả đều được navigation expose**; một số meta targets đã được đọc làm mẫu, không audit toàn bộ page-tree.
- Collection generated có thể stale; không chạy hook trong đợt chỉ tài liệu. Khi muốn công bố trạng thái build mới nhất phải đồng bộ nguồn trong nhiệm vụ được phép ghi repo con.
- Marker được kiểm chứng ở template hiện hành; nếu tác giả dùng template khác, đổi câu marker hoặc chỉ viết dở một phần thì có thể không trúng bộ lọc. Cần mở body trước kết luận.
- Không kiểm tra mọi code sample, external claim, broken link trong curriculum hoặc độ đầy đủ của runnable labs.
- Đã chạy kiểm kê đọc-only và đối chiếu số tổng/phân nhóm; không chạy tests/build/deploy ứng dụng. Các tests cấu trúc trong repo thường kiểm tra compile/render/contracts, không tự chứng nhận nội dung giảng giải đã hoàn chỉnh.
