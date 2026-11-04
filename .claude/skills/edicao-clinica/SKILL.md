---
name: edicao-clinica
description: Edita vídeos verticais de médicos, dentistas e clínicas (Reels, Stories, anúncios) a partir do bruto, em um estilo premium validado por cliente real, com cortes só em silêncio medido, legendas curtas, palavras de destaque, prova visual e cartão final. Use quando pedirem para editar, refazer ou revisar vídeo de doutor ou doutora, criar capa de Reels de clínica, cadastrar cliente de edição ou instalar este kit.
---

# Edição de vídeo para clínicas

Kit instalado em: `{{KIT}}` (se aparecer esse texto com chaves, o kit é a raiz deste repositório).
Todos os comandos: `python {{KIT}}/kit.py <comando>`. Sem argumentos, o `kit.py` lista os comandos.

Leia antes de agir:
- [referencias/estilo.md](referencias/estilo.md): como o vídeo tem que parecer, com medidas.
- [referencias/receita-roteiro.md](referencias/receita-roteiro.md): como transformar a fala em cenas.
- [referencias/qualidade.md](referencias/qualidade.md): defeitos conhecidos e checklists.
- [referencias/conformidade.md](referencias/conformidade.md): regras do CFM e do CFO. Leia antes de usar imagem de paciente ou de procedimento.
- [referencias/briefing.md](referencias/briefing.md): o que perguntar a um cliente novo.
- [referencias/ferramentas-extras.md](referencias/ferramentas-extras.md): Hyperframes, Openverse, OBS e Epidemic Sound.

## Regras que não mudam

1. **Corte só em silêncio medido.** Nunca corte pela transcrição. A causa da pior reclamação que este fluxo já teve foi a transcrição adiantada em relação ao vídeo.
2. **Não invente.** Nada de resultado, número, depoimento, nome ou registro que não venha do cliente. Sem nome e registro confirmados nas artes dele, o motor não renderiza.
3. **Fundo real enquanto a pessoa fala.** Só use `--fundo-desfocado` se o cliente pedir. Cliente quer provar que atende naquele lugar.
4. **Material real antes de banco de imagens.** Banco só com aviso na tela, e nunca como caso, resultado ou paciente.
5. **Não repita tema nem paciente** de vídeos anteriores do cliente. Confira `CLIENTE.md` antes de começar: repetir tema já derrubou um vídeo bem editado.
6. **Dados de paciente ficam na pasta do cliente.** Não copie nome, foto ou print para notas, memória, repositório ou mensagem. Se a imagem tiver nome ou legenda gravados, recorte antes de usar.
7. **Conformidade antes da entrega.** Passe a lista de `conformidade.md` e diga ao usuário o que precisa de confirmação. Você não dá parecer jurídico: aponta o risco e o artigo.
8. **Mostre antes de renderizar tudo.** Folha de quadros primeiro, vídeo inteiro depois. Na revisão, mude só o que foi pedido.

## Fluxo

Pasta de trabalho: `<raiz>/<cliente>/`, fora de OneDrive, Dropbox e similares.

### 1. Cliente

Cliente novo: faça as perguntas de `briefing.md`, depois:

```bash
python {{KIT}}/kit.py novo-cliente dra-nome --raiz C:/Edicao-IA --nome "Dra. Nome Sobrenome" --conselho CFM --profissao Médica --registro "CRM-SP 123456" --rqe "RQE 1234" --especialidade "Dermatologia" --tema rose-champanhe --canal "Chame no WhatsApp"
```

Dentista: `--conselho CFO --registro "CRO-MG 12.345"`. Temas: `ouro-creme`, `rose-champanhe`, `azul-marinho`, `verde-salvia`, `grafite-prata`. Assinatura do nome: `--assinatura script` (manuscrita) ou `serif`.

Cliente que já existe: leia `CLIENTE.md`, com preferências, temas e pacientes já usados.

### 2. Bruto

Guarde o bruto em `originais/` e nunca altere esse arquivo. Depois:

```bash
python {{KIT}}/kit.py diagnostico-video originais/video.MOV
python {{KIT}}/kit.py preparar-video <pasta_cliente> <id-do-video> originais/video.MOV
```

O `preparar-video` transcreve, corta, recorta o apresentador, limpa a voz, prepara a trilha e escreve um rascunho de roteiro que já renderiza. Em 1 min de bruto, leva de 10 a 15 min em CPU.

Leia a transcrição em `analise/<id>/transcricao.json`:
- **Frase regravada ou erro de fala:** ache o tempo e refaça com `--descartar ini-fim --refazer-cortes`.
- **Termo errado** (nome de procedimento, marca): acrescente em `correcoes.json` e refaça os cortes.
- **Música do cliente ou licenciada:** `--trilha arquivo`. Sem isso, entra uma trilha ambiente sintetizada, livre de direitos.
- **Manchas verdes na pele:** a ferramenta avisa quando desconfia. Olhe os quadros. Se o defeito existir, apague `public/<id>/apresentador.mp4` e `analise/<id>/camadas/cor.mp4` e rode de novo com `--pele`.

### 3. Material

Separe em `assets/`: `casos/` (resultados, com autorização), `ambiente/` (consultório, equipe), `banco/`, `marca/`.

```bash
python {{KIT}}/kit.py catalogar assets/casos analise/catalogo casos
python {{KIT}}/kit.py normalizar-imagens assets/casos projeto/public/casos
python {{KIT}}/kit.py preparar-midia assets/ambiente/consulta.mp4 projeto/public/ambiente/consulta.mp4
```

Olhe as folhas de contato. Copie para `projeto/public/` só o que vai usar. Imagem de banco vai em `projeto/public/banco/`, para o motor exigir o aviso.

### 4. Roteiro

Edite `projeto/src/videos/<id>/roteiro.ts` seguindo `receita-roteiro.md`. Comece listando, para o usuário, o que entra em cada frase. Depois:

```bash
cd projeto
npm run validar
python {{KIT}}/kit.py stills . <id-do-video> ../analise/<id>/folha.jpg 5 1.5,4,7,10,13,16,20,24,28,32
```

Abra a folha e olhe de verdade. Se a sua ferramenta não mostra imagem, diga isso ao usuário: sem olhar, a revisão não foi feita.

### 5. Entrega

```bash
python {{KIT}}/kit.py renderizar <pasta_cliente> <id-do-video> v1 --capa --conferir
```

Entrega em `entregas/`, com master em -14 LUFS e até -1 dBTP. O `--conferir` transcreve o final e compara com o bruto: leia o resultado e explique qualquer diferença. Palavras curtas como "a" e "e" costumam ser variação da transcrição, e não corte. Em caso de dúvida, ouça o trecho. Use uma versão nova a cada rodada.

Atualize `CLIENTE.md` com tema, pacientes usados, feedback e versão aprovada.

## Ao terminar uma edição, diga

- Onde está o arquivo, duração e medidas de áudio.
- O que `--conferir` encontrou.
- O que precisa de confirmação: autorização de imagem, itens da conformidade, dados pendentes.
- O que você não conseguiu verificar.
