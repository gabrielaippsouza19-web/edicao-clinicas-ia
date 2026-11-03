"""Faz toda a parte mecanica de um video novo, do bruto ate um rascunho que ja renderiza.

Uso: preparar_video.py <pasta_cliente> <id_video> <bruto>
       [--descartar ini-fim,...] [--whisper medium] [--limiar -35]
       [--pele] [--fundo-desfocado] [--trilha musica.mp3] [--trilha-ini s]
       [--refazer-cortes]

Etapas (cada uma e pulada se o resultado ja existir):
 1. transcreve o bruto             analise/<id>/transcricao.json
 2. monta os cortes em silencio    projeto/src/videos/<id>/edl.json
 3. recorte e cor do apresentador  analise/<id>/camadas -> public/<id>/apresentador.mp4
 4. limpa a voz                    public/<id>/voz.wav
 5. prepara a trilha               public/<id>/trilha.wav
 6. escreve o rascunho do roteiro  projeto/src/videos/<id>/roteiro.ts
 7. registra o video no projeto    projeto/src/videos/index.ts

--refazer-cortes refaz so a etapa 2, por exemplo depois de corrigir --descartar.
Os tempos do roteiro sao do bruto, entao refazer os cortes nao desalinha nada.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

AQUI = Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("cliente")
ap.add_argument("video")
ap.add_argument("bruto")
ap.add_argument("--descartar", default="")
ap.add_argument("--whisper", default="medium")
ap.add_argument("--limiar", default="-35")
ap.add_argument("--pele", action="store_true")
ap.add_argument("--fundo-desfocado", action="store_true")
ap.add_argument("--trilha")
ap.add_argument("--trilha-ini", default="0")
ap.add_argument("--refazer-cortes", action="store_true")
args = ap.parse_args()

if not re.fullmatch(r"[a-zA-Z0-9-]+", args.video):
    raise SystemExit("id do video: use so letras, numeros e hifen")
raiz = Path(args.cliente).resolve()
projeto = raiz / "projeto"
if not (projeto / "src/motor/Edicao.tsx").exists():
    raise SystemExit(f"{raiz} nao parece uma pasta de cliente. Rode novo-cliente antes.")
bruto = Path(args.bruto).resolve()
analise = raiz / "analise" / args.video
camadas = analise / "camadas"
camadas.mkdir(parents=True, exist_ok=True)
fonte = projeto / "src/videos" / args.video
fonte.mkdir(parents=True, exist_ok=True)
publico = projeto / "public" / args.video
publico.mkdir(parents=True, exist_ok=True)


def ferramenta(nome, *resto):
    subprocess.run([sys.executable, str(AQUI / nome), *[str(x) for x in resto]], check=True)


# 1 ---- transcricao
transcricao = analise / "transcricao.json"
if not transcricao.exists():
    print("== transcrevendo", flush=True)
    ferramenta("transcrever.py", bruto, transcricao, args.whisper)

# 2 ---- cortes
edl = fonte / "edl.json"
if args.refazer_cortes or not edl.exists():
    print("== montando cortes", flush=True)
    resto = [args.descartar] if args.descartar else []
    correcoes = raiz / "correcoes.json"
    if correcoes.exists():
        resto += ["--correcoes", correcoes]
    ferramenta("montar_edl.py", bruto, transcricao, edl, *resto, f"--limiar={args.limiar}")
if args.refazer_cortes:
    sys.exit(0)

# 3 ---- apresentador
apresentador = publico / "apresentador.mp4"
if not apresentador.exists():
    print("== tratando o apresentador (recorte a ~8 fps em CPU)", flush=True)
    opcoes = []
    if args.pele:
        opcoes.append("--pele")
    if args.fundo_desfocado:
        opcoes.append("--fundo-desfocado")
    ferramenta("preparar_apresentador.py", bruto, camadas, *opcoes)
    shutil.copy2(camadas / ("base.mp4" if args.fundo_desfocado else "cor.mp4"), apresentador)
shutil.copy2(camadas / "enquadramento.json", fonte / "enquadramento.json")

# 4 ---- voz
voz = publico / "voz.wav"
if not voz.exists():
    print("== limpando a voz", flush=True)
    ferramenta("preparar_voz.py", bruto, voz)

# 5 ---- trilha
trilha = publico / "trilha.wav"
if not trilha.exists():
    print("== preparando a trilha", flush=True)
    duracao = json.load(open(edl, encoding="utf-8"))["duracao"] + 6
    if args.trilha:
        ferramenta("preparar_trilha.py", trilha, duracao, "--arquivo", args.trilha, "--ini", args.trilha_ini)
    else:
        ferramenta("preparar_trilha.py", trilha, duracao)

# 6 ---- rascunho do roteiro
roteiro = fonte / "roteiro.ts"
if not roteiro.exists():
    ferramenta("rascunho_roteiro.py", edl, roteiro, "--id", args.video)

# 7 ---- registro
pastas = sorted(p.parent.name for p in (projeto / "src/videos").glob("*/roteiro.ts"))
linhas = ['// Gerado por preparar_video.py. Não edite à mão.', 'import { Video } from "../motor/tipos";']
linhas += [f'import {{ video as v{k} }} from "./{nome}/roteiro";' for k, nome in enumerate(pastas)]
linhas += ["", f"export const VIDEOS: Video[] = [{', '.join(f'v{k}' for k in range(len(pastas)))}];", ""]
(projeto / "src/videos/index.ts").write_text("\n".join(linhas), encoding="utf-8")

print(f"\npronto: {roteiro}")
print("o rascunho ja renderiza. Agora escreva as cenas seguindo referencias/receita-roteiro.md")
