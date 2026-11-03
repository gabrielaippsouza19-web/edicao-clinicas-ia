import { Tema } from "./tipos";

// "ouro-creme" é a paleta do vídeo aprovado que deu origem ao estilo.
// As outras seguem a mesma lógica: destaque metálico claro sobre o vídeo e cartão final claro.
export const TEMAS: Record<string, Tema> = {
  "ouro-creme": {
    metalico: "linear-gradient(100deg,#b58a3a 0%,#f3dc9d 22%,#fff6d8 40%,#e2bf6f 58%,#fbeab8 76%,#b58a3a 100%)",
    metalicoCapa: "linear-gradient(100deg,#c79a48 0%,#f6e2a8 24%,#fff7dc 42%,#e6c477 60%,#fbeab8 78%,#c79a48 100%)",
    linhaCapa: "#d9b865",
    acento: "#b58a3a",
    seloTexto: "#2c2219",
    rotulo: { fundo: "linear-gradient(100deg,#e4c67c,#fbeec4 50%,#dcb965)", texto: "#3a2a12" },
    fundo: "#efe7da",
    flash: "radial-gradient(circle at 50% 42%, #ffffff 0%, #fffaf0 55%, #ffeccb 100%)",
    final: {
      fundo: "linear-gradient(170deg,#fbf6ec 0%,#f2e9d9 55%,#e9dcc6 100%)",
      arco1: "#c9a65c",
      arco2: "#e3cf9f",
      nome: "linear-gradient(100deg,#7a5718 0%,#a57c2c 30%,#c9a24e 50%,#a57c2c 70%,#7a5718 100%)",
      linha: "#b58a3a",
      texto: "#4f3e29",
      titulo: "#33261a",
    },
  },
  "rose-champanhe": {
    metalico: "linear-gradient(100deg,#b07a6a 0%,#f2cfc2 22%,#fff1ea 40%,#dca894 58%,#f8dccf 76%,#b07a6a 100%)",
    acento: "#b5766a",
    seloTexto: "#3a241d",
    rotulo: { fundo: "linear-gradient(100deg,#e6bfb2,#fbe9e2 50%,#dcae9e)", texto: "#4a2a22" },
    fundo: "#f2e6e0",
    flash: "radial-gradient(circle at 50% 42%, #ffffff 0%, #fff6f2 55%, #ffe3d8 100%)",
    final: {
      fundo: "linear-gradient(170deg,#fbf3ef 0%,#f3e4dd 55%,#e9d3c9 100%)",
      arco1: "#c9917f",
      arco2: "#e7c8bb",
      nome: "linear-gradient(100deg,#7d4b3e 0%,#a86c5b 30%,#c98f7c 50%,#a86c5b 70%,#7d4b3e 100%)",
      linha: "#b5766a",
      texto: "#553a31",
      titulo: "#3a241d",
    },
  },
  "azul-marinho": {
    metalico: "linear-gradient(100deg,#7d9cc4 0%,#d3e3f7 22%,#f4f9ff 40%,#a9c4e6 58%,#dfebfa 76%,#7d9cc4 100%)",
    acento: "#1f3f6e",
    seloTexto: "#12233f",
    rotulo: { fundo: "linear-gradient(100deg,#bcd0ea,#eaf2fb 50%,#aac2e2)", texto: "#14294a" },
    fundo: "#e6ebf2",
    flash: "radial-gradient(circle at 50% 42%, #ffffff 0%, #f4f8ff 55%, #dde9fb 100%)",
    final: {
      fundo: "linear-gradient(170deg,#f5f8fc 0%,#e8eef6 55%,#d9e3ef 100%)",
      arco1: "#5f83b3",
      arco2: "#b8cce4",
      nome: "linear-gradient(100deg,#132c52 0%,#234a80 30%,#3a6aa8 50%,#234a80 70%,#132c52 100%)",
      linha: "#1f3f6e",
      texto: "#2c4060",
      titulo: "#12233f",
    },
  },
  "verde-salvia": {
    metalico: "linear-gradient(100deg,#7f9a78 0%,#d8e6cf 22%,#f5faf0 40%,#aec6a3 58%,#e3eedb 76%,#7f9a78 100%)",
    acento: "#4f6f52",
    seloTexto: "#1f2e20",
    rotulo: { fundo: "linear-gradient(100deg,#c3d6b9,#eef5e8 50%,#b4cba8)", texto: "#24361f" },
    fundo: "#e9eee4",
    flash: "radial-gradient(circle at 50% 42%, #ffffff 0%, #f7fbf3 55%, #e3efd9 100%)",
    final: {
      fundo: "linear-gradient(170deg,#f6f9f2 0%,#e9f0e2 55%,#dbe6d1 100%)",
      arco1: "#7f9a78",
      arco2: "#c3d6b9",
      nome: "linear-gradient(100deg,#2f4a33 0%,#4f6f52 30%,#6c8f6c 50%,#4f6f52 70%,#2f4a33 100%)",
      linha: "#4f6f52",
      texto: "#3b4d3c",
      titulo: "#1f2e20",
    },
  },
  "grafite-prata": {
    metalico: "linear-gradient(100deg,#8f949b 0%,#e6e8eb 22%,#ffffff 40%,#b9bdc3 58%,#eceef0 76%,#8f949b 100%)",
    acento: "#3b3f45",
    seloTexto: "#1c1e21",
    rotulo: { fundo: "linear-gradient(100deg,#c8ccd1,#f1f2f4 50%,#b9bdc3)", texto: "#1c1e21" },
    fundo: "#e8e9eb",
    flash: "radial-gradient(circle at 50% 42%, #ffffff 0%, #f7f8f9 55%, #e4e6e9 100%)",
    final: {
      fundo: "linear-gradient(170deg,#f6f7f8 0%,#e9ebed 55%,#dadde0 100%)",
      arco1: "#7d8289",
      arco2: "#c4c8cd",
      nome: "linear-gradient(100deg,#1c1e21 0%,#3b3f45 30%,#62676e 50%,#3b3f45 70%,#1c1e21 100%)",
      linha: "#3b3f45",
      texto: "#3b3f45",
      titulo: "#1c1e21",
    },
  },
};

export const resolverTema = (tema: string | Tema): Tema => {
  if (typeof tema !== "string") return tema;
  const t = TEMAS[tema];
  if (!t) throw new Error(`Tema "${tema}" não existe. Opções: ${Object.keys(TEMAS).join(", ")}`);
  return t;
};
