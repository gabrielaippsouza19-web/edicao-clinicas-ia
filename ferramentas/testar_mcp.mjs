// Testa um servidor MCP stdio: initialize, tools/list e, opcionalmente, uma chamada.
// Uso: node testar_mcp.mjs '<nome_ferramenta>' '<args json>' -- comando arg1 arg2 ...
import { spawn } from "node:child_process";

const sep = process.argv.indexOf("--");
const [ferramenta, argsJson] = process.argv.slice(2, sep);
const [cmd, ...cmdArgs] = process.argv.slice(sep + 1);
const filho = spawn(cmd, cmdArgs, { stdio: ["pipe", "pipe", "pipe"], shell: process.platform === "win32" });

let buffer = "";
const pendentes = new Map();
filho.stdout.on("data", (d) => {
  buffer += d.toString();
  let i;
  while ((i = buffer.indexOf("\n")) >= 0) {
    const linha = buffer.slice(0, i).trim();
    buffer = buffer.slice(i + 1);
    if (!linha) continue;
    try {
      const msg = JSON.parse(linha);
      if (pendentes.has(msg.id)) {
        pendentes.get(msg.id)(msg);
        pendentes.delete(msg.id);
      }
    } catch {
      /* linha que nao e JSON-RPC */
    }
  }
});
let stderr = "";
filho.stderr.on("data", (d) => (stderr += d.toString()));
filho.on("exit", (c) => {
  console.log(`[processo terminou, codigo ${c}] ${stderr.trim().split("\n").slice(-2).join(" | ")}`);
  process.exit(0);
});

let id = 0;
const chamar = (method, params) =>
  new Promise((res, rej) => {
    const n = ++id;
    pendentes.set(n, res);
    filho.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: n, method, params }) + "\n");
    setTimeout(() => rej(new Error(`tempo esgotado em ${method}`)), 90000);
  });

try {
  const ini = await chamar("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "teste", version: "1" },
  });
  console.log("servidor:", JSON.stringify(ini.result?.serverInfo));
  filho.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
  const lista = await chamar("tools/list", {});
  console.log(`ferramentas (${lista.result?.tools?.length}):`, lista.result?.tools?.slice(0, 8).map((t) => t.name).join(", "));
  if (ferramenta && ferramenta !== "-") {
    const r = await chamar("tools/call", { name: ferramenta, arguments: JSON.parse(argsJson) });
    if (r.result?.isError) console.log("ERRO:", JSON.stringify(r.result).slice(0, 400));
    else {
      const dados = JSON.parse(r.result.content[0].text);
      console.log("total:", dados.total);
      for (const x of dados.resultados.slice(0, 3)) {
        console.log(" -", x.titulo, "|", x.licenca, "|", x.duracao_s ?? "", "s |", x.fonte, "|", x.arquivo);
      }
    }
  }
} catch (e) {
  console.log("falha:", e.message);
}
filho.kill();
process.exit(0);
