# My Docs

Tập hợp 24 repo tài liệu tiếng Việt, landing [`docs`](https://tbh-docs.pages.dev/) và component package `docs-kit`. Mỗi repo con là **Git submodule theo nhánh `main`**; root quản lý skill chung, Wiki và commit pointer của từng repo.

## Clone và đồng bộ

```bash
git clone https://github.com/vanhiep99w/my-docs.git
cd my-docs
git submodule update --init
python3 scripts/sync-repos.py --commit
git push origin main
```

Không cần `--recursive`: các submodule bên thứ ba trong repo con không nằm trong phạm vi đồng bộ của root.

Submodule luôn pin một commit để clone tái lập được; `branch = main` không tự cập nhật pointer. Workflow `.github/workflows/sync-repos.yml` kiểm tra `main` của tất cả repo con **mỗi 30 phút** và commit/push pointer mới. Có thể chạy ngay từ GitHub Actions → **Sync child repositories → Run workflow**, hoặc phát event `child-main-updated` qua `repository_dispatch` từ một integration có quyền.

Đây là đồng bộ định kỳ/event-triggered, không phải bảo đảm realtime tuyệt đối. GitHub có thể trì hoãn cron hoặc tắt lịch khi repo lâu không hoạt động; nếu cần cập nhật tức thì, gọi dispatch sau push hoặc chạy script local. Branch protection/Actions policy phải cho phép bot push `main`; workflow sẽ fail rõ nếu bị chặn, không force-push hay bỏ qua policy.

## Khi sửa repo con

```bash
cd redis-learn
git switch main
# sửa, kiểm tra, commit và push trong repo con
git push origin main
cd ..
python3 scripts/sync-repos.py --commit
git push origin main
```

Script chỉ fast-forward checkout sạch tới `origin/main`; không commit nội dung repo con, không stash/reset/clean hoặc push hộ. Dừng nếu có uncommitted work, branch khác, commit chưa push/divergence hay operation Git dang dở. Commit/push công việc ở repo con trước, rồi mới cập nhật root pointer.

```bash
python3 scripts/sync-repos.py --check   # fetch và kiểm tra; exit 1 nếu có checkout cũ
python3 scripts/sync-repos.py           # fast-forward, chưa commit root
python3 scripts/sync-repos.py --commit  # fast-forward và commit pointer; chưa push
python3 -m unittest discover -s tests -v
```

Nếu root push bị từ chối do có commit mới từ người khác, đồng bộ root bằng Git theo quy trình của nhóm, xử lý conflict rồi chạy script lại; không force-push. Chỉ đồng bộ source/pointers, không tự cài npm dependencies, build hay deploy mọi site. Repo con có thể có CI/deploy Git integration riêng khi nhận push.

## Skill và Wiki

- `.agents/skills/fumadocs-project-init/SKILL.md`: khởi tạo site và curriculum.
- `.agents/skills/fumadocs-technical-writer/SKILL.md`: viết bài bằng component `docs-kit` phù hợp; không sinh Mermaid/ASCII diagram.
- `wiki/quickstart.md`: bản đồ hệ thống, nguồn nội dung và validation theo repo.
- `AGENTS.md`: hướng dẫn đọc có chọn lọc cho coding agent.

Không đặt lại skill chung trong từng repo con. Giữ các skill AWS còn lại; checkout Excalidraw bên thứ ba trong AWS đã được xóa theo yêu cầu riêng của tác giả. Không lưu env/auth/token, log phiên làm việc hoặc generated build artifacts tại root.

## Ranh giới commit

Commit trong `my-docs` chỉ lưu root files và gitlink; code của mỗi doc phải commit/push tại repo của chính nó. Commit/push root không xuất bản thay đổi chưa push trong repo con. Dữ liệu Wiki kiểm kê là snapshot tại lần khảo sát, không tự tính lại khi workflow cập nhật submodule.
