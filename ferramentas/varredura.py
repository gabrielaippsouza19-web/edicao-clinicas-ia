"""Procura o que nao pode ir para o repositorio. Rode antes de todo commit e de tornar publico.

Uso: varredura.py [--nomes arquivo.txt]
--nomes: lista local, um termo por linha (nomes de clientes e pacientes). Essa lista nao entra
no repositorio. A busca ignora maiusculas e acentos. Sai com codigo 1 se achar algo.
"""
import argparse
import re
import subprocess
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MIDIA = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv", ".wav", ".mp3", ".m4a", ".aac", ".flac", ".heic",
         ".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".pdf", ".onnx", ".zip", ".rar", ".7z"}
PERMITIDOS = {"docs/previa-demo.jpg"}  # imagem gerada por gerar_demo.py, sem pessoa real
SEGREDOS = {
    "token do GitHub": r"\bgh[oprsu]_[A-Za-z0-9]{20,}",
    "chave de API": r"\b(sk|pk|rk)[-_](live|test|proj|ant)?[-_]?[A-Za-z0-9]{20,}",
    "chave AWS": r"\bAKIA[0-9A-Z]{16}\b",
    "chave privada": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "Bearer preenchido": r"Bearer\s+(?!\$\{)[A-Za-z0-9._-]{20,}",
    "chave em URL": r"[?&](api[_-]?key|token|key|secret)=[A-Za-z0-9._-]{12,}",
    "e-mail": r"[\w.+-]+@(?!users\.noreply\.github\.com|anthropic\.com|exemplo\.com)[\w-]+\.[A-Za-z]{2,}\b",
    "caminho pessoal": r"[A-Za-z]:\\+Users\\+[^\\\s]+|/home/[a-z][\w-]+/|/Users/[A-Za-z][\w-]+/|OneDrive[\\/]",
}
GRANDE = 1_000_000


def sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


ap = argparse.ArgumentParser()
ap.add_argument("--nomes")
args = ap.parse_args()
nomes = []
if args.nomes:
    nomes = [sem_acento(x.strip()) for x in open(args.nomes, encoding="utf-8") if x.strip()]

arquivos = subprocess.run(
    ["git", "ls-files", "-co", "--exclude-standard"], cwd=RAIZ, capture_output=True, text=True, check=True,
    encoding="utf-8",
).stdout.splitlines()

problemas = []
esta_ferramenta = "ferramentas/varredura.py"
for rel in arquivos:
    caminho = RAIZ / rel
    if not caminho.is_file():
        continue
    if caminho.suffix.lower() in MIDIA and rel not in PERMITIDOS:
        problemas.append(f"{rel}: arquivo de midia ou binario")
        continue
    if caminho.stat().st_size > GRANDE and not rel.endswith("package-lock.json"):
        problemas.append(f"{rel}: maior que 1 MB")
    if rel in PERMITIDOS:
        continue
    try:
        texto = caminho.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        problemas.append(f"{rel}: nao e texto UTF-8")
        continue
    if rel != esta_ferramenta and not rel.endswith("package-lock.json"):
        for nome, padrao in SEGREDOS.items():
            for m in re.finditer(padrao, texto):
                problemas.append(f"{rel}: {nome}: {m.group(0)[:12]}...")
    limpo = sem_acento(texto + "\n" + rel)
    for termo in nomes:
        if termo in limpo:
            problemas.append(f"{rel}: contem um termo da lista --nomes")

print(f"{len(arquivos)} arquivos conferidos")
if problemas:
    print(f"{len(problemas)} PROBLEMA(S):")
    for p in problemas:
        print(" -", p)
    raise SystemExit(1)
print("nada encontrado")
