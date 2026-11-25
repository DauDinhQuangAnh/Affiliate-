# Affiliate Video Script & Voice Generator

Quy trình tự động hóa sản xuất kịch bản video và giọng đọc AI (TTS) cho **TikTok Shop** và **Shopee Video** từ hình ảnh và thông tin sản phẩm.

---

## 📁 Cấu trúc dự án

```text
Affiliate/
├── .agent/
│   └── skills/
│       └── affiliate-video-script-voice/
│           ├── SKILL.md                          # Quy trình 5 bước chuẩn
│           └── references/
│               ├── hook-formulas.md              # 12 công thức Hook + Visual
│               ├── banned-words.md               # Từ cấm & từ thay thế an toàn
│               └── tts-rules.md                  # Quy tắc chuẩn hóa văn bản TTS
├── scripts/
│   └── generate_voice.py                         # Tool sinh giọng đọc TTS v2.0 Pro
├── web/
│   ├── app.py                                    # Backend Web Studio (FastAPI)
│   └── static/                                   # Giao diện Web (HTML/CSS/JS)
├── requirements.txt                              # Thư viện phụ thuộc Python
└── .gitignore
```

---

## 🌐 Giao diện Web Studio (Chạy trực tiếp trên trình duyệt)

Khởi động Web UI để nhập kịch bản, quét từ cấm, chọn 1 trong 12 giọng (hoặc Random), chỉnh tốc độ và nghe thử trực tiếp MP3:

```bash
python web/app.py
```
Sau đó mở trình duyệt tại: **http://127.0.0.1:8000**

---

## 🚀 Hướng dẫn cài đặt & Tái sử dụng ở máy khác

### 1. Yêu cầu môi trường
- Python 3.9+ (khuyến nghị Python 3.11).
- Trình soạn thảo hoặc AI Agent IDE (như Google Antigravity).

### 2. Cài đặt thư viện
Tại thư mục gốc dự án, chạy lệnh:
```bash
pip install -r requirements.txt
```

### 3. Tích hợp Skill vào AI Agent
Thư mục Skill nằm tại `.agent/skills/affiliate-video-script-voice/`. Khi mở workspace này trong Antigravity hoặc hệ sinh thái Agent tương thích, skill sẽ tự động được nhận diện và kích hoạt.

---

## 🎬 Quy trình 5 bước sản xuất kịch bản & Voice

1. **Bước 1 (Research):** Phân tích hình ảnh sản phẩm để lấy ít nhất 3 chi tiết trực quan nhìn thấy rõ; kết hợp tìm kiếm thực tế về công dụng, nỗi đau và đánh giá của khách hàng.
2. **Bước 2 (Kịch bản & Shotlist):** Chọn 1 trong 12 công thức Hook từ `references/hook-formulas.md`, viết kịch bản 85–130 từ (30–45s) theo 4 phân đoạn chuẩn: Hook (0-4s) $\rightarrow$ Nỗi đau (4-12s) $\rightarrow$ Trải nghiệm & Chứng minh (12-32s) $\rightarrow$ CTA tự nhiên (32-40s). Mỗi câu dưới 18 chữ.
3. **Bước 3 (Kiểm duyệt):** Đối chiếu với `references/banned-words.md` để loại bỏ các từ vi phạm chính sách sàn thương mại điện tử.
4. **Bước 4 (Xuất 2 file):** Lưu vào thư mục `output/<slug-san-pham>/`:
   - `shotlist.md`: Bảng phân cảnh quay + 2 Hook test A/B.
   - `voice.txt`: Thuần văn bản thoại đã chuẩn hóa theo `references/tts-rules.md`.
5. **Bước 5 (Tạo âm thanh TTS):** Tự động gọi script với cơ chế RANDOM giọng ngẫu nhiên:
   ```bash
   python scripts/generate_voice.py --input "output/<slug>/voice.txt" --output "output/<slug>/voice.mp3" --voice random --speed 1.25
   ```

---

## 🎙️ Kho 12 Giọng đọc Tiếng Việt & Audio Mastering (v2.0 Pro)

Script hỗ trợ kho **12 giọng đọc tiếng Việt đa phong cách** (an toàn tuyệt đối với Symantec/Firewall) kèm bộ hậu kỳ Audio Mastering tự động (Dead-air trim + Vocal Clarity EQ + Normalize `-1 dBFS`).

### Danh sách 12 giọng đọc có sẵn:

| Tên giọng (`--voice`) | Giới tính | Tốc độ mặc định | Phong cách & Sản phẩm phù hợp |
| :--- | :--- | :--- | :--- |
| `tiktok-co-gai` | Nữ | `1.28x` | Phong cách TikTok Cô gái hoạt ngôn: sáng rõ, cuốn hút |
| `tiktok-thanh-nien` | Nam | `1.25x` | Phong cách TikTok Thanh niên tự tin: dứt khoát, rõ ràng |
| `tiktok-chi-google` | Nữ | `1.28x` | Phong cách Chị Google huyền thoại: nhịp nhanh, tròn chữ |
| `tiktok-genz` | Nữ | `1.28x` | Phong cách Gen Z tươi trẻ, nhí nhảnh, năng động |
| `tiktok-mc-chot-don` | Nam | `1.22x` | Phong cách MC trầm ấm, thuyết phục cao |
| `nu-truyen-cam` | Nữ | `1.22x` | Miền Bắc ngọt ngào, truyền cảm (Gia dụng, Mẹ bé, Mỹ phẩm) |
| `nam-dut-khoat` | Nam | `1.25x` | Miền Bắc dứt khoát, tin cậy (Dụng cụ, Đồ gia dụng) |
| `nu-hien-dai` | Nữ | `1.25x` | Hiện đại, phát âm từ mượn mượt mà (Decor, Phụ kiện) |
| `nam-cong-nghe` | Nam | `1.25x` | Trẻ trung, review đồ điện tử (Tai nghe, Cáp sạc, Smart home) |
| `nu-tuoi-tan` | Nữ | `1.26x` | Tươi tắn, dễ thương (Mỹ phẩm, Phụ kiện xinh) |
| `nam-soi-noi` | Nam | `1.26x` | Hào hứng, lôi cuốn (Đồ chơi, Phụ kiện xe, Thể thao) |
| `nam-tin-cay` | Nam | `1.20x` | Giọng trầm chững chạc, uy tín (Thiết bị sức khỏe, Điện máy) |

### Cách sử dụng dòng lệnh:

```bash
# 1. Triển khai thực tế: Chọn giọng NGẪU NHIÊN trong 12 giọng (Mặc định)
python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice random

# 2. Chọn ngẫu nhiên trong nhóm 5 giọng phong cách TikTok Review
python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice tiktok

# 3. Chọn ngẫu nhiên 1 giọng Nữ / Nam
python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice nu
python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice nam

# 4. Xem danh sách toàn bộ giọng:
python scripts/generate_voice.py --list-voices
```
