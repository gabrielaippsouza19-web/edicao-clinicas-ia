# Qualidade

## Como revisar

1. Quadros primeiro (`stills`), em pontos onde algo muda. Procure: texto sobre o rosto, texto cortado, duas coisas na mesma altura, mídia errada para a frase.
2. Assista ao vídeo inteiro uma vez, com som, no tamanho do celular, antes de mexer. Quadro parado não prova sincronia nem corte.
3. Prioridade: mensagem e dados, depois voz e sincronia, depois enquadramento e leitura, por último acabamento.
4. Na revisão, mude só o que foi pedido e veja o trecho alterado com alguns segundos antes e depois.
5. Descubra a causa antes de mexer. Texto sobre o rosto pode ser posição, ordem de camadas ou recorte: corrija o mecanismo certo.
6. O mesmo erro voltou? Pare. Compare esperado e observado, teste uma hipótese no menor trecho possível. Não refaça tudo por tentativa.

## Defeitos que já aconteceram

| Sintoma | Causa | Correção |
|---|---|---|
| Cortes comem o início ou o fim das palavras, legenda adiantada | Em `.MOV` de iPhone o áudio pode começar ~0,7 s depois do vídeo. A transcrição fica deslocada | `transcrever.py` já alinha. Corte só pelo silêncio medido, nunca pela transcrição |
| Zoom exagerado, rosto cortado | Enquadramento mal medido (medir pelo contorno confunde cabelo comprido com ombros) | A medida usa detecção de rosto. Confira `metodo` em `enquadramento.json` e corrija `olhosY` à mão se preciso |
| Salto logo no primeiro segundo | Ruído curto antes da primeira palavra virou trecho | `montar-edl` retira trecho curto sem palavra nas pontas do bruto |
| Salto de imagem incomoda | Corte sem mudar o enquadramento, ou pausa pequena cortada | Trocar `base`, `medio`, `perto` em todo corte. Não cortar pausa abaixo de 0,7 s |
| Música sobe sozinha no fim | `loudnorm` em modo dinâmico | Ganho fixo e limitador (`renderizar` já faz) |
| Música alta demais ou inaudível | Trilha fora do nível esperado | `preparar-trilha` deixa em -12 LUFS |
| Manchas verdes nos pontos claros da pele | Altas luzes estouradas no próprio arquivo do celular | `--pele`, depois de confirmar nos quadros |
| Pele laranja | Luz da gravação | `filtroApresentador` em `cliente.ts` |
| Cliente recusou o fundo desfocado | Quer mostrar o lugar onde atende | Fundo real é o padrão. Desfoque só a pedido |
| Cliente recusou imagens de banco | Quer provar que atende lá de verdade | Pedir vídeos reais antes de recorrer a banco |
| Cliente achou repetitivo | Tema de um vídeo antigo | Conferir a lista de temas em `CLIENTE.md` antes de editar |
| Palavra atrás da cabeça ilegível | A cabeça cobre o meio | Dividir em `partes` com vão, ou subir `y` |
| Nome de paciente aparece na imagem | Legenda gravada no vídeo ou na foto | Ampliar a partir do topo ou recortar. Conferir no vídeo final |
| Vídeo de apoio borrado | Veio comprimido pelo WhatsApp | Pedir o original. Em último caso, `preparar-midia` |
| Vídeo de apoio escuro | Exposição | `preparar-midia --escuro`, se não for imagem de resultado |
| Render falha com `spawn ... chrome-headless-shell.exe ENOENT` no Windows | Caminho do projeto longo demais | Use uma pasta de caminho curto, como `C:\Edicao-IA\<cliente>` |
| Rótulo afirma mais do que a imagem mostra | Ex.: "pós-operatório" em um vídeo de avaliação | Rótulo que a imagem sustente, como "Acompanhamento" |

## Antes de renderizar

- [ ] `npm run validar` passou
- [ ] Nome e registro conferidos nas artes do cliente
- [ ] Tema não repete vídeo anterior
- [ ] Cada mídia combina com a frase em que entra
- [ ] Folha de quadros revisada: nada sobre o rosto, nada cortado, área segura respeitada
- [ ] Mídia de banco com aviso e em `public/banco/`

## Antes de entregar

- [ ] `--conferir`: todos os cortes em silêncio, diferenças de palavras explicadas
- [ ] Áudio entre -14,7 e -13,3 LUFS, pico até -0,7 dBFS
- [ ] Vídeo assistido inteiro com som
- [ ] Nenhum dado de paciente visível sem autorização
- [ ] Lista de `conformidade.md` passada e pendências avisadas
- [ ] `CLIENTE.md` atualizado

## Como pedir ajuste

Um pedido que dá para verificar tem tempo, problema e mudança: `00:08-00:10, a imagem cobre os olhos, mover para a esquerda, manter voz e legenda`. Se o cliente disser "não gostei", pergunte o que incomodou e em que momento antes de refazer.
