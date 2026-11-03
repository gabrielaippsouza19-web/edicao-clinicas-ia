#!/usr/bin/env node
// Servidor MCP local para o Openverse (mídia com licença aberta).
// Fala direto com a API oficial, sem chave e sem gateway de terceiro.
// Por padrão só traz o que pode ser usado em anúncio e editado (CC0, CC BY, CC BY-SA, PDM).
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const API = "https://api.openverse.org/v1";
const TIMEOUT_MS = 60000;

const consultar = async (caminho, params) => {
  const url = new URL(`${API}/${caminho}/`);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, String(v));
  }
  const resposta = await fetch(url, {
    headers: { "User-Agent": "openverse-mcp-local/1.0" },
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  if (!resposta.ok) {
    throw new Error(`Openverse respondeu ${resposta.status}: ${(await resposta.text()).slice(0, 200)}`);
  }
  return resposta.json();
};

const resumir = (r) => ({
  id: r.id,
  titulo: r.title,
  autor: r.creator,
  licenca: `${r.license} ${r.license_version ?? ""}`.trim(),
  url_licenca: r.license_url,
  atribuicao: r.attribution,
  arquivo: r.url,
  pagina: r.foreign_landing_url,
  fonte: r.source,
  formato: r.filetype,
  duracao_s: r.duration ? Math.round(r.duration / 1000) : undefined,
  largura: r.width,
  altura: r.height,
});

const responder = (dados) => ({
  content: [
    {
      type: "text",
      text: JSON.stringify(
        {
          total: dados.result_count,
          aviso:
            "CC0 e PDM não exigem crédito. CC BY exige crédito ao autor (campo atribuicao). CC BY-SA também exige compartilhar pela mesma licença: evite em anúncio. Confira a licença na página original antes de publicar.",
          resultados: dados.results.map(resumir),
        },
        null,
        1,
      ),
    },
  ],
});

const LICENCA = z
  .enum(["uso_comercial_e_edicao", "uso_comercial", "qualquer"])
  .default("uso_comercial_e_edicao")
  .describe("uso_comercial_e_edicao serve para anúncio com edição; qualquer inclui licenças não comerciais");
const TIPO = {
  uso_comercial_e_edicao: "commercial,modification",
  uso_comercial: "commercial",
  qualquer: "",
};

const server = new McpServer({ name: "openverse-local", version: "1.0.0" });

server.tool(
  "buscar_audio",
  "Busca música e efeitos sonoros com licença aberta no Openverse. Devolve licença, atribuição e link do arquivo.",
  {
    busca: z.string().describe("Termos em inglês funcionam melhor, ex.: ambient piano"),
    licenca: LICENCA,
    categoria: z.enum(["music", "sound_effect", "podcast", "audiobook", "news", "pronunciation"]).optional(),
    duracao: z.enum(["shortest", "short", "medium", "long"]).optional(),
    quantidade: z.number().int().min(1).max(20).default(10),
  },
  async ({ busca, licenca, categoria, duracao, quantidade }) =>
    responder(
      await consultar("audio", {
        q: busca,
        license_type: TIPO[licenca],
        category: categoria,
        length: duracao,
        page_size: quantidade,
      }),
    ),
);

server.tool(
  "buscar_imagem",
  "Busca imagens com licença aberta no Openverse. Devolve licença, atribuição e link do arquivo.",
  {
    busca: z.string().describe("Termos em inglês funcionam melhor"),
    licenca: LICENCA,
    formato: z.enum(["square", "tall", "wide"]).optional(),
    tamanho: z.enum(["small", "medium", "large"]).optional(),
    quantidade: z.number().int().min(1).max(20).default(10),
  },
  async ({ busca, licenca, formato, tamanho, quantidade }) =>
    responder(
      await consultar("images", {
        q: busca,
        license_type: TIPO[licenca],
        aspect_ratio: formato,
        size: tamanho,
        page_size: quantidade,
      }),
    ),
);

await server.connect(new StdioServerTransport());
