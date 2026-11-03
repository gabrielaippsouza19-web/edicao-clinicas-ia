import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";
import { loadFont as loadScript } from "@remotion/google-fonts/GreatVibes";

export const { fontFamily: INTER } = loadInter("normal", { weights: ["400", "500", "600"], subsets: ["latin", "latin-ext"] });
export const { fontFamily: PLAYFAIR } = loadPlayfair("normal", { weights: ["600", "700"], subsets: ["latin", "latin-ext"] });
export const { fontFamily: PLAYFAIR_IT } = loadPlayfair("italic", { weights: ["700", "800"], subsets: ["latin", "latin-ext"] });
export const { fontFamily: SCRIPT } = loadScript("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] });

// Reduz a fonte quando o texto não cabe: nomes e registros mudam muito de um cliente para outro.
// "largura" é a largura média de um caractere em relação ao tamanho da fonte.
export const caber = (texto: string, maximo: number, largura: number, disponivel = 980) =>
  Math.min(maximo, Math.floor(disponivel / Math.max(1, texto.length * largura)));
