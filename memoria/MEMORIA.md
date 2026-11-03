Kit de edição de vídeo para clínicas instalado em `{{KIT}}`. Para editar vídeo de médico, dentista ou clínica, leia `{{KIT}}/.claude/skills/edicao-clinica/SKILL.md` e rode as ferramentas com `python {{KIT}}/kit.py <comando>`.

Regras que valem sempre nesse trabalho:
- Cortar só dentro de silêncio medido, nunca pela transcrição.
- Não inventar resultado, número, nome ou registro. Nome e registro vêm das artes do cliente.
- Fundo real enquanto a pessoa fala, salvo pedido do cliente. Material real antes de banco de imagens.
- Conferir em `CLIENTE.md` os temas e pacientes já usados: repetir tema já derrubou vídeo bem editado.
- Dados e imagens de pacientes ficam na pasta do cliente, nunca em memória, repositório ou mensagem.
- Antes de entregar, passar a lista de conformidade (CFM 2.336/2023, CFO 196/2019) e avisar o que está pendente, principalmente autorização de imagem e cena de procedimento.
- Folha de quadros antes de renderizar. Master com ganho fixo e limitador, nunca loudnorm.
