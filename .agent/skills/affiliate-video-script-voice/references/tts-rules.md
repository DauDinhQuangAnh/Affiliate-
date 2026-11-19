# Quy tắc chuẩn hóa văn bản cho Tool Giọng đọc (TTS)

Áp dụng toàn bộ quy tắc dưới đây khi tạo file `voice.txt`. File này được nạp trực tiếp vào model TTS (như edge-tts) nên phải đảm bảo giọng đọc tự nhiên, liền mạch, đúng nhịp ngắt nghỉ và không bị vấp hoặc đọc lỗi ký tự.

---

## 1. Cấu trúc thuần văn bản (Plain Text Only)
- **Tuyệt đối không chứa Markdown:** Không dùng dấu sao (`*`), thăng (`#`), gạch chân (`_`), gạch đầu dòng (`-`), số thứ tự (`1.`, `2.`).
- **Không chứa chú thích phân cảnh:** Không ghi `[Cảnh 1]`, `(Visual: ...)`, `Hook:`, `CTA:`.
- **Khoảng cách dòng:** Mỗi phân đoạn ý cách nhau đúng 1 dòng trống để TTS tự động tạo khoảng nghỉ thở nhẹ nhàng (khoảng 0.3 - 0.5s) trước khi sang ý tiếp theo.

---

## 2. Nhịp điệu, Độ dài câu & Dấu ngắt nghỉ (Quyết định độ tự nhiên)
- **Độ dài mỗi câu:** Giữ mỗi câu ngắn, dưới **15 – 18 chữ**. Tuyệt đối tránh câu ghép 3 - 4 mệnh đề dài lê thê khiến AI đọc bị đuối hơi hoặc giật cục.
- **Tách câu dài:** Nếu câu có nhiều ý, tách hẳn thành 2 câu đơn hoặc ngắt bằng dấu phẩy.
- **Dùng dấu phẩy (`,`) để ngắt hơi có chủ đích:**
  - Đặt dấu phẩy sau các cụm từ cảm thán hoặc từ nối đầu câu (Ví dụ: *"Thật sự luôn, nhìn bên ngoài không nghĩ nó chắc như vậy đâu."*).
- **Hạn chế dấu chấm than (`!`):** Nhiều engine TTS đọc dấu `!` với tông giọng bị chói, gắt hoặc mất tự nhiên. Ưu tiên dùng dấu chấm (`.`) và dấu hỏi (`?`).
- **Tuyệt đối không dùng dấu ba chấm (`...`) và dấu gạch ngang (`-`, `–`):**
  - Dấu `...` làm TTS dừng quá lâu, tạo khoảng lặng chết (dead air). Thay bằng dấu phẩy hoặc dấu chấm.
  - Dấu gạch ngang dễ bị TTS đọc thành chữ "gạch ngang" hoặc "trừ". Hãy thay bằng dấu phẩy.

---

## 3. Chuyển đổi Số, Đơn vị & Ký hiệu sang Chữ nói tự nhiên

| Ký hiệu / Định dạng | Chuyển đổi sang chữ nói tự nhiên |
| :--- | :--- |
| `500ml` | `500 mi li lít` (hoặc `năm trăm mi li lít`) |
| `1.5L` / `1,5L` | `một phẩy năm lít` |
| `20W` / `65W` | `20 oát` / `65 oát` |
| `10000mAh` | `mười nghìn mi li am pe giờ` |
| `5V/2A` | `năm vôn hai am pe` |
| `3in1` / `4in1` | `ba trong một` / `bốn trong một` |
| `24/7` | `hai tư trên bảy` |
| `50%` | `năm mươi phần trăm` |
| `199k` / `199.000đ` | `chưa tới hai trăm nghìn` hoặc `một trăm chín mươi chín nghìn` |
| `89k` | `tám mươi chín nghìn` |
| `&` | `và` |
| `+` | `cộng thêm` hoặc `với` |
| `/` | `trên` hoặc `hoặc` |
| `%` | `phần trăm` |
| `#`, `@`, `~`, `=`, `"` | Xóa bỏ hoặc thay thế bằng từ ngữ ngữ cảnh |

---

## 4. Phiên âm mềm từ tiếng Anh & Thuật ngữ công nghệ
Engine TTS tiếng Việt khi gặp từ tiếng Anh thường phát âm ngọng, nuốt âm hoặc chuyển sang giọng đọc tiếng Anh làm đứt mạch cảm xúc. Do đó cần phiên âm mềm sang chữ nói tiếng Việt:

| Từ gốc | Phiên âm mềm cho TTS đọc chuẩn |
| :--- | :--- |
| `Type-C` | `tai xi` |
| `Bluetooth` | `bờ lu tút` |
| `Freeship` | `phờ ri síp` |
| `Review` | `rì viu` |
| `Combo` | `com bô` |
| `Voucher` | `vâu chờ` |
| `Balo` | `ba lô` |
| `Unbox` | `mở hộp` |
| `Design` | `thiết kế` (ưu tiên dịch hẳn sang tiếng Việt) |
| `Fullbox` | `nguyên hộp` |
| `Smart` | `thông minh` |
| `Bass` (âm thanh) | `âm bát` |

- **Tên thương hiệu quốc tế hoặc khó đọc:**
  Sau lần gọi tên đầu tiên (ví dụ hãng nổi tiếng đã có cách đọc quen thuộc), các câu sau nên dùng đại từ thay thế tự nhiên như: *"em này"*, *"chiếc quạt này"*, *"bộ dụng cụ này"*, *"mẫu tai nghe này"*.

---

## 5. Tiêu chuẩn nghiệm thu file `voice.txt`
Trước khi lưu file và chuyển sang bước chạy TTS:
1. Đọc lướt và nhẩm to lời thoại: kiểm tra xem có câu nào bị gượng gạo, đậm mùi văn viết học thuật hay không.
2. Kiểm tra lại toàn bộ số, đơn vị, giá tiền đã được viết dưới dạng chữ nói chưa.
3. Đảm bảo file không sót bất kỳ ký tự đặc biệt hay thẻ tag nào.
