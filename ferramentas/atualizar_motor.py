"""Copia o motor atual do kit para o projeto de um cliente, sem tocar em roteiros e midia.

Uso: atualizar_motor.py <pasta_cliente>
Faca isso entre videos, nunca no meio de uma revisao: o enquadramento e as animacoes podem mudar.
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import TEMPLATE  # noqa: E402

destino = Path(sys.argv[1]).resolve() / "projeto" / "src" / "motor"
if not destino.exists():
    raise SystemExit(f"{destino} nao existe")
shutil.copytree(TEMPLATE / "src" / "motor", destino, dirs_exist_ok=True)
print("motor atualizado em", destino)
