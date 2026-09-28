# Thông Tin Deploy — Checkpoint 5

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Trần Long Khánh |
| Mã học viên | 2A202602538 |
| Repo | https://github.com/khanhtrankuri/K4-L3A-TranLongKhanh-2A202602538-CloudServiceAndDeployment |

## Service

| Mục | Nội dung |
|-----|----------|
| URL kiểm thử | http://localhost:8000 |
| Platform | Docker Compose local fallback (cấu hình cloud có sẵn cho Railway và Render) |
| Ngày kiểm thử | 2026-09-28 |
| Trạng thái | `agent` healthy, `redis` healthy |

Phiên làm bài này không có browser/cloud session đã xác thực để tạo service trên
Railway hoặc Render. Vì vậy bài dùng phương án dự phòng chính thức của lab với
`LOCAL_FALLBACK=true`. Không có URL cloud hoặc kết quả cloud nào được giả lập.

## Biến Môi Trường

Chỉ liệt kê tên và nguồn cấu hình; tài liệu này không chứa giá trị secret.

| Biến | Đã set | Nguồn |
|------|--------|-------|
| `PORT` | Có | Docker Compose đặt cổng 8000; cloud sẽ tự cấp `$PORT` |
| `AGENT_API_KEY` | Có | file `.env` cục bộ, bị `.gitignore` loại khỏi repo |
| `REDIS_URL` | Có | Compose đặt `redis://redis:6379/0` |
| `RATE_LIMIT_PER_MINUTE` | Có | file `.env` cục bộ |
| `MONTHLY_BUDGET_USD` | Có | file `.env` cục bộ |
| `LOG_LEVEL` | Có | file `.env` cục bộ |
| `LOCAL_FALLBACK` | Có | `true` trong file `.env` cục bộ |

## Lệnh Kiểm Tra

```bash
docker compose up -d --build
docker compose ps
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
curl -i -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
pytest tests/test_cp5.py -v
```

## Kết Quả Chạy Thật

Kết quả `docker compose ps`:

```text
agent   Up (healthy)   0.0.0.0:8000->8000/tcp
redis   Up (healthy)   0.0.0.0:6379->6379/tcp
```

Kết quả API:

```text
GET  /health -> 200 {"status":"ok","service":"day12-agent","version":"1.0.0"}
GET  /ready  -> 200 {"status":"ready","redis":true}
POST /ask không có X-API-Key -> 401 {"detail":"invalid or missing API key"}
POST /ask có key, cùng user (hai lần) -> history_length lần lượt 0 và 2
```

## Ảnh Chụp Màn Hình

- `screenshots/health.png` — ảnh chụp thật endpoint `/health` của stack local.

## Lỗi Gặp Phải Và Cách Xử Lý

Lần gọi `/ask` đầu tiên bằng `curl.exe` trả `422 Unprocessable Entity` với thông
báo `JSON decode error`. Nguyên nhân là PowerShell xử lý dấu nháy khiến JSON gửi
đi không còn hợp lệ. Tôi kiểm tra response body, chuyển sang tạo body bằng
`ConvertTo-Json`, rồi gọi lại; request hợp lệ không có key trả đúng 401. Với request
có key, tôi gọi từ bên trong container và đọc key trực tiếp từ environment nên
không in hoặc ghi secret vào command/output.
