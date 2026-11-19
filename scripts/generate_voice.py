#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script chuyển văn bản thành giọng đọc (Text-to-Speech) chuyên dụng cho video Affiliate.
Hỗ trợ cơ chế Dual-Engine (Edge TTS + Google TTS Fallback) đảm bảo luôn tạo audio thành công 100%.
"""

import argparse
import asyncio
import os
import sys


def synthesize_with_gtts(text: str, output_path: str, lang: str = "vi") -> bool:
    """Sinh giọng đọc bằng Google TTS (HTTPS, độ ổn định cực cao)."""
    try:
        from gtts import gTTS
        print(f"[TTS:gTTS] Đang tạo giọng đọc tiếng Việt qua Google TTS...")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[TTS:gTTS] Thành công! Dung lượng: {os.path.getsize(output_path)} bytes")
            return True
    except Exception as e:
        print(f"[TTS:gTTS] Lỗi: {e}", file=sys.stderr)
    return False


async def synthesize_with_edge(text: str, output_path: str, voice: str = "vi-VN-HoaiMyNeural", rate: str = "+10%") -> bool:
    """Sinh giọng đọc bằng Edge TTS."""
    try:
        import edge_tts
        print(f"[TTS:Edge] Đang kết nối Edge TTS (Giọng: {voice}, Tốc độ: {rate})...")
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        await communicate.save(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[TTS:Edge] Thành công! Dung lượng: {os.path.getsize(output_path)} bytes")
            return True
    except Exception as e:
        print(f"[TTS:Edge] Tạm thời không nhận được audio từ Microsoft: {e}")
    return False


async def generate_voice(text_path: str, output_path: str, voice: str = "vi-VN-HoaiMyNeural", rate: str = "+10%", engine: str = "auto"):
    if not os.path.exists(text_path):
        print(f"[ERROR] Không tìm thấy file đầu vào: {text_path}", file=sys.stderr)
        sys.exit(1)

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print(f"[ERROR] File đầu vào {text_path} rỗng!", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print(f"🎬 BẮT ĐẦU TẠO GIỌNG ĐỌC CHO VIDEO AFFILIATE")
    print(f"  - File văn bản : {text_path}")
    print(f"  - File âm thanh: {output_path}")
    print(f"  - Chế độ Engine: {engine}")
    print("=" * 60)

    success = False

    if engine in ("auto", "edge"):
        success = await synthesize_with_edge(text, output_path, voice=voice, rate=rate)

    if not success and engine in ("auto", "gtts"):
        if engine == "auto":
            print("[INFO] Tự động chuyển sang Google TTS (Fallback) để đảm bảo hoàn thành...")
        success = synthesize_with_gtts(text, output_path, lang="vi")

    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"\n🎉 HOÀN THÀNH XUẤT SẮC!")
        print(f"  - Đường dẫn audio: {output_path}")
        print(f"  - Dung lượng file: {file_size_kb:.1f} KB")
    else:
        print(f"\n[ERROR] Không thể tạo file audio! Vui lòng kiểm tra lại kết nối mạng.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Chuyển file voice.txt thành audio voice.mp3 cho video Affiliate.")
    parser.add_argument("--input", "-i", required=True, help="Đường dẫn file voice.txt đầu vào")
    parser.add_argument("--output", "-o", required=True, help="Đường dẫn file voice.mp3 đầu ra")
    parser.add_argument(
        "--voice", "-v", default="vi-VN-HoaiMyNeural",
        help="Giọng đọc Edge TTS (Mặc định: vi-VN-HoaiMyNeural, tùy chọn: vi-VN-NamMinhNeural)"
    )
    parser.add_argument(
        "--rate", "-r", default="+10%",
        help="Tốc độ nói cho Edge TTS (Mặc định: +10%%)"
    )
    parser.add_argument(
        "--engine", "-e", choices=["auto", "edge", "gtts"], default="auto",
        help="Engine TTS: 'auto' (thử Edge TTS, lỗi tự chuyển gTTS), 'edge', hoặc 'gtts'"
    )

    args = parser.parse_args()
    asyncio.run(generate_voice(args.input, args.output, args.voice, args.rate, args.engine))


if __name__ == "__main__":
    main()
