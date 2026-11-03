// Formato de dados da edição. Todos os tempos do roteiro são do BRUTO. A conversão para a
// edição é automática (ver tempo.ts), então refazer os cortes não desalinha nada.

export type Clip = { srcIni: number; srcFim: number; editIni: number };
export type Edl = { duracao: number; clips: Clip[] };

// ------------------------------------------------------------------ cenas de tela cheia
export type Entrada = "zoom" | "whip" | "whipEsq";
export type Broll = {
  tipo: "broll";
  ini: number;
  fim: number;
  src: string;
  srcIni: number;
  entrada: Entrada;
  zoomDe?: number;
  zoomAte?: number;
  origem?: string;
  rate?: number; // velocidade do vídeo (câmera lenta para caber na fala)
  ilustrativa?: boolean; // obrigatório em mídia de banco (pasta banco/)
};
export type MidiaCartao = { src: string; video?: boolean; srcIni?: number; em: number };
export type Cartao = {
  tipo: "cartao";
  ini: number;
  fim: number;
  midias: MidiaCartao[];
  titulo?: string;
  tituloEm?: number;
  ilustrativa?: boolean;
};
export type Resumo = { tipo: "resumo"; ini: number; fim: number; palavras: { t: number; texto: string }[] };
export type Cena = Broll | Cartao | Resumo;

// ------------------------------------------------------------------ cartões pequenos (polaroids)
export type CartaoPeq = {
  t: number;
  src: string;
  video?: boolean;
  srcIni?: number;
  rotulo?: string;
  x: number;
  y: number;
  w: number;
  h: number;
  rot: number;
};
export type GrupoCartoes = { fim: number; itens: CartaoPeq[]; ilustrativa?: boolean };

// ------------------------------------------------------------------ letreiros
export type Linha = { t: number; texto: string; estilo: "sans" | "serif" | "destaque"; tam?: number };
export type Letreiro = { ini: number; fim: number; y: number; linhas: Linha[] };

// palavra ATRÁS do apresentador (precisa de trecho com transparência, sem corte no meio)
// "partes": a palavra é dividida para a cabeça passar no meio sem esconder letra
export type Atras = {
  ini: number;
  fim: number;
  partes: string[];
  vao: number;
  tam: number;
  y: number;
  clipe: string;
  clipeIni: number;
  clipeFim: number;
};

export type Legenda = { t: number; fim?: number; texto: string };
export type Nivel = "base" | "medio" | "perto";
export type Zoom = { em: number; z: Nivel };
export type NomeSom = "whoosh" | "pop" | "brilho" | "impacto";
export type Som = { t: number; som: NomeSom; vol: number };

export type Capa = {
  imagem: string; // quadro extraído com capa_quadro.py
  linha1: string;
  destaque: string;
  rodape?: string;
  escala?: number;
  filtro?: string;
};

// ------------------------------------------------------------------ um vídeo
export type Video = {
  id: string; // só letras, números e hífen: vira o nome da composição
  edl: Edl;
  midia: { apresentador: string; voz: string; trilha: string };
  // medido por preparar_apresentador.py; normaliza o enquadramento de qualquer gravação
  enquadramento: { olhosY: number; centroX: number };
  filtroApresentador?: string; // sobrepõe o do cliente só neste vídeo
  creditoBanco?: string; // texto do aviso em mídia de banco
  segundosCta?: number;
  cenas: Cena[];
  grupos: GrupoCartoes[];
  letreiros: Letreiro[];
  atras: Atras[];
  legendas: Legenda[];
  zooms: Zoom[];
  flashes: number[];
  selo: [number, number][];
  sons: Som[];
  capa?: Capa;
};

// ------------------------------------------------------------------ identidade do cliente
export type Conselho = "CFM" | "CFO" | "outro";

export type Tema = {
  metalico: string; // palavras de destaque sobre o vídeo
  metalicoCapa?: string;
  linhaCapa?: string;
  acento: string; // pino e ponto do selo
  seloTexto: string;
  rotulo: { fundo: string; texto: string };
  fundo: string; // atrás do apresentador
  flash: string;
  final: {
    fundo: string;
    arco1: string;
    arco2: string;
    nome: string; // gradiente do nome no cartão final
    linha: string;
    texto: string;
    titulo: string;
  };
};

export type Cliente = {
  demo?: boolean; // só para o vídeo de demonstração do kit
  nome: string; // "Dra. Nome Sobrenome" ou "Dr. Nome Sobrenome"
  conselho: Conselho;
  profissao?: string; // peças médicas exigem a palavra Médico(a) ao lado do CRM
  registro: string; // "CRM-SP 123456" ou "CRO-MG 12.345"
  rqe?: string; // "RQE 1234"
  especialidade: string[];
  especialidadeRevisada?: boolean; // CFM sem RQE: só depois de conferir a conformidade
  cta: string[];
  canal?: string; // "Chame no WhatsApp"
  logo?: string;
  tema: string | Tema;
  assinatura: "script" | "serif";
  filtroApresentador?: string; // ajuste de cor só do apresentador; "none" por padrão
};
