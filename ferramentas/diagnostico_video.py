"""Mede um bruto antes de editar e aponta o que pode dar errado.

Uso: diagnostico_video.py <video>
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import medir_audio, sondar, stream  # noqa: E402

video = sys.argv[1]
dados = sondar(video)
v, a = stream(dados, "video"), stream(dados, "audio")
avisos = []

larg, alt = int(v["width"]), int(v["height"])
for lado in v.get("side_data_list", []):
    if abs(int(lado.get("rotation", 0))) in (90, 270):
        larg, alt = alt, larg
num, den = v["r_frame_rate"].split("/")
fps = float(num) / float(den)
num2, den2 = v["avg_frame_rate"].split("/")
fps_medio = float(num2) / float(den2) if float(den2) else 0
print(f"arquivo: {Path(video).name}")
print(f"duracao: {float(dados['format']['duration']):.2f} s")
print(f"imagem: {larg}x{alt}, {v['codec_name']}, {fps_medio:.2f} fps (nominal {fps:.2f})")
print(f"cor: {v.get('color_transfer', '?')} / {v.get('color_primaries', '?')} / {v.get('pix_fmt')}")

if alt < 1280:
    avisos.append("resolucao baixa (provavel WhatsApp): peca o arquivo original do celular")
if larg >= alt:
    avisos.append("video horizontal: o estilo e vertical e as bordas vao ser cortadas. Confira o enquadramento")
elif abs(larg / alt - 9 / 16) > 0.02:
    avisos.append("proporcao diferente de 9:16: as bordas vao ser cortadas para cobrir o quadro")
if abs(fps - fps_medio) > 0.5:
    avisos.append("taxa de quadros variavel: normal em celular, as ferramentas convertem para 30 fps")
if v.get("color_transfer") in ("smpte2084", "arib-std-b67") or v.get("color_primaries") == "bt2020":
    avisos.append("HDR: as ferramentas convertem para SDR. Confira a cor da pele nos quadros de revisao")

if not a:
    avisos.append("SEM AUDIO: nao da para cortar nem transcrever")
else:
    atraso = float(a.get("start_time", 0)) - float(v.get("start_time", 0))
    print(f"audio: {a['codec_name']}, {a.get('sample_rate')} Hz, comeca {atraso:+.2f} s em relacao ao video")
    if abs(atraso) > 0.05:
        avisos.append(f"audio deslocado em {atraso:+.2f} s (comum em .MOV de iPhone): transcrever.py ja alinha")
    lufs, pico = medir_audio(video)
    print(f"volume: {lufs:.1f} LUFS, pico {pico:.1f} dBFS")
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", video, "-vn", "-af",
         "highpass=f=80,silencedetect=n=-35dB:d=0.2", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    pausas = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", log)]
    longas = [p for p in pausas if p >= 0.7]
    print(f"pausas a -35 dB: {len(pausas)}, das quais {len(longas)} com 0,7 s ou mais")
    if not pausas:
        avisos.append("nenhum silencio a -35 dB: ruido de fundo alto. Tente montar_edl com --limiar -30")
    if pico >= -0.5:
        avisos.append("audio perto de estourar: ouca o bruto antes de seguir")

print("\nAVISOS:" if avisos else "\nsem avisos")
for x in avisos:
    print(" -", x)
