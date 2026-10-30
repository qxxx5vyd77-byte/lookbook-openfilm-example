// Shared by the film's pages. Everything here is a pure function of t: the picture at t comes from t alone.
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const span = (t, a, b) => clamp((t - a) / (b - a));
export const smooth = (u) => { u = clamp(u); return u * u * (3 - 2 * u); };   // the plan's e
export const snap = (u) => 1 - Math.pow(1 - clamp(u), 4);                     // a fast settle for things snapping in

/** Fonts, pictures and this shot's beats before the first frame. at: the shot's start in the film, in seconds. */
export async function prepare(at) {
  await Promise.all([document.fonts.load('500 64px "Inter Tight"'), document.fonts.load('800 64px "Inter Tight"')]);
  await document.fonts.ready;
  await Promise.all([...document.images].map((im) => im.decode()));
  const { beats } = await (await fetch(new URL('../assets/beats.json', import.meta.url))).json();
  const own = beats.map((b) => b - at).filter((b) => b > -0.02);   // a beat on the cut counts as this shot's first
  /* B(n): this shot's nth beat, in its own time; fractions fall between beats */
  return (n) => { const i = Math.floor(n), a = own[i], b = own[i + 1] ?? a + (a - own[i - 1]); return a + (b - a) * (n - i); };
}

/** A line of type in a .mask: up from below at tin, out through the top at tout. */
export function slide(el, t, tin, tout = null) {
  const i = snap(span(t, tin, tin + 0.22)), o = tout == null ? 0 : snap(span(t, tout, tout + 0.22));
  const k = (1 - i) - o;   // 1: waiting below the mask, 0: in place, -1: gone through the top
  el.style.transform = `translateY(calc(${(k * 100).toFixed(3)}% + ${(k * 20).toFixed(2)}px))`;
  el.style.visibility = i > 0 && o < 1 ? 'visible' : 'hidden';
}
