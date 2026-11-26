#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module gọi AI (Gemini Vision + Google Search Grounding) để thực hiện đúng quy trình
5 bước trong .agent/skills/affiliate-video-script-voice/SKILL.md.
"""

import os
from pathlib import Path
from typing import Dict, Optional

import script_engine

BASE_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR = BASE_DIR / ".agent" / "skills" / "affiliate-video-script-voice"


def _load_skill_context() -> str:
    """Đọc toàn bộ tài liệu quy chuẩn từ bộ Skill để nạp cho AI."""
    files = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "references" / "hook-formulas.md",
        SKILL_DIR / "references" / "banned-words.md",
        SKILL_DIR / "references" / "tts-rules.md",
    ]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f"--- {f.name} ---\n{f.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def generate_script_with_ai(
    api_key: str,
    product_name: str,
    price_text: str = "",
    notes: str = "",
    hook_id: str = "auto",
    image_bytes: Optional[bytes] = None,
    image_mime: str = "image/jpeg",
    model_name: str = "gemini-2.5-flash",
) -> Dict[str, str]:
    """
    Gọi Gemini API (kèm ảnh sản phẩm nếu có + Google Search) để tự động
    Research -> Viết kịch bản 85-130 từ -> Kiểm duyệt -> Chuẩn hóa TTS.
    """
    from google import genai
    from google.genai import types

    key = (api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if not key:
        raise ValueError("Chưa có Gemini API Key.")

    skill_rules = _load_skill_context()
    hook_hint = (
        f"Ưu tiên sử dụng công thức Hook có id '{hook_id}'."
        if hook_id and hook_id != "auto"
        else "Tự chọn 1 công thức Hook phù hợp nhất trong 12 mẫu của hook-formulas.md."
    )

    prompt = f"""Bạn là chuyên gia sáng tạo nội dung Affiliate TikTok Shop & Shopee Video.
Hãy thực hiện ĐẦY ĐỦ 4 bước đầu tiên theo đúng tài liệu Skill bên dưới để tạo kịch bản cho sản phẩm sau:

- Tên sản phẩm: {product_name}
- Mức giá tham khảo: {price_text or "Chưa cung cấp (tự tìm mức giá phổ biến qua Google Search nếu cần)"}
- Ghi chú thêm từ người bán: {notes or "Không có"}
- Yêu cầu Hook: {hook_hint}

QUY TẮC BẮT BUỘC:
1. Nếu có hình ảnh đính kèm, hãy quan sát kỹ ảnh và đưa ít nhất 3 chi tiết trực quan nhìn thấy thật (màu sắc, chất liệu, nút bấm, kiểu dáng...) vào lời thoại.
2. Dùng Google Search tìm công dụng thực tế, nỗi đau và câu hỏi thường gặp của khách hàng về sản phẩm này. KHÔNG sao chép văn mẫu mô tả sàn.
3. Kịch bản dài 85–130 từ (30–45 giây), văn phong nói chuyện tự nhiên như bạn bè chia sẻ, mỗi câu dưới 18 chữ.
4. Quét sạch mọi từ cấm trong banned-words.md.
5. Phần VOICE phải là thuần văn bản thoại đã chuẩn hóa tuyệt đối theo tts-rules.md (không markdown, không dấu ba chấm `...`, không gạch ngang `-`, giá tiền và đơn vị viết thành chữ nói tiếng Việt, phiên âm mềm tiếng Anh như `tai xi`, `mắc xếp`, `ca me ra`...).

ĐỊNH DẠNG TRẢ VỀ CHÍNH XÁC GỒM 2 KHỐI SAU (KHÔNG THÊM LỜI BÌNH LUẬN BÊN NGOÀI):

===SHOTLIST_START===
(Nội dung file shotlist.md: tiêu đề, bảng 4 cột Thời gian | Phân đoạn | Gợi ý cảnh quay (Visual) | Lời thoại gốc, và 2 Hook dự phòng bên dưới bảng)
===SHOTLIST_END===

===VOICE_START===
(Nội dung thuần văn bản cho file voice.txt, mỗi phân đoạn cách nhau đúng 1 dòng trống)
===VOICE_END===

