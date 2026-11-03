"""Renderiza um video do cliente, masteriza o audio e entrega em entregas/.

Uso: renderizar.py <pasta_cliente> <id_video> <versao> [--capa] [--conferir] [--whisper medium]
                   [--descartar ini-fim,...]

Master: ganho fixo + limitador para -14 LUFS e cerca de -1 dBTP, nunca loudnorm.
--capa      gera tambem a capa (jpg e png), se o roteiro tiver capa.
--conferir  transcreve o final e compara com o bruto: cortes em silencio e nenhuma palavra perdida.
Nao sobrescreve entrega existente: cada rodada recebe uma versao nova.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import medir_audio  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("cliente")
ap.add_argument("video")
ap.add_argument("versao")
ap.add_argument("--capa", action="store_true")
ap.add_argument("--conferir", action="store_true")
ap.add_argument("--whisper", default="medium")
ap.add_argument("--descartar", default="")
args = ap.parse_args()

raiz = Path(args.cliente).resolve()
projeto = raiz / "projeto"
entregas = raiz / "entregas"
entregas.mkdir(exist_ok=True)
base = f"{raiz.name}-{args.video}-{args.versao}"
final = entregas / f"{base}.mp4"
if final.exists():
    raise SystemExit(f"{final} ja existe. Use uma versao nova.")
npx = shutil.which("npx")
tmp = entregas / f"_tmp_{base}.mp4"

subprocess.run(
    [npx, "remotion", "render", args.video, str(tmp), "--codec=h264", "--crf=17",
     "--audio-codec=aac", "--audio-bitrate=256k", "--log=error"],
    cwd=projeto, check=True,
)
lufs, _ = medir_audio(tmp)
ganho = -14 - lufs + 0.2
subprocess.run(
    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp), "-c:v", "copy", "-af",
     f"volume={ganho:.2f}dB,alimiter=limit=0.88:attack=5:release=80:level=disabled",
     "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(final)],
    check=True,
)
tmp.unlink()
lufs, pico = medir_audio(final)
print(f"entrega: {final}\naudio: {lufs:.1f} LUFS, pico verdadeiro {pico:.1f} dBFS")
if not -14.7 <= lufs <= -13.3 or pico > -0.7:
    print("ATENCAO: audio fora do alvo (-14 LUFS, ate -1 dBTP). Ouca e ajuste a trilha.")

if args.capa:
    png = entregas / f"{base}-capa.png"
    subprocess.run(
        [npx, "remotion", "still", f"{args.video}-capa", str(png), "--log=error"],
        cwd=projeto, check=True,
    )
    Image.open(png).convert("RGB").save(png.with_suffix(".jpg"), quality=93)
    print("capa:", png.with_suffix(".jpg"))

if args.conferir:
    analise = raiz / "analise" / args.video
    transcricao = analise / f"transcricao-final-{args.versao}.json"
    aqui = Path(__file__).resolve().parent
    subprocess.run([sys.executable, aqui / "transcrever.py", final, transcricao, args.whisper], check=True)
    subprocess.run(
        [sys.executable, aqui / "conferir_cortes.py", projeto / "src" / "videos" / args.video / "edl.json",
         analise / "transcricao.json", transcricao, args.descartar],
        check=True,
    )
    duracao = json.load(open(projeto / "src" / "videos" / args.video / "edl.json", encoding="utf-8"))["duracao"]
    print(f"fala editada: {duracao:.2f} s")
