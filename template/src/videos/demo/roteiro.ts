// Vídeo de demonstração: usa só material gerado por gerar_demo.py (nenhuma pessoa real).
// Mostra todos os elementos do estilo em ~19 s. Serve de exemplo para escrever um roteiro:
// cada elemento nasce de uma frase da fala e todos os tempos são do bruto.
import { Video } from "../../motor/tipos";
import edl from "./edl.json";
import enquadramento from "./enquadramento.json";

export const video: Video = {
  id: "demo",
  edl,
  enquadramento,
  midia: {
    apresentador: "demo/apresentador.mp4",
    voz: "demo/voz.wav",
    trilha: "demo/trilha.wav",
  },
  creditoBanco: "Imagens ilustrativas · material gerado",

  cenas: [
    // fala cita um lugar: vídeo de apoio em tela cheia
    { tipo: "broll", ini: 5.6, fim: 7.2, src: "demo/ambiente-a.mp4", srcIni: 0, entrada: "zoom", zoomDe: 1.0, zoomAte: 1.06 },
    { tipo: "broll", ini: 7.2, fim: 9.0, src: "banco/demo-ambiente-b.mp4", srcIni: 0, entrada: "whip", zoomDe: 1.0, zoomAte: 1.05, ilustrativa: true },
    // fala cita o resultado: cartão grande sobre o apresentador desfocado
    {
      tipo: "cartao",
      ini: 10.1,
      fim: 12.8,
      midias: [
        { src: "demo/caso-a.jpg", em: 10.1 },
        { src: "demo/caso-b.jpg", em: 11.4 },
      ],
      titulo: "Resultado",
      tituloEm: 11.6,
    },
    // fechamento: as palavras que resumem a fala
    {
      tipo: "resumo",
      ini: 14.1,
      fim: 15.8,
      palavras: [
        { t: 14.15, texto: "Planejamento" },
        { t: 14.55, texto: "Estrutura" },
        { t: 14.95, texto: "Segurança" },
      ],
    },
  ],

  grupos: [
    // fala enumera itens: um cartão salta em cada item
    {
      fim: 4.5,
      itens: [
        { t: 2.7, src: "demo/caso-a.jpg", rotulo: "Item um", x: 36, y: 1262, w: 350, h: 350, rot: -4 },
        { t: 3.2, src: "demo/caso-b.jpg", rotulo: "Item dois", x: 694, y: 1262, w: 350, h: 350, rot: 4 },
        { t: 3.7, src: "demo/caso-c.jpg", rotulo: "Item três", x: 372, y: 1420, w: 336, h: 336, rot: 0 },
      ],
    },
  ],

  letreiros: [
    {
      ini: 2.7,
      fim: 4.5,
      y: 1090,
      linhas: [
        { t: 2.7, texto: "os meus", estilo: "sans", tam: 60 },
        { t: 3.0, texto: "procedimentos?", estilo: "serif", tam: 128 },
      ],
    },
    {
      ini: 5.6,
      fim: 7.2,
      y: 1170,
      linhas: [
        { t: 5.6, texto: "aqui no meu", estilo: "sans", tam: 62 },
        { t: 6.0, texto: "consultório", estilo: "destaque", tam: 148 },
      ],
    },
  ],

  atras: [
    // o gancho: palavra grande passando atrás da cabeça
    { ini: 0.9, fim: 2.6, partes: ["on", "de"], vao: 340, tam: 282, y: 268, clipe: "demo/fg-a.webm", clipeIni: 0.6, clipeFim: 2.7 },
  ],

  legendas: [
    { t: 7.25, texto: "em uma estrutura" },
    { t: 8.1, fim: 8.95, texto: "adequada" },
    { t: 10.1, texto: "porque cirurgia" },
    { t: 11.0, texto: "não é apenas" },
    { t: 11.9, fim: 12.8, texto: "o resultado." },
    { t: 15.9, texto: "antes, durante" },
    { t: 16.5, fim: 17.2, texto: "e depois" },
  ],

  zooms: [
    { em: 0, z: "base" },
    { em: 2.7, z: "medio" },
    { em: 5.34, z: "perto" },
    { em: 9.84, z: "medio" },
    { em: 13.84, z: "base" },
    { em: 15.9, z: "perto" },
  ],

  flashes: [5.34, 13.84],
  selo: [
    [0.6, 4.4],
    [15.0, 17.2],
  ],
  sons: [
    { t: 0.9, som: "impacto", vol: 0.32 },
    { t: 0.92, som: "brilho", vol: 0.09 },
    { t: 2.7, som: "pop", vol: 0.2 },
    { t: 3.2, som: "pop", vol: 0.2 },
    { t: 3.7, som: "pop", vol: 0.2 },
    { t: 5.5, som: "whoosh", vol: 0.1 },
    { t: 6.0, som: "brilho", vol: 0.09 },
    { t: 7.12, som: "whoosh", vol: 0.12 },
    { t: 10.0, som: "whoosh", vol: 0.1 },
    { t: 11.6, som: "brilho", vol: 0.09 },
    { t: 14.15, som: "brilho", vol: 0.09 },
  ],
  capa: {
    imagem: "demo/capa.png",
    linha1: "Onde são realizados os meus",
    destaque: "procedimentos?",
    rodape: "Consultório · Estrutura · Segurança",
  },
};