TÀI LIỆU SKILL THAM CHIẾU:
{skill_rules}
"""

    contents = []
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))
    contents.append(prompt)

    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.7,
        ),
    )

    raw_text = (response.text or "").strip()
    shotlist_md = ""
    voice_txt = ""

    if "===SHOTLIST_START===" in raw_text and "===SHOTLIST_END===" in raw_text:
        shotlist_md = raw_text.split("===SHOTLIST_START===", 1)[1].split("===SHOTLIST_END===", 1)[0].strip()
    if "===VOICE_START===" in raw_text and "===VOICE_END===" in raw_text:
        voice_txt = raw_text.split("===VOICE_START===", 1)[1].split("===VOICE_END===", 1)[0].strip()

    if not voice_txt:
        raise RuntimeError("AI không trả về đúng định dạng ===VOICE_START===. Phản hồi nhận được:\n" + raw_text[:400])

    # Hậu kiểm an toàn lần cuối bằng rule engine
    voice_txt, _ = script_engine.auto_fix_banned_words(voice_txt)
    voice_txt = script_engine.normalize_for_tts(voice_txt)
    word_count = len(voice_txt.split())

    return {
        "shotlist_md": shotlist_md or f"# Shotlist - {product_name}\n\n{voice_txt}",
        "voice_txt": voice_txt,
        "word_count": word_count,
        "mode": "ai-gemini",
    }


def suggest_hooks_with_ai(
    api_key: str,
    product_name: str,
    price_text: str = "",
    notes: str = "",
    image_bytes: Optional[bytes] = None,
    image_mime: str = "image/jpeg",
    model_name: str = "gemini-2.5-flash",
) -> list:
    """
    Dùng Gemini Vision + Google Search để phân tích sản phẩm và chọn ra
    Top 3 công thức Hook thịnh hành phù hợp nhất trong 20 mẫu.
    """
    import json
    from google import genai
    from google.genai import types

    key = (api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if not key:
        raise ValueError("Chưa có Gemini API Key.")

    hooks_catalog = "\n".join(
        f"- id: {h['id']} | nhóm: {h['group']} | mẫu: {h['label']} | hợp với: {h['best_for']}"
        for h in script_engine.HOOK_TEMPLATES
    )

    prompt = f"""Bạn là chuyên gia chiến lược TikTok Shop Affiliate.
Hãy phân tích sản phẩm dưới đây (kèm ảnh nếu có) và chọn ra **ĐÚNG 3 công thức Hook phù hợp nhất** trong danh sách 20 mẫu Hook thịnh hành bên dưới để tối ưu tỷ lệ giữ chân 3 giây đầu.

- Sản phẩm: {product_name}
- Mức giá: {price_text or "Chưa rõ"}
- Ghi chú: {notes or "Không có"}

DANH SÁCH 20 HOOK THỊNH HÀNH:
{hooks_catalog}

YÊU CẦU: Trả về DUY NHẤT một mảng JSON hợp lệ (không giải thích thêm, không bọc markdown ```json) gồm 3 phần tử theo thứ tự phù hợp từ cao xuống thấp:
[
  {{
    "id": "id_hook_trong_danh_sach",
    "score": 96,
    "reason": "Giải thích ngắn gọn 1 câu vì sao sản phẩm này hợp với Hook này",
    "sample_hook": "Câu Hook viết sẵn cụ thể cho sản phẩm (dưới 18 chữ, sạch từ cấm)"
  }}
]
"""

    contents = []
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))
    contents.append(prompt)

    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.4,
        ),
    )

    raw = (response.text or "").strip()
    # Trích xuất đoạn JSON [...] an toàn
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        raise RuntimeError("AI không trả về mảng JSON hợp lệ.")
    parsed = json.loads(raw[start : end + 1])

    valid_ids = {h["id"]: h for h in script_engine.HOOK_TEMPLATES}
    suggestions = []
    for item in parsed:
        hid = item.get("id")
        if hid in valid_ids:
            safe_sample, _ = script_engine.auto_fix_banned_words(item.get("sample_hook", ""))
            suggestions.append({
                "id": hid,
                "group": valid_ids[hid]["group"],
                "label": valid_ids[hid]["label"],
                "score": int(item.get("score", 90)),
                "reason": item.get("reason", ""),
                "sample_hook": safe_sample,
            })
    return suggestions[:3]
