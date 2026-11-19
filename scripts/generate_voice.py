#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script chuyển văn bản thành giọng đọc (Text-to-Speech) chuyên dụng cho video Affiliate.
Hỗ trợ:
- Kho 10 giọng đọc tiếng Việt (Nam / Nữ / Đa phong cách).
- Cơ chế RANDOM giọng ngẫu nhiên khi sản xuất hàng loạt video.
- Tự động fallback giữa Edge TTS và Google TTS để đạt tỷ lệ thành công 100%.
- Tăng tốc độ nói chuyên nghiệp (Phase Vocoder, giữ nguyên cao độ).
- Tự động cắt tỉa khoảng lặng thừa (dead air) giúp video sôi động, cuốn hút.
"""

import argparse
import asyncio
import os
import random
import sys
import numpy as np


# ==============================================================================
# BẢNG ĐẶC TẢ CÁC GIỌNG ĐỌC TIẾNG VIỆT CHO VIDEO AFFILIATE
# ==============================================================================
VOICE_PROFILES = {
    # 1. Giọng Nữ truyền cảm (Edge TTS)
    "nu-truyen-cam": {
        "engine": "edge",
        "voice_id": "vi-VN-HoaiMyNeural",
        "gender": "female",
        "desc": "Nữ miền Bắc ngọt ngào, truyền cảm (Gia dụng, Mẹ bé, Mỹ phẩm)",
        "pitch_shift": 0.0,
    },
    # 2. Giọng Nam dứt khoát (Edge TTS)
    "nam-dut-khoat": {
        "engine": "edge",
        "voice_id": "vi-VN-NamMinhNeural",
        "gender": "male",
        "desc": "Nam miền Bắc dứt khoát, tin cậy (Gia dụng, Dụng cụ, Đời sống)",
        "pitch_shift": 0.0,
    },
    # 3. Giọng Nữ hiện đại (Edge Multilingual)
    "nu-hien-dai": {
        "engine": "edge",
        "voice_id": "en-US-EmmaMultilingualNeural",
        "gender": "female",
        "desc": "Nữ hiện đại, phát âm mượt mà (Phụ kiện, Decor, Công nghệ nhẹ)",
        "pitch_shift": 0.0,
    },
    # 4. Giọng Nam công nghệ (Edge Multilingual)
    "nam-cong-nghe": {
        "engine": "edge",
        "voice_id": "en-US-AndrewMultilingualNeural",
        "gender": "male",
        "desc": "Nam trẻ trung, review đồ công nghệ (Tai nghe, Cáp sạc, Smart device)",
        "pitch_shift": 0.0,
    },
    # 5. Giọng Nữ tươi tắn (Edge Multilingual)
    "nu-tuoi-tan": {
        "engine": "edge",
        "voice_id": "en-US-AvaMultilingualNeural",
        "gender": "female",
        "desc": "Nữ năng động, nhí nhảnh (Thời trang, Đồ ăn vặt, Phụ kiện xinh)",
        "pitch_shift": 0.0,
    },
    # 6. Giọng Nam sôi nổi (Edge Multilingual)
    "nam-soi-noi": {
        "engine": "edge",
        "voice_id": "en-US-BrianMultilingualNeural",
        "gender": "male",
        "desc": "Nam hào hứng, lôi cuốn (Đồ chơi, Phụ kiện xe, Thể thao)",
        "pitch_shift": 0.0,
    },
    # 7. Giọng Nữ rõ chữ (Google TTS chuẩn)
    "nu-ro-chu": {
        "engine": "gtts",
        "voice_id": "gtts-standard",
        "gender": "female",
        "desc": "Nữ tròn vành rõ chữ, tự nhiên, ổn định tuyệt đối (Review tổng hợp)",
        "pitch_shift": 0.0,
    },
    # 8. Giọng Nam trầm ấm (Google TTS + Pitch Shift)
    "nam-tram-am": {
        "engine": "gtts",
        "voice_id": "gtts-male",
        "gender": "male",
        "desc": "Nam trầm ấm áp, thuyết phục cao (Đồ gia đình, Sản phẩm sức khỏe)",
        "pitch_shift": -2.8,
    },
    # 9. Giọng Nữ nhí nhảnh (Google TTS + Pitch Shift)
    "nu-nhi-nhanh": {
        "engine": "gtts",
        "voice_id": "gtts-young",
        "gender": "female",
        "desc": "Nữ trẻ trung, bắt tai, hợp tệp học sinh sinh viên Gen Z",
        "pitch_shift": 1.4,
    },
    # 10. Giọng Nam tin cậy (Google TTS + Pitch Shift)
    "nam-tin-cay": {
        "engine": "gtts",
        "voice_id": "gtts-deep",
        "gender": "male",
        "desc": "Nam chững chạc, uy tín, dễ chốt đơn đơn hàng giá trị cao",
        "pitch_shift": -4.0,
    },
}

# Alias tra cứu nhanh
VOICE_ALIASES = {
    "hoaimy": "nu-truyen-cam",
    "namminh": "nam-dut-khoat",
    "emma": "nu-hien-dai",
    "andrew": "nam-cong-nghe",
    "ava": "nu-tuoi-tan",
    "brian": "nam-soi-noi",
    "gtts": "nu-ro-chu",
}


def pick_voice(requested: str) -> tuple[str, dict]:
    """Chọn giọng đọc dựa trên yêu cầu (cụ thể, theo giới tính hoặc ngẫu nhiên)."""
    req = requested.strip().lower()

    # Xử lý alias
    if req in VOICE_ALIASES:
        req = VOICE_ALIASES[req]

    # Nếu chỉ định rõ 1 giọng trong danh sách
    if req in VOICE_PROFILES:
        return req, VOICE_PROFILES[req]

    # Nếu yêu cầu ngẫu nhiên giọng Nam
    if req in ("nam", "male"):
        male_keys = [k for k, v in VOICE_PROFILES.items() if v["gender"] == "male"]
        chosen = random.choice(male_keys)
        return chosen, VOICE_PROFILES[chosen]

    # Nếu yêu cầu ngẫu nhiên giọng Nữ
    if req in ("nu", "female"):
        female_keys = [k for k, v in VOICE_PROFILES.items() if v["gender"] == "female"]
        chosen = random.choice(female_keys)
        return chosen, VOICE_PROFILES[chosen]

    # Mặc định: Chọn ngẫu nhiên hoàn toàn (Random) trong 10 giọng
    chosen = random.choice(list(VOICE_PROFILES.keys()))
    return chosen, VOICE_PROFILES[chosen]


# ==============================================================================
# XỬ LÝ ÂM THANH: TĂNG TỐC ĐỘ, CẮT KHOẢNG LẶNG & DỊCH CAO ĐỘ (PITCH SHIFT)
# ==============================================================================
def post_process_audio(audio_path: str, speed_factor: float = 1.25, pitch_shift_semitones: float = 0.0, max_pause_sec: float = 0.18):
    """
    Tối ưu hóa âm thanh:
    1. Cắt tỉa khoảng lặng thừa giữa các câu.
    2. Tăng tốc độ nói bằng Phase Vocoder (pitch-preserved).
    3. Dịch cao độ nếu cần (để biến đổi giọng nam/nữ theo profile).
    """
    try:
        import soundfile as sf
        from scipy import signal
    except ImportError:
        print("[WARN] Thiếu soundfile hoặc scipy, bỏ qua khâu xử lý âm thanh hậu kỳ.")
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

        cur_data = np.concatenate(trimmed) if trimmed else data

        # 2. Dịch cao độ (Pitch Shift) nếu có cấu hình
        if pitch_shift_semitones != 0.0:
            p_factor = 2.0 ** (pitch_shift_semitones / 12.0)
            new_len = int(len(cur_data) / p_factor)
            cur_data = signal.resample(cur_data, new_len)
            speed_factor = speed_factor * p_factor

        # 3. Phase Vocoder time stretch
        if abs(speed_factor - 1.0) > 0.01:
            n_fft = 1024
            hop_length = n_fft // 4
            _, _, stft = signal.stft(cur_data, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)

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

            _, cur_data = signal.istft(stretched, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)

        sf.write(audio_path, cur_data, sr)
        new_duration = len(cur_data) / sr
        print(f"[POST-PROCESS] Tối ưu nhịp điệu hoàn tất:")
        print(f"  - Thời lượng gốc : {orig_duration:.2f}s")
        print(f"  - Thời lượng mới : {new_duration:.2f}s (chuẩn nhịp video ngắn cuốn hút)")
    except Exception as e:
        print(f"[WARN] Lỗi khi xử lý âm thanh hậu kỳ: {e}", file=sys.stderr)


# ==============================================================================
# CÁC ENGINE TẠO GIỌNG ĐỌC
# ==============================================================================
def synthesize_with_gtts(text: str, output_path: str, lang: str = "vi") -> bool:
    """Sinh giọng đọc bằng Google TTS (HTTPS, độ ổn định cực cao)."""
    try:
        from gtts import gTTS
        print(f"[TTS:gTTS] Đang tạo giọng đọc qua Google TTS...")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[TTS:gTTS] Tạo âm thanh thành công ({os.path.getsize(output_path)} bytes)")
            return True
    except Exception as e:
        print(f"[TTS:gTTS] Lỗi: {e}", file=sys.stderr)
    return False


async def synthesize_with_edge(text: str, output_path: str, voice_id: str, rate: str = "+25%") -> bool:
    """Sinh giọng đọc bằng Edge TTS (có timeout 5s để chuyển fallback nhanh chóng)."""
    try:
        import edge_tts
        print(f"[TTS:Edge] Đang kết nối Edge TTS (Voice: {voice_id}, Tốc độ: {rate})...")
        communicate = edge_tts.Communicate(text=text, voice=voice_id, rate=rate)
        await asyncio.wait_for(communicate.save(output_path), timeout=6.0)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[TTS:Edge] Tạo âm thanh thành công ({os.path.getsize(output_path)} bytes)")
            return True
    except asyncio.TimeoutError:
        print("[TTS:Edge] Microsoft phản hồi quá chậm (> 6s), chuyển sang fallback...")
    except Exception as e:
        print(f"[TTS:Edge] Không nhận được audio từ Microsoft: {e}")
    return False


# ==============================================================================
# HÀM CHÍNH
# ==============================================================================
async def generate_voice(
    text_path: str,
    output_path: str,
    voice_request: str = "random",
    speed: float = 1.25,
    engine_override: str = "auto"
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

    # Chọn giọng đọc (random hoặc chỉ định)
    voice_key, profile = pick_voice(voice_request)

    rate_percent = int((speed - 1.0) * 100)
    rate_str = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"

    print("=" * 70)
    print(f"🎬 BẮT ĐẦU TẠO GIỌNG ĐỌC CHO VIDEO AFFILIATE")
    print(f"  - File văn bản    : {text_path}")
    print(f"  - File âm thanh   : {output_path}")
    print(f"  - Giọng đọc chọn  : [{voice_key}] - {profile['desc']}")
    print(f"  - Tốc độ đọc      : {speed}x (+{rate_percent}%)")
    print("=" * 70)

    success = False
    used_engine = profile["engine"] if engine_override == "auto" else engine_override

    # 1. Thử với Edge TTS nếu profile thuộc edge hoặc engine_override = edge
    if used_engine == "edge" or engine_override == "edge":
        voice_id = profile["voice_id"] if profile["engine"] == "edge" else "vi-VN-NamMinhNeural"
        success = await synthesize_with_edge(text, output_path, voice_id=voice_id, rate=rate_str)

    # 2. Fallback sang Google TTS nếu Edge không thành công hoặc engine là gtts
    if not success:
        if used_engine == "edge":
            print("[INFO] Tự động kích hoạt Google TTS (Fallback) để đảm bảo thành công...")
        success = synthesize_with_gtts(text, output_path, lang="vi")

    # 3. Tối ưu hóa nhịp điệu (cắt khoảng lặng + chuẩn hóa tốc độ) cho tất cả audio
    if success:
        post_process_audio(
            output_path,
            speed_factor=speed,
            pitch_shift_semitones=profile.get("pitch_shift", 0.0)
        )

    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"\n🎉 HOÀN THÀNH XUẤT SẮC!")
        print(f"  - File âm thanh : {output_path}")
        print(f"  - Dung lượng    : {file_size_kb:.1f} KB")
        print(f"  - Giọng đọc     : {voice_key} ({profile['desc']})")
    else:
        print(f"\n[ERROR] Không thể tạo file audio! Vui lòng kiểm tra lại kết nối mạng.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Chuyển file voice.txt thành audio voice.mp3 với kho giọng đọc tiếng Việt đa dạng cho video Affiliate."
    )
    parser.add_argument("--input", "-i", required=False, help="Đường dẫn file voice.txt đầu vào")
    parser.add_argument("--output", "-o", required=False, help="Đường dẫn file voice.mp3 đầu ra")
    parser.add_argument(
        "--voice", "-v", default="random",
        help="Giọng đọc: 'random' (mặc định ngẫu nhiên trong 10 giọng), 'nam' (ngẫu nhiên giọng nam), 'nu' (ngẫu nhiên giọng nữ), hoặc tên giọng cụ thể (ví dụ: 'nam-dut-khoat', 'nu-truyen-cam', 'nu-hien-dai', 'nam-cong-nghe', 'nam-tram-am', 'nu-nhi-nhanh'...)"
    )
    parser.add_argument(
        "--speed", "-s", type=float, default=1.25,
        help="Tốc độ nói (Mặc định: 1.25x - tăng 25%% phù hợp nhịp điệu nhanh, dứt khoát của video ngắn)"
    )
    parser.add_argument(
        "--engine", "-e", choices=["auto", "edge", "gtts"], default="auto",
        help="Engine TTS: 'auto' (thông minh tự chọn và fallback), 'edge', hoặc 'gtts'"
    )
    parser.add_argument(
        "--list-voices", action="store_true",
        help="Hiển thị danh sách 10 giọng đọc tiếng Việt có sẵn và thoát"
    )

    args = parser.parse_args()

    if args.list_voices:
        print("\n=== DANH SÁCH 10 GIỌNG ĐỌC TIẾNG VIỆT CHO VIDEO AFFILIATE ===")
        for key, p in VOICE_PROFILES.items():
            print(f"- {key:<15} ({p['gender'].upper()}): {p['desc']}")
        print("\nCách dùng:")
        print("  python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice random")
        print("  python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice nam")
        print("  python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice nu\n")
        return

    if not args.input or not args.output:
        parser.error("Vui lòng cung cấp cả --input và --output để tạo file âm thanh.")

    asyncio.run(generate_voice(
        text_path=args.input,
        output_path=args.output,
        voice_request=args.voice,
        speed=args.speed,
        engine_override=args.engine
    ))


if __name__ == "__main__":
    main()
