# 🔥 HƯỚNG DẪN TEST VÀ VẬN HÀNH HỆ THỐNG FIREEYES AI

> **Dự án:** Hệ Thống Giám Sát và Cảnh Báo Sớm Cháy & Khói Bằng AI (FireEyes AI)  
> **Kiến trúc:** Chuẩn **MVC (Model - View - Controller)** theo đúng Class Diagram thiết kế  
> **Công nghệ:** YOLO11n AI · SQLite v2 (11 bảng) · FastAPI REST Backend · Single-Page Web Frontend (Tailwind + Lucide + Canvas)

---

## 📂 1. Cấu Trúc Thư Mục Sau Khi Tích Hợp

Toàn bộ mã nguồn giao diện Web Frontend đã được tích hợp trực tiếp vào thư mục mã nguồn chính của dự án:

```
fire_detection_ai-main/
│
├── backend/                       # Backend Python & CSDL SQLite
│   ├── api.py                     # FastAPI REST API (tích hợp CORS, StaticFiles, /api/demo)
│   ├── main.py                    # CLI quản trị CSDL (init, demo, stats, incidents)
│   └── CSDL/
│       ├── controllers/
│       │   ├── __init__.py
│       │   └── app_controller.py  # ⭐ AppController (theo đúng Class Diagram MVC)
│       └── models/
│           ├── database.py        # ⭐ FireEyesDB (SQLite v2 với 11 bảng nghiệp vụ)
│           └── schema.sql         # File DDL 11 bảng chuẩn
│
├── frontend/                      # ⭐ Giao diện Web Frontend hoàn chỉnh
│   ├── index.html                 # Giao diện SPA (Dashboard, Monitor, Incidents, History, Devices)
│   └── app.js                     # Xử lý Controller, API client, Cửa sổ trượt 3/5, Audio siren
│
├── configs/
│   └── detection_thresholds.json  # Ngưỡng calibrated tối ưu F1 (Fire=0.2633, Smoke=0.1792)
├── detection/
│   └── fire_logic.py              # Thuật toán cửa sổ trượt W=5, K=3 (FireConfirmation)
│
├── Cai_Dat_Moi_Truong.bat         # ⚡ Script 1-click tạo venv & cài thư viện Python
├── Chay_FastAPI_Backend.bat       # ⚡ Script 1-click khởi chạy FastAPI Backend (:8000)
├── Mo_Giao_Dien_Web.bat           # ⚡ Script 1-click mở Giao Diện Web (:3000)
├── server.js                      # Máy chủ Node.js phục vụ web và proxy API
├── requirements.txt               # Danh sách thư viện Python cần thiết
└── HUONG_DAN_TEST.md              # Tài liệu này
```

---

## 🚀 2. Hai Chế Độ Chạy & Kiểm Thử (Dual-Mode)

Hệ thống được thiết kế thông minh hỗ trợ **2 chế độ hoạt động**:

### 🟢 CHẾ ĐỘ 1: Chạy Ngay Bằng Node.js (Không Cần Cài Python)
> **Phù hợp nhất:** Khi bạn muốn xem và kiểm thử toàn bộ giao diện ngay lập tức mà máy chưa cài Python. Máy tính của bạn đã có sẵn Node.js (v24.11.0).

* **Cách chạy:**
  1. Mở thư mục dự án `fire_detection_ai-main`.
  2. **Click đúp vào file `Mo_Giao_Dien_Web.bat`**  
     *(Hoặc mở terminal tại thư mục này và gõ: `node server.js`)*
  3. Trình duyệt sẽ tự động mở địa chỉ: **`http://localhost:3000`**
* **Cơ chế hoạt động:**
  - Giao diện tự động phát hiện backend FastAPI chưa bật và chuyển sang chế độ **Client Mock DB** (lưu dữ liệu tạm thời vào trình duyệt qua LocalStorage).
  - Mọi thao tác: bấm **Tạo Demo**, xem thống kê, mô phỏng Lửa/Khói, kích hoạt còi, xác nhận cảnh báo (Acknowledge), giải quyết sự kiện (Resolve), thêm Camera... đều hoạt động 100% mượt mà!

---

