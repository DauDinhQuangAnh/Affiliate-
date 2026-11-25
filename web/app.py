#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Studio Server (FastAPI) cho Affiliate Video Script & Voice Generator.
Cho phép thao tác trực quan qua trình duyệt: nhập/chỉnh kịch bản, kiểm tra từ cấm,
chọn 12 giọng tiếng Việt (hoặc Random), chỉnh tốc độ, tạo & nghe thử trực tiếp MP3.
"""

import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Thêm thư mục scripts/ vào sys.path để tái sử dụng logic TTS v2.0 Pro
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = Path(__file__).resolve().parent / "static"

sys.path.insert(0, str(SCRIPTS_DIR))
import generate_voice as tts_core  # noqa: E402

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Affiliate Voice & Script Studio", version="2.0.0")


class GenerateRequest(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = Field(default="random")
    speed: Optional[float] = Field(default=None, ge=0.8, le=1.6)


class CheckBannedRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)


# Danh sách cụm từ cấm phổ biến trích xuất theo references/banned-words.md
BANNED_PATTERNS = [
    ("Cam kết tuyệt đối", ["tốt nhất", "số 1", "số một", "đỉnh nhất", "hoàn hảo", "vô địch", "100%", "chắc chắn 100%", "vĩnh viễn", "mãi mãi", "không bao giờ hỏng", "siêu rẻ", "rẻ nhất", "giá sốc", "phá giá", "sale sập sàn", "thần thánh", "vi diệu", "kỳ diệu"]),
    ("Y tế & Mỹ phẩm", ["trị dứt điểm", "chữa khỏi", "đặc trị", "diệt sạch", "trắng bật tông", "hết mụn", "giảm cân cấp tốc", "tan mỡ", "kháng khuẩn 99.9%", "tiêu diệt vi khuẩn", "bác sĩ khuyên dùng", "chuẩn y khoa"]),
    ("Điều hướng nền tảng", ["shopee", "lazada", "facebook", "zalo", "inbox", "nhắn tin riêng", "link bio", "tiktok", "miễn phí 100%", "tặng free", "chuyển khoản", "hàng nhái", "fake", "rep 1:1", "siêu cấp"]),
    ("Ngôn từ tiêu cực", ["lừa đảo", "rác rưởi", "vứt đi", "bóc phốt", "chết tiệt", "kinh khủng", "ghê tởm"]),
]


def slugify(value: str) -> str:
    """Chuyển chuỗi tiếng Việt bất kỳ thành slug an toàn cho tên thư mục."""
    value = value.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or f"san-pham-{int(time.time())}"


@app.get("/")
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/voices")
async def get_voices():
    """Trả về danh sách 12 profile giọng đọc tiếng Việt."""
    voices = []
    for key, profile in tts_core.VOICE_PROFILES.items():
        voices.append({
            "key": key,
            "gender": profile["gender"],
            "desc": profile["desc"],
            "default_speed": profile["default_speed"],
            "is_tiktok": key.startswith("tiktok-"),
        })
    return {"voices": voices}


@app.post("/api/check-banned")
async def check_banned(req: CheckBannedRequest):
    """Kiểm tra nhanh từ cấm TikTok Shop / Shopee Video trong lời thoại."""
    lower_text = req.text.lower()
    matches = []
    for group, words in BANNED_PATTERNS:
        for w in words:
            if w in lower_text:
                matches.append({"group": group, "word": w})
    return {"count": len(matches), "matches": matches}


@app.post("/api/generate")
async def api_generate(req: GenerateRequest):
    """Lưu voice.txt và sinh file voice.mp3 bằng Dual-Engine + Audio Mastering."""
    safe_slug = slugify(req.slug)
    project_dir = OUTPUT_DIR / safe_slug
    project_dir.mkdir(parents=True, exist_ok=True)

    voice_txt_path = project_dir / "voice.txt"
    voice_mp3_path = project_dir / "voice.mp3"

    clean_text = req.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Nội dung lời thoại không được để trống.")

    voice_txt_path.write_text(clean_text, encoding="utf-8")

    # Chọn giọng trước để trả về chính xác giọng đã dùng cho UI
    chosen_key, profile = tts_core.pick_voice(req.voice)
    target_speed = req.speed if req.speed is not None else profile.get("default_speed", 1.25)

    try:
        await tts_core.generate_voice(
            text_path=str(voice_txt_path),
            output_path=str(voice_mp3_path),
            voice_request=chosen_key,
            speed=target_speed,
            engine_override="auto",
        )
    except SystemExit as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo giọng đọc (mã {e.code}).")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống TTS: {e}")

    if not voice_mp3_path.exists():
        raise HTTPException(status_code=500, detail="Không tìm thấy file MP3 sau khi tạo.")

    size_kb = round(voice_mp3_path.stat().st_size / 1024, 1)
    duration_sec = 0.0
    try:
        import soundfile as sf
        data, sr = sf.read(str(voice_mp3_path))
        duration_sec = round(len(data) / sr, 2)
    except Exception:
        pass

    ts = int(time.time())
    return {
        "slug": safe_slug,
        "chosen_voice": chosen_key,
        "chosen_desc": profile["desc"],
        "speed": target_speed,
        "size_kb": size_kb,
        "duration_sec": duration_sec,
        "audio_url": f"/output/{safe_slug}/voice.mp3?t={ts}",
        "text_url": f"/output/{safe_slug}/voice.txt?t={ts}",
    }


@app.get("/api/projects")
async def list_projects():
    """Liệt kê các sản phẩm đã tạo trong thư mục output/."""
    projects = []
    if OUTPUT_DIR.exists():
        dirs = sorted(
            [d for d in OUTPUT_DIR.iterdir() if d.is_dir()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for d in dirs:
            voice_txt = d / "voice.txt"
            voice_mp3 = d / "voice.mp3"
            shotlist = d / "shotlist.md"

            text_content = voice_txt.read_text(encoding="utf-8") if voice_txt.exists() else ""
            shotlist_content = shotlist.read_text(encoding="utf-8") if shotlist.exists() else ""
            ts = int(voice_mp3.stat().st_mtime) if voice_mp3.exists() else 0

            projects.append({
                "slug": d.name,
                "has_audio": voice_mp3.exists(),
                "has_shotlist": shotlist.exists(),
                "audio_url": f"/output/{d.name}/voice.mp3?t={ts}" if voice_mp3.exists() else None,
                "text": text_content,
                "shotlist": shotlist_content,
            })
    return {"projects": projects}


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Đang khởi động Affiliate Voice & Script Studio tại: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
