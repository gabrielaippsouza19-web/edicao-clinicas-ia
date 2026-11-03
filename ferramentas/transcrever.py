"""Transcreve um audio/video com tempos por palavra (faster-whisper, local).

Uso: transcrever.py <arquivo> <saida.json> [modelo]
O audio e convertido para WAV 16 kHz mono via FFmpeg (o decoder do PyAV
instalado e incompativel com esta versao do faster-whisper).
O modelo "medium" (~1,5 GB) e baixado na primeira execucao.
"""
import json
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from faster_whisper import WhisperModel

arquivo, saida = sys.argv[1], sys.argv[2]
modelo = sys.argv[3] if len(sys.argv) > 3 else "medium"

fd, tmp = tempfile.mkstemp(suffix=".wav")
os.close(fd)
# first_pts=0 preenche com silencio o atraso inicial do audio (comum em .MOV de
# iPhone, onde o audio comeca ~0,7 s depois do video), alinhando os tempos ao video.
subprocess.run(
    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", arquivo,
     "-vn", "-af", "aresample=async=1:first_pts=0",
     "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", tmp],
    check=True,
)
with wave.open(tmp, "rb") as w:
    audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
os.remove(tmp)
audio = audio.astype(np.float32) / 32768.0

model = WhisperModel(modelo, device="cpu", compute_type="int8")
usar_vad = os.environ.get("TRANSCREVER_VAD", "0") == "1"
segments, info = model.transcribe(
    audio, language=os.environ.get("TRANSCREVER_IDIOMA", "pt"), word_timestamps=True,
    vad_filter=usar_vad, beam_size=5, condition_on_previous_text=False,
)

resultado = {"idioma": info.language, "duracao": info.duration, "segmentos": []}
for s in segments:
    resultado["segmentos"].append(
        {
            "inicio": round(s.start, 2),
            "fim": round(s.end, 2),
            "texto": s.text.strip(),
            "palavras": [
                {"p": w.word.strip(), "i": round(w.start, 2), "f": round(w.end, 2)}
                for w in (s.words or [])
            ],
        }
    )
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}", flush=True)

with open(saida, "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=1)
