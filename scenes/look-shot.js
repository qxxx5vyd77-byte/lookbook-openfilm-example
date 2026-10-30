// One named look, full-bleed: a camera card on the picture, the name on a cream block that wipes in on the beat.
import { prepare, span, smooth, snap } from './kit.js';
/* the camera cards' code_move recipes (from the brief's FILM PLAN), e = the plan's ease of u = t / d */
const MOVES = {
  push: (e) => `scale(${(1 + 0.08 * e).toFixed(5)})`,                                      // Dolly Push-In: 1.00 to 1.08
  pull: (e) => `scale(${(1.08 - 0.08 * e).toFixed(5)})`,                                   // Pull-Back Reveal: 1.08 to 1.00
  pan: (e) => `translateX(${(115.2 - 230.4 * e).toFixed(2)}px) scale(1.14)`,               // Slow Pan: 12% of the stage width, scaled so no edge shows
};
export function lookShot({ D, AT, move = 'push', arrive = false, nameAt = 0.5 }) {
  const $ = (s) => document.querySelector(s);
  let B;
  window.film = {
    duration: D,
    ready: prepare(AT).then((b) => { B = b; }),
    frame(t) {
      /* Whip Pan, arriving (first look only): it lands from the right with the blur dying out */
      const a = arrive ? smooth(span(t, 0, 0.2)) : 1, blur = 24 * (1 - a);
      $('#whip-blur').setAttribute('stdDeviation', `${blur.toFixed(2)} 0`);
      $('#scene').style.filter = blur > 0.01 ? 'url(#whip)' : 'none';
      $('#scene').style.transform = `translateX(${(960 * (1 - a)).toFixed(2)}px) ${MOVES[move](smooth(t / D))}`;
      const r = snap(span(t, B(nameAt), B(nameAt) + 0.2));
      $('#name').style.clipPath = `inset(0 ${((1 - r) * 100).toFixed(3)}% 0 0)`;
      $('#name').style.visibility = r > 0 ? 'visible' : 'hidden';
    },
  };
}
