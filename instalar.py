#!/usr/bin/env python3
"""Instala o kit de edicao de video para clinicas.

Uso:
  python instalar.py              instala o que e local ao kit e a skill para o Claude Code
  python instalar.py --verificar  so mostra o que esta instalado, nao altera nada
  python instalar.py --teste      gera e renderiza o video de demonstracao (2 a 4 min)
  python instalar.py --extras     skills do Remotion e do Hyperframes (com telemetria desligada)
                                  e servidores MCP (Openverse, OBS, Epidemic Sound) no Claude Code
  python instalar.py --sem-skill  nao copia a skill para ~/.claude/skills

O que este script altera:
  .venv/ e modelos/ dentro do kit, template/node_modules, ferramentas/openverse-mcp/node_modules
  ~/.claude/skills/edicao-clinica (exceto com --sem-skill)
  --extras tambem altera ~/.claude/skills e a configuracao de MCP do usuario
Nao instala programas no sistema: se faltar Node, FFmpeg ou Git, mostra o comando e para.
"""
import argparse
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VENV = RAIZ / ".venv"
PY_VENV = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
MODELO = RAIZ / "modelos" / "rvm_mobilenetv3_fp32.onnx"
MODELO_URL = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx"
MODELO_SHA256 = "88d4531297118f595bf2fd60f6f566aec2e559393802d1f436c380f0cbbd2828"
SKILL_ORIGEM = RAIZ / ".claude" / "skills" / "edicao-clinica"
HYPERFRAMES = ["hyperframes", "hyperframes-cli", "hyperframes-registry", "media-use",
               "remotion-to-hyperframes", "reverse-any-video", "style-sampling"]

COMO_INSTALAR = {
    "Windows": {"node": "winget install OpenJS.NodeJS.LTS", "ffmpeg": "winget install Gyan.FFmpeg",
                "git": "winget install Git.Git"},
    "Darwin": {"node": "brew install node", "ffmpeg": "brew install ffmpeg", "git": "brew install git"},
    "Linux": {"node": "use o gerenciador da sua distribuicao ou https://nodejs.org", "ffmpeg": "sudo apt install ffmpeg",
              "git": "sudo apt install git"},
}


def titulo(texto):
    print(f"\n== {texto}", flush=True)


