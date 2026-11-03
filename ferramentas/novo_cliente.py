"""Cria a pasta de um cliente novo com o projeto Remotion pronto.

Uso: novo_cliente.py <slug> --raiz <pasta> --nome "Dra. Nome Sobrenome" --conselho CFM|CFO|outro
                     --registro "CRM-SP 123456" [--profissao Médica] [--rqe "RQE 1234"]
                     [--especialidade "Linha 1;Linha 2"] [--tema ouro-creme] [--assinatura script|serif]
                     [--cta "Agende sua;avaliação"] [--canal "Chame no WhatsApp"] [--sem-npm]

Cria <raiz>/<slug>/ com originais, assets, analise, entregas, projeto e CLIENTE.md.
Dado que nao foi informado fica como PREENCHER, e o motor recusa renderizar assim.
Nao use pasta sincronizada (OneDrive, Dropbox): video e node_modules pesam e geram conflito.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import KIT, TEMPLATE  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("slug")
ap.add_argument("--raiz", required=True)
ap.add_argument("--nome", default="PREENCHER")
ap.add_argument("--conselho", choices=["CFM", "CFO", "outro"], default="CFM")
ap.add_argument("--registro", default="PREENCHER")
ap.add_argument("--profissao")
ap.add_argument("--rqe")
ap.add_argument("--especialidade", default="")
ap.add_argument("--tema", default="ouro-creme")
ap.add_argument("--assinatura", choices=["script", "serif"], default="script")
ap.add_argument("--cta", default="Agende sua;avaliação")
ap.add_argument("--canal")
ap.add_argument("--sem-npm", action="store_true")
args = ap.parse_args()

if not re.fullmatch(r"[a-z0-9-]+", args.slug):
    raise SystemExit("slug: use so letras minusculas, numeros e hifen")
temas = re.findall(r'^  "([a-z-]+)": \{', (TEMPLATE / "src/motor/temas.ts").read_text(encoding="utf-8"), re.M)
if args.tema not in temas:
    raise SystemExit(f"tema {args.tema} nao existe. Opcoes: {', '.join(temas)}")

raiz = Path(args.raiz).resolve() / args.slug
if raiz.exists():
    raise SystemExit(f"{raiz} ja existe. Nada foi alterado.")
for pasta in ("originais", "assets/casos", "assets/ambiente", "assets/banco", "assets/marca", "analise", "entregas"):
    (raiz / pasta).mkdir(parents=True)

# ---- projeto: copia do template, sem demonstracao e sem midia
projeto = raiz / "projeto"
shutil.copytree(
    TEMPLATE, projeto,
    ignore=shutil.ignore_patterns("node_modules", "out", "build", "dist", "demo", "public"),
    ignore_dangling_symlinks=True,
)
publico = projeto / "public"
publico.mkdir()
(publico / ".gitkeep").touch()


def js(valor):
    return json.dumps(valor, ensure_ascii=False)


campos = [
    f"  nome: {js(args.nome)},",
    f"  conselho: {js(args.conselho)},",
]
if args.profissao:
    campos.append(f"  profissao: {js(args.profissao)},")
campos.append(f"  registro: {js(args.registro)},")
if args.rqe:
    campos.append(f"  rqe: {js(args.rqe)},")
especialidade = [x.strip() for x in args.especialidade.split(";") if x.strip()]
campos += [
    f"  especialidade: {js(especialidade)},",
    f"  cta: {js([x.strip() for x in args.cta.split(';') if x.strip()])},",
]
if args.canal:
    campos.append(f"  canal: {js(args.canal)},")
campos += [
    f"  tema: {js(args.tema)},",
    f"  assinatura: {js(args.assinatura)},",
    '  filtroApresentador: "none",',
]
(projeto / "src/cliente.ts").write_text(
    '// Identidade do cliente. Confira nome e registro nas artes da própria clínica.\n'
    'import { Cliente } from "./motor/tipos";\n\n'
    "export const CLIENTE: Cliente = {\n" + "\n".join(campos) + "\n};\n",
    encoding="utf-8",
)
(projeto / "src/videos/index.ts").write_text(
    '// Gerado por preparar_video.py. Não edite à mão.\nimport { Video } from "../motor/tipos";\n\n'
    "export const VIDEOS: Video[] = [];\n",
    encoding="utf-8",
)

# ---- ficha do cliente
modelo = KIT / ".claude/skills/edicao-clinica/referencias/modelo-cliente.md"
ficha = modelo.read_text(encoding="utf-8").replace("{{NOME}}", args.nome).replace("{{REGISTRO}}", args.registro)
(raiz / "CLIENTE.md").write_text(ficha, encoding="utf-8")
(raiz / "correcoes.json").write_text("{}\n", encoding="utf-8")

# ---- efeitos sonoros e dependencias
subprocess.run(
    [sys.executable, str(Path(__file__).with_name("efeitos_sonoros.py")), str(publico / "audio/sfx")], check=True
)
if not args.sem_npm:
    subprocess.run([shutil.which("npm"), "ci", "--no-audit", "--no-fund"], cwd=projeto, check=True)

print(f"cliente criado: {raiz}")
if "PREENCHER" in (args.nome, args.registro):
    print("ATENCAO: nome ou registro como PREENCHER. Edite projeto/src/cliente.ts antes de renderizar.")
print("proximo passo: coloque o bruto em originais/ e rode preparar-video")
