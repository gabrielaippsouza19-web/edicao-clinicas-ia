# O estilo

Vídeo vertical 1080×1920, 30 fps, para clínica que quer parecer cara e confiável sem parecer propaganda de loja. Nasceu de uma edição aprovada por uma cirurgiã, a partir de referências de anúncios premium que ela e o gestor gostavam. Os números abaixo já estão no motor (`template/src/motor`). Eles estão aqui para você saber o que é o quê, sem precisar reinventar.

## A ideia em uma frase

A pessoa fala olhando para a câmera, e tudo o que aparece nasce de uma palavra que ela acabou de dizer.

## Elementos

| Elemento | Como é | Quando usar |
|---|---|---|
| **Selo** | Pílula branca no topo (y 190) com pino, nome e registro | Primeiros ~4 s e últimos ~3 s da fala |
| **Legenda** | Branca, Inter 500, 54 px, y 1098, 2 a 3 palavras por vez, sombra suave | Quando não há letreiro nem cena com texto próprio |
| **Letreiro sans** | Inter 500, 60 a 76 px | Frase de apoio, antes da palavra forte |
| **Letreiro serif** | Playfair itálico 800, branco, 120 a 156 px | A palavra de impacto que não é da marca |
| **Letreiro destaque** | Playfair 700 com gradiente metálico que corre pela palavra, 120 a 168 px | A palavra que o vídeo quer deixar na cabeça |
| **Palavra atrás da cabeça** | Playfair itálico, 230 a 280 px, entre o fundo e o apresentador | No máximo 2 por vídeo, na pergunta do gancho e em uma virada |
| **Cartões pequenos** | Fotos com borda branca e rótulo, levemente girados, que saltam um a um | Quando a fala enumera itens |
| **Vídeo de apoio** | Tela cheia, com véu escuro embaixo para o texto | Quando a fala cita um lugar ou uma ação que dá para mostrar |
| **Cartão grande** | 900×900, cantos 54, sobre o apresentador desfocado, título metálico embaixo | Prova: resultado, caso, antes e depois autorizado |
| **Resumo** | Até 3 palavras metálicas empilhadas sobre o fundo desfocado | Fechamento de uma ideia |
| **Flash de luz** | Branco quente, ~0,5 s | Virada de bloco. No máximo a cada 10 ou 15 s |
| **Cartão final** | Fundo claro, arcos, nome, especialidade, registro e chamada | Sempre, 4 s |

## Ritmo

- Algo muda a cada 2 a 4 s: corte, enquadramento, letreiro ou cena.
- Três enquadramentos (`base`, `medio`, `perto`), trocados a cada corte. A troca esconde o salto de imagem.
- Aproximação lenta e contínua entre as trocas.
- Transições: zoom com desfoque, chicote lateral (`whip`, `whipEsq`). Duram 8 quadros.
- Abertura sai de um flash com desfoque em ~0,4 s.

## Enquadramento

O `preparar-video` mede a altura dos olhos e o centro do rosto no próprio recorte e grava em `enquadramento.json`. O motor calcula a escala para deixar os olhos em ~38% da altura. Por isso legendas e letreiros caem no mesmo lugar em gravações diferentes.

Confira na folha de quadros. Se a medida errar (cabelo volumoso, boné, duas pessoas), corrija `olhosY` e `centroX` à mão em `enquadramento.json`. Se a cabeça estiver muito perto do topo do quadro no bruto, peça para regravar: nenhum zoom cria espaço que não existe.

## Áreas seguras

- Texto importante longe dos 250 px de baixo e dos 220 px da direita, onde ficam os botões do Reels.
- Na capa, tudo dentro do recorte central que a grade do perfil mostra (y de 240 a 1680).

## Áudio

| Faixa | Nível |
|---|---|
| Voz | -16 LUFS depois da limpeza |
| Trilha | Normalizada em -12 LUFS. O motor toca em 0,085 sob a voz e sobe para 0,24 no cartão final |
| Efeitos | whoosh 0,08 a 0,12 · pop 0,2 · brilho 0,09 · impacto 0,25 a 0,32 |
| Master | -14 LUFS, até -1 dBTP, com ganho fixo e limitador |

Nunca use `loudnorm` no master: ele entrou em modo dinâmico e subiu a música no cartão final.

## Adaptar a cada cliente

| O que muda | Onde |
|---|---|
| Nome, registro, RQE, especialidade, chamada, canal, logo | `projeto/src/cliente.ts` |
| Paleta | `tema` em `cliente.ts`: escolha um dos 5 ou passe um objeto com as mesmas chaves de `motor/temas.ts` |
| Assinatura do nome | `assinatura: "script"` (manuscrita) ou `"serif"`. Serif costuma combinar mais com identidade sóbria |
| Cor da pele ou luz da gravação | `filtroApresentador` em `cliente.ts`, por exemplo `saturate(0.86) hue-rotate(-4deg) brightness(0.985) contrast(1.02)` para gravação alaranjada. O padrão é `none` |
| Fundo desfocado | `--fundo-desfocado` no `preparar-video`, só a pedido |

Escolha a paleta pelas artes que o cliente já usa, não pelo gênero da pessoa. Peça o logo e as artes: a identidade vem delas.

## O que evitar

- Caixa alta gritando, emoji, seta, moldura de "promoção".
- Música animada, batida forte, efeito de câmera tremendo.
- Mais de um foco na tela ao mesmo tempo.
- Selo, legenda e letreiro brigando pela mesma altura.
- Cor saturada de fundo no cartão final: claro e sóbrio funciona melhor com o resto.
