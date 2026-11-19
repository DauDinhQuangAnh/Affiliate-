#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script chuyển văn bản thành giọng đọc (Text-to-Speech) chuyên dụng cho video Affiliate.
Hỗ trợ:
- Cơ chế Dual-Engine (Edge TTS + Google TTS Fallback).
- Tăng tốc độ nói chuyên nghiệp (Phase Vocoder, giữ nguyên cao độ, không bị méo tiếng).
- Tự động cắt tỉa khoảng lặng thừa (dead air) để nhịp điệu dứt khoát, bắt tai.
"""

import argparse
import asyncio
import os
import sys
import numpy as np


def post_process_audio_speed(audio_path: str, speed_factor: float = 1.25, max_pause_sec: float = 0.18):
    """
    Tối ưu hóa âm thanh:
    1. Cắt tỉa khoảng lặng thừa giữa các câu xuống tối đa max_pause_sec.
    2. Tăng tốc độ nói với speed_factor bằng thuật toán Phase Vocoder (pitch-preserved).
    """
    try:
        import soundfile as sf
        from scipy import signal
    except ImportError:
        print("[WARN] Thiếu soundfile hoặc scipy, bỏ qua khâu tăng tốc hậu kỳ.")
        return

    try:
        data, sr = sf.read(audio_path)
        orig_duration = len(data) / sr

        # 1. Rút ngắn các khoảng lặng thừa
        chunk_size = int(sr * 0.04)  # 40ms
        threshold = 0.012
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        max_silent_chunks = int(max_pause_sec / 0.04)

        trimmed = []
        silent_count = 0
        for c in chunks:
            is_silent = np.max(np.abs(c)) < threshold
            if is_silent:
                silent_count += 1
                if silent_count <= max_silent_chunks:
                    trimmed.append(c)
            else:
                silent_count = 0
                trimmed.append(c)

        trimmed_data = np.concatenate(trimmed) if trimmed else data

        # 2. Phase vocoder time stretch nếu speed_factor khác 1.0
        if speed_factor != 1.0:
            n_fft = 1024
            hop_length = n_fft // 4
            _, _, stft = signal.stft(trimmed_data, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)

            time_steps = np.arange(0, stft.shape[1] - 1, speed_factor)
            phase_acc = np.angle(stft[:, 0])
            stretched = np.zeros((stft.shape[0], len(time_steps)), dtype=complex)
            expected_adv = 2 * np.pi * hop_length * np.arange(stft.shape[0]) / n_fft

            for i, t in enumerate(time_steps):
                t0, t1 = int(t), int(t) + 1
                alpha = t - t0
                mag = (1 - alpha) * np.abs(stft[:, t0]) + alpha * np.abs(stft[:, t1])
                p_diff = np.angle(stft[:, t1]) - np.angle(stft[:, t0])
                p_diff = (p_diff - expected_adv + np.pi) % (2 * np.pi) - np.pi
                phase_acc += expected_adv + p_diff
                stretched[:, i] = mag * np.exp(1j * phase_acc)

            _, final_data = signal.istft(stretched, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)
        else:
            final_data = trimmed_data

        sf.write(audio_path, final_data, sr)
        new_duration = len(final_data) / sr
        print(f"[POST-PROCESS] Tối ưu nhịp điệu thành công:")
        print(f"  - Thời lượng gốc : {orig_duration:.2f}s")
        print(f"  - Thời lượng mới : {new_duration:.2f}s (nhanh hơn {orig_duration - new_duration:.2f}s, nhịp chuẩn video ngắn)")
    except Exception as e:
        print(f"[WARN] Lỗi khi tối ưu tốc độ audio: {e}", file=sys.stderr)


def synthesize_with_gtts(text: str, output_path: str, lang: str = "vi") -> bool:
    """Sinh giọng đọc bằng Google TTS (HTTPS, độ ổn định cực cao)."""
    try:
        from gtts import gTTS
        print(f"[TTS:gTTS] Đang tạo giọng đọc tiếng Việt qua Google TTS...")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[TTS:gTTS] Tạo âm thanh thành công! ({os.path.getsize(output_path)} bytes)")
            return True
    except Exception as e:
        print(f"[TTS:gTTS] Lỗi: {e}", file=sys.stderr)
    return False


async def synthesize_with_edge(text: str, output_path: str, voice: str = "vi-VN-HoaiMyNeural", rate: str = "+25%") -> bool:
    """Sinh giọng đọc bằng Edge TTS (có timeout 5s để chuyển fallback nhanh chóng)."""
    try:
        import edge_tts
        print(f"[TTS:Edge] Đang kết nối Edge TTS (Giọng: {voice}, Tốc độ: {rate})...")
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        # Timeout 5 giây nếu Microsoft không phản hồi
        await asyncio.wait_for(communicate.save(output_path), timeout=5.0)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[TTS:Edge] Tạo âm thanh thành công! ({os.path.getsize(output_path)} bytes)")
            return True
    except asyncio.TimeoutError:
        print("[TTS:Edge] Microsoft phản hồi quá chậm (Timeout > 5s).")
    except Exception as e:
        print(f"[TTS:Edge] Tạm thời không nhận được audio từ Microsoft: {e}")
    return False


async def generate_voice(
    text_path: str,
    output_path: str,
    voice: str = "vi-VN-HoaiMyNeural",
    speed: float = 1.25,
    engine: str = "auto"
):
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

    # Tính toán rate cho Edge TTS theo speed (ví dụ: speed 1.25 tương đương +25%)
    rate_percent = int((speed - 1.0) * 100)
    rate_str = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"

    print("=" * 65)
    print(f"🎬 BẮT ĐẦU TẠO GIỌNG ĐỌC NHANH CHO VIDEO AFFILIATE")
    print(f"  - File văn bản : {text_path}")
    print(f"  - File âm thanh: {output_path}")
    print(f"  - Tốc độ đọc   : {speed}x (nhanh hơn {rate_percent}%)")
    print(f"  - Chế độ Engine: {engine}")
    print("=" * 65)

    success = False

    if engine in ("auto", "edge"):
        success = await synthesize_with_edge(text, output_path, voice=voice, rate=rate_str)

    if not success and engine in ("auto", "gtts"):
        if engine == "auto":
            print("[INFO] Tự động chuyển sang Google TTS (Fallback) để đảm bảo hoàn thành...")
        success = synthesize_with_gtts(text, output_path, lang="vi")
        if success:
            # Google TTS mặc định 1.0x, tiến hành tăng tốc hậu kỳ theo speed
            post_process_audio_speed(output_path, speed_factor=speed)

    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"\n🎉 HOÀN THÀNH XUẤT SẮC!")
        print(f"  - Đường dẫn audio: {output_path}")
        print(f"  - Dung lượng file: {file_size_kb:.1f} KB")
    else:
        print(f"\n[ERROR] Không thể tạo file audio! Vui lòng kiểm tra lại kết nối mạng.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Chuyển file voice.txt thành audio voice.mp3 tốc độ cao cho video Affiliate.")
    parser.add_argument("--input", "-i", required=True, help="Đường dẫn file voice.txt đầu vào")
    parser.add_argument("--output", "-o", required=True, help="Đường dẫn file voice.mp3 đầu ra")
    parser.add_argument(
        "--speed", "-s", type=float, default=1.25,
        help="Tốc độ nói (Mặc định: 1.25x - tăng tốc 25%% phù hợp nhịp điệu video ngắn TikTok/Shopee)"
    )
    parser.add_argument(
        "--voice", "-v", default="vi-VN-HoaiMyNeural",
        help="Giọng đọc Edge TTS (Mặc định: vi-VN-HoaiMyNeural, tùy chọn: vi-VN-NamMinhNeural)"
    )
    parser.add_argument(
        "--engine", "-e", choices=["auto", "edge", "gtts"], default="auto",
        help="Engine TTS: 'auto' (thử Edge TTS, lỗi tự chuyển gTTS), 'edge', hoặc 'gtts'"
    )

    args = parser.parse_args()
    asyncio.run(generate_voice(args.input, args.output, voice=args.voice, speed=args.speed, engine=args.engine))


if __name__ == "__main__":
    main()
