import React, { createContext, useContext, useMemo } from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { caber, INTER, PLAYFAIR, PLAYFAIR_IT, SCRIPT } from "./fontes";
import { SeloPilula } from "./SeloPilula";
import { resolverTema } from "./temas";
import { criarS2e, ctaIni, duracao, F, FPS, fimFala, H, W } from "./tempo";
import {
  Atras,
  Broll as BrollT,
  Cartao as CartaoT,
  CartaoPeq,
  Cliente,
  GrupoCartoes,
  Linha,
  Nivel,
  Resumo as ResumoT,
  Tema,
  Video,
} from "./tipos";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const easeOut = Easing.out(Easing.cubic);
const TRANS = 8;

// ------------------------------------------------------------------ enquadramento
// A base deixa os olhos em ~38% da altura e a parte de baixo do vídeo colada na borda.
// Os outros níveis são proporcionais, então qualquer gravação cai no mesmo desenho de tela.
const niveisPara = (olhosSrc: number): Record<Nivel, { s: number; olhos: number }> => {
  const base = Math.max(1, (H - 733) / (H - olhosSrc));
  return {
    base: { s: base, olhos: 733 },
    medio: { s: base * 1.076, olhos: 715 },
    perto: { s: base * 1.181, olhos: 695 },
  };
};

// ------------------------------------------------------------------ dados derivados do roteiro
type CenaEd = (BrollT | CartaoT | ResumoT) & { de: number; ate: number };

