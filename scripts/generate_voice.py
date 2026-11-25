#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script chuyển văn bản thành giọng đọc (Text-to-Speech) chuyên dụng cho video Affiliate (v2.0 Pro).
Tính năng nổi bật:
- An toàn 100% với môi trường có Symantec / Firewall (chỉ dùng nguồn chính thống Google & Microsoft).
- Kho 12 giọng đọc tiếng Việt đa phong cách (bao gồm phong cách TikTok Review, Chị Google, MC Chốt đơn...).
- Cơ chế RANDOM giọng ngẫu nhiên khi sản xuất hàng loạt video.
- Bộ Audio Mastering chuẩn TikTok: Cắt khoảng lặng chết + Phase Vocoder tăng tốc + EQ Vocal Boost + Chuẩn hóa âm lượng -1 dBFS.
"""

import argparse
import asyncio
import os
import random
import sys
import numpy as np


# ==============================================================================
# BẢNG ĐẶC TẢ 12 PROFILE GIỌNG ĐỌC TIẾNG VIỆT CHO VIDEO AFFILIATE
# ==============================================================================
VOICE_PROFILES = {
    # --- NHÓM GIỌNG ADAM & TIKTOK TRENDING (DỄ LÊN XU HƯỚNG) ---
    "adam-elevenlabs": {
        "engine": "elevenlabs",
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam chính chủ ElevenLabs
        "gender": "male",
        "desc": "🔥 Adam (ElevenLabs Chính chủ): Nam trầm dày uy lực, giữ chân người xem cực tốt (cần ElevenLabs Key)",
        "pitch_shift": 0.0,
        "default_speed": 1.15,
        "eq_boost": 0.15,
    },
    "tiktok-adam-pro": {
        "engine": "edge",
        "voice_id": "vi-VN-NamMinhNeural",
        "gender": "male",
        "desc": "🎙️ Adam Style (Miễn phí): Nam trầm dày, ấm áp, nhấn bass + clarity kiểu storyteller TikTok",
        "pitch_shift": -3.2,
        "default_speed": 1.22,
        "eq_boost": 0.28,
        "warm_boost": 0.25,
    },
    "tiktok-co-gai": {
        "engine": "edge",
        "voice_id": "vi-VN-HoaiMyNeural",
        "gender": "female",
        "desc": "Phong cách TikTok Cô gái hoạt ngôn: sáng rõ, cuốn hút (Gia dụng, Mỹ phẩm)",
        "pitch_shift": 0.6,
        "default_speed": 1.28,
        "eq_boost": 0.28,
    },
    "tiktok-thanh-nien": {
        "engine": "edge",
        "voice_id": "vi-VN-NamMinhNeural",
        "gender": "male",
        "desc": "Phong cách TikTok Thanh niên tự tin: dứt khoát, rõ ràng (Công nghệ, Tiện ích)",
        "pitch_shift": -1.8,
        "default_speed": 1.25,
        "eq_boost": 0.25,
    },
    "tiktok-chi-google": {
        "engine": "gtts",
        "voice_id": "gtts-standard",
        "gender": "female",
        "desc": "Phong cách Chị Google huyền thoại: nhịp nhanh, tròn vành rõ chữ (Review tổng hợp)",
        "pitch_shift": 0.0,
        "default_speed": 1.28,
        "eq_boost": 0.30,
    },
    "tiktok-genz": {
        "engine": "gtts",
        "voice_id": "gtts-young",
        "gender": "female",
        "desc": "Phong cách Gen Z tươi trẻ, nhí nhảnh, năng động (Đồ ăn vặt, Thời trang, Phụ kiện)",
        "pitch_shift": 1.4,
        "default_speed": 1.28,
        "eq_boost": 0.28,
    },
    "tiktok-mc-chot-don": {
        "engine": "gtts",
        "voice_id": "gtts-male",
        "gender": "male",
        "desc": "Phong cách MC trầm ấm, thuyết phục cao (Đồ gia đình, Sản phẩm giá trị cao)",
        "pitch_shift": -2.8,
        "default_speed": 1.22,
        "eq_boost": 0.22,
    },

    # --- NHÓM GIỌNG REVIEW CHUYÊN SÂU & ĐA DẠNG ---
    "nu-truyen-cam": {
        "engine": "edge",
        "voice_id": "vi-VN-HoaiMyNeural",
        "gender": "female",
        "desc": "Nữ miền Bắc ngọt ngào, truyền cảm (Mẹ & Bé, Skincare, Chăm sóc cá nhân)",
        "pitch_shift": 0.0,
        "default_speed": 1.22,
        "eq_boost": 0.20,
    },
    "nam-dut-khoat": {
        "engine": "edge",
        "voice_id": "vi-VN-NamMinhNeural",
        "gender": "male",
        "desc": "Nam miền Bắc dứt khoát, tin cậy (Dụng cụ sửa chữa, Đồ gia dụng thông minh)",
        "pitch_shift": 0.0,
        "default_speed": 1.25,
        "eq_boost": 0.25,
    },
    "nu-hien-dai": {
        "engine": "edge",
        "voice_id": "en-US-EmmaMultilingualNeural",
        "gender": "female",
        "desc": "Nữ hiện đại, phát âm từ mượn mượt mà (Decor phòng, Phụ kiện tối giản)",
        "pitch_shift": 0.0,
        "default_speed": 1.25,
        "eq_boost": 0.25,
    },
    "nam-cong-nghe": {
        "engine": "edge",
        "voice_id": "en-US-AndrewMultilingualNeural",
        "gender": "male",
        "desc": "Nam trẻ trung chuyên review công nghệ (Tai nghe, Sạc dự phòng, Smart home)",
        "pitch_shift": -1.2,
        "default_speed": 1.25,
        "eq_boost": 0.25,
    },
    "nu-tuoi-tan": {
        "engine": "edge",
        "voice_id": "en-US-AvaMultilingualNeural",
        "gender": "female",
        "desc": "Nữ tươi tắn, dễ thương (Mỹ phẩm, Phụ kiện tóc, Túi xách)",
        "pitch_shift": 0.8,
        "default_speed": 1.26,
        "eq_boost": 0.25,
    },
    "nam-soi-noi": {
        "engine": "edge",
        "voice_id": "en-US-BrianMultilingualNeural",
        "gender": "male",
        "desc": "Nam hào hứng, nhịp điệu lôi cuốn (Đồ chơi, Phụ kiện xe, Thể thao)",
        "pitch_shift": -1.5,
        "default_speed": 1.26,
        "eq_boost": 0.28,
    },
    "nam-tin-cay": {
        "engine": "gtts",
        "voice_id": "gtts-deep",
        "gender": "male",
        "desc": "Nam giọng trầm chững chạc, uy tín (Thiết bị sức khỏe, Điện máy)",
        "pitch_shift": -3.8,
        "default_speed": 1.20,
        "eq_boost": 0.22,
    },
}

VOICE_ALIASES = {
    "hoaimy": "nu-truyen-cam",
    "namminh": "nam-dut-khoat",
    "emma": "nu-hien-dai",
    "andrew": "nam-cong-nghe",
    "ava": "nu-tuoi-tan",
    "brian": "nam-soi-noi",
    "chigoogle": "tiktok-chi-google",
    "gtts": "tiktok-chi-google",
    "cogai": "tiktok-co-gai",
    "thanhnien": "tiktok-thanh-nien",
    "genz": "tiktok-genz",
    "adam": "adam-elevenlabs",
    "adam-free": "tiktok-adam-pro",
}


def pick_voice(requested: str) -> tuple[str, dict]:
    """Chọn giọng đọc dựa trên yêu cầu (cụ thể, theo giới tính hoặc ngẫu nhiên)."""
    req = requested.strip().lower()

    if req in VOICE_ALIASES:
        req = VOICE_ALIASES[req]

    if req in VOICE_PROFILES:
        return req, VOICE_PROFILES[req]

    if req in ("nam", "male"):
        male_keys = [k for k, v in VOICE_PROFILES.items() if v["gender"] == "male"]
        chosen = random.choice(male_keys)
        return chosen, VOICE_PROFILES[chosen]

    if req in ("nu", "female"):
        female_keys = [k for k, v in VOICE_PROFILES.items() if v["gender"] == "female"]
        chosen = random.choice(female_keys)
        return chosen, VOICE_PROFILES[chosen]

    if req == "tiktok":
        tiktok_keys = [k for k in VOICE_PROFILES if k.startswith("tiktok-")]
        chosen = random.choice(tiktok_keys)
        return chosen, VOICE_PROFILES[chosen]

    chosen = random.choice(list(VOICE_PROFILES.keys()))
    return chosen, VOICE_PROFILES[chosen]


# ==============================================================================
# AUDIO MASTERING: DEAD AIR TRIMMING + PITCH/SPEED + EQ VOCAL BOOST + NORMALIZE
# ==============================================================================
def post_process_audio(
    audio_path: str,
    speed_factor: float = 1.25,
    pitch_shift_semitones: float = 0.0,
    eq_boost: float = 0.25,
    warm_boost: float = 0.0,
    max_pause_sec: float = 0.16,
):
    """
    Hậu kỳ âm thanh chuẩn TikTok/Shopee Video:
    1. Cắt tỉa khoảng lặng thừa (dead air) xuống tối đa max_pause_sec.
    2. Dịch cao độ (Pitch Shift) theo profile giọng nếu cần.
    3. Tăng tốc độ nói bằng Phase Vocoder (pitch-preserved).
    4. High-pass filter (85Hz) + Vocal Presence Boost (2.2kHz - 5kHz) cho tiếng thoát nền nhạc.
    5. Chuẩn hóa âm lượng (Peak Normalization về -1.0 dBFS).
    """
    try:
        import soundfile as sf
        from scipy import signal
    except ImportError:
        print("[WARN] Thiếu soundfile hoặc scipy, bỏ qua khâu hậu kỳ âm thanh.")
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
            if np.max(np.abs(c)) < threshold:
                silent_count += 1
                if silent_count <= max_silent_chunks:
                    trimmed.append(c)
            else:
                silent_count = 0
                trimmed.append(c)

        cur_data = np.concatenate(trimmed) if trimmed else data

        # 2. Dịch cao độ (Pitch Shift) nếu có
        eff_speed = speed_factor
        if pitch_shift_semitones != 0.0:
            p_factor = 2.0 ** (pitch_shift_semitones / 12.0)
            new_len = int(len(cur_data) / p_factor)
            cur_data = signal.resample(cur_data, new_len)
            eff_speed = speed_factor * p_factor

        # 3. Phase Vocoder time stretch
        if abs(eff_speed - 1.0) > 0.01:
            n_fft = 1024
            hop_length = n_fft // 4
            _, _, stft = signal.stft(cur_data, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)

            time_steps = np.arange(0, stft.shape[1] - 1, eff_speed)
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

        # 4. Vocal Clarity EQ (High-pass 85Hz + Warm Low-Mid nếu cần + Presence Boost 2.2kHz-5kHz)
        sos_hp = signal.butter(2, 85, btype="highpass", fs=sr, output="sos")
        cur_data = signal.sosfilt(sos_hp, cur_data)

        if warm_boost > 0:
            sos_warm = signal.butter(2, [140, 320], btype="bandpass", fs=sr, output="sos")
            cur_data = cur_data + warm_boost * signal.sosfilt(sos_warm, cur_data)

        if eq_boost > 0:
            sos_bp = signal.butter(2, [2200, 5000], btype="bandpass", fs=sr, output="sos")
            presence = signal.sosfilt(sos_bp, cur_data)
            cur_data = cur_data + eq_boost * presence

        # 5. Peak Normalization (-1.0 dBFS ~ 0.891)
        max_val = np.max(np.abs(cur_data))
        if max_val > 0:
            cur_data = cur_data * (0.891 / max_val)

        sf.write(audio_path, cur_data, sr)
        new_duration = len(cur_data) / sr
        print(f"[MASTERING] Hậu kỳ âm thanh chuẩn TikTok hoàn tất:")
        print(f"  - Thời lượng gốc : {orig_duration:.2f}s -> Mới: {new_duration:.2f}s")
        print(f"  - Xử lý          : Dead-air trim + Vocal EQ Boost + Normalize -1 dBFS")
    except Exception as e:
        print(f"[WARN] Lỗi khi hậu kỳ âm thanh: {e}", file=sys.stderr)


# ==============================================================================
# CÁC ENGINE TẠO GIỌNG ĐỌC (AN TOÀN TUYỆT ĐỐI VỚI SYMANTEC)
# ==============================================================================
def synthesize_with_elevenlabs(text: str, output_path: str, voice_id: str, api_key: str = "") -> bool:
    """Sinh giọng đọc qua ElevenLabs REST API (mặc định giọng Adam - eleven_multilingual_v2)."""
    key = (api_key or os.environ.get("ELEVENLABS_API_KEY") or "").strip()
    if not key:
        print("[TTS:ElevenLabs] Chưa có ELEVENLABS_API_KEY, chuyển sang giọng Adam Style miễn phí...")
        return False
    try:
        import urllib.request
        import json

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        payload = json.dumps({
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.80,
                "style": 0.35,
                "use_speaker_boost": True,
            },
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "xi-api-key": key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            method="POST",
        )
        print(f"[TTS:ElevenLabs] Đang tạo giọng Adam chính chủ qua ElevenLabs...")
        with urllib.request.urlopen(req, timeout=25) as resp:
            audio_bytes = resp.read()
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[TTS:ElevenLabs] Thành công! ({os.path.getsize(output_path)} bytes)")
            return True
    except Exception as e:
        print(f"[TTS:ElevenLabs] Lỗi gọi ElevenLabs API: {e}", file=sys.stderr)
    return False


def synthesize_with_gtts(text: str, output_path: str, lang: str = "vi") -> bool:
    """Sinh giọng đọc bằng Google TTS (HTTPS chuẩn, không bị Symantec chặn)."""
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


async def synthesize_with_edge(text: str, output_path: str, voice_id: str, rate: str = "+0%") -> bool:
    """Sinh giọng đọc bằng Edge TTS (timeout 6s để tự chuyển fallback nếu mạng nghẽn)."""
    try:
        import edge_tts
        print(f"[TTS:Edge] Đang kết nối Edge TTS (Voice: {voice_id})...")
        communicate = edge_tts.Communicate(text=text, voice=voice_id, rate=rate)
        await asyncio.wait_for(communicate.save(output_path), timeout=6.0)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[TTS:Edge] Tạo âm thanh thành công ({os.path.getsize(output_path)} bytes)")
            return True
    except asyncio.TimeoutError:
        print("[TTS:Edge] Microsoft phản hồi chậm (> 6s), chuyển sang fallback...")
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
    speed: float = None,
    engine_override: str = "auto",
    elevenlabs_key: str = "",
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

    voice_key, profile = pick_voice(voice_request)
    # Nếu random trúng adam-elevenlabs mà chưa có key, tự chuyển sang tiktok-adam-pro miễn phí
    has_el_key = bool((elevenlabs_key or os.environ.get("ELEVENLABS_API_KEY") or "").strip())
    if voice_request.strip().lower() in ("random", "nam", "male") and voice_key == "adam-elevenlabs" and not has_el_key:
        voice_key = "tiktok-adam-pro"
        profile = VOICE_PROFILES[voice_key]

    target_speed = speed if speed is not None else profile.get("default_speed", 1.25)

    print("=" * 72)
    print(f"🎬 BẮT ĐẦU TẠO GIỌNG ĐỌC CHO VIDEO AFFILIATE (v2.3)")
    print(f"  - File văn bản    : {text_path}")
    print(f"  - File âm thanh   : {output_path}")
    print(f"  - Giọng đọc chọn  : [{voice_key}] - {profile['desc']}")
    print(f"  - Tốc độ mục tiêu : {target_speed}x")
    print("=" * 72)

    success = False
    used_engine = profile["engine"] if engine_override == "auto" else engine_override

    if used_engine == "elevenlabs":
        success = synthesize_with_elevenlabs(text, output_path, voice_id=profile["voice_id"], api_key=elevenlabs_key)
        if not success:
            print("[INFO] Tự động chuyển sang giọng Adam Style (Edge/gTTS + Warm Mastering) miễn phí...")
            profile = VOICE_PROFILES["tiktok-adam-pro"]
            used_engine = profile["engine"]

    if not success and (used_engine == "edge" or engine_override == "edge"):
        voice_id = profile["voice_id"] if profile["engine"] == "edge" else "vi-VN-NamMinhNeural"
        success = await synthesize_with_edge(text, output_path, voice_id=voice_id, rate="+0%")

    if not success:
        if used_engine == "edge":
            print("[INFO] Tự động kích hoạt Google TTS (Fallback) để đảm bảo thành công...")
        success = synthesize_with_gtts(text, output_path, lang="vi")

    if success:
        if used_engine == "elevenlabs":
            # Giữ nguyên chất giọng gốc của ElevenLabs Adam, chỉ chuẩn hóa tốc độ nhẹ nếu cần
            post_process_audio(
                output_path,
                speed_factor=target_speed,
                pitch_shift_semitones=0.0,
                eq_boost=profile.get("eq_boost", 0.15),
                warm_boost=0.0,
            )
        else:
            effective_pitch = profile.get("pitch_shift", 0.0)
            if used_engine == "edge" and os.path.exists(output_path) and profile["engine"] == "edge":
                effective_pitch = effective_pitch * 0.5

            post_process_audio(
                output_path,
                speed_factor=target_speed,
                pitch_shift_semitones=effective_pitch,
                eq_boost=profile.get("eq_boost", 0.25),
                warm_boost=profile.get("warm_boost", 0.0),
            )

    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"\n🎉 HOÀN THÀNH XUẤT SẮC!")
        print(f"  - File âm thanh : {output_path}")
        print(f"  - Dung lượng    : {file_size_kb:.1f} KB")
        print(f"  - Giọng đọc     : {voice_key}")
    else:
        print(f"\n[ERROR] Không thể tạo file audio! Vui lòng kiểm tra lại kết nối mạng.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Chuyển file voice.txt thành audio voice.mp3 chuẩn TikTok Mastering (v2.0 Pro)."
    )
    parser.add_argument("--input", "-i", required=False, help="Đường dẫn file voice.txt đầu vào")
    parser.add_argument("--output", "-o", required=False, help="Đường dẫn file voice.mp3 đầu ra")
    parser.add_argument(
        "--voice", "-v", default="random",
        help="Giọng đọc: 'random' (mặc định ngẫu nhiên 12 giọng), 'tiktok' (ngẫu nhiên phong cách TikTok), 'nam', 'nu', hoặc tên cụ thể"
    )
    parser.add_argument(
        "--speed", "-s", type=float, default=None,
        help="Tốc độ nói (Mặc định tự động tối ưu theo từng profile từ 1.22x - 1.28x)"
    )
    parser.add_argument(
        "--engine", "-e", choices=["auto", "edge", "gtts"], default="auto",
        help="Engine TTS: 'auto' (khuyến nghị), 'edge', hoặc 'gtts'"
    )
    parser.add_argument(
        "--list-voices", action="store_true",
        help="Hiển thị danh sách 12 profile giọng đọc tiếng Việt và thoát"
    )

    args = parser.parse_args()

    if args.list_voices:
        print("\n=== KHO 12 GIỌNG ĐỌC TIẾNG VIỆT CHUẨN TIKTOK / AFFILIATE ===")
        for key, p in VOICE_PROFILES.items():
            print(f"- {key:<20} ({p['gender'].upper():<6}) [{p['default_speed']}x]: {p['desc']}")
        print("\nCách dùng:")
        print("  python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice random")
        print("  python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice tiktok")
        print("  python scripts/generate_voice.py --input voice.txt --output voice.mp3 --voice nam\n")
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
