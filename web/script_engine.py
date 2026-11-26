#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Engine xử lý Kịch bản Affiliate (Smart Script Builder + Banned-Word Auto-Fix + TTS Normalizer)
Dựa trên bộ quy tắc trong .agent/skills/affiliate-video-script-voice/references/.
"""

import re
import unicodedata
import time
from typing import Dict, List, Optional, Tuple


# 20 công thức Hook thịnh hành từ references/hook-formulas.md
HOOK_TEMPLATES = [
    {
        "id": "pain-1",
        "group": "Nỗi đau & Cảnh báo",
        "label": "Ai hay bị [nỗi đau] thì nhìn kỹ cái này nha",
        "best_for": "gia dụng, tiện ích, ốp lưng, quạt, phụ kiện giải quyết sự cố hằng ngày",
        "template": "Ai hay bị {pain} thì nhìn kỹ cái này nha.",
        "visual": "Quay cận cảnh tình huống bất tiện thường ngày, sau đó chuyển ngay góc máy sang {product}.",
    },
    {
        "id": "pain-2",
        "group": "Nỗi đau & Cảnh báo",
        "label": "Trước giờ cứ tưởng loại cũ là bình thường...",
        "best_for": "đồ nâng cấp thói quen cũ, gia dụng thông minh, phụ kiện điện thoại",
        "template": "Trước giờ mình cứ tưởng dùng loại cũ là bình thường, cho tới khi thử {product} này.",
        "visual": "Đặt đồ cũ và {product} cạnh nhau để thấy ngay sự khác biệt.",
    },
    {
        "id": "pain-3",
        "group": "Nỗi đau & Cảnh báo",
        "label": "Bỏ ngay kiểu dùng đồ cũ cồng kềnh đi mọi người ơi",
        "best_for": "sản phẩm nhỏ gọn thay thế đồ to cồng kềnh, cáp sạc, giá đỡ, hộp đựng",
        "template": "Bỏ ngay kiểu dùng đồ cũ cồng kềnh đi mọi người ơi, giờ người ta chuyển qua {product} này hết rồi.",
        "visual": "Tay gạt đồ cũ ra ngoài khung hình, đặt {product} vào chính giữa.",
    },
    {
        "id": "pain-warn",
        "group": "Nỗi đau & Cảnh báo",
        "label": "Khoan mua nếu bạn chưa biết chi tiết quan trọng này",
        "best_for": "đồ điện tử, mỹ phẩm, phụ kiện nhiều phân loại dễ mua nhầm",
        "template": "Khoan mua {product} nếu bạn vẫn chưa biết chi tiết quan trọng này.",
        "visual": "Giơ tay ra hiệu dừng lại, zoom thẳng vào chi tiết ăn tiền nhất của {product}.",
    },
    {
        "id": "contrarian-1",
        "group": "Phản biện / Phá vỡ định kiến",
        "label": "Nhiều người nghĩ cách cũ là ổn, thử cái này mới khác hẳn",
        "best_for": "mỹ phẩm, skincare, vệ sinh nhà cửa, công nghệ mới",
        "template": "Nhiều người cứ nghĩ làm theo cách cũ là ổn, nhưng dùng thử {product} mới thấy khác hẳn.",
        "visual": "Lắc đầu nhẹ trước cách làm cũ, sau đó thao tác trực tiếp bằng {product}.",
    },
    {
        "id": "contrarian-2",
        "group": "Phản biện / Phá vỡ định kiến",
        "label": "Không cần chi tiền triệu, mẫu này giá mềm mà trải nghiệm rất ổn",
        "best_for": "tai nghe, loa, đồng hồ, túi xách, đồ decor giá hợp lý",
        "template": "Không cần chi tiền triệu cho hàng đắt đỏ, em {product} này giá mềm hơn nhiều mà trải nghiệm rất ổn.",
        "visual": "Đặt {product} gọn đẹp lên bàn, xoay nhẹ khoe độ hoàn thiện.",
    },
    {
        "id": "contrarian-3",
        "group": "Phản biện / Phá vỡ định kiến",
        "label": "Mọi người hay hiểu nhầm về tính năng, sự thật trên tay là...",
        "best_for": "sản phẩm đang hot có nhiều ý kiến trái chiều, thực phẩm, mỹ phẩm",
        "template": "Mọi người hay hiểu nhầm về {product}, sự thật khi cầm trên tay là như này đây.",
        "visual": "Cầm sát {product} trước ống kính, test trực tiếp tính năng.",
    },
    {
        "id": "curious-4",
        "group": "Gây tò mò / Lật ngược kỳ vọng",
        "label": "Nhìn bên ngoài tưởng bình thường, bấm thử mới thấy tiện",
        "best_for": "đồ công nghệ, quạt mini, đèn ngủ, đồ gia dụng có nút/cơ chế ẩn",
        "template": "Nhìn bên ngoài tưởng bình thường, nhưng lúc thử {product} mới thấy nó tiện thật sự.",
        "visual": "Quay góc bình thường 1 giây đầu, sau đó kích hoạt tính năng nổi bật nhất của {product}.",
    },
    {
        "id": "curious-5",
        "group": "Gây tò mò / Lật ngược kỳ vọng",
        "label": "Mua vì gọn đẹp, bất ngờ nhất lại là tính năng phụ",
        "best_for": "sản phẩm đa năng 2 trong 1, 3 trong 1, phụ kiện có chi tiết ẩn",
        "template": "Mình mua {product} chỉ vì nhìn gọn đẹp, ai ngờ cái làm mình bất ngờ nhất lại là {detail_1}.",
        "visual": "Cầm {product} xoay nhẹ trên tay, zoom cận cảnh vào chi tiết bất ngờ.",
    },
    {
        "id": "curious-6",
        "group": "Gây tò mò / Lật ngược kỳ vọng",
        "label": "Món nhỏ xíu mà giải quyết đúng chỗ khó chịu bấy lâu",
        "best_for": "phụ kiện nhỏ gọn bỏ túi, móc khóa, kẹp dây, dụng cụ mini",
        "template": "Không hiểu sao món nhỏ gọn như {product} mà giải quyết được đúng chỗ mình khó chịu bấy lâu nay.",
        "visual": "Cầm gọn {product} trong lòng bàn tay để thấy kích thước thực tế.",
    },
    {
        "id": "curious-guess",
        "group": "Gây tò mò / Lật ngược kỳ vọng",
        "label": "Đố mọi người món nhìn sang xịn mịn này giá bao nhiêu?",
        "best_for": "thời trang, túi xách, đồng hồ, đèn decor, ốp lưng sang trọng",
        "template": "Đố mọi người {product} nhìn sang xịn mịn như này giá bao nhiêu, mềm hơn bạn nghĩ nhiều luôn.",
        "visual": "Quay góc ánh sáng đẹp làm nổi bật chất liệu của {product}.",
    },
    {
        "id": "proof-1",
        "group": "Chứng minh kết quả / Thử thách",
        "label": "Đây là kết quả sau mấy hôm dùng thử, nhìn phát thấy khác liền",
        "best_for": "mỹ phẩm, chăm sóc tóc, tẩy rửa, vệ sinh giày/nhà cửa",
        "template": "Đây là kết quả sau mấy hôm dùng thử {product}, nhìn phát thấy khác liền.",
        "visual": "Đưa kết quả thực tế (before/after) lên ngay giây đầu tiên.",
    },
    {
        "id": "proof-test",
        "group": "Chứng minh kết quả / Thử thách",
        "label": "Thử test độ bền & khả năng thực tế xem có ổn như lời đồn",
        "best_for": "ốp lưng chống sốc, kính cường lực, đồ chống nước, bình giữ nhiệt",
        "template": "Thử test độ bền và khả năng thực tế của {product} xem có ổn như lời đồn không nha.",
        "visual": "Thực hiện bài test trực quan ngay giây đầu (đổ nước, gõ nhẹ, test lực).",
    },
    {
        "id": "review-7",
        "group": "Chứng minh kết quả / Thử thách",
        "label": "Dùng mấy hôm rồi, nay nói thật điểm thích lẫn chưa ưng",
        "best_for": "review chân thực mỹ phẩm, đồ cá nhân, thiết bị dùng hằng ngày",
        "template": "Dùng thử {product} được mấy hôm rồi, nay chia sẻ thật cả điểm thích lẫn trải nghiệm cho mọi người dễ chọn.",
        "visual": "Quay cận bề mặt {product} đang sử dụng thực tế trong đời sống.",
    },
    {
        "id": "review-8",
        "group": "Chứng minh kết quả / Thử thách",
        "label": "Đang phân vân thì xem kỹ chất liệu thực tế trước khi đặt",
        "best_for": "quần áo, giày dép, balo, ốp lưng, đồ da/vải",
        "template": "Bác nào đang phân vân {product} thì xem kỹ chất liệu thực tế này trước khi đặt nha.",
        "visual": "Zoom sát vào đường may, bề mặt chất liệu của {product}.",
    },
    {
        "id": "value-9",
        "group": "Giá trị / Độ hời & FOMO",
        "label": "Chưa tới tiền trà sữa mà cầm trên tay chắc chắn ngoài mong đợi",
        "best_for": "sản phẩm giá mềm dưới 150k, dễ chốt đơn bốc đồng",
        "template": "Mức giá chỉ {price_spoken} mà cầm {product} trên tay chắc chắn ngoài mong đợi luôn.",
        "visual": "Gõ nhẹ hoặc bóp thử {product} để thấy độ cứng cáp, chắc chắn.",
    },
    {
        "id": "value-10",
        "group": "Giá trị / Độ hời & FOMO",
        "label": "Tìm mãi mới ra món vừa gọn vừa tiện mà giá dễ tiếp cận",
        "best_for": "đồ văn phòng, bàn làm việc, góc bếp, phụ kiện đa năng",
        "template": "Tìm mãi mới ra một em {product} vừa gọn, vừa tiện mà mức giá lại cực kỳ dễ tiếp cận.",
        "visual": "Đặt {product} vào đúng không gian sử dụng thực tế.",
    },
    {
        "id": "trend-fomo",
        "group": "Giá trị / Độ hời & FOMO",
        "label": "Món đang được săn lùng nhiều tuần qua nay mới kịp về tay",
        "best_for": "sản phẩm đang viral, đồ ăn vặt hot trend, phụ kiện mới ra",
        "template": "{product} đang được săn lùng rất nhiều tuần qua, nay mình mới kịp cầm trên tay để chia sẻ với mọi người.",
        "visual": "Khui hộp hoặc bóc seal nhanh gọn ngay 2 giây đầu.",
    },
    {
        "id": "niche-11",
        "group": "Gọi đúng tệp khách hàng",
        "label": "Dân văn phòng / sinh viên / hay đi xa phải thủ sẵn trong balo",
        "best_for": "sạc dự phòng, quạt mini, bình nước, túi đựng phụ kiện, đồ du lịch",
        "template": "Dân văn phòng hay mấy bạn hay đi làm xa nhất định nên thủ sẵn {product} này nha.",
        "visual": "Lấy {product} từ trong túi xách hoặc balo ra sử dụng ngay.",
    },
    {
        "id": "niche-12",
        "group": "Gọi đúng tệp khách hàng",
        "label": "Nhà có không gian hẹp / bé nhỏ / thú cưng xem hết clip này",
        "best_for": "đồ cho mẹ & bé, thú cưng, kệ xếp gọn phòng trọ/chung cư nhỏ",
        "template": "Ai đang tìm đồ dùng gọn gàng cho không gian sống và sinh hoạt hằng ngày thì xem hết clip này nha.",
        "visual": "Quay {product} đặt đúng trong bối cảnh sử dụng thực tế.",
    },
]

# Bảng đối chiếu từ cấm -> từ thay thế an toàn (khớp references/banned-words.md)
BANNED_REPLACEMENTS: List[Tuple[str, str, str]] = [
    ("Cam kết tuyệt đối", "tốt nhất", "rất ổn trong tầm giá"),
    ("Cam kết tuyệt đối", "số 1", "rất đáng cân nhắc"),
    ("Cam kết tuyệt đối", "số một", "rất đáng cân nhắc"),
    ("Cam kết tuyệt đối", "đỉnh nhất", "cực kỳ ưng"),
    ("Cam kết tuyệt đối", "hoàn hảo", "rất chỉn chu"),
    ("Cam kết tuyệt đối", "vô địch", "rất nổi bật"),
    ("Cam kết tuyệt đối", "100%", "rõ rệt"),
    ("Cam kết tuyệt đối", "chắc chắn", "yên tâm"),
    ("Cam kết tuyệt đối", "cam kết", "hỗ trợ tốt"),
    ("Cam kết tuyệt đối", "đảm bảo", "dùng yên tâm"),
    ("Cam kết tuyệt đối", "vĩnh viễn", "lâu dài"),
    ("Cam kết tuyệt đối", "mãi mãi", "lâu dài"),
    ("Cam kết tuyệt đối", "không bao giờ hỏng", "dùng rất bền"),
    ("Cam kết tuyệt đối", "giá siêu rẻ", "giá dễ tiếp cận"),
    ("Cam kết tuyệt đối", "siêu rẻ", "giá dễ tiếp cận"),
    ("Cam kết tuyệt đối", "rẻ nhất", "mức giá hợp lý"),
    ("Cam kết tuyệt đối", "giá sốc", "ưu đãi tốt"),
    ("Cam kết tuyệt đối", "phá giá", "mức giá mềm"),
    ("Cam kết tuyệt đối", "sale sập sàn", "đang có ưu đãi tốt"),
    ("Cam kết tuyệt đối", "thần thánh", "rất tiện"),
    ("Cam kết tuyệt đối", "vi diệu", "hiệu quả rõ"),
    ("Cam kết tuyệt đối", "kỳ diệu", "đáng trải nghiệm"),
    ("Y tế & Mỹ phẩm", "trị dứt điểm", "hỗ trợ cải thiện"),
    ("Y tế & Mỹ phẩm", "chữa khỏi", "hỗ trợ làm dịu"),
    ("Y tế & Mỹ phẩm", "đặc trị", "chăm sóc chuyên biệt"),
    ("Y tế & Mỹ phẩm", "diệt sạch", "hỗ trợ làm sạch"),
    ("Y tế & Mỹ phẩm", "trắng bật tông", "giúp da trông sáng hơn"),
    ("Y tế & Mỹ phẩm", "hết mụn", "hỗ trợ giảm tình trạng mụn"),
    ("Y tế & Mỹ phẩm", "giảm cân cấp tốc", "hỗ trợ kiểm soát vóc dáng"),
    ("Y tế & Mỹ phẩm", "tan mỡ", "cảm giác nhẹ nhàng hơn"),
    ("Y tế & Mỹ phẩm", "kháng khuẩn 99.9%", "hỗ trợ giữ vệ sinh"),
    ("Y tế & Mỹ phẩm", "tiêu diệt vi khuẩn", "giúp bề mặt sạch sẽ hơn"),
    ("Y tế & Mỹ phẩm", "bác sĩ khuyên dùng", "được nhiều người tin dùng"),
    ("Y tế & Mỹ phẩm", "chuẩn y khoa", "thiết kế an toàn"),
    ("Điều hướng nền tảng", "shopee", "giỏ hàng góc trái"),
    ("Điều hướng nền tảng", "lazada", "giỏ hàng góc trái"),
    ("Điều hướng nền tảng", "facebook", "giỏ hàng"),
    ("Điều hướng nền tảng", "zalo", "giỏ hàng"),
    ("Điều hướng nền tảng", "inbox", "bấm vào giỏ hàng"),
    ("Điều hướng nền tảng", "nhắn tin riêng", "bấm vào giỏ hàng"),
    ("Điều hướng nền tảng", "link bio", "giỏ hàng góc trái"),
    ("Điều hướng nền tảng", "tiktok", "giỏ hàng bên dưới"),
    ("Điều hướng nền tảng", "miễn phí 100%", "có mã ưu đãi"),
    ("Điều hướng nền tảng", "tặng free", "có quà kèm ưu đãi"),
    ("Điều hướng nền tảng", "chuyển khoản", "đặt trực tiếp qua sàn"),
    ("Điều hướng nền tảng", "hàng nhái", "mẫu phổ thông"),
    ("Điều hướng nền tảng", "fake", "mẫu phổ thông"),
    ("Điều hướng nền tảng", "rep 1:1", "phiên bản tương đồng"),
    ("Điều hướng nền tảng", "siêu cấp", "hoàn thiện tốt"),
    ("Ngôn từ tiêu cực", "lừa đảo", "chưa đúng kỳ vọng"),
    ("Ngôn từ tiêu cực", "rác rưởi", "dùng hơi bất tiện"),
    ("Ngôn từ tiêu cực", "vứt đi", "chưa được gọn lắm"),
    ("Ngôn từ tiêu cực", "bóc phốt", "chia sẻ thẳng thắn"),
    ("Ngôn từ tiêu cực", "chết tiệt", "khá khó chịu"),
    ("Ngôn từ tiêu cực", "kinh khủng", "khá bất tiện"),
    ("Ngôn từ tiêu cực", "ghê tởm", "chưa ổn lắm"),
]

# Phiên âm mềm từ tiếng Anh sang tiếng Việt cho TTS (khớp references/tts-rules.md)
ENGLISH_PHONETIC_MAP = [
    (r"\btype-c\b", "tai xi"),
    (r"\btype c\b", "tai xi"),
    (r"\bbluetooth\b", "bờ lu tút"),
    (r"\bfreeship\b", "phờ ri síp"),
    (r"\breview\b", "rì viu"),
    (r"\bcombo\b", "com bô"),
    (r"\bvoucher\b", "vâu chờ"),
    (r"\bmagsafe\b", "mắc xếp"),
    (r"\bsamsung\b", "sam sung"),
    (r"\bgalaxy\b", "ga la xi"),
    (r"\biphone\b", "ai phôn"),
    (r"\bultra\b", "un tra"),
    (r"\bcamera\b", "ca me ra"),
    (r"\bdesign\b", "thiết kế"),
]


def slugify(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or f"san-pham-{int(time.time())}"


def scan_banned_words(text: str) -> List[Dict[str, str]]:
    lower_text = text.lower()
    matches = []
    seen = set()
    for group, word, safe in BANNED_REPLACEMENTS:
        if word in lower_text and word not in seen:
            seen.add(word)
            matches.append({"group": group, "word": word, "replacement": safe})
    return matches


def auto_fix_banned_words(text: str) -> Tuple[str, List[Dict[str, str]]]:
    fixed = text
    applied = []
    for group, word, safe in BANNED_REPLACEMENTS:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(fixed):
            fixed = pattern.sub(safe, fixed)
            applied.append({"group": group, "word": word, "replacement": safe})
    return fixed, applied


def _read_digits_vi(num_str: str) -> str:
    """Chuyển số giá tiền dạng 199k -> một trăm chín mươi chín nghìn (đơn giản, tự nhiên)."""
    digits = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    n = int(num_str)
    if n <= 0:
        return "rất mềm"
    if n < 10:
        return f"{digits[n]} nghìn"
    if n < 100:
        chuc, donvi = divmod(n, 10)
        res = "mười" if chuc == 1 else f"{digits[chuc]} mươi"
        if donvi == 1 and chuc > 1:
            res += " mốt"
        elif donvi == 5:
            res += " lăm"
        elif donvi > 0:
            res += f" {digits[donvi]}"
        return f"{res} nghìn"
    if n < 1000:
        tram, rem = divmod(n, 100)
        res = f"{digits[tram]} trăm"
        if rem == 0:
            return f"{res} nghìn"
        if rem < 10:
            return f"{res} lẻ {digits[rem]} nghìn"
        chuc, donvi = divmod(rem, 10)
        res += " mười" if chuc == 1 else f" {digits[chuc]} mươi"
        if donvi == 1 and chuc > 1:
            res += " mốt"
        elif donvi == 5:
            res += " lăm"
        elif donvi > 0:
            res += f" {digits[donvi]}"
        return f"{res} nghìn"
    return f"{n} nghìn"


def normalize_for_tts(text: str) -> str:
    """Chuẩn hóa văn bản theo references/tts-rules.md."""
    out = text.strip()
    # Bỏ markdown, ngoặc vuông, ngoặc đơn ghi chú
    out = re.sub(r"\[[^\]]*\]", "", out)
    out = re.sub(r"[*#_~=`\"']", "", out)
    out = out.replace("...", ", ").replace("…", ", ")
    out = out.replace("–", ", ").replace("—", ", ").replace(" - ", ", ")

    # Chuyển giá tiền 199k / 199.000đ -> chữ nói
    out = re.sub(r"\b(\d{1,3})\s*[kK]\b", lambda m: _read_digits_vi(m.group(1)), out)
    out = re.sub(r"\b(\d{1,3})\.000\s*(?:đ|vnđ|d)?\b", lambda m: _read_digits_vi(m.group(1)), out, flags=re.IGNORECASE)

    # Đơn vị đo phổ biến
    out = re.sub(r"\b(\d+)\s*ml\b", r"\1 mi li lít", out, flags=re.IGNORECASE)
    out = re.sub(r"\b(\d+)\s*mah\b", r"\1 mi li am pe giờ", out, flags=re.IGNORECASE)
    out = re.sub(r"\b(\d+)\s*w\b", r"\1 oát", out, flags=re.IGNORECASE)
    out = out.replace("&", " và ").replace("+", " cộng thêm ").replace("%", " phần trăm ")

    # Phiên âm mềm tiếng Anh
    for pat, rep in ENGLISH_PHONETIC_MAP:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)

    # Làm sạch khoảng trắng thừa theo từng đoạn
    paragraphs = []
    for p in re.split(r"\n\s*\n", out):
        cleaned = re.sub(r"\s+", " ", p).strip()
        if cleaned:
            paragraphs.append(cleaned)
    return "\n\n".join(paragraphs)


def build_affiliate_script(
    product_name: str,
    pain_point: str = "",
    highlights: Optional[List[str]] = None,
    price_text: str = "",
    hook_id: str = "pain-1",
) -> Dict[str, str]:
    """
    Tạo kịch bản Affiliate 4 phần (85-130 từ), shotlist.md (bảng 4 cột + 2 Hook dự phòng)
    và voice.txt đã chuẩn hóa + lọc từ cấm.
    """
    product = product_name.strip()
    details = [h.strip() for h in (highlights or []) if h and h.strip()]
    if not details:
        details = [
            "thiết kế gọn gàng cầm rất chắc tay",
            "bề mặt hoàn thiện mịn, màu sắc nhìn rất sang",
            "dùng thực tế hằng ngày cực kỳ tiện lợi",
        ]
    while len(details) < 3:
        details.append("tính năng thực tế đáp ứng tốt nhu cầu hằng ngày")

    pain = pain_point.strip() or "bất tiện và tốn thời gian khi dùng đồ cũ"
    price_spoken = price_text.strip() or "hơn một trăm nghìn một chút"

    hook_obj = next((h for h in HOOK_TEMPLATES if h["id"] == hook_id), HOOK_TEMPLATES[0])
    hook_line = hook_obj["template"].format(
        product=product,
        pain=pain,
        detail_1=details[0],
        price_spoken=price_spoken,
    )
    hook_visual = hook_obj["visual"].format(product=product)

    pain_line = f"Trước đây mỗi lần gặp cảnh {pain}, mình thấy khá bất tiện và hay bị vướng víu."
    exp_line_1 = f"Từ lúc chuyển sang {product} này, điểm mình ưng đầu tiên là {details[0]}."
    exp_line_2 = f"Ngoài ra còn có {details[1]}, kết hợp thêm {details[2]} nên dùng hằng ngày rất thoải mái."
    cta_line = f"Mức giá hiện chỉ {price_spoken}, mọi người bấm vào giỏ hàng góc trái màn hình để xem ưu đãi nha."

    raw_segments = [
        ("0s - 4s", "Hook", hook_visual, hook_line),
        ("4s - 12s", "Nỗi đau / Bối cảnh", f"Quay tình huống {pain} trong sinh hoạt hằng ngày.", pain_line),
        ("12s - 24s", "Trải nghiệm trực quan", f"Quay cận cảnh {product}: {details[0]}, {details[1]}.", exp_line_1),
        ("24s - 32s", "Chứng minh công dụng", f"Thao tác sử dụng thực tế {details[2]} ngay trên khung hình.", exp_line_2),
        ("32s - 40s", "CTA tự nhiên", "Chỉ tay nhẹ về biểu tượng giỏ hàng góc trái dưới màn hình.", cta_line),
    ]

    # Lọc từ cấm cho toàn bộ lời thoại
    cleaned_segments = []
    voice_paragraphs = []
    for t_range, part, visual, line in raw_segments:
        safe_line, _ = auto_fix_banned_words(line)
        cleaned_segments.append((t_range, part, visual, safe_line))
        voice_paragraphs.append(safe_line)

    # 2 Hook dự phòng khác nhóm
    backup_hooks = [h for h in HOOK_TEMPLATES if h["id"] != hook_obj["id"]][:2]
    backup_md = []
    for idx, bh in enumerate(backup_hooks, 1):
        b_line = bh["template"].format(product=product, pain=pain, detail_1=details[0], price_spoken=price_spoken)
        b_line, _ = auto_fix_banned_words(b_line)
        b_vis = bh["visual"].format(product=product)
        backup_md.append(f"{idx}. **{bh['group']}:**\n   - *Visual:* {b_vis}\n   - *Thoại:* *\"{b_line}\"*")

    table_rows = "\n".join(
        f"| **{t}** | **{p}** | {v} | {l} |" for t, p, v, l in cleaned_segments
    )

    raw_voice = "\n\n".join(voice_paragraphs)
    tts_voice = normalize_for_tts(raw_voice)
    word_count = len(tts_voice.split())

    shotlist_md = (
        f"# Kịch bản Phân cảnh (Shotlist) - {product}\n\n"
        f"- **Sản phẩm:** {product}\n"
        f"- **Độ dài thoại:** {word_count} từ (~{round(word_count / 3.0)} giây)\n"
        f"- **Công thức Hook:** {hook_obj['group']} ({hook_obj['id']})\n\n"
        f"| Thời gian | Phân đoạn | Gợi ý cảnh quay (Visual) | Lời thoại gốc |\n"
        f"| :--- | :--- | :--- | :--- |\n"
        f"{table_rows}\n\n"
        f"### 2 Hook dự phòng (Test A/B)\n\n"
        + "\n".join(backup_md)
        + "\n"
    )

    return {
        "shotlist_md": shotlist_md,
        "voice_txt": tts_voice,
        "word_count": word_count,
    }
