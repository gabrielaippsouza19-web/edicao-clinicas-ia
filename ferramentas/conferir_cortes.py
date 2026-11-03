"""Confere uma edicao: cada corte cai em silencio e nenhuma palavra sumiu.

Uso: conferir_cortes.py <edl.json> <transcricao_bruto.json> <transcricao_final.json> [descartar=ini-fim,...]
"""
import difflib
import json
import re
import sys

edl = json.load(open(sys.argv[1], encoding="utf-8"))
bruto = json.load(open(sys.argv[2], encoding="utf-8"))
final = json.load(open(sys.argv[3], encoding="utf-8"))
descartes = []
if len(sys.argv) > 4 and sys.argv[4]:
    for faixa in sys.argv[4].split(","):
        a, b = faixa.split("-")
        descartes.append((float(a), float(b)))


def dentro(t, folga=0.17):
    return any(a - 0.02 <= t <= b + folga for a, b in edl["silencios"])


print("== cortes")
ok = True
for k, c in enumerate(edl["clips"]):
    i = k == 0 or dentro(c["srcIni"])
    f = k == len(edl["clips"]) - 1 or dentro(c["srcFim"])
    ok = ok and i and f
    print(f"  {c['srcIni']:7.2f} -> {c['srcFim']:7.2f}  inicio em silencio: {i}  fim em silencio: {f}")
print("todos os cortes em silencio:", ok)


def palavras(dados, filtro=False):
    saida = []
    for s in dados["segmentos"]:
        for p in s["palavras"]:
            if filtro and any(a <= p["i"] <= b for a, b in descartes):
                continue
            w = re.sub(r"[^\wà-ÿ-]", "", p["p"].lower())
            if w:
                saida.append(w)
    return saida


a = palavras(bruto, filtro=True)
b = palavras(final)
print(f"\n== palavras: bruto {len(a)} | final {len(b)}")
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if op != "equal":
        print(f"  {op}: bruto {a[i1:i2]} -> final {b[j1:j2]}")
print("fim da comparacao")
