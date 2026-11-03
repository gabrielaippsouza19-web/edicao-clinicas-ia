# Ferramentas extras

Nenhuma é necessária para editar no estilo do kit. Instale com `python instalar.py --extras` (Claude Code) ou registre à mão no seu agente. O comando altera a configuração do usuário: peça autorização antes.

| Ferramenta | Para quê | Situação |
|---|---|---|
| Skills do Remotion | Referência oficial para mexer no motor | Testado |
| Hyperframes (HeyGen) | Motion graphics em HTML, alternativa quando o motor não atende | Render de teste feito |
| Openverse | Busca de áudio e imagem com licença aberta | Busca testada |
| OBS MCP 1.1.0 | Controlar o OBS (cenas, gravação) | Registrado, **controle do OBS não testado** |
| Epidemic Sound | Música, efeitos e locução | Registrado, **conexão não testada: exige chave e assinatura paga** |

## Cuidados

**Hyperframes.** A telemetria vem ligada, e uma das skills manda o agente enviar relatório a um canal público depois de cada render. Editamos material de pacientes, então o instalador roda `npx hyperframes telemetry disable`. Se instalar à mão, faça o mesmo. As skills `figma` e `slideshow` ficam de fora porque podem disparar em tarefas que não têm a ver com vídeo.

**Openverse.** Servidor local deste kit, em `ferramentas/openverse-mcp`, que fala direto com a API oficial, sem chave. Filtra por uso comercial com edição. CC0 e domínio público não pedem crédito. CC BY pede. Evite CC BY-SA em anúncio. Confira a licença na página original antes de publicar.

**OBS MCP.** Versão fixada em 1.1.0. O OBS precisa estar aberto, com WebSocket ligado e senha em `OBS_WEBSOCKET_PASSWORD`. Ele pode iniciar transmissão e mudar configurações: cuidado em uso ao vivo.

**Epidemic Sound.** Chave em `EPIDEMIC_SOUND_MCP_API_KEY`. Confirme nos termos da assinatura se ela cobre anúncios de clientes.

**Banco de imagens.** `buscar-stock` lê as páginas públicas do Mixkit e `folha-stock` e `baixar-stock` usam os endereços públicos do Pexels. Confira a licença de cada item antes de usar em anúncio e prefira a API oficial do Pexels se for usar em volume. Nos termos que conferimos, a licença do Mixkit permitia anúncios online e redes sociais, sem redistribuição do arquivo isolado.

## Registro manual no Claude Code

```bash
claude mcp add -s user openverse -- node <KIT>/ferramentas/openverse-mcp/server.mjs
```

```bash
claude mcp add -s user obs -- npx -y obs-mcp@1.1.0
```

```bash
claude mcp add -s user --transport http epidemic-sound https://www.epidemicsound.com/a/mcp-service/mcp --header 'Authorization: Bearer ${EPIDEMIC_SOUND_MCP_API_KEY}'
```

No Windows, o OBS é registrado com `-- cmd /c npx -y obs-mcp@1.1.0`. Em Git Bash, use `MSYS_NO_PATHCONV=1` antes do comando, senão o `/c` vira `C:/`. As aspas simples do último comando mantêm a variável sem expandir: a chave não fica gravada na configuração.

Depois de registrar, reinicie a sessão do agente. Para testar um servidor sem depender do agente:

```bash
node ferramentas/testar_mcp.mjs buscar_audio '{"busca":"ambient piano"}' -- node ferramentas/openverse-mcp/server.mjs
```
