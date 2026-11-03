"""Funcoes comuns das ferramentas do kit."""
import json
import re
import subprocess
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
MODELO_RVM = KIT / "modelos" / "rvm_mobilenetv3_fp32.onnx"
TEMPLATE = KIT / "template"
W, H, FPS = 1080, 1920, 30

# Cobre o quadro sem deformar: bruto fora de 9:16 perde as bordas, nunca fica achatado.
CONFORMAR = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={FPS}"
# Gravacao HDR de celular (HLG/PQ) convertida para SDR antes de qualquer outro filtro.
TONEMAP = (
    "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
    "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
)


def rodar(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def sondar(arquivo):
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(arquivo)],
        capture_output=True, text=True, check=True, encoding="utf-8",
    ).stdout
    return json.loads(saida)


def stream(dados, tipo):
    return next((s for s in dados["streams"] if s["codec_type"] == tipo), None)


def duracao(arquivo):
    return float(sondar(arquivo)["format"]["duration"])


def e_hdr(video):
    v = stream(sondar(video), "video")
    return bool(v) and (
        v.get("color_transfer") in ("smpte2084", "arib-std-b67") or v.get("color_primaries") == "bt2020"
    )


def filtro_video(video):
    return (TONEMAP if e_hdr(video) else "") + CONFORMAR


def medir_audio(arquivo, filtro=None):
    """Devolve (LUFS integrado, pico verdadeiro em dBFS)."""
    af = (filtro + "," if filtro else "") + "ebur128=peak=true"
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(arquivo), "-vn", "-af", af, "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    resumo = log[log.rfind("Summary:"):]
    return (
        float(re.search(r"I:\s+(-?[\d.]+) LUFS", resumo).group(1)),
        float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", resumo).group(1)),
    )


def corrige_pele(rgb, alfa=None):
    """rgb float 0-1. Tira o verde das altas luzes e reduz o excesso de amarelo.

    Com alfa (matte do apresentador) a correcao fica so na pessoa: sem isso, parede
    verde ou planta clara no fundo tambem seria puxada para tom de pele.
    """
    import numpy as np
    from PIL import Image, ImageFilter

    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    verde = np.clip((g - r + 0.05) / 0.07, 0, 1) * np.clip((y - 0.5) / 0.15, 0, 1)
    if alfa is not None:
        verde = verde * alfa
    verde = np.asarray(
        Image.fromarray((verde * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)),
        dtype=np.float32,
    ) / 255.0
    verde = np.clip(verde * 1.6, 0, 1)
    alvo = np.stack([np.clip(y * 1.07, 0, 1), y * 0.975, y * 0.90], axis=2)
    saida = rgb * (1 - verde[..., None]) + alvo * verde[..., None]
    # altas luzes menos estouradas e menos amarelo no geral
    saida = saida * np.array([0.985, 0.985, 1.035], dtype=np.float32)
    saida = np.where(saida > 0.8, 0.8 + (saida - 0.8) * 0.72, saida)
    return np.clip(saida, 0, 1)
