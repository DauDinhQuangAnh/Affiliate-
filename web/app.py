#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Studio Server (FastAPI) cho Affiliate Video Script & Voice Generator (v2.2).
Hỗ trợ đầy đủ 5 bước theo SKILL.md:
- Upload ảnh sản phẩm + Tên + Giá -> AI (Gemini Vision + Google Search) tự phân tích & viết kịch bản.
- Fallback Smart Script Builder nếu chưa cấu hình Gemini API Key.
- Quét & Tự sửa từ cấm + Chuẩn hóa TTS + Tạo & Nghe thử MP3 + Quản lý output/.
"""

import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = Path(__file__).resolve().parent / "static"

sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_generator  # noqa: E402
import generate_voice as tts_core  # noqa: E402
import script_engine  # noqa: E402

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Affiliate Voice & Script Studio", version="2.2.0")


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


@app.get("/api/config")
async def get_config():
    """Kiểm tra xem server đã có sẵn biến môi trường GEMINI_API_KEY chưa."""
    has_env_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    return {"has_env_key": has_env_key}


@app.get("/api/hooks")
async def get_hooks():
    return {"hooks": script_engine.HOOK_TEMPLATES}


@app.get("/api/voices")
async def get_voices():
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
async def api_build_script(
    product_name: str = Form(...),
    price_text: str = Form(""),
    pain_point: str = Form(""),
    highlights: str = Form(""),
    hook_id: str = Form("auto"),
    api_key: str = Form(""),
    image: Optional[UploadFile] = File(None),
):
    """
    Sinh kịch bản theo đúng flow SKILL.md:
    - Nếu có Gemini API Key (từ form hoặc env): dùng AI Vision + Google Search.
    - Nếu chưa có Key: fallback sang Smart Template Builder nội bộ và báo rõ chế độ.
    """
    clean_name = product_name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Vui lòng nhập tên sản phẩm.")

    slug = script_engine.slugify(clean_name)
    project_dir = OUTPUT_DIR / slug
    project_dir.mkdir(parents=True, exist_ok=True)

    image_bytes = None
    image_mime = "image/jpeg"
    if image and image.filename:
        image_bytes = await image.read()
        if image_bytes:
            image_mime = image.content_type or "image/jpeg"
            ext = Path(image.filename).suffix or ".jpg"
            (project_dir / f"product{ext}").write_bytes(image_bytes)

    effective_key = api_key.strip() or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""

    if effective_key:
        notes_combined = "\n".join(filter(None, [
            f"Nỗi đau khách hàng: {pain_point.strip()}" if pain_point.strip() else "",
            f"Điểm nổi bật: {highlights.strip()}" if highlights.strip() else "",
        ]))
        try:
            result = ai_generator.generate_script_with_ai(
                api_key=effective_key,
                product_name=clean_name,
                price_text=price_text.strip(),
                notes=notes_combined,
                hook_id=hook_id,
                image_bytes=image_bytes,
                image_mime=image_mime,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi gọi Gemini AI: {e}")
    else:
        highlight_list = [h.strip() for h in highlights.replace("\n", ",").split(",") if h.strip()]
        chosen_hook = "pain-1" if hook_id == "auto" else hook_id
        result = script_engine.build_affiliate_script(
            product_name=clean_name,
            pain_point=pain_point.strip(),
            highlights=highlight_list,
            price_text=price_text.strip(),
            hook_id=chosen_hook,
        )
        result["mode"] = "template-fallback"

    (project_dir / "shotlist.md").write_text(result["shotlist_md"], encoding="utf-8")
    (project_dir / "voice.txt").write_text(result["voice_txt"], encoding="utf-8")

    return {
        "slug": slug,
        "shotlist_md": result["shotlist_md"],
        "voice_txt": result["voice_txt"],
        "word_count": result["word_count"],
        "mode": result["mode"],
    }


@app.post("/api/check-banned")
async def check_banned(req: TextRequest):
    matches = script_engine.scan_banned_words(req.text)
    return {"count": len(matches), "matches": matches}


@app.post("/api/fix-banned")
async def fix_banned(req: TextRequest):
    fixed_text, applied = script_engine.auto_fix_banned_words(req.text)
    return {"text": fixed_text, "fixed_count": len(applied), "applied": applied}


@app.post("/api/normalize-tts")
async def normalize_tts(req: TextRequest):
    normalized = script_engine.normalize_for_tts(req.text)
    return {"text": normalized}


@app.post("/api/generate")
async def api_generate(req: GenerateRequest):
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