def versao(cmd):
    caminho = shutil.which(cmd)
    if not caminho:
        return None
    saida = subprocess.run([caminho, "-version" if cmd.startswith("ff") else "--version"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (saida.stdout or saida.stderr).splitlines()[0].strip()


def rodar(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def checar_sistema():
    titulo("programas do sistema")
    faltando = []
    node = versao("node")
    print("node  :", node or "FALTA")
    if not node:
        faltando.append("node")
    else:
        m = re.match(r"v(\d+)\.(\d+)", node)
        maior, menor = int(m.group(1)), int(m.group(2))
        if not (maior >= 24 or (maior == 22 and menor >= 13) or (maior == 20 and menor >= 19)):
            print("        versao antiga: o Remotion pede 20.19+, 22.13+ ou 24+")
            faltando.append("node")
    print("npm   :", versao("npm") or "FALTA")
    for cmd in ("ffmpeg", "ffprobe", "git"):
        v = versao(cmd)
        print(f"{cmd:6}:", v or "FALTA")
        if not v:
            faltando.append("ffmpeg" if cmd.startswith("ff") else cmd)
    if shutil.which("ffmpeg"):
        filtros = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        for f in ("alimiter", "ebur128", "silencedetect", "afftdn", "alphamerge", "minterpolate", "zscale"):
            if not re.search(rf"\s{f}\s", filtros):
                print(f"        ffmpeg sem o filtro {f}: instale uma versao completa")
                if f == "zscale":
                    print("        (zscale so e necessario em gravacao HDR)")
                else:
                    faltando.append("ffmpeg")
    py = sys.version_info
    print(f"python: {py.major}.{py.minor}.{py.micro}")
    if not (3, 11) <= (py.major, py.minor) <= (3, 13):
        print("        ATENCAO: o kit foi testado em Python 3.12. Se o pip falhar, instale o 3.12.")
    return sorted(set(faltando))


def instalar_python():
    titulo("dependencias Python em .venv")
    if not PY_VENV.exists():
        rodar([sys.executable, "-m", "venv", VENV])
    rodar([PY_VENV, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-r", RAIZ / "requirements.txt"])


def sha256(arquivo):
    h = hashlib.sha256()
    with open(arquivo, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def baixar_modelo():
    titulo("modelo de recorte (Robust Video Matting, GPL-3.0, 15 MB)")
    MODELO.parent.mkdir(exist_ok=True)
    if MODELO.exists() and sha256(MODELO) == MODELO_SHA256:
        print("ja instalado")
        return
    print("baixando", MODELO_URL, flush=True)
    urllib.request.urlretrieve(MODELO_URL, MODELO)
    if sha256(MODELO) != MODELO_SHA256:
        MODELO.unlink()
        raise SystemExit("o modelo baixado nao confere com o hash esperado. Nada foi usado.")
    print("modelo conferido")


def instalar_node():
    npm = shutil.which("npm")
    titulo("dependencias do projeto Remotion (template)")
    rodar([npm, "ci", "--no-audit", "--no-fund"], cwd=RAIZ / "template")
    titulo("servidor MCP do Openverse")
    rodar([npm, "ci", "--no-audit", "--no-fund"], cwd=RAIZ / "ferramentas" / "openverse-mcp")


def instalar_skill():
    destino = Path.home() / ".claude" / "skills" / "edicao-clinica"
    titulo(f"skill em {destino}")
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(SKILL_ORIGEM, destino)
    arquivo = destino / "SKILL.md"
    arquivo.write_text(arquivo.read_text(encoding="utf-8").replace("{{KIT}}", RAIZ.as_posix()), encoding="utf-8")
    print("skill instalada; ela aponta para", RAIZ.as_posix())


def escrever_memoria():
    origem = RAIZ / "memoria" / "MEMORIA.md"
    destino = RAIZ / "memoria" / "MEMORIA-instalada.md"
    destino.write_text(origem.read_text(encoding="utf-8").replace("{{KIT}}", RAIZ.as_posix()), encoding="utf-8")
    print(f"\nTexto para a memoria da IA: {destino}")


def instalar_extras():
    npx = shutil.which("npx")
    titulo("skills do Remotion")
    rodar([npx, "--yes", "skills", "add", "remotion-dev/skills", "-g", "-a", "claude-code", "-s", "*", "-y", "--copy"])
    titulo("skills do Hyperframes (sem figma e slideshow)")
    rodar([npx, "--yes", "skills", "add", "heygen-com/hyperframes", "-g", "-a", "claude-code",
           "-s", *HYPERFRAMES, "-y", "--copy"])
    titulo("telemetria do Hyperframes: desligando")
    rodar([npx, "--yes", "hyperframes", "telemetry", "disable"])
    claude = shutil.which("claude")
    if not claude:
        print("\nClaude Code nao encontrado no PATH. Registre os MCP no seu agente; veja referencias/ferramentas-extras.md")
        return
    titulo("servidores MCP do Claude Code")
    existentes = subprocess.run([claude, "mcp", "list"], capture_output=True, text=True, encoding="utf-8",
                                errors="replace").stdout
    npx_obs = ["cmd", "/c", "npx", "-y", "obs-mcp@1.1.0"] if os.name == "nt" else ["npx", "-y", "obs-mcp@1.1.0"]
    pedidos = {
        "openverse": ["-s", "user", "openverse", "--", "node", (RAIZ / "ferramentas/openverse-mcp/server.mjs").as_posix()],
        "obs": ["-s", "user", "obs", "--", *npx_obs],
        "epidemic-sound": ["-s", "user", "--transport", "http", "epidemic-sound",
                           "https://www.epidemicsound.com/a/mcp-service/mcp",
                           "--header", "Authorization: Bearer ${EPIDEMIC_SOUND_MCP_API_KEY}"],
    }
    ambiente = dict(os.environ, MSYS_NO_PATHCONV="1")
    for nome, argumentos in pedidos.items():
        if re.search(rf"^{nome}\b", existentes, re.M):
            print(f"{nome}: ja registrado")
            continue
        rodar([claude, "mcp", "add", *argumentos], env=ambiente)
    print("\nFalta o usuario: chave do Epidemic Sound (EPIDEMIC_SOUND_MCP_API_KEY) e WebSocket do OBS (OBS_WEBSOCKET_PASSWORD).")


def teste():
    if not PY_VENV.exists():
        raise SystemExit("rode python instalar.py antes do teste")
    npx = shutil.which("npx")
    template = RAIZ / "template"
    saida = template / "out"
    saida.mkdir(exist_ok=True)
    ambiente = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")

    def py(script, *resto):
        rodar([PY_VENV, RAIZ / "ferramentas" / script, *resto], env=ambiente)

    titulo("teste: gerando o material de demonstracao")
    py("gerar_demo.py")
    titulo("teste: recorte com o modelo real em 1 s de video")
    py("recortar_rvm.py", template / "public/demo/apresentador.mp4", saida / "matte-teste.mp4", MODELO, "0", "1")
    titulo("teste: transcricao com o modelo tiny (baixa 75 MB na primeira vez)")
    py("transcrever.py", template / "public/demo/voz.wav", saida / "transcricao-teste.json", "tiny")
    titulo("teste: tipos e validacao do roteiro")
    rodar([shutil.which("npm"), "run", "validar"], cwd=template)
    titulo("teste: render do video de demonstracao")
    video = saida / "demo.mp4"
    rodar([npx, "remotion", "render", "demo", video, "--codec=h264", "--crf=20", "--log=error"], cwd=template)
    titulo("teste: capa")
    rodar([npx, "remotion", "still", "demo-capa", saida / "demo-capa.png", "--log=error"], cwd=template)
    print(f"\nTESTE OK. Video: {video}")


def estado():
    titulo("estado do kit")
    print(".venv :", "ok" if PY_VENV.exists() else "FALTA")
    print("modelo:", "ok" if MODELO.exists() and sha256(MODELO) == MODELO_SHA256 else "FALTA")
    print("node_modules do template:", "ok" if (RAIZ / "template/node_modules").exists() else "FALTA")
    print("skill :", "ok" if (Path.home() / ".claude/skills/edicao-clinica/SKILL.md").exists() else "nao instalada")


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--verificar", action="store_true")
ap.add_argument("--teste", action="store_true")
ap.add_argument("--extras", action="store_true")
ap.add_argument("--sem-skill", action="store_true")
args = ap.parse_args()

faltando = checar_sistema()
if args.verificar:
    estado()
    sys.exit(1 if faltando else 0)
if faltando:
    guia = COMO_INSTALAR.get(platform.system(), COMO_INSTALAR["Linux"])
    print("\nFALTA instalar. Peca autorizacao ao usuario, instale e rode de novo:")
    for f in faltando:
        print(f"  {f}: {guia[f]}")
    sys.exit(1)

if args.teste:
    teste()
    sys.exit(0)
if args.extras:
    instalar_extras()
    sys.exit(0)

instalar_python()
baixar_modelo()
instalar_node()
if not args.sem_skill:
    instalar_skill()
escrever_memoria()
estado()
print("\nINSTALACAO OK. Agora rode: python instalar.py --teste")