const montar = (video: Video, cliente: Cliente) => {
  const fala = fimFala(video);
  const s2e = criarS2e(video.edl.clips, fala);
  const E = (t: number) => F(s2e(t)); // tempo do bruto -> frame da edição
  const cenas: CenaEd[] = video.cenas.map((c) => ({ ...c, de: E(c.ini), ate: Math.min(E(c.fim), F(fala)) }));
  const niveis = niveisPara(video.enquadramento.olhosY);
  const centroX = video.enquadramento.centroX;
  const inicioClipes = new Set(video.edl.clips.map((c) => F(c.editIni)));
  const zoomEventos = video.zooms.map((z) => ({ f: E(z.em), z: z.z })).sort((a, b) => a.f - b.f);

  const enquadramento = (f: number) => {
    let i = 0;
    zoomEventos.forEach((e, k) => {
      if (e.f <= f) i = k;
    });
    const atual = niveis[zoomEventos[i].z];
    const prev = niveis[zoomEventos[Math.max(0, i - 1)].z];
    const desde = f - zoomEventos[i].f;
    const seco = inicioClipes.has(zoomEventos[i].f);
    const p = seco ? 1 : interpolate(desde, [0, 7], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
    const deriva = 1 + Math.min(0.03, desde * 0.00035); // aproximação lenta contínua
    const s = (prev.s + (atual.s - prev.s) * p) * deriva;
    const olhos = prev.olhos + (atual.olhos - prev.olhos) * p;
    const tx = Math.min(0, Math.max(W * (1 - s), W / 2 - s * centroX));
    const ty = Math.min(0, Math.max(H * (1 - s), olhos - s * video.enquadramento.olhosY));
    return `translate(${tx}px, ${ty}px) scale(${s})`;
  };

  return {
    video,
    cliente,
    tema: resolverTema(cliente.tema),
    filtro: video.filtroApresentador ?? cliente.filtroApresentador ?? "none",
    credito: video.creditoBanco ?? "Imagens ilustrativas",
    E,
    cenas,
    cenaEm: (f: number) => cenas.find((c) => f >= c.de && f < c.ate),
    enquadramento,
    fala,
    cta: ctaIni(video),
    total: duracao(video),
  };
};

type Contexto = ReturnType<typeof montar>;
const Ctx = createContext<Contexto | null>(null);
const useEd = () => {
  const c = useContext(Ctx);
  if (!c) throw new Error("Edicao: contexto ausente");
  return c;
};

const comFiltro = (filtro: string, blur: number) => {
  const partes = [filtro === "none" ? "" : filtro, blur > 0.2 ? `blur(${blur}px)` : ""].filter(Boolean);
  return partes.length ? partes.join(" ") : undefined;
};

// ------------------------------------------------------------------ apresentador + voz
const Apresentador: React.FC = () => {
  const { cenas, cenaEm, enquadramento, filtro, tema, video, total } = useEd();
  const f = useCurrentFrame();
  const cena = cenaEm(f);
  // desfoque do fundo quando entra cartão/resumo
  let blur = 0;
  for (const c of cenas) {
    if (c.tipo === "broll") continue;
    blur = Math.max(
      blur,
      Math.min(
        interpolate(f, [c.de - 2, c.de + TRANS], [0, 30], clamp),
        interpolate(f, [c.ate - TRANS, c.ate], [30, 0], clamp),
      ),
    );
  }
  // abertura desfocada
  blur = Math.max(blur, interpolate(f, [0, 14], [26, 0], clamp));
  const oculta = cena?.tipo === "broll" && f > cena.de + TRANS && f < cena.ate - TRANS;
  const clips = video.edl.clips;
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: tema.fundo }}>
      <AbsoluteFill
        style={{
          transformOrigin: "0 0",
          transform: enquadramento(f),
          filter: comFiltro(filtro, blur),
          width: W,
          height: H,
          visibility: oculta ? "hidden" : "visible",
        }}
      >
        {clips.map((c, k) => {
          const de = F(c.editIni);
          const prox = clips[k + 1];
          const ate = prox ? F(prox.editIni) : F(total);
          return (
            <Sequence key={k} from={de} durationInFrames={ate - de} layout="none">
              <OffthreadVideo
                src={staticFile(video.midia.apresentador)}
                trimBefore={Math.round(c.srcIni * FPS)}
                muted
                style={{ width: W, height: H, position: "absolute" }}
              />
            </Sequence>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Voz: React.FC = () => {
  const { video } = useEd();
  return (
    <>
      {video.edl.clips.map((c, k) => {
        const de = F(c.editIni);
        const dur = Math.round((c.srcFim - c.srcIni) * FPS);
        return (
          <Sequence key={k} from={de} durationInFrames={dur} layout="none">
            <Audio
              src={staticFile(video.midia.voz)}
              trimBefore={Math.round(c.srcIni * FPS)}
              volume={(x) =>
                Math.min(
                  interpolate(x, [0, 3], [0, 1], clamp),
                  interpolate(x, [dur - 3, dur], [1, 0], clamp),
                )
              }
            />
          </Sequence>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------ palavra atrás do apresentador
const PalavraAtras: React.FC<{ a: Atras }> = ({ a }) => {
  const { E, enquadramento, filtro, tema } = useEd();
  const f = useCurrentFrame(); // relativo ao início do clipe
  const { fps } = useVideoConfig();
  const entra = E(a.ini) - E(a.clipeIni);
  const sai = E(a.fim) - E(a.clipeIni);
  const absoluto = E(a.clipeIni) + f;
  const p = spring({ frame: f - entra, fps, config: { damping: 18, stiffness: 120 } });
  const saida = interpolate(f, [sai - 6, sai], [1, 0], clamp);
  const visivel = f >= entra;
  return (
    <>
      {visivel ? (
        <AbsoluteFill style={{ alignItems: "center" }}>
          <div
            style={{
              position: "absolute",
              top: a.y,
              display: "flex",
              gap: a.vao,
              opacity: p * saida,
              filter: `blur(${(1 - p) * 16}px)`,
              transform: `translateY(${(1 - p) * 90}px) scale(${0.9 + 0.1 * p})`,
            }}
          >
            {a.partes.map((parte) => (
              <span
                key={parte}
                style={{
                  fontFamily: PLAYFAIR_IT,
                  fontStyle: "italic",
                  fontWeight: 800,
                  fontSize: a.tam,
                  lineHeight: 1,
                  letterSpacing: -6,
                  whiteSpace: "nowrap",
                  backgroundImage: tema.metalico,
                  backgroundSize: "220% 100%",
                  backgroundPosition: `${(f - entra) * 2}% 0`,
                  WebkitBackgroundClip: "text",
                  backgroundClip: "text",
                  color: "transparent",
                  filter: "drop-shadow(0 4px 12px rgba(0,0,0,0.6))",
                  padding: "0 14px 70px",
                }}
              >
                {parte}
              </span>
            ))}
          </div>
        </AbsoluteFill>
      ) : null}
      {/* camada do apresentador com transparência, no mesmo enquadramento da base */}
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <AbsoluteFill
          style={{ transformOrigin: "0 0", transform: enquadramento(absoluto), width: W, height: H, filter: comFiltro(filtro, 0) }}
        >
          <OffthreadVideo
            src={staticFile(a.clipe)}
            transparent
            muted
            style={{ width: W, height: H, position: "absolute" }}
          />
        </AbsoluteFill>
      </AbsoluteFill>
    </>
  );
};

// ------------------------------------------------------------------ mídia genérica
const Midia: React.FC<{ src: string; video?: boolean; srcIni?: number; rate?: number; style?: React.CSSProperties }> = ({
  src,
  video,
  srcIni,
  rate,
  style,
}) =>
  video ? (
    <OffthreadVideo
      src={staticFile(src)}
      trimBefore={Math.round((srcIni ?? 0) * FPS)}
      playbackRate={rate ?? 1}
      muted
      style={{ width: "100%", height: "100%", objectFit: "cover", ...style }}
    />
  ) : (
    <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", ...style }} />
  );

const Ilustrativa: React.FC<{ opacidade?: number }> = ({ opacidade = 1 }) => {
  const { credito } = useEd();
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 92,
        textAlign: "center",
        fontFamily: INTER,
        fontWeight: 400,
        fontSize: 25,
        letterSpacing: 0.3,
        color: "rgba(255,255,255,0.78)",
        textShadow: "0 1px 6px rgba(0,0,0,0.7)",
        opacity: opacidade,
      }}
    >
      {credito}
    </div>
  );
};

// ------------------------------------------------------------------ b-roll
const Broll: React.FC<{ c: BrollT & { de: number; ate: number }; dur: number; saidaSuave: boolean }> = ({
  c,
  dur,
  saidaSuave,
}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, TRANS], [1, 0], { ...clamp, easing: easeOut });
  const saida = saidaSuave ? interpolate(f, [dur - TRANS, dur], [1, 0], clamp) : 1;
  const z = interpolate(f, [0, dur], [c.zoomDe ?? 1, c.zoomAte ?? 1.06], clamp);
  let transform = `scale(${z})`;
  let filtro: string | undefined;
  let opacidade = saida;
  const idFiltro = `w${c.de}f${f}`;
  if (c.entrada === "zoom") {
    transform = `scale(${z * (1 + p * 0.16)})`;
    filtro = p > 0.02 ? `blur(${p * 22}px)` : undefined;
    opacidade = Math.min(saida, 1 - p);
  } else {
    const dir = c.entrada === "whip" ? 1 : -1;
    transform = `translateX(${dir * p * W * 0.85}px) scale(${z})`;
    filtro = p > 0.02 ? `url(#${idFiltro})` : undefined;
  }
  return (
    <AbsoluteFill style={{ overflow: "hidden", opacity: opacidade }}>
      {filtro?.startsWith("url") ? (
        <svg style={{ position: "absolute", width: 0, height: 0 }}>
          <filter id={idFiltro} x="-20%" y="0" width="140%" height="100%">
            <feGaussianBlur stdDeviation={`${p * 90} 0`} />
          </filter>
        </svg>
      ) : null}
      <AbsoluteFill style={{ transform, transformOrigin: c.origem ?? "50% 50%", filter: filtro, backgroundColor: "#111" }}>
        <Midia src={c.src} video srcIni={c.srcIni} rate={c.rate} />
      </AbsoluteFill>
      {/* véu inferior: dá leitura à legenda e às palavras */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0) 40%, rgba(0,0,0,0.24) 54%, rgba(0,0,0,0.24) 68%, rgba(0,0,0,0.36) 100%)",
        }}
      />
      {c.ilustrativa ? <Ilustrativa /> : null}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ cartão grande sobre fundo desfocado
const CARTAO_Y = 300;
const CARTAO_LADO = 900;
const Cartao: React.FC<{ c: CartaoT & { de: number; ate: number }; dur: number }> = ({ c, dur }) => {
  const { E, tema } = useEd();
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sobe = spring({ frame: f, fps, config: { damping: 16, stiffness: 110 } });
  const saida = interpolate(f, [dur - 7, dur], [0, 1], clamp);
  const tituloF = c.tituloEm !== undefined ? E(c.tituloEm) - c.de : 0;
  const pt = spring({ frame: f - tituloF, fps, config: { damping: 200 }, durationInFrames: 16 });
  return (
    <AbsoluteFill style={{ opacity: 1 - saida }}>
      <div
        style={{
          position: "absolute",
          left: (W - CARTAO_LADO) / 2,
          top: CARTAO_Y,
          width: CARTAO_LADO,
          height: CARTAO_LADO,
          borderRadius: 54,
          overflow: "hidden",
          boxShadow: "0 30px 80px rgba(60,40,10,0.35)",
          transform: `translateY(${(1 - sobe) * 1100}px) scale(${1 - saida * 0.04})`,
        }}
      >
        {c.midias.map((m, k) => {
          const ini = E(m.em) - c.de;
          const prox = c.midias[k + 1];
          const fim = prox ? E(prox.em) - c.de : dur + 20;
          const op = Math.min(
            k === 0 ? 1 : interpolate(f, [ini - 2, ini + 5], [0, 1], clamp),
            interpolate(f, [fim + 3, fim + 8], [1, 0], clamp),
          );
          if (op <= 0) return null;
          const z = interpolate(f, [ini, fim + 8], [1.0, 1.05], clamp);
          return (
            <AbsoluteFill key={m.src} style={{ opacity: op, transform: `scale(${z})` }}>
              <Midia src={m.src} video={m.video} srcIni={m.srcIni} />
            </AbsoluteFill>
          );
        })}
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 62%, rgba(0,0,0,0.5) 100%)" }} />
      </div>
      {c.titulo && f >= tituloF ? (
        <div
          style={{
            position: "absolute",
            top: CARTAO_Y + CARTAO_LADO + 30,
            left: 0,
            right: 0,
            textAlign: "center",
            fontFamily: PLAYFAIR,
            fontWeight: 700,
            fontSize: caber(c.titulo, 118, 0.52, 1000),
            lineHeight: 1.05,
            letterSpacing: -2,
            backgroundImage: tema.metalico,
            backgroundSize: "220% 100%",
            backgroundPosition: `${f * 1.5}% 0`,
            WebkitBackgroundClip: "text",
            backgroundClip: "text",
            color: "transparent",
            paddingBottom: 20,
            opacity: pt,
            filter: `blur(${(1 - pt) * 10}px) drop-shadow(0 4px 14px rgba(30,10,5,0.75))`,
            transform: `translateY(${(1 - pt) * 30}px)`,
          }}
        >
          {c.titulo}
        </div>
      ) : null}
      {c.ilustrativa ? <Ilustrativa /> : null}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ resumo: palavras de destaque
const Resumo: React.FC<{ c: ResumoT & { de: number; ate: number }; dur: number }> = ({ c, dur }) => {
  const { E, tema } = useEd();
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const saida = interpolate(f, [dur - 6, dur], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingBottom: 260, opacity: saida }}>
      {c.palavras.map((p) => {
        const ini = E(p.t) - c.de;
        const pr = spring({ frame: f - ini, fps, config: { damping: 200 }, durationInFrames: 12 });
        if (f < ini) return <div key={p.texto} style={{ height: 150 }} />;
        return (
          <div
            key={p.texto}
            style={{
              height: 150,
              fontFamily: PLAYFAIR,
              fontWeight: 700,
              fontSize: caber(p.texto, 128, 0.52, 1000),
              lineHeight: "150px",
              letterSpacing: -2,
              backgroundImage: tema.metalico,
              backgroundSize: "220% 100%",
              backgroundPosition: `${f * 1.5}% 0`,
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
              paddingBottom: 10,
              opacity: pr,
              filter: `blur(${(1 - pr) * 12}px) drop-shadow(0 4px 14px rgba(30,10,5,0.8))`,
              transform: `translateY(${(1 - pr) * 34}px)`,
            }}
          >
            {p.texto}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ cartões pequenos
const CartaoPequeno: React.FC<{ item: CartaoPeq; fimGrupo: number }> = ({ item, fimGrupo }) => {
  const { tema } = useEd();
  const f = useCurrentFrame(); // relativo ao início do cartão
  const { fps } = useVideoConfig();
  const pop = spring({ frame: f, fps, config: { damping: 11, stiffness: 150, mass: 0.7 } });
  const sai = interpolate(f, [fimGrupo - 7, fimGrupo], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  return (
    <div
      style={{
        position: "absolute",
        left: item.x,
        top: item.y,
        width: item.w,
        height: item.h,
        transform: `translateY(${sai * 700}px) rotate(${item.rot + (1 - pop) * 8}deg) scale(${0.55 + 0.45 * pop})`,
        opacity: Math.min(1, pop * 1.4),
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          borderRadius: 30,
          border: "8px solid #fff",
          boxSizing: "border-box",
          overflow: "hidden",
          boxShadow: "0 18px 46px rgba(40,25,5,0.42)",
          backgroundColor: "#fff",
        }}
      >
        <Midia src={item.src} video={item.video} srcIni={item.srcIni} />
      </div>
      {item.rotulo ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            bottom: -24,
            transform: "translateX(-50%)",
            whiteSpace: "nowrap",
            fontFamily: INTER,
            fontWeight: 600,
            fontSize: 31,
            letterSpacing: -0.3,
            color: tema.rotulo.texto,
            padding: "9px 26px",
            borderRadius: 40,
            background: tema.rotulo.fundo,
            boxShadow: "0 6px 16px rgba(40,25,5,0.3)",
          }}
        >
          {item.rotulo}
        </div>
      ) : null}
    </div>
  );
};

const Grupo: React.FC<{ g: GrupoCartoes }> = ({ g }) => {
  const { E } = useEd();
  const f = useCurrentFrame();
  const inicio = E(g.itens[0].t);
  const fim = E(g.fim);
  return (
    <AbsoluteFill>
      {g.itens.map((it) => {
        const de = E(it.t);
        return (
          <Sequence key={it.src + it.t} from={de - inicio} durationInFrames={fim - de} layout="none">
            <CartaoPequeno item={it} fimGrupo={fim - de} />
          </Sequence>
        );
      })}
      {g.ilustrativa ? <Ilustrativa opacidade={interpolate(f, [0, 8], [0, 1], clamp)} /> : null}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ letreiros
const LinhaTexto: React.FC<{ l: Linha; desde: number; tema: Tema }> = ({ l, desde, tema }) => {
  const { fps } = useVideoConfig();
  const p = spring({ frame: desde, fps, config: { damping: 200 }, durationInFrames: l.estilo === "sans" ? 9 : 14 });
  const tam = l.tam ?? 62;
  const sombra = "0 4px 22px rgba(0,0,0,0.45), 0 1px 3px rgba(0,0,0,0.35)";
  const comum: React.CSSProperties = {
    display: "block",
    whiteSpace: "nowrap",
    opacity: p,
    filter: `blur(${(1 - p) * 12}px)`,
    transform: `translateY(${(1 - p) * 26}px) scale(${1 + (1 - p) * 0.08})`,
  };
  if (l.estilo === "sans") {
    return (
      <span style={{ ...comum, fontFamily: INTER, fontWeight: 500, fontSize: caber(l.texto, tam, 0.52, 1000), letterSpacing: -1.5, color: "#fff", textShadow: sombra, lineHeight: 1.12 }}>
        {l.texto}
      </span>
    );
  }
  if (l.estilo === "serif") {
    return (
      <span style={{ ...comum, fontFamily: PLAYFAIR_IT, fontStyle: "italic", fontWeight: 800, fontSize: caber(l.texto, tam, 0.47, 1000), letterSpacing: -3, color: "#fff", textShadow: `0 0 34px rgba(255,255,255,0.35), ${sombra}`, lineHeight: 1.04 }}>
        {l.texto}
      </span>
    );
  }
  // destaque: revela da esquerda para a direita e o brilho corre pela palavra
  const wipe = interpolate(desde, [0, 12], [0, 130], { ...clamp, easing: easeOut });
  return (
    <span
      style={{
        ...comum,
        filter: `blur(${(1 - p) * 8}px) drop-shadow(0 6px 18px rgba(0,0,0,0.55))`,
        fontFamily: PLAYFAIR,
        fontWeight: 700,
        fontSize: caber(l.texto, tam, 0.5, 1000),
        letterSpacing: -2.5,
        lineHeight: 1.1,
        backgroundImage: tema.metalico,
        backgroundSize: "240% 100%",
        backgroundPosition: `${desde * 1.8}% 0`,
        WebkitBackgroundClip: "text",
        backgroundClip: "text",
        color: "transparent",
        paddingBottom: 16,
        WebkitMaskImage: `linear-gradient(90deg,#000 ${wipe - 25}%,transparent ${wipe}%)`,
        maskImage: `linear-gradient(90deg,#000 ${wipe - 25}%,transparent ${wipe}%)`,
      }}
    >
      {l.texto}
    </span>
  );
};

const Letreiros: React.FC = () => {
  const { E, tema, video } = useEd();
  const f = useCurrentFrame();
  const atual = video.letreiros.find((b) => f >= E(b.ini) && f < E(b.fim));
  if (!atual) return null;
  const saida = interpolate(f, [E(atual.fim) - 3, E(atual.fim)], [1, 0], clamp);
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: atual.y,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        opacity: saida,
      }}
    >
      {atual.linhas.map((l) => {
        const desde = f - E(l.t);
        return desde >= 0 ? <LinhaTexto key={l.texto} l={l} desde={desde} tema={tema} /> : null;
      })}
    </div>
  );
};

// ------------------------------------------------------------------ legendas
const Legendas: React.FC = () => {
  const { cenaEm, E, fala, video } = useEd();
  const f = useCurrentFrame();
  const legendas = video.legendas;
  const k = legendas.findIndex((b, i) => {
    const prox = legendas[i + 1];
    const fim = b.fim !== undefined ? E(b.fim) : prox ? E(prox.t) : F(fala);
    return f >= E(b.t) && f < fim;
  });
  if (k < 0) return null;
  const b = legendas[k];
  const desde = f - E(b.t);
  const op = interpolate(desde, [0, 3], [0, 1], clamp);
  const cena = cenaEm(f);
  let y = 1098;
  if (cena?.tipo === "cartao") y = CARTAO_Y + CARTAO_LADO - 110;
  if (cena?.tipo === "resumo") y = 1200;
  return (
    <div
      style={{
        position: "absolute",
        left: 50,
        right: 50,
        top: y,
        textAlign: "center",
        fontFamily: INTER,
        fontWeight: 500,
        fontSize: 54,
        letterSpacing: -1.2,
        lineHeight: 1.15,
        color: "#fff",
        textShadow: "0 2px 18px rgba(0,0,0,0.8), 0 1px 3px rgba(0,0,0,0.7)",
        opacity: op,
        transform: `translateY(${(1 - op) * 6}px)`,
      }}
    >
      {b.texto}
    </div>
  );
};

// ------------------------------------------------------------------ selo com nome e registro
const Selo: React.FC = () => {
  const { cliente, E, tema, video } = useEd();
  const f = useCurrentFrame();
  const faixa = video.selo.find(([a, b]) => f >= E(a) && f < E(b));
  if (!faixa) return null;
  const p = interpolate(f, [E(faixa[0]) + 4, E(faixa[0]) + 14], [0, 1], { ...clamp, easing: easeOut });
  const s = interpolate(f, [E(faixa[1]) - 8, E(faixa[1])], [1, 0], clamp);
  return (
    <div
      style={{
        position: "absolute",
        top: 190,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        opacity: p * s,
        transform: `translateY(${(1 - p) * -18}px)`,
      }}
    >
      <SeloPilula cliente={cliente} tema={tema} sombra="0 8px 26px rgba(40,25,5,0.2)" />
    </div>
  );
};

// ------------------------------------------------------------------ flash de luz
const Flash: React.FC = () => {
  const { cta, E, tema, video } = useEd();
  const f = useCurrentFrame();
  let o = interpolate(f, [0, 12], [0.9, 0], { ...clamp, easing: easeOut });
  for (const t of video.flashes) {
    const c = E(t);
    const d = Math.abs(f - c);
    if (d <= 8) o = Math.max(o, interpolate(d, [0, 8], [0.96, 0], { ...clamp, easing: Easing.out(Easing.quad) }));
  }
  const c = F(cta) - 2;
  if (Math.abs(f - c) <= 10) o = Math.max(o, interpolate(Math.abs(f - c), [0, 10], [1, 0], clamp));
  if (o <= 0.01) return null;
  return <AbsoluteFill style={{ opacity: o, background: tema.flash }} />;
};

// ------------------------------------------------------------------ cartão final
const CartaoFinal: React.FC = () => {
  const { cliente, tema } = useEd();
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const anima = (de: number) => {
    const p = spring({ frame: f - de, fps, config: { damping: 200 }, durationInFrames: 16 });
    return {
      opacity: p,
      filter: `blur(${(1 - p) * 10}px)`,
      transform: `translateY(${(1 - p) * 26}px)`,
    } as React.CSSProperties;
  };
  const brilho = (f * 1.2) % 220;
  const script = cliente.assinatura === "script";
  const registro = [cliente.profissao, cliente.registro, cliente.rqe].filter(Boolean).join(" · ");
  const fin = tema.final;
  return (
    <AbsoluteFill style={{ background: fin.fundo }}>
      {/* arcos decorativos */}
      <svg width={W} height={H} style={{ position: "absolute", opacity: 0.55 }}>
        <path d="M-40 1500 C 260 1560 300 1860 360 1980" fill="none" stroke={fin.arco1} strokeWidth="3" />
        <path d="M-40 1400 C 340 1470 400 1800 470 1980" fill="none" stroke={fin.arco2} strokeWidth="2" />
        <path d="M640 -30 C 800 90 1010 170 1120 420" fill="none" stroke={fin.arco1} strokeWidth="3" />
        <path d="M540 -30 C 720 130 960 230 1120 520" fill="none" stroke={fin.arco2} strokeWidth="2" />
      </svg>
      {cliente.logo ? (
        <div style={{ ...anima(1), position: "absolute", top: 340, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
          <Img src={staticFile(cliente.logo)} style={{ maxWidth: 420, maxHeight: 170, objectFit: "contain" }} />
        </div>
      ) : null}
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 560 }}>
        <div
          style={{
            ...anima(3),
            fontFamily: script ? SCRIPT : PLAYFAIR_IT,
            fontStyle: script ? "normal" : "italic",
            fontWeight: script ? 400 : 700,
            fontSize: script ? caber(cliente.nome, 138, 0.37, 1000) : caber(cliente.nome, 96, 0.5, 1000),
            lineHeight: 1.1,
            whiteSpace: "nowrap",
            textAlign: "center",
            padding: "0 40px 20px",
            backgroundImage: fin.nome,
            backgroundSize: "220% 100%",
            backgroundPosition: `${brilho}% 0`,
            WebkitBackgroundClip: "text",
            backgroundClip: "text",
            color: "transparent",
          }}
        >
          {cliente.nome}
        </div>
        <div style={{ ...anima(8), width: 420, height: 2, marginTop: 6, background: `linear-gradient(90deg,transparent,${fin.linha},transparent)` }} />
        <div
          style={{
            ...anima(10),
            marginTop: 24,
            textAlign: "center",
            fontFamily: INTER,
            fontWeight: 400,
            fontSize: 37,
            lineHeight: 1.5,
            letterSpacing: 0.2,
            color: fin.texto,
          }}
        >
          {cliente.especialidade.map((l) => (
            <div key={l} style={{ fontSize: caber(l, 37, 0.5, 1000) }}>
              {l}
            </div>
          ))}
          <div style={{ fontWeight: 500, marginTop: 4, letterSpacing: 2, fontSize: caber(registro, 37, 0.58, 1000) }}>{registro}</div>
        </div>
        <div
          style={{
            ...anima(20),
            marginTop: 90,
            textAlign: "center",
            fontFamily: PLAYFAIR,
            fontWeight: 700,
            lineHeight: 1.08,
            letterSpacing: -2.5,
            color: fin.titulo,
          }}
        >
          {cliente.cta.map((l) => (
            <div key={l} style={{ fontSize: caber(l, 124, 0.5, 1000) }}>
              {l}
            </div>
          ))}
        </div>
        {cliente.canal ? (
          <div
            style={{
              ...anima(26),
              marginTop: 40,
              fontFamily: INTER,
              fontWeight: 500,
              fontSize: caber(cliente.canal, 44, 0.52, 1000),
              letterSpacing: -0.5,
              color: fin.texto,
            }}
          >
            {cliente.canal}
          </div>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ áudio de apoio
const Trilha: React.FC = () => {
  const { cta, total, video } = useEd();
  const fim = F(total);
  const c = F(cta);
  return (
    <Audio
      src={staticFile(video.midia.trilha)}
      volume={(x) => {
        const entra = interpolate(x, [0, 18], [0, 1], clamp);
        const sai = interpolate(x, [fim - 36, fim], [1, 0], clamp);
        const nivel = interpolate(x, [c - 12, c + 10], [0.085, 0.24], clamp);
        return nivel * entra * sai;
      }}
    />
  );
};

const Sons: React.FC = () => {
  const { cta, E, video } = useEd();
  return (
    <>
      {video.sons.map((s, k) => (
        <Sequence key={k} from={Math.max(0, E(s.t))} durationInFrames={60} layout="none">
          <Audio src={staticFile(`audio/sfx/${s.som}.wav`)} volume={s.vol} />
        </Sequence>
      ))}
      <Sequence from={F(cta) - 3} durationInFrames={60} layout="none">
        <Audio src={staticFile("audio/sfx/impacto.wav")} volume={0.3} />
      </Sequence>
      <Sequence from={F(cta) + 2} durationInFrames={60} layout="none">
        <Audio src={staticFile("audio/sfx/brilho.wav")} volume={0.1} />
      </Sequence>
    </>
  );
};

// ------------------------------------------------------------------ montagem
const Camadas: React.FC = () => {
  const { cenas, cta, E, tema, video } = useEd();
  return (
    <AbsoluteFill style={{ backgroundColor: tema.fundo }}>
      <Apresentador />
      {video.atras.map((a) => {
        const de = E(a.clipeIni);
        return (
          <Sequence key={a.clipe} from={de} durationInFrames={E(a.clipeFim) - de}>
            <PalavraAtras a={a} />
          </Sequence>
        );
      })}
      {video.grupos.map((g) => {
        const de = E(g.itens[0].t);
        return (
          <Sequence key={g.fim} from={de} durationInFrames={E(g.fim) - de}>
            <Grupo g={g} />
          </Sequence>
        );
      })}
      {cenas.map((c, k) => {
        const prox = cenas[k + 1];
        const colada = prox && prox.de <= c.ate + 1 && prox.tipo === "broll";
        const dur = c.ate - c.de + (colada ? TRANS + 2 : 0);
        return (
          <Sequence key={k} from={c.de} durationInFrames={dur}>
            {c.tipo === "broll" ? <Broll c={c} dur={dur} saidaSuave={!colada} /> : null}
            {c.tipo === "cartao" ? <Cartao c={c} dur={dur} /> : null}
            {c.tipo === "resumo" ? <Resumo c={c} dur={dur} /> : null}
          </Sequence>
        );
      })}
      <Letreiros />
      <Legendas />
      <Selo />
      <Sequence from={F(cta)}>
        <CartaoFinal />
      </Sequence>
      <Flash />
      <Voz />
      <Trilha />
      <Sons />
    </AbsoluteFill>
  );
};

export const Edicao: React.FC<{ video: Video; cliente: Cliente }> = ({ video, cliente }) => {
  const valor = useMemo(() => montar(video, cliente), [video, cliente]);
  return (
    <Ctx.Provider value={valor}>
      <Camadas />
    </Ctx.Provider>
  );
};
