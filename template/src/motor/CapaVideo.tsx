import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { caber, INTER, PLAYFAIR, PLAYFAIR_IT } from "./fontes";
import { SeloPilula } from "./SeloPilula";
import { resolverTema } from "./temas";
import { Capa, Cliente } from "./tipos";

// Capa 1080x1920. O texto fica dentro do recorte central que a grade do perfil mostra.
export const CapaVideo: React.FC<{ capa: Capa; cliente: Cliente; olhosY: number }> = ({ capa, cliente, olhosY }) => {
  const tema = resolverTema(cliente.tema);
  const s = capa.escala ?? 1.2;
  const ty = Math.min(0, Math.max(1920 * (1 - s), 768 - s * olhosY));
  return (
    <AbsoluteFill style={{ backgroundColor: "#16100c", overflow: "hidden" }}>
      <Img
        src={staticFile(capa.imagem)}
        style={{
          position: "absolute",
          width: 1080,
          height: 1920,
          left: 0,
          top: 0,
          transformOrigin: "0 0",
          transform: `translate(${540 * (1 - s)}px, ${ty}px) scale(${s})`,
          filter: capa.filtro ?? cliente.filtroApresentador ?? "none",
        }}
      />
      {/* base escura para o título */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(18,8,6,0) 52%, rgba(18,8,6,0.5) 62%, rgba(18,8,6,0.68) 72%, rgba(18,8,6,0.62) 84%, rgba(18,8,6,0.82) 100%)",
        }}
      />
      {/* selo */}
      <div style={{ position: "absolute", top: 316, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <SeloPilula cliente={cliente} tema={tema} sombra="0 8px 26px rgba(20,10,5,0.28)" />
      </div>
      {/* título */}
      <div
        style={{
          position: "absolute",
          top: 1196,
          left: 0,
          right: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontFamily: PLAYFAIR,
            fontWeight: 600,
            fontSize: caber(capa.linha1, 72, 0.47, 1000),
            lineHeight: 1.1,
            letterSpacing: -1.2,
            color: "#fff",
            textShadow: "0 3px 16px rgba(0,0,0,0.55)",
          }}
        >
          {capa.linha1}
        </div>
        <div
          style={{
            fontFamily: PLAYFAIR_IT,
            fontStyle: "italic",
            fontWeight: 800,
            fontSize: caber(capa.destaque, 138, 0.5, 980),
            lineHeight: 1.12,
            letterSpacing: -3.5,
            padding: "0 30px 18px",
            whiteSpace: "nowrap",
            backgroundImage: tema.metalicoCapa ?? tema.metalico,
            WebkitBackgroundClip: "text",
            backgroundClip: "text",
            color: "transparent",
            filter: "drop-shadow(0 5px 16px rgba(0,0,0,0.6))",
          }}
        >
          {capa.destaque}
        </div>
        <div style={{ width: 340, height: 2, marginTop: 14, background: `linear-gradient(90deg,transparent,${tema.linhaCapa ?? tema.acento},transparent)` }} />
        {capa.rodape ? (
          <div
            style={{
              marginTop: 22,
              fontFamily: INTER,
              fontWeight: 400,
              fontSize: caber(capa.rodape, 34, 0.5, 1000),
              letterSpacing: 0.6,
              color: "rgba(255,255,255,0.92)",
            }}
          >
            {capa.rodape}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