### 🔵 CHẾ ĐỘ 2: Chạy Tích Hợp Đầy Đủ FastAPI Backend + SQLite Thật
> **Phù hợp nhất:** Khi bạn muốn kết nối thực tế vào cơ sở dữ liệu SQLite `backend/data/fireeyes.db` và chạy cùng mô hình AI.

#### Bước 2.1: Cài đặt Python 3.12 (nếu máy chưa có)
1. Tải bộ cài đặt chính thức tại: [https://www.python.org/downloads/](https://www.python.org/downloads/) (chọn bản Python 3.12).
2. **QUAN TRỌNG:** Khi chạy file cài đặt, hãy tích chọn ô **`Add python.exe to PATH`** ở màn hình đầu tiên trước khi bấm Install Now.

#### Bước 2.2: Cài đặt môi trường tự động
* **Click đúp vào file `Cai_Dat_Moi_Truong.bat`**  
  Script sẽ tự động:
  - Tạo môi trường ảo `.venv`
  - Cài đặt đầy đủ `fastapi[standard]`, `uvicorn`, `torch`, `ultralytics`, `opencv-python`, `aiofiles`...
  - Khởi tạo file cơ sở dữ liệu SQLite `backend/data/fireeyes.db` với 11 bảng chuẩn.

#### Bước 2.3: Khởi chạy hệ thống
* **Bước A (Chạy Backend):** Click đúp file `Chay_FastAPI_Backend.bat`  
  Backend sẽ chạy tại: `http://127.0.0.1:8000`  
  *(Tài liệu Swagger API: `http://127.0.0.1:8000/docs`)*
* **Bước B (Mở Giao Diện Web):** Click đúp file `Mo_Giao_Dien_Web.bat`  
  Trình duyệt mở `http://localhost:3000`. Góc dưới bên trái thanh menu sẽ hiện chấm tròn màu xanh lá: **`● FastAPI Online`**!  
  *(Lúc này mọi dữ liệu sẽ được đọc/ghi trực tiếp vào file SQLite thật).*

---

## 🧪 3. Các Kịch Bản Kiểm Thử Chi Tiết (Test Scenarios)

Dưới đây là các bước kiểm thử từng tính năng nghiệp vụ theo đúng thiết kế:

### Kịch Bản 1: Kiểm thử Nút "Tạo demo" (Theo Class Diagram MVC)
1. Trên thanh tiêu đề trên cùng (Top Bar), nhấn nút màu cam **"Tạo Demo"** (hoặc bấm nút "Làm mới").
2. **Kết quả quan sát được:**
   - Xuất hiện thông báo Toast màu xanh lá: *"Tạo demo thành công!"*.
   - Các thẻ thống kê ở Dashboard tự động cập nhật số lượng bản ghi:
     + **Frames**: Tăng thêm 1 khung hình.
     + **Detections**: Tăng thêm bản ghi nhận diện.
     + **Incidents**: Tăng thêm 1 sự kiện cảnh báo.
     + **Thông báo (Notifications)**: Tăng thêm 1 lượt mô phỏng gửi tin.
   - Bảng **"Sự kiện cảnh báo gần nhất"** xuất hiện ngay sự kiện mới với nhãn đỏ **`OPEN`**.

---

### Kịch Bản 2: Kiểm thử Thuật Toán Cửa Sổ Trượt (Sliding Window 3/5)
Thuật toán đối sánh đa khung hình từ file `detection/fire_logic.py` (Cửa sổ $W=5$ frames, ngưỡng xác nhận $K \ge 3$):
1. Chuyển sang menu **"Giám sát Camera AI"** ở cột bên trái.
2. Tại khung điều khiển bên dưới màn hình camera:
   - Bấm nút **"🔥 Mô phỏng Lửa"**:
     + Màn hình camera xuất hiện hộp Bounding Box màu đỏ `FIRE` kèm độ tin cậy ~90%.
     + Cột bên phải: Cửa sổ **Fire Window** hiển thị 5 ô khung hình ($F_1 \to F_5$). Các ô lần lượt chuyển sang màu đỏ `HIT`.
     + Khi đạt đủ 3 khung hình có lửa: Trạng thái đổi thành **`✅ ĐÃ XÁC NHẬN`**.
     + Còi báo động (Siren) phát âm thanh qua loa máy tính.
     + Khung viền camera nhấp nháy đỏ kèm dòng chữ: **`🔥 CẢNH BÁO CHÁY XÁC NHẬN!`**.
     + Hệ thống tự động gửi yêu cầu mở một Incident mới vào cơ sở dữ liệu.
   - Bấm nút **"💨 Mô phỏng Khói"**:
     + Xuất hiện Bounding Box màu xanh `SMOKE`.
     + Cửa sổ **Smoke Window** kích hoạt quy tắc 3/5 và xác nhận khói.
   - Bấm nút **"Normal (Clear)"**: Xóa mô phỏng, camera trở về trạng thái an toàn bình thường.
   - Bấm nút biểu tượng **Loa** bên phải để bật/tắt tiếng còi báo động.

---

### Kịch Bản 3: Kiểm thử Quy Trình Xử Lý Sự Kiện Cảnh Báo (Incident Lifecycle)
1. Chuyển sang tab **"Sự kiện cảnh báo"** trên thanh menu bên trái.
2. Tìm một sự kiện có trạng thái **`open`** trong bảng:
   - **Bước 3.1: Xác nhận xem (Acknowledge):**
     + Nhấn nút **"Xem"**.
     + Một hộp thoại hiện lên yêu cầu cán bộ xác nhận. Giữ nguyên hoặc nhập tên (VD: *"Nguyễn Văn A - Trực ban"*).
     + Nhấn **"Xác nhận đã xem"**.
     + Cột "Xác nhận xem" trong bảng sẽ cập nhật tên người xác nhận kèm mốc thời gian chính xác.
   - **Bước 3.2: Đóng sự kiện (Resolve):**
     + Nhấn nút **"Đóng"** (màu xanh lá).
     + Hộp thoại đóng sự kiện hiện lên. Chọn kết quả:
       * *Đã xử lý an toàn (resolved)*: Nếu hiện trường đã được chữa cháy an toàn.
       * *Báo động giả (false_alarm)*: Nếu do chập hơi nước hoặc ánh sáng phản chiếu.
     + Nhập nội dung ghi chú xử lý hiện trường (bắt buộc).
     + Nhấn **"Lưu & Đóng sự kiện"**.
     + Trạng thái sự kiện trong bảng lập tức chuyển thành `resolved` hoặc `false_alarm`.
     + Banner cảnh báo màu đỏ trên đầu trang sẽ tự động biến mất khi không còn sự kiện nào ở trạng thái `open`.

---

### Kịch Bản 4: Kiểm thử Nguồn Camera (Webcam Thực & Upload Ảnh)
1. Tại tab **"Giám sát Camera AI"**:
   - Ở mục **"Nguồn:"** góc trên bên phải màn hình camera:
     + Chọn **"Webcam"**: Trình duyệt sẽ hỏi quyền truy cập Camera máy tính của bạn. Bấm Cho phép (Allow) để hiển thị video trực tiếp từ webcam lên màn hình AI.
     + Chọn **"Upload ảnh"**: Chọn một file ảnh từ máy tính để hiển thị lên khung hình giám sát.
     + Chọn **"Mô phỏng"**: Trở lại chế độ đồ họa mô phỏng phòng thí nghiệm.
   - Nhấn nút **"Gửi Heartbeat"**: Kiểm tra tính năng duy trì kết nối camera (API `/api/cameras/{id}/heartbeat`). Đèn trạng thái camera sẽ giữ màu xanh **`Active`**.
   - Nhấn nút **"Tắt camera" / "Bật camera"**: Thử nghiệm vô hiệu hóa camera.

---

### Kịch Bản 5: Kiểm thử Quản Lý Thiết Bị & CSDL (Locations & Cameras)
1. Chuyển sang tab **"CSDL & Thiết bị"**:
   - Xem danh sách đầy đủ 4 nhóm bảng chính:
     + **Địa điểm (locations)**
     + **Camera (cameras)**
     + **Bộ dữ liệu huấn luyện (dataset_versions)**: Gồm bộ dữ liệu mẫu D-Fire (21.527 ảnh).
     + **Mô hình AI (model_versions)**: Gồm DEMO-NO-AI và YOLO11n.
   - Thử bấm nút **"+ Địa điểm"**: Nhập tên (VD: *"Kho Hàng Số 3"*), địa chỉ -> Bấm Lưu.
   - Thử bấm nút **"+ Camera"**: Chọn địa điểm vừa tạo, nhập tên camera mới -> Bấm Đăng ký.
   - Xem số lượng bản ghi cập nhật ngay lập tức.

---

### Kịch Bản 6: Kiểm thử Lịch Sử Nhận Diện (Detection History)
1. Chuyển sang tab **"Lịch sử nhận diện"**:
   - Bảng hiển thị chi tiết từng khung hình (`frame_id`), thời điểm ghi nhận, tọa độ bounding box chuẩn hóa `[xc, yc, w, h]`, độ tin cậy và mô hình AI phát hiện.
   - Có thể chọn lọc theo từng camera cụ thể để kiểm tra dữ liệu.

---

## 🛠️ 4. Danh Sách Endpoint REST API Đã Tích Hợp

| Phương Thức | Đường Dẫn Endpoint | Chức Năng | Tương Ứng Trong Giao Diện |
|---|---|---|---|
| `GET` | `/health` | Kiểm tra tình trạng backend | Đèn báo `FastAPI Online` / `Offline` |
| `GET` | `/api/stats` | Thống kê số bản ghi của 11 bảng | 11 Thẻ thống kê tại Dashboard |
| `POST` | `/api/demo` | Tạo dữ liệu giả lập mẫu | Nút **"Tạo Demo"** trên thanh tiêu đề |
| `GET` | `/api/alerts` | Lấy danh sách sự kiện cảnh báo | Bảng danh sách tại tab "Sự kiện cảnh báo" |
| `PATCH` | `/api/alerts/{id}/acknowledge` | Cán bộ xác nhận đã xem cảnh báo | Nút **"Xem"** trong bảng sự kiện |
| `PATCH` | `/api/alerts/{id}/resolve` | Đóng và kết luận sự kiện | Nút **"Đóng"** trong bảng sự kiện |
| `GET` | `/api/alerts/{id}/snapshot` | Tải ảnh chụp bằng chứng thời điểm cháy | Hộp thoại xem ảnh bằng chứng |
| `GET` | `/api/cameras` | Lấy danh sách camera giám sát | Dropdown chọn camera tại tab Monitor |
| `GET` | `/api/cameras/{id}/status` | Xem trạng thái hoạt động của camera | Huy hiệu trạng thái Active/Stopped |
| `PATCH` | `/api/cameras/{id}/status` | Bật hoặc tắt kích hoạt camera | Nút **"Bật/Tắt camera"** |
| `POST` | `/api/cameras/{id}/heartbeat`| Cập nhật mốc thời gian sống camera | Nút **"Gửi Heartbeat"** |
| `GET` | `/api/locations` | Lấy danh sách các địa điểm | Danh sách tại tab "CSDL & Thiết bị" |
| `POST` | `/api/locations` | Thêm địa điểm mới vào CSDL | Nút **"+ Địa điểm"** |
| `POST` | `/api/cameras` | Đăng ký camera mới vào địa điểm | Nút **"+ Camera"** |
| `GET` | `/api/detections/history` | Lấy lịch sử tất cả lượt nhận diện | Bảng tại tab "Lịch sử nhận diện" |
| `POST` | `/api/detections` | Nhận kết quả AI từ camera đẩy về | Tự động kích hoạt khi có cháy/khói xác nhận |

---

## ✅ 5. Tổng Kết

Hệ thống đã được đóng gói và tích hợp hoàn chỉnh:
1. Giao diện trực quan, thẩm mỹ cao theo chuẩn công nghiệp (Tailwind CSS Dark Mode, biểu tượng Lucide vector, đồ họa Canvas sắc nét).
2. Chuẩn mực cấu trúc **MVC**: `AppController` và `MainView` tương ứng chặt chẽ với Class Diagram.
3. Chạy được ngay lập tức chỉ với 1 click chuột mà không bắt buộc cấu hình phức tạp.
4. Tương thích 100% với backend FastAPI và cơ sở dữ liệu SQLite v2 của dự án.
