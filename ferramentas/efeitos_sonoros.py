"""Sintetiza efeitos sutis de edicao (livres de direitos): whoosh, pop, brilho e impacto.

Uso: efeitos_sonoros.py <pasta_saida>
"""
import os
import sys
import wave

import numpy as np

SR = 48000
pasta = sys.argv[1]
os.makedirs(pasta, exist_ok=True)
rng = np.random.default_rng(11)


def salvar(nome, x):
    x = x / max(1e-6, np.abs(x).max()) * 0.8
    estereo = np.stack([x, x], axis=1) if x.ndim == 1 else x
    with wave.open(os.path.join(pasta, nome), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((estereo * 32767).astype(np.int16).tobytes())


def passa_banda_varrido(ruido, f_ini, f_fim, q=2.5):
    """Filtro de estado variavel com frequencia varrendo (whoosh)."""
    n = len(ruido)
    fs = np.geomspace(f_ini, f_fim, n)
    baixo = banda = 0.0
    saida = np.zeros(n)
    for i in range(n):
        f = 2 * np.sin(np.pi * fs[i] / SR)
        alto = ruido[i] - baixo - banda / q
        banda += f * alto
        baixo += f * banda
        saida[i] = banda
    return saida


# whoosh: ruido filtrado que sobe e desce, com pico perto do meio
dur = 0.55
n = int(dur * SR)
sobe = passa_banda_varrido(rng.standard_normal(n), 300, 4200)
env = np.sin(np.pi * (np.arange(n) / n) ** 0.7) ** 2
salvar("whoosh.wav", sobe * env)

# pop suave: seno com queda de afinacao e estalo curto
dur = 0.16
t = np.arange(int(dur * SR)) / SR
f = 720 * np.exp(-t * 26) + 240
pop = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
salvar("pop.wav", pop)

# brilho: sinos agudos com decaimento, para palavras douradas
dur = 1.5
t = np.arange(int(dur * SR)) / SR
brilho = np.zeros_like(t)
for k, (freq, atraso) in enumerate(((1760, 0), (2217, 0.05), (2637, 0.1), (3520, 0.16))):
    tt = np.clip(t - atraso, 0, None)
    brilho += np.sin(2 * np.pi * freq * tt) * np.exp(-tt * (4 + k)) * (t >= atraso) * (0.9 - k * 0.15)
ruido_ar = passa_banda_varrido(rng.standard_normal(len(t)), 5000, 9000) * np.exp(-t * 5) * 0.25
salvar("brilho.wav", brilho + ruido_ar)

# impacto grave suave, para abertura e cartao final
dur = 0.9
t = np.arange(int(dur * SR)) / SR
f = 95 * np.exp(-t * 3) + 42
impacto = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5) * np.minimum(1, t / 0.004)
salvar("impacto.wav", impacto)
print("efeitos prontos em", pasta)
