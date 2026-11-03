# Edição de vídeo para clínicas com IA

Kit para uma IA com terminal editar Reels e anúncios de médicos e dentistas a partir do vídeo bruto, em um estilo premium que já foi aprovado por uma cliente real. Serve para qualquer profissional: nome, registro, paleta e enquadramento são configuração.

**Inclui:** motor de edição em Remotion, mais de 20 ferramentas (transcrição, cortes em silêncio medido, recorte do apresentador, limpeza de voz, master, capa), método completo, regras de publicidade do CFM e do CFO e um instalador que a própria IA roda.

## Como usar

Cole isto na sua IA (Claude Code, Codex ou outra com terminal), trocando o link:

```text
Instale o kit de edição deste repositório na minha máquina e guarde na sua memória:
https://github.com/gabrielaippsouza19-web/edicao-clinicas-ia
Leia o AGENTS.md e siga os passos de instalação. Você tem minha autorização para clonar,
rodar o instalador e o teste. Antes de instalar programas no sistema ou rodar os extras, me pergunte.
No fim, me diga o que funcionou e o que falta eu fazer.
```

Depois, para editar:

```text
Edite este vídeo: [caminho do bruto]. Cliente: [nome e registro]. Material em [pasta].
```

Um chat sem terminal consegue ler o método, mas não consegue editar.

## O que precisa

- Windows, macOS ou Linux, com pelo menos 8 GB de RAM e 5 GB livres. Testado só em Windows 11.
- Python 3.12 (o kit foi testado nessa versão), Node 20.19+, 22.13+ ou 24+, FFmpeg e Git. O instalador confere e mostra o que falta.
- Uma pasta de trabalho fora de OneDrive e Dropbox.

## Como funciona

```text
bruto -> diagnóstico -> transcrição -> cortes em silêncio medido -> recorte e cor -> voz e trilha
      -> roteiro (a IA liga cada frase a uma imagem) -> folha de quadros -> render -> master -> conferência
```

Tudo roda na sua máquina. Transcrição e recorte não mandam vídeo para nenhum serviço. O vídeo de demonstração (`python instalar.py --teste`) usa só material gerado, sem nenhuma pessoa real.

| Pasta | O que tem |
|---|---|
| `AGENTS.md` | Instruções para a IA instalar e trabalhar |
| `.claude/skills/edicao-clinica/` | O método: fluxo, estilo, roteiro, qualidade, conformidade, briefing |
| `template/` | Projeto Remotion: motor, temas e vídeo de demonstração |
| `ferramentas/` | Scripts, todos chamados por `python kit.py <comando>` |
| `memoria/` | Texto curto para a memória persistente da IA |

## O que não está aqui, de propósito

- Vídeos, fotos, trilhas, dados de clientes e de pacientes. Cada cliente tem a própria pasta, fora do repositório.
- Chaves de API e senhas.
- Modelos de IA (recorte e transcrição): baixados na instalação.
- Material de cursos de terceiros.

Rode `python kit.py varredura` antes de cada commit, e sempre antes de tornar o repositório público.

## Licenças

- **Remotion:** gratuito para pessoa física e empresa de até 3 pessoas. Acima disso, [exige licença paga](https://www.remotion.dev/license). Confira o seu caso.
- **Robust Video Matting** (modelo de recorte): GPL-3.0, baixado do [repositório oficial](https://github.com/PeterL1n/RobustVideoMatting).
- **Música e imagens:** confira a licença de cada item antes de usar em anúncio.
- **Este kit:** sem licença de uso definida. Todos os direitos reservados ao autor até que ele defina outra.

## Limites

- Regra de publicidade muda. `conformidade.md` aponta riscos, mas não substitui o conselho regional ou um advogado.
- A qualidade depende da gravação: luz, áudio e arquivo original. Veja `referencias/briefing.md`.
- O recorte funciona melhor com uma pessoa só na imagem.
- O kit foi calibrado com uma única cliente e testado com material de demonstração. Espere ajustes nos primeiros vídeos de outros clientes.
