#!/usr/bin/env python3
"""Porta de entrada das ferramentas: escolhe o Python certo e chama o script.

Uso: python kit.py <comando> [argumentos]
     python kit.py            (lista os comandos)
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
COMANDOS = {
    "novo-cliente": "cria a pasta e o projeto de um cliente",
    "diagnostico-video": "mede um bruto e aponta problemas",
    "preparar-video": "do bruto ate um rascunho que ja renderiza",
    "stills": "folha de quadros para revisar",
    "renderizar": "render, master e entrega",
    "catalogar": "folhas de contato de uma pasta de assets",
    "normalizar-imagens": "converte HEIC e fotos para JPG",
    "preparar-midia": "video de apoio em 1080x1920, com ampliacao e camera lenta",
    "preparar-trilha": "musica em -12 LUFS na duracao do video",
    "clipe-alpha": "trecho transparente para a palavra atras da cabeca",
    "capa-quadro": "extrai um quadro para a capa",
    "folha-rostos": "folha de quadros para escolher a foto da capa",
    "rascunho-roteiro": "reescreve o rascunho do roteiro a partir do EDL",
    "montar-edl": "refaz os cortes",
    "transcrever": "transcreve com tempo por palavra",
    "conferir-cortes": "confere cortes e palavras",
    "atualizar-motor": "copia o motor do kit para um cliente",
    "buscar-stock": "lista videos gratuitos do Mixkit",
    "folha-stock": "folhas de contato de candidatos do Pexels",
    "baixar-stock": "baixa videos do Pexels e gera proxies",
    "varredura": "procura segredos e dados sensiveis no repositorio",
    "gerar-demo": "gera o material do video de demonstracao",
}

if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
    print(__doc__)
    for nome, descricao in COMANDOS.items():
        print(f"  {nome:20} {descricao}")
    sys.exit(0 if len(sys.argv) < 2 else 2)

venv = RAIZ / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
python = str(venv) if venv.exists() else sys.executable
script = RAIZ / "ferramentas" / (sys.argv[1].replace("-", "_") + ".py")
ambiente = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
sys.exit(subprocess.run([python, str(script), *sys.argv[2:]], env=ambiente).returncode)
