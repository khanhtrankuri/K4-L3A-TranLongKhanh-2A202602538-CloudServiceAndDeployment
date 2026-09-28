# Phiếu Phản Ánh — K4 Level 3A, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay từng dòng giữ chỗ bên dưới bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Trần Long Khánh  Mã học viên: 2A202602538

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Nếu tôi quên set `AGENT_API_KEY` trên production, fail fast làm container dừng
> ngay và log startup chỉ thẳng vào biến còn thiếu. Nếu có mặc định
> `"changeme"`, service vẫn báo healthy và có thể nhận request bằng khóa mà ai
> đọc source cũng biết; lỗi cấu hình khi đó trở thành một lỗ hổng đang chạy thật.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Dòng log thu được khi gọi `/ask`:
> `{"event": "ask_completed", "level": "info", "timestamp": "2026-09-28T09:38:09.774972+00:00", "user_id": "sv-observe", "tokens_in": 3, "tokens_out": 41, "cost_usd": 2.505e-05}`.
> Tôi có thể (1) lọc/tìm tất cả event của riêng `sv-observe` trong một khoảng
> thời gian và (2) cộng `cost_usd` hoặc số token để dựng metric/cảnh báo. Chuỗi
> `print("đã trả lời xong")` không có trường dữ liệu ổn định để làm hai việc đó.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1,692.4 MB (Docker hiển thị 1.69 GB) |
| Multi-stage | 247.0 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Tôi đo bằng `docker image inspect`: bản đầu là 1,692,401,745 byte, bản mới là
> 247,021,717 byte, giảm khoảng 1,445 MB (xấp xỉ 85%). Phần lớn chênh lệch đến
> từ base `python:3.11` đầy đủ so với `python:3.11-slim`; multi-stage cũng chỉ
> copy dependency đã cài sang runtime, không kéo theo nội dung và công cụ chỉ cần
> trong builder. `.dockerignore` còn loại Git, test, ảnh và file môi trường khỏi
> build context.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Khi chỉ sửa source, các layer base, `COPY requirements.txt` và `RUN pip install`
> vẫn được lấy từ cache; Docker chỉ chạy lại layer copy source và các layer đứng
> sau nó. Nếu `COPY . .` đứng trước `RUN pip install`, mọi thay đổi source làm
> checksum của layer copy đổi, nên pip phải cài lại toàn bộ dependency dù
> `requirements.txt` không đổi. Trong build thực tế, lần build lại cũng cho thấy
> `WORKDIR` được báo `CACHED`.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Một lỗi thực thi mã từ xa trong endpoint Python có thể cho kẻ tấn công chạy
> lệnh trong container. Nếu process là root và runtime/container còn có lỗi escape
> hoặc được cấp mount/capability nguy hiểm, kẻ đó có thể thoát ranh giới container
> và thao tác host với quyền cao. `USER agent` hạ quyền process trước lúc app chạy;
> vì vậy bước đầu chỉ chiếm được tài khoản ít quyền, giảm mạnh tác động và làm đứt
> giả định “chiếm app đồng nghĩa có root”. Nó không thay thế việc bỏ capability và
> tránh mount Docker socket.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Tối đa là **20 request**: gửi 10 request ở giây 59 của phút trước, bộ đếm reset
> ở giây 00, rồi gửi thêm 10 request ở giây 00 của phút sau. Tất cả nằm trong
> khoảng hai giây nhưng thuộc hai bucket phút khác nhau. Sliding window 60 giây
> vẫn nhìn thấy 10 request cũ nên không cho burst kiểu này.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit khống chế tần suất trong 60 giây, còn cost guard khống chế tổng tiền
> theo user trong tháng. User mới chỉ gọi một request đắt tiền thì rate limit vẫn
> cho qua nhưng cost guard có thể chặn vì đã hết ngân sách tháng. Ngược lại, user
> còn nguyên ngân sách nhưng gửi request thứ 11 trong cùng cửa sổ 60 giây sẽ bị
> rate limit trả 429 trong khi cost guard vẫn còn cho phép về mặt chi phí.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Redis mất kết nối làm endpoint gộp trả lỗi cho cả readiness lẫn liveness trên
> cả ba container. Load balancer trước hết ngừng gửi traffic; sau số lần probe
> thất bại, orchestrator còn coi process là chết và restart đồng loạt ba container.
> Container mới vẫn không qua probe vì Redis chưa hồi phục, nên tiếp tục restart
> và làm thời gian gián đoạn dài hơn. Với hai endpoint tách biệt, `/ready` trả 503
> để rút instance khỏi traffic nhưng `/health` vẫn 200, nên process không bị
> restart vô ích; khi Redis hồi phục, readiness tự xanh lại.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Với Redis dùng chung, mỗi câu hỏi thêm hai message nên `history_length` trước
> khi thêm lượt mới tăng đều `0, 2, 4, 6, ...` bất kể request vào container nào.
> Nếu mỗi process giữ một dict riêng, ba instance có ba lịch sử khác nhau: qua
> load balancer tôi có thể thấy các số lặp hoặc nhảy như `0, 0, 0, 2, 2, 4`, và
> sau khi một container restart thì nhánh lịch sử của nó lại về 0.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Phiên này tôi không có browser/cloud session đã xác thực nên dùng local fallback
> và không ghi một URL cloud giả. Lỗi deploy/build thật tôi gặp là pip lặp
> `ReadTimeoutError ... /simple/watchfiles/`, sau đó báo đang thử nhiều phiên bản
> `uvicorn[standard]` và backtrack rất lâu. Tôi tìm nguyên nhân trong log layer
> `RUN pip install`: extra `standard` kéo `watchfiles` vào dù service production
> không dùng auto-reload. Tôi đổi dependency thành `uvicorn>=0.29`, build lại thành
> công; image multi-stage còn 247 MB và stack Compose lên `healthy`.
