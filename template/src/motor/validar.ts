import { getStaticFiles } from "remotion";
import { resolverTema } from "./temas";
import { Cliente, Video } from "./tipos";

const midias = (v: Video): string[] => {
  const lista = [v.midia.apresentador, v.midia.voz, v.midia.trilha];
  for (const c of v.cenas) {
    if (c.tipo === "broll") lista.push(c.src);
    if (c.tipo === "cartao") c.midias.forEach((m) => lista.push(m.src));
  }
  v.grupos.forEach((g) => g.itens.forEach((i) => lista.push(i.src)));
  v.atras.forEach((a) => lista.push(a.clipe));
  v.sons.forEach((s) => lista.push(`audio/sfx/${s.som}.wav`));
  if (v.capa) lista.push(v.capa.imagem);
  return lista;
};

const usaBanco = (src: string) => src.startsWith("banco/");

// Para o render com uma mensagem clara antes de gastar tempo com um vídeo errado.
export const validarVideo = (v: Video, c: Cliente) => {
  const erros: string[] = [];

  // ---- identidade: nenhuma peça sai sem nome e registro
  resolverTema(c.tema);
  if (!c.demo) {
    if (!c.nome.trim() || c.nome.includes("PREENCHER")) erros.push("cliente.nome não preenchido");
    if (!c.registro.trim() || c.registro.includes("PREENCHER")) erros.push("cliente.registro não preenchido");
    if (c.conselho === "CFM") {
      if (!c.profissao) erros.push('CFM: informe cliente.profissao ("Médica" ou "Médico"), exigido ao lado do CRM');
      if (c.especialidade.length > 0 && !c.rqe && !c.especialidadeRevisada) {
        erros.push("CFM: especialidade sem RQE. Informe cliente.rqe ou revise o texto (ver referencias/conformidade.md)");
      }
    }
  }

  // ---- identificador da composição
  if (!/^[a-zA-Z0-9-]+$/.test(v.id)) erros.push(`id "${v.id}": use só letras, números e hífen`);

  // ---- mídia
  const publicos = new Set(getStaticFiles().map((f) => f.name));
  if (publicos.size > 0) {
    for (const m of new Set(midias(v))) {
      if (!publicos.has(m)) erros.push(`mídia ausente em public/: ${m}`);
    }
  }

  // ---- banco de imagens: sempre avisado
  const avisoFaltando = (src: string, ok?: boolean) => {
    if (usaBanco(src) && !ok) erros.push(`${src}: mídia de banco precisa de ilustrativa: true`);
  };
  for (const cena of v.cenas) {
    if (cena.tipo === "broll") avisoFaltando(cena.src, cena.ilustrativa);
    if (cena.tipo === "cartao") cena.midias.forEach((m) => avisoFaltando(m.src, cena.ilustrativa));
  }
  v.grupos.forEach((g) => g.itens.forEach((i) => avisoFaltando(i.src, g.ilustrativa)));
  if (c.conselho === "CFM" && !v.creditoBanco && midias(v).some(usaBanco)) {
    erros.push("CFM: mídia de banco exige citar a origem. Preencha video.creditoBanco");
  }

  // ---- tempos
  const crescente = (nome: string, t: number[]) => {
    t.forEach((x, k) => {
      if (k > 0 && x < t[k - 1]) erros.push(`${nome}: fora de ordem em ${x}`);
    });
  };
  crescente("legendas", v.legendas.map((l) => l.t));
  crescente("zooms", v.zooms.map((z) => z.em));
  crescente("cenas", v.cenas.map((x) => x.ini));
  if (v.zooms.length === 0 || v.zooms[0].em !== 0) erros.push("zooms: o primeiro precisa estar em 0");
  v.cenas.forEach((x) => {
    if (x.fim <= x.ini) erros.push(`cena em ${x.ini}: fim antes do início`);
  });
  const ultimoSrc = v.edl.clips[v.edl.clips.length - 1]?.srcFim ?? 0;
  const foraDoBruto = (nome: string, t: number) => {
    if (t > ultimoSrc + 0.5) erros.push(`${nome} em ${t}: depois do fim da fala (${ultimoSrc})`);
  };
  v.legendas.forEach((l) => foraDoBruto("legenda", l.t));
  v.cenas.forEach((x) => foraDoBruto("cena", x.ini));
  v.flashes.forEach((t) => foraDoBruto("flash", t));

  // ---- palavra atrás: a camada transparente não pode atravessar um corte
  for (const a of v.atras) {
    const dentro = v.edl.clips.some((k) => a.clipeIni >= k.srcIni && a.clipeFim <= k.srcFim);
    if (!dentro) erros.push(`palavra atrás "${a.partes.join("")}": o trecho ${a.clipeIni}-${a.clipeFim} atravessa um corte`);
  }

  if (erros.length > 0) {
    throw new Error(`Roteiro "${v.id}" com ${erros.length} problema(s):\n- ${erros.join("\n- ")}`);
  }
};
