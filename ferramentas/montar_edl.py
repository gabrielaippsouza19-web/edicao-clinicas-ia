"""Gera a lista de cortes (EDL) cortando apenas dentro de silencio real.

Uso: montar_edl.py <video> <transcricao.json> <saida.json> [descartar=ini-fim,...]
                   [--correcoes arquivo.json] [--limiar -35]

- Os silencios sao medidos no audio do proprio video (ffmpeg silencedetect),
  com tempos no mesmo relogio do video.
- Silencio >= CORTAR_ACIMA vira corte, mantendo RESPIRO_DEPOIS apos a fala e
  RESPIRO_ANTES antes da proxima fala (pausa natural). Silencios menores ficam.
- "descartar" remove trechos do bruto (ex.: frase regravada); o corte e
  ajustado para cair dentro dos silencios vizinhos.
- --correcoes: JSON {"palavra ouvida": "palavra certa"} para termos que a
  transcricao erra (nomes de procedimentos, do cliente). Fica na pasta do cliente.
- As palavras da transcricao (tempos do bruto) ficam no EDL; a conversao para o
  tempo da edicao e feita no motor (tempo.ts).
- Termina avisando se alguma palavra caiu fora dos trechos mantidos.
"""
import argparse
import json
import re
import subprocess

SILENCIO_MIN = 0.2
CORTAR_ACIMA = 0.7  # cortes menores que ~0,3 s so criam salto de imagem
RESPIRO_DEPOIS = 0.20
RESPIRO_ANTES = 0.16

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("transcricao")
ap.add_argument("saida")
ap.add_argument("descartar", nargs="?", default="")
ap.add_argument("--correcoes")
ap.add_argument("--limiar", type=int, default=-35)
args = ap.parse_args()

correcoes = json.load(open(args.correcoes, encoding="utf-8")) if args.correcoes else {}
descartes = []
if args.descartar:
    for faixa in args.descartar.split(","):
        a, b = faixa.split("-")
        descartes.append((float(a), float(b)))

# --- silencios reais
log = subprocess.run(
    ["ffmpeg", "-hide_banner", "-i", args.video, "-vn", "-af",
     f"highpass=f=80,silencedetect=n={args.limiar}dB:d={SILENCIO_MIN}", "-f", "null", "-"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
).stderr
h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", log).groups()
dur_video = 3600 * float(h) + 60 * float(m) + float(s)
inicios = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
fins = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
silencios = list(zip(inicios, fins + [dur_video] * (len(inicios) - len(fins))))

# funde silencios vizinhos (separados por menos de 0,05 s)
fundidos = []
for a, b in silencios:
    if fundidos and a - fundidos[-1][1] < 0.05:
        fundidos[-1] = (fundidos[-1][0], b)
    else:
        fundidos.append((a, b))
silencios = fundidos

# --- trechos de fala = complemento dos silencios
falas, t = [], 0.0
for a, b in silencios:
    if a > t:
        falas.append([t, a])
    t = b
if t < dur_video:
    falas.append([t, dur_video])

# --- monta trechos mantidos: une falas separadas por silencio curto
mantidos = []
for ini, fim in falas:
    if any(da <= ini and fim <= db for da, db in descartes):
        continue
    if mantidos and ini - mantidos[-1][1] < CORTAR_ACIMA and not any(
        mantidos[-1][1] <= da <= ini or mantidos[-1][1] <= db <= ini for da, db in descartes
    ):
        mantidos[-1][1] = fim
    else:
        mantidos.append([ini, fim])

# ruido curto sem nenhuma palavra no comeco ou no fim do bruto nao e fala: vira corte sem motivo
dados = json.load(open(args.transcricao, encoding="utf-8"))
ditas = [p for seg in dados["segmentos"] for p in seg["palavras"]]


def sem_fala(trecho):
    ini, fim = trecho
    return fim - ini < 1.0 and not any(ini - 0.3 <= (p["i"] + p["f"]) / 2 <= fim + 0.3 for p in ditas)


if ditas:
    while len(mantidos) > 1 and sem_fala(mantidos[0]):
        print(f"retirado do inicio, sem fala: {mantidos[0]}")
        mantidos.pop(0)
    while len(mantidos) > 1 and sem_fala(mantidos[-1]):
        print(f"retirado do fim, sem fala: {mantidos[-1]}")
        mantidos.pop()

clips, t = [], 0.0
for ini, fim in mantidos:
    a = max(0.0, ini - RESPIRO_ANTES)
    b = min(dur_video, fim + RESPIRO_DEPOIS)
    clips.append({"srcIni": round(a, 3), "srcFim": round(b, 3), "editIni": round(t, 3)})
    t += b - a

# --- palavras (tempos do bruto), sem as descartadas, com correcoes
palavras = []
for seg in dados["segmentos"]:
    for p in seg["palavras"]:
        if any(da <= p["i"] <= db for da, db in descartes):
            continue
        if palavras and p["p"].startswith("-"):
            palavras[-1]["p"] += p["p"]
            palavras[-1]["f"] = p["f"]
            continue
        base = p["p"].strip(",.?!")
        texto = p["p"].replace(base, correcoes[base]) if base in correcoes else p["p"]
        palavras.append({"p": texto, "i": p["i"], "f": p["f"]})

json.dump(
    {"duracao": round(t, 3), "clips": clips, "palavras": palavras, "silencios": silencios},
    open(args.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1,
)
print(f"{len(clips)} trechos, duracao editada {t:.2f}s")
for c in clips:
    print(c)

# --- nenhuma palavra pode cair em um corte
fora = [
    p for p in palavras
    if not any(c["srcIni"] <= (p["i"] + p["f"]) / 2 <= c["srcFim"] for c in clips)
]
if fora:
    print(f"\nATENCAO: {len(fora)} palavra(s) fora dos trechos mantidos. Confira no bruto:")
    for p in fora:
        print(f"  {p['i']:7.2f} {p['p']}")
else:
    print("todas as palavras dentro dos trechos mantidos")
