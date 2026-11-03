# Da fala ao roteiro

O `roteiro.ts` é só dados. Todos os tempos são do **bruto** e o motor converte para a edição, então refazer os cortes não desalinha nada. O exemplo completo está em `template/src/videos/demo/roteiro.ts`.

## Como pensar

1. Leia a transcrição inteira e diga em uma frase do que o vídeo trata. Confira em `CLIENTE.md` se esse tema já foi usado. Se já foi, avise antes de continuar.
2. Separe a fala em blocos: gancho, desenvolvimento, prova, fechamento.
3. Para cada frase, pergunte: **o que ela nomeia que dá para mostrar?**
4. Use só o material que existe. Se a frase não tiver imagem real, deixe a pessoa falando: rosto bem enquadrado com legenda boa é melhor do que imagem genérica.
5. Mostre o mapa ao usuário antes de escrever o código, assim:

```
12,4 s  "aqui no meu consultório"     vídeo do consultório + letreiro "consultório"
19,6 s  "de acordo com a complexidade" vídeo de avaliação
43,4 s  "não é apenas o resultado"     cartão grande com 3 casos autorizados
```

## Qual elemento para qual frase

| A fala... | Use |
|---|---|
| Faz a pergunta do gancho | `atras` em uma palavra curta + `letreiros` para o resto |
| Enumera itens ("blefaroplastia, papada, rinoplastia") | `grupos`: um cartão salta em cada item, no tempo exato da palavra |
| Cita um lugar ou uma ação que dá para filmar | `cenas` tipo `broll` |
| Cita resultado ou caso | `cenas` tipo `cartao`, se houver autorização |
| Diz a palavra central do vídeo | `letreiros` com estilo `destaque` |
| Resume em palavras ("planejamento, estrutura, segurança") | `broll` curtos e fecha com `resumo` |
| Sequência no tempo ("antes, durante, depois") | `grupos` com rótulos |
| Explica sem nada para mostrar | Apresentador e `legendas` |

## Formato de cada parte

```ts
// tela cheia. srcIni = de onde o vídeo de apoio começa. rate < 1 = câmera lenta
{ tipo: "broll", ini: 10.84, fim: 12.42, src: "ambiente/consulta.mp4", srcIni: 0.1, entrada: "zoom", zoomDe: 1.0, zoomAte: 1.05 }

// cartão grande. "em" é quando cada mídia entra
{ tipo: "cartao", ini: 43.46, fim: 47.0, midias: [{ src: "casos/a.jpg", em: 43.46 }, { src: "casos/b.jpg", em: 44.9 }], titulo: "Resultado", tituloEm: 46.0 }

// resumo. Até 3 palavras
{ tipo: "resumo", ini: 55.5, fim: 57.2, palavras: [{ t: 55.52, texto: "Planejamento" }, { t: 55.72, texto: "Estrutura" }] }

// cartões pequenos. Área livre: y de 1210 a 1800. Largura de 336 a 470
{ fim: 6.0, itens: [{ t: 4.14, src: "casos/a.jpg", rotulo: "Blefaroplastia", x: 36, y: 1262, w: 350, h: 350, rot: -4 }] }

// letreiro. Enquanto ele aparece, tire a legenda desse trecho
{ ini: 10.84, fim: 12.42, y: 1170, linhas: [
  { t: 10.84, texto: "aqui no meu", estilo: "sans", tam: 62 },
  { t: 11.6, texto: "consultório", estilo: "destaque", tam: 148 },
] }

// legenda. Sem "fim", vai até a próxima
{ t: 12.64, texto: "onde eu acompanho" }

// zoom em cima do início de um corte troca seco; no meio de um trecho, troca suave
{ em: 10.84, z: "perto" }

// som. Tempo do bruto: whoosh ~0,08 s antes da troca
{ t: 12.32, som: "whoosh", vol: 0.12 }
```

Regra de tempo: use o início da palavra na transcrição. Cena que acompanha a fala entra junto com a palavra, não antes.

Para evitar sobreposição: legenda some quando há letreiro. Em cena `cartao` a legenda sobe automaticamente. Em `broll`, letreiro e legenda ficam na parte de baixo, onde já existe um véu escuro.

## Palavra atrás da cabeça

Precisa de um trecho transparente que não atravesse corte. Tempos do bruto:

```bash
python kit.py clipe-alpha analise/<id>/camadas 2.6 4.3 projeto/public/<id>/fg-a.webm
```

```ts
{ ini: 2.84, fim: 4.14, partes: ["on", "de"], vao: 340, tam: 282, y: 268, clipe: "<id>/fg-a.webm", clipeIni: 2.6, clipeFim: 4.3 }
```

A cabeça não pode esconder letras. Palavra curta: divida em `partes` com um `vao` da largura da cabeça. Palavra longa: `y` mais alto, para só a base dela ficar atrás. Se a pessoa se mexe muito no trecho, escolha outro.

## Capa

Veja os quadros, escolha um com olhar para a câmera e expressão boa:

```bash
python kit.py folha-rostos originais/video.MOV analise/<id>/rostos.jpg 6 5 8 12 15 20 24
python kit.py capa-quadro originais/video.MOV 12 projeto/public/<id>/capa.png
```

```ts
capa: { imagem: "<id>/capa.png", linha1: "Onde são realizados os meus", destaque: "procedimentos?", rodape: "Consultório · Bloco cirúrgico · Segurança" }
```

## Vídeo de apoio ruim

Veio do WhatsApp, em baixa resolução? Peça o original. Se não houver, `preparar-midia` amplia e limpa, e `--escuro` levanta vídeo escuro. Se o vídeo for mais curto do que a fala, `--lento 0.68` faz câmera lenta com interpolação, ou use `rate` no roteiro para ajustes pequenos.

Nome, legenda ou arroba gravados na imagem de um paciente: recorte antes de usar, ou use `origem` e `zoomDe` no `broll` para deixar fora do quadro. Confira depois de renderizar.

Não aplique melhora em foto ou vídeo de resultado de paciente. Veja `conformidade.md`.
