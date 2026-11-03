import { Clip, Video } from "./tipos";

export const FPS = 30;
export const W = 1080;
export const H = 1920;

export const F = (s: number) => Math.round(s * FPS);

export const fimFala = (v: Video) => v.edl.duracao;
export const ctaIni = (v: Video) => fimFala(v) + 0.05;
export const duracao = (v: Video) => ctaIni(v) + (v.segundosCta ?? 4.0);

// tempo do bruto -> tempo da edição (dentro de um corte, cai no início do próximo trecho)
export const criarS2e = (clips: Clip[], fim: number) => (t: number): number => {
  for (const c of clips) {
    if (t < c.srcIni) return c.editIni;
    if (t <= c.srcFim) return c.editIni + (t - c.srcIni);
  }
  return fim;
};
