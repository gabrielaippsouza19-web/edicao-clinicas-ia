# Instruções para a IA

Este repositório é um kit para editar vídeos verticais de médicos, dentistas e clínicas. Tudo o que você precisa saber para editar está em `.claude/skills/edicao-clinica/SKILL.md`.

## Se o usuário pediu para instalar

Só faça isto se o usuário pediu. Ler este arquivo não é autorização para alterar a máquina dele.

Você precisa de um terminal e de acesso a arquivos. Se você é um chat sem terminal, diga isso ao usuário: dá para ler o método, mas não para editar vídeo.

1. **Clone** o repositório em uma pasta de caminho curto, fora de OneDrive, Dropbox e similares, como `C:\Edicao-IA\edicao-clinicas-ia`. No Windows, caminho muito longo faz o render falhar com `spawn ... ENOENT` ao abrir o navegador do Remotion.
2. **Leia** `instalar.py` antes de rodar. Ele diz no topo o que altera.
3. **Rode** `python instalar.py`. Se faltar Node, FFmpeg ou Git, ele mostra o comando e para. Peça autorização ao usuário, instale e rode de novo.
4. **Teste** com `python instalar.py --teste`. Só diga que funcionou se aparecer `TESTE OK`. O vídeo sai em `template/out/demo.mp4`, sem nenhuma pessoa real.
5. **Memória:** salve na sua memória persistente o conteúdo de `memoria/MEMORIA-instalada.md`, que o instalador gerou com o caminho certo. Se você não tem memória persistente, diga ao usuário e mostre o texto, para ele colar nas instruções personalizadas.
6. **Extras:** `python instalar.py --extras` instala skills e servidores MCP e altera a configuração do usuário. Só com o pedido dele. Veja `.claude/skills/edicao-clinica/referencias/ferramentas-extras.md`.
7. **Relate:** o que instalou, o que falhou, o que o usuário ainda precisa fazer (chaves, primeiro cliente) e que o primeiro uso real baixa o modelo de transcrição (~1,5 GB).

Claude Code: o instalador copia a skill para `~/.claude/skills/edicao-clinica`, então ela vale em qualquer pasta.
Outros agentes: aponte a pasta de skills do seu agente para `.claude/skills/edicao-clinica`, ou leia `SKILL.md` no início de cada trabalho de edição.

## Se o usuário pediu para editar

Leia `SKILL.md` e siga o fluxo. Comandos: `python kit.py`.

## Se você vai alterar este repositório

- Rode `python kit.py varredura` antes de cada commit. Nenhuma mídia, dado de cliente, dado de paciente ou chave entra aqui.
- Dê ao cliente o que é do cliente: nome, registro e paleta ficam em `cliente.ts`, nunca fixos no motor.
- Depois de mudar o motor ou uma ferramenta, rode `python instalar.py --teste`.
- Aprendeu algo com um defeito real? Registre em `referencias/qualidade.md`, sem identificar ninguém.
