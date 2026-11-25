#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Studio Server (FastAPI) cho Affiliate Video Script & Voice Generator.
Hỗ trợ quy trình đầy đủ: Nhập sản phẩm -> Tự sinh kịch bản & Shotlist ->
Quét & tự sửa từ cấm -> Chuẩn hóa TTS -> Tạo & Nghe thử MP3 -> Quản lý output/.
"""

import os
import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = Path(__file__).resolve().parent / "static"

sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_voice as tts_core  # noqa: E402
import script_engine  # noqa: E402

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Affiliate Voice & Script Studio", version="2.1.0")


class BuildScriptRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=150)
    pain_point: str = Field(default="", max_length=300)
    highlights: List[str] = Field(default_factory=list)
    price_text: str = Field(default="", max_length=100)
    hook_id: str = Field(default="pain-1")


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)


class GenerateRequest(BaseModel):
    slug: str = Field(..., min_length=1, max_length=120)
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = Field(default="random")
    speed: Optional[float] = Field(default=None, ge=0.8, le=1.6)


@app.get("/")
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/hooks")
async def get_hooks():
    """Trả về 12 công thức Hook chia theo 5 nhóm."""
    return {"hooks": script_engine.HOOK_TEMPLATES}


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


@app.post("/api/build-script")
async def api_build_script(req: BuildScriptRequest):
    """Tạo kịch bản Affiliate chuẩn 5 bước và lưu shotlist.md + voice.txt."""
    slug = script_engine.slugify(req.product_name)
    result = script_engine.build_affiliate_script(
        product_name=req.product_name,
        pain_point=req.pain_point,
        highlights=req.highlights,
        price_text=req.price_text,
        hook_id=req.hook_id,
    )

    project_dir = OUTPUT_DIR / slug
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "shotlist.md").write_text(result["shotlist_md"], encoding="utf-8")
    (project_dir / "voice.txt").write_text(result["voice_txt"], encoding="utf-8")

    return {
        "slug": slug,
        "shotlist_md": result["shotlist_md"],
        "voice_txt": result["voice_txt"],
        "word_count": result["word_count"],
    }


@app.post("/api/check-banned")
async def check_banned(req: TextRequest):
    """Kiểm tra từ cấm TikTok Shop / Shopee Video."""
    matches = script_engine.scan_banned_words(req.text)
    return {"count": len(matches), "matches": matches}


@app.post("/api/fix-banned")
async def fix_banned(req: TextRequest):
    """Tự động thay thế từ cấm bằng từ an toàn."""
    fixed_text, applied = script_engine.auto_fix_banned_words(req.text)
    return {"text": fixed_text, "fixed_count": len(applied), "applied": applied}


@app.post("/api/normalize-tts")
async def normalize_tts(req: TextRequest):
    """Chuẩn hóa văn bản cho engine TTS (số, đơn vị, phiên âm mềm)."""
    normalized = script_engine.normalize_for_tts(req.text)
    return {"text": normalized}


@app.post("/api/generate")
async def api_generate(req: GenerateRequest):
    """Lưu voice.txt và sinh file voice.mp3 bằng Dual-Engine + Audio Mastering."""
    safe_slug = script_engine.slugify(req.slug)
    project_dir = OUTPUT_DIR / safe_slug
    project_dir.mkdir(parents=True, exist_ok=True)

    voice_txt_path = project_dir / "voice.txt"
    voice_mp3_path = project_dir / "voice.mp3"

    clean_text = req.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Nội dung lời thoại không được để trống.")

    voice_txt_path.write_text(clean_text, encoding="utf-8")

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


@app.delete("/api/projects/{slug}")
async def delete_project(slug: str):
    """Xóa thư mục sản phẩm trong output/."""
    safe_slug = script_engine.slugify(slug)
    target = (OUTPUT_DIR / safe_slug).resolve()
    if not str(target).startswith(str(OUTPUT_DIR.resolve())) or not target.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy thư mục sản phẩm.")
    shutil.rmtree(target)
    return {"deleted": safe_slug}


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8088))
    print(f"🚀 Đang khởi động Affiliate Voice & Script Studio tại: http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
