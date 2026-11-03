"""Sintetiza uma trilha ambiente original (livre de direitos) para videos de clinica.

Uso: trilha_ambiente.py <saida.wav> <duracao_s> [bpm]
Pad quente (acordes Dmaj9 - Bm9 - Gmaj9 - A6/9), arpejo suave tipo piano,
sub-grave discreto e reverb por convolucao. Saida 48 kHz estereo, ~-16 LUFS
(o nivel final e ajustado na mixagem).
"""
import sys
import wave

import numpy as np

saida = sys.argv[1]
duracao = float(sys.argv[2])
bpm = float(sys.argv[3]) if len(sys.argv) > 3 else 72.0
SR = 48000
rng = np.random.default_rng(7)

n = int(duracao * SR)
t = np.arange(n) / SR
esq = np.zeros(n)
dir_ = np.zeros(n)


def nota(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


# progressao (notas MIDI), 2 compassos de 4 tempos cada acorde
ACORDES = [
    [50, 57, 61, 64, 66],  # Dmaj9: D A C# E F#
    [47, 54, 57, 61, 62],  # Bm9:  B F# A C# D
    [43, 50, 54, 57, 59],  # Gmaj9: G D F# A B
    [45, 52, 54, 59, 61],  # A6/9: A E F# B C#
]
batida = 60.0 / bpm
dur_acorde = 8 * batida


def envelope(m, ataque, release):
    env = np.ones(m)
    a = min(int(ataque * SR), m)
    r = min(int(release * SR), m)
    env[:a] = np.linspace(0, 1, a) ** 2
    env[m - r:] *= np.linspace(1, 0, r) ** 2
    return env


# ---- pad: senoides levemente desafinadas + 2o e 3o harmonicos fracos
k = 0
inicio = 0.0
while inicio < duracao:
    acorde = ACORDES[k % len(ACORDES)]
    i0 = int(inicio * SR)
    m = min(int((dur_acorde + 2.5) * SR), n - i0)  # sobreposicao de 2,5 s entre acordes
    tt = np.arange(m) / SR
    env = envelope(m, 2.2, 2.8)
    for j, md in enumerate(acorde):
        f = nota(md + 12 if j > 0 else md)
        for desaf, pan in ((-0.0025, 0.3), (0.0025, 0.7)):
            ff = f * (1 + desaf)
            onda = np.sin(2 * np.pi * ff * tt) + 0.18 * np.sin(4 * np.pi * ff * tt) + 0.06 * np.sin(6 * np.pi * ff * tt)
            onda *= env * (0.05 if j > 0 else 0.07)
            esq[i0:i0 + m] += onda * (1 - pan)
            dir_[i0:i0 + m] += onda * pan
    # sub-grave
    sub = np.sin(2 * np.pi * nota(acorde[0] - 12) * tt) * env * 0.06
    esq[i0:i0 + m] += sub
    dir_[i0:i0 + m] += sub
    inicio += dur_acorde
    k += 1

# ---- arpejo suave (colcheias), comeca no 2o acorde
passo = batida / 2
padrao = [0, 2, 3, 4, 3, 2, 1, 2]
tempo = dur_acorde
idx = 0
while tempo < duracao - 1:
    acorde = ACORDES[int(tempo // dur_acorde) % len(ACORDES)]
    md = acorde[padrao[idx % len(padrao)]] + 12
    f = nota(md)
    i0 = int(tempo * SR)
    m = min(int(2.2 * SR), n - i0)
    tt = np.arange(m) / SR
    dec = np.exp(-tt * 3.2) * np.minimum(1, tt / 0.004)
    tom = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 6)
           + 0.12 * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 9)) * dec
    vel = 0.035 * (0.75 + 0.25 * rng.random())
    pan = 0.35 + 0.3 * rng.random()
    esq[i0:i0 + m] += tom * vel * (1 - pan)
    dir_[i0:i0 + m] += tom * vel * pan
    tempo += passo
    idx += 1

# ---- passa-baixa suave (um polo) para tirar brilho
def passa_baixa(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


esq = passa_baixa(esq, 4200)
dir_ = passa_baixa(dir_, 4200)

# ---- reverb: convolucao com ruido de decaimento exponencial (via FFT)
ir_len = int(2.8 * SR)
ti = np.arange(ir_len) / SR
ir_e = rng.standard_normal(ir_len) * np.exp(-ti * 2.4)
ir_d = rng.standard_normal(ir_len) * np.exp(-ti * 2.4)
ir_e /= np.sqrt(np.sum(ir_e ** 2))
ir_d /= np.sqrt(np.sum(ir_d ** 2))


def conv(x, ir):
    m = len(x) + len(ir) - 1
    nfft = 1 << (m - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    return y


esq = 0.62 * esq + 0.38 * conv(esq, ir_e)
dir_ = 0.62 * dir_ + 0.38 * conv(dir_, ir_d)

# fade geral e normalizacao de pico
fade = np.minimum(1, t / 2.0) * np.minimum(1, (duracao - t) / 3.0)
esq *= fade
dir_ *= fade
pico = max(np.abs(esq).max(), np.abs(dir_).max())
estereo = np.stack([esq, dir_], axis=1) / pico * 0.5

with wave.open(saida, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((estereo * 32767).astype(np.int16).tobytes())
print(f"trilha: {duracao:.1f}s, {bpm} bpm -> {saida}")
