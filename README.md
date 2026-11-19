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
5. **Bước 5 (Tạo âm thanh TTS):** Tự động gọi script:
   ```bash
   python scripts/generate_voice.py --input "output/<slug>/voice.txt" --output "output/<slug>/voice.mp3" --speed 1.25
   ```

---

## 🎙️ Sử dụng Script Giọng đọc riêng lẻ

Bạn cũng có thể chạy trực tiếp script TTS cho bất kỳ file văn bản nào:
```bash
python scripts/generate_voice.py \
  --input "duong/dan/file.txt" \
  --output "duong/dan/file.mp3" \
  --speed 1.25 \
  --engine auto
```
- `--speed`: Tốc độ đọc (mặc định `1.25x` nhanh hơn 25%, tự động cắt tỉa khoảng lặng thừa, giữ nguyên cao độ tự nhiên). Có thể chỉnh `1.15`, `1.2`, `1.3`...
- `--engine`: `auto` (thử Edge TTS, lỗi tự chuyển gTTS), `edge` hoặc `gtts`.
- Giọng nữ mặc định: `vi-VN-HoaiMyNeural`
- Giọng nam: `vi-VN-NamMinhNeural`
