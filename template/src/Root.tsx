import React from "react";
import { Composition } from "remotion";
import { CLIENTE } from "./cliente";
import { CapaVideo } from "./motor/CapaVideo";
import { Edicao } from "./motor/Edicao";
import { duracao, FPS, H, W } from "./motor/tempo";
import { validarVideo } from "./motor/validar";
import { VIDEOS } from "./videos";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {VIDEOS.map((v) => (
        <React.Fragment key={v.id}>
          <Composition
            id={v.id}
            component={Edicao}
            durationInFrames={Math.round(duracao(v) * FPS)}
            fps={FPS}
            width={W}
            height={H}
            defaultProps={{ video: v, cliente: CLIENTE }}
            calculateMetadata={async ({ props }) => {
              validarVideo(props.video, props.cliente);
              return {};
            }}
          />
          {v.capa ? (
            <Composition
              id={`${v.id}-capa`}
              component={CapaVideo}
              durationInFrames={1}
              fps={FPS}
              width={W}
              height={H}
              defaultProps={{ capa: v.capa, cliente: CLIENTE, olhosY: v.enquadramento.olhosY }}
            />
          ) : null}
        </React.Fragment>
      ))}
    </>
  );
};
