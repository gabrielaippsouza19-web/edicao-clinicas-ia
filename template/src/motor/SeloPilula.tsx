import React from "react";
import { caber, INTER } from "./fontes";
import { Cliente, Tema } from "./tipos";

// Nome, registro e RQE na ordem que aparece nas peças. A pílula encolhe em nomes longos.
export const identificacao = (c: Cliente) =>
  [c.nome, c.profissao, c.registro, c.rqe].filter((x): x is string => Boolean(x));

export const SeloPilula: React.FC<{ cliente: Cliente; tema: Tema; sombra: string }> = ({ cliente, tema, sombra }) => {
  const partes = identificacao(cliente);
  const tamanho = caber(partes.join(" · "), 31, 0.52, 930);
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 14,
        padding: "13px 30px",
        borderRadius: 50,
        whiteSpace: "nowrap",
        backgroundColor: "rgba(255,255,255,0.97)",
        boxShadow: sombra,
        fontFamily: INTER,
        fontWeight: 500,
        fontSize: tamanho,
        letterSpacing: -0.4,
        color: tema.seloTexto,
      }}
    >
      <svg width="28" height="34" viewBox="0 0 24 30">
        <path
          d="M12 1C6.2 1 2 5.3 2 10.8 2 18 12 29 12 29s10-11 10-18.2C22 5.3 17.8 1 12 1z"
          fill="none"
          stroke={tema.acento}
          strokeWidth="2.6"
        />
        <circle cx="12" cy="11" r="3.4" fill="none" stroke={tema.acento} strokeWidth="2.6" />
      </svg>
      {partes.map((p, k) => (
        <React.Fragment key={p}>
          {k > 0 ? <span style={{ color: tema.acento }}>·</span> : null}
          <span style={{ fontWeight: k === 0 ? 500 : 400 }}>{p}</span>
        </React.Fragment>
      ))}
    </div>
  );
};
