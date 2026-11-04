"""Escreve o primeiro roteiro.ts de um video a partir do EDL.

Uso: rascunho_roteiro.py <edl.json> <saida.ts> --id <id_video> [--forcar]

O rascunho ja renderiza: legendas de 2-3 palavras, enquadramento mudando a cada corte,
flashes, selo e cartao final. Cenas, cartoes e letreiros dependem de olhar a fala e o
material do cliente, e sao escritos depois (ver referencias/receita-roteiro.md).
"""
import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("edl")
ap.add_argument("saida")
ap.add_argument("--id", required=True)
ap.add_argument("--forcar", action="store_true")
args = ap.parse_args()

saida = Path(args.saida)
if saida.exists() and not args.forcar:
    raise SystemExit(f"{saida} ja existe. Use --forcar para sobrescrever.")
edl = json.load(open(args.edl, encoding="utf-8"))
clips, palavras = edl["clips"], edl["palavras"]


def indice_clipe(t):
    for k, c in enumerate(clips):
        if c["srcIni"] <= t <= c["srcFim"]:
            return k
    return -1


# ---- legendas: quebra em pontuacao, pausa, corte, 3 palavras ou 24 caracteres.
# Nao termina em palavra de ligacao ("de", "e", "com"): ela abre o bloco seguinte.
LIGACAO = {"a", "o", "as", "os", "e", "ou", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
           "com", "que", "para", "por", "um", "uma", "meu", "minha", "meus", "minhas", "seu", "sua"}
MAX_CARACTERES = 24
legendas, atual = [], []


def fechar(palavras_bloco, pausa):
    bloco = {"t": palavras_bloco[0]["i"], "texto": " ".join(x["p"] for x in palavras_bloco)}
    if pausa > 0.45:
        bloco["fim"] = round(palavras_bloco[-1]["f"] + 0.15, 2)
    legendas.append(bloco)


for i, p in enumerate(palavras):
    if atual and len(" ".join(x["p"] for x in atual + [p])) > MAX_CARACTERES:
        guardada = atual.pop() if len(atual) > 1 and atual[-1]["p"].lower() in LIGACAO else None
        fechar(atual, 0.0)
        atual = [guardada] if guardada else []
    atual.append(p)
    prox = palavras[i + 1] if i + 1 < len(palavras) else None
    pausa = prox["i"] - p["f"] if prox else 9.0
    natural = (
        prox is None
        or p["p"][-1] in ".?!,;:"
        or pausa > 0.35
        or indice_clipe(prox["i"]) != indice_clipe(p["i"])
    )
    if natural:
        fechar(atual, pausa)
        atual = []
    elif len(atual) >= 3:
        guardada = atual.pop() if atual[-1]["p"].lower() in LIGACAO else None
        fechar(atual, 0.0)
        atual = [guardada] if guardada else []

# ---- enquadramento: muda em todo corte; trecho longo muda tambem no meio
CICLO = ["base", "medio", "perto", "medio"]
zooms, passo = [{"em": 0, "z": "base"}], 0
for k, c in enumerate(clips):
    if k > 0:
        passo += 1
        zooms.append({"em": c["srcIni"], "z": CICLO[passo % len(CICLO)]})
    if c["srcFim"] - c["srcIni"] > 6:
        meio = (c["srcIni"] + c["srcFim"]) / 2
        candidatas = [p for p in palavras if c["srcIni"] + 2 < p["f"] < c["srcFim"] - 2]
        if candidatas:
            melhor = min(candidatas, key=lambda p: abs(p["f"] - meio) - (2 if p["p"][-1] in ".?!," else 0))
            passo += 1
            zooms.append({"em": round(melhor["f"] + 0.02, 2), "z": CICLO[passo % len(CICLO)]})

# ---- flashes nos cortes perto de 1/3 e 2/3 do video
flashes = []
if len(clips) >= 3:
    for fracao in (1 / 3, 2 / 3):
        alvo = edl["duracao"] * fracao
        escolhido = min(clips[1:], key=lambda c: abs(c["editIni"] - alvo))
        if escolhido["srcIni"] not in flashes:
            flashes.append(escolhido["srcIni"])

primeira = palavras[0]["i"] if palavras else clips[0]["srcIni"]
ultima = palavras[-1]["f"] if palavras else clips[-1]["srcFim"]
selo = [[round(primeira, 2), round(primeira + 4.2, 2)], [round(max(primeira + 5, ultima - 3), 2), round(ultima, 2)]]
sons = [{"t": round(t - 0.06, 2), "som": "whoosh", "vol": 0.1} for t in flashes]

fala, linha_atual, inicio = [], [], None
for p in palavras:
    if inicio is None:
        inicio = p["i"]
    linha_atual.append(p["p"])
    if p["p"][-1] in ".?!" or len(linha_atual) >= 14:
        fala.append(f"// [{inicio:6.2f}] {' '.join(linha_atual)}")
        linha_atual, inicio = [], None
if linha_atual:
    fala.append(f"// [{inicio:6.2f}] {' '.join(linha_atual)}")


def lista(itens, formatar):
    return "\n".join("    " + formatar(x) + "," for x in itens)


def fmt_legenda(b):
    fim = f', fim: {b["fim"]}' if "fim" in b else ""
    return f'{{ t: {b["t"]}{fim}, texto: {json.dumps(b["texto"], ensure_ascii=False)} }}'


corpo = f"""// Rascunho gerado por rascunho_roteiro.py. Todos os tempos são do BRUTO.
// Falta escrever: cenas, grupos, letreiros, palavra atrás e capa (referencias/receita-roteiro.md).
//
// Fala:
{chr(10).join(fala)}
import {{ Video }} from "../../motor/tipos";
import edl from "./edl.json";
import enquadramento from "./enquadramento.json";

export const video: Video = {{
  id: {json.dumps(args.id)},
  edl,
  enquadramento,
  midia: {{
    apresentador: "{args.id}/apresentador.mp4",
    voz: "{args.id}/voz.wav",
    trilha: "{args.id}/trilha.wav",
  }},
  cenas: [],
  grupos: [],
  letreiros: [],
  atras: [],
  legendas: [
{lista(legendas, fmt_legenda)}
  ],
  zooms: [
{lista(zooms, lambda z: f'{{ em: {z["em"]}, z: "{z["z"]}" }}')}
  ],
  flashes: {json.dumps(flashes)},
  selo: {json.dumps(selo)},
  sons: [
{lista(sons, lambda s: f'{{ t: {s["t"]}, som: "{s["som"]}", vol: {s["vol"]} }}')}
  ],
}};
"""
saida.write_text(corpo, encoding="utf-8")
print(f"rascunho: {saida} ({len(legendas)} legendas, {len(zooms)} mudancas de enquadramento)")
