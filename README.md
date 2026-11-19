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
│   └── generate_voice.py                         # Tool sinh giọng đọc TTS qua edge-tts
├── requirements.txt                              # Thư viện phụ thuộc Python
└── .gitignore
```

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

## 🎙️ Kho 10 Giọng đọc Tiếng Việt & Sử dụng Script riêng lẻ

Script hỗ trợ kho **10 giọng đọc tiếng Việt đa dạng phong cách** phù hợp từng dòng sản phẩm khác nhau.

### Danh sách 10 giọng đọc có sẵn:

| Tên giọng (`--voice`) | Giới tính | Phong cách & Sản phẩm phù hợp |
| :--- | :--- | :--- |
| `nu-truyen-cam` | Nữ | Miền Bắc ngọt ngào, truyền cảm (Gia dụng, Mẹ bé, Mỹ phẩm) |
| `nam-dut-khoat` | Nam | Miền Bắc dứt khoát, tin cậy (Gia dụng, Dụng cụ tiện ích) |
| `nu-hien-dai` | Nữ | Hiện đại, phát âm mượt mà (Phụ kiện, Decor, Công nghệ nhẹ) |
| `nam-cong-nghe` | Nam | Trẻ trung, review đồ điện tử (Tai nghe, Cáp sạc, Smart device) |
| `nu-tuoi-tan` | Nữ | Năng động, vui tươi (Thời trang, Đồ ăn vặt, Phụ kiện xinh) |
| `nam-soi-noi` | Nam | Hào hứng, lôi cuốn (Đồ chơi, Phụ kiện xe, Thể thao) |
| `nu-ro-chu` | Nữ | Tròn vành rõ chữ, tự nhiên, ổn định tuyệt đối (Review tổng hợp) |
| `nam-tram-am` | Nam | Trầm ấm áp, thuyết phục cao (Đồ gia đình, Sản phẩm giá trị) |
| `nu-nhi-nhanh` | Nữ | Trẻ trung, bắt tai, hợp tệp học sinh sinh viên Gen Z |
| `nam-tin-cay` | Nam | Chững chạc, uy tín, tạo độ tin tưởng chốt đơn cao |

### Cách sử dụng dòng lệnh:

```bash
# 1. Triển khai thực tế: Chọn giọng NGẪU NHIÊN trong 10 giọng (Mặc định)
python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice random

# 2. Chọn ngẫu nhiên 1 giọng Nữ (Mỹ phẩm, Gia dụng, Mẹ bé)
python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice nu

# 3. Chọn ngẫu nhiên 1 giọng Nam (Công nghệ, Dụng cụ, Đồ chơi)
python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice nam

# 4. Chỉ định đích danh một giọng cố định:
python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice nu-hien-dai --speed 1.25

# 5. Xem danh sách toàn bộ giọng:
python scripts/generate_voice.py --list-voices
```
