#!/usr/bin/env python3
"""Build an offline stock Mandarin voice track fitted to verified story beats."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import wave

import numpy as np

RATE = 48000


def decode(path, speed=1):
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(path), "-af", f"atempo={speed:.6f}",
        "-ar", str(RATE), "-ac", "1", "-f", "f32le", "pipe:1"
    ])
    a = np.frombuffer(raw, dtype="<f4").copy()
    pos = np.flatnonzero(np.abs(a) > .002)
    if not len(pos):
        raise ValueError("A synthesized beat is silent")
    return a[:pos[-1]+1+round(.055*RATE)]


def track(manifest, voice, cfg, out, max_speed):
    beats = json.loads(manifest.read_text(encoding="utf-8"))["beats"]
    out.parent.mkdir(parents=True, exist_ok=True)
    timing = []
    cursor = 0
    with TemporaryDirectory(prefix="news-stock-voice-") as temp:
        segments = []
        for i, beat in enumerate(beats, 1):
            text = beat.get("narration", beat.get("caption", "")).strip()
            if not text:
                raise ValueError(f"Beat {i}: specify narration or caption")
            duration = float(beat["duration"])
            if not 1 <= duration <= 60:
                raise ValueError(f"Beat {i}: invalid duration")
            file = Path(temp) / f"{i}.wav"
            with wave.open(str(file), "wb") as wav:
                voice.synthesize_wav(text, wav, syn_config=cfg)
            samples = decode(file)
            lead = .12 if i == 1 else .08
            room = duration - lead - .14
            pace = max(1, (len(samples)/RATE) / room)
            if pace > 1:
                pace *= 1.025
                if pace > max_speed:
                    raise ValueError(f"Beat {i}: needs {pace:.2f}× speed; shorten narration or extend beat")
                samples = decode(file, pace)
            lead_samples = round(lead * RATE)
            stem = np.zeros(round(duration * RATE), dtype=np.float32)
            if len(samples) + lead_samples > len(stem):
                raise ValueError(f"Beat {i}: narration does not fit; shorten or extend")
            n = min(len(samples)//2, round(.012*RATE))
            if n:
                samples[:n] *= np.linspace(0,1,n)
                samples[-n:] *= np.linspace(1,0,n)
            stem[lead_samples:lead_samples+len(samples)] = np.clip(samples*.87, -.97, .97)
            segments.append(stem)
            timing.append({
                "beat": i, "start": round(cursor/RATE + lead, 3),
                "spoken_seconds": round(len(samples)/RATE, 3), "max_tempo_multiplier": round(pace, 3)
            })
            cursor += len(stem)
        with wave.open(str(out), "wb") as wav:
            wav.setparams((1,2,RATE,0,"NONE","not compressed"))
            wav.writeframes(np.int16(np.concatenate(segments)*32767).tobytes())
    print(json.dumps(timing, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--data", type=Path, required=True,
                   help="Directory containing unpacked g2pW/ and offline tokenizer configured in g2pW/config.py")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-speed", type=float, default=1.32)
    a = p.parse_args()
    if not 1 <= a.max_speed <= 1.5:
        p.error("--max-speed must be between 1 and 1.5")
    model = a.model.resolve()
    data = a.data.resolve()
    if not model.is_file() or not model.with_suffix(".onnx.json").is_file():
        p.error("model .onnx and .onnx.json files are required")
    for name in ("g2pw.onnx", "config.py", "version", "MONOPHONIC_CHARS.txt", "POLYPHONIC_CHARS.txt"):
        if not (data/"g2pW"/name).is_file():
            p.error(f"Missing trusted g2pW local dependency: {name}")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import onnxruntime
    from piper import PiperVoice, SynthesisConfig
    from story_preflight import validate
    onnxruntime.disable_telemetry_events()
    validate(json.loads(a.manifest.read_text(encoding="utf-8")))
    voice = PiperVoice.load(model, download_dir=data)
    track(a.manifest, voice, SynthesisConfig(length_scale=.94), a.out, a.max_speed)

if __name__ == "__main__":
    main()
