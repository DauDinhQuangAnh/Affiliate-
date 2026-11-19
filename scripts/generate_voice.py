#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script chuyển văn bản thành giọng đọc (Text-to-Speech) sử dụng edge-tts.
Phù hợp sản xuất video Affiliate TikTok Shop và Shopee Video.
"""

import argparse
import asyncio
import os
import sys
import edge_tts


async def text_to_speech(text_path: str, output_path: str, voice: str = "vi-VN-HoaiMyNeural", rate: str = "+10%"):
    if not os.path.exists(text_path):
        print(f"[ERROR] Không tìm thấy file đầu vào: {text_path}", file=sys.stderr)
        sys.exit(1)

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print(f"[ERROR] Nội dung file {text_path} rỗng!", file=sys.stderr)
        sys.exit(1)

    # Đảm bảo thư mục đầu ra tồn tại
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    print(f"[TTS] Đang tạo giọng đọc...")
    print(f"  - File đầu vào : {text_path}")
    print(f"  - File đầu ra  : {output_path}")
    print(f"  - Giọng đọc    : {voice}")
    print(f"  - Tốc độ nói   : {rate}")

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(output_path)
    print(f"[TTS] Thành công! File âm thanh đã lưu tại: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Chuyển file voice.txt thành audio voice.mp3 qua edge-tts.")
    parser.add_argument("--input", "-i", required=True, help="Đường dẫn file voice.txt đầu vào")
    parser.add_argument("--output", "-o", required=True, help="Đường dẫn file voice.mp3 đầu ra")
    parser.add_argument(
        "--voice", "-v", default="vi-VN-HoaiMyNeural",
        help="Giọng đọc Edge TTS (Mặc định: vi-VN-HoaiMyNeural, tùy chọn nam: vi-VN-NamMinhNeural)"
    )
    parser.add_argument(
        "--rate", "-r", default="+10%",
        help="Tốc độ nói (Mặc định: +10%% cho video Affiliate ngắn sôi nổi)"
    )

    args = parser.parse_args()
    asyncio.run(text_to_speech(args.input, args.output, args.voice, args.rate))


if __name__ == "__main__":
    main()
