/**
 * Off-thread diffusion fill for the object remover.
 *
 * Receives the DOWNSCALED image and mask as raw pixel buffers, runs the
 * onion-peel + Jacobi fill (pure typed-array math, no canvas), and posts the
 * filled pixels back. Keeping the heavy loops here means a big brush area on a
 * slow device can't jank the page; the main thread does only canvas work
 * (downscale before, upscale + feather-blend after).
 *
 * A classic worker (not a module) so it can be spawned same-origin without any
 * import-path rewriting concerns. The algorithm must stay in lockstep with the
 * fallback in remove-object.js — both call the same steps in the same order.
 */
'use strict';

/**
 * Fill masked pixels of `d` (RGBA, w×h) in place.
 * `maskAlpha` is the mask's alpha channel (Uint8ClampedArray, stride 4 offset 3
 * already resolved by the caller into a w*h Uint8Array of 0/1).
 */
function diffusionFill(d, maskArr, w, h) {
  const n = w * h;
  const unknown = new Uint8Array(maskArr);   // 1 = needs filling (consumed)
  const masked = maskArr;                    // original mask, for the relax pass
  const idx = (x, y) => y * w + x;

  // Onion peel: fill unknown pixels that touch a known one, layer by layer.
  let remaining = true;
  let guard = 0;
  while (remaining && guard++ < Math.max(w, h)) {
    remaining = false;
    const next = [];
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = idx(x, y);
        if (!unknown[i]) continue;
        let r = 0, g = 0, b = 0, c = 0;
        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            const nx = x + dx, ny = y + dy;
            if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
            const j = idx(nx, ny);
            if (unknown[j]) continue;
            r += d[j * 4]; g += d[j * 4 + 1]; b += d[j * 4 + 2]; c++;
          }
        }
        if (c) {
          d[i * 4] = r / c; d[i * 4 + 1] = g / c; d[i * 4 + 2] = b / c; d[i * 4 + 3] = 255;
          next.push(i);
        } else {
          remaining = true;
        }
      }
    }
    for (const i of next) unknown[i] = 0;
    if (!next.length) break;   // isolated region with no known boundary at all
  }

  // Jacobi relaxation smooths the onion-peel seams into one gradient.
  const src = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    src[i * 3] = d[i * 4]; src[i * 3 + 1] = d[i * 4 + 1]; src[i * 3 + 2] = d[i * 4 + 2];
  }
  const dst = src.slice();
  const iters = 60;
  for (let it = 0; it < iters; it++) {
    const a = it % 2 ? dst : src;
    const b = it % 2 ? src : dst;
    for (let y = 1; y < h - 1; y++) {
      for (let x = 1; x < w - 1; x++) {
        const i = idx(x, y);
        if (!masked[i]) continue;
        for (let ch = 0; ch < 3; ch++) {
          b[i * 3 + ch] = (
            a[(i - 1) * 3 + ch] + a[(i + 1) * 3 + ch] +
            a[(i - w) * 3 + ch] + a[(i + w) * 3 + ch]
          ) / 4;
        }
      }
    }
  }
  const out = iters % 2 ? dst : src;
  for (let i = 0; i < n; i++) {
    if (!masked[i]) continue;
    d[i * 4] = out[i * 3]; d[i * 4 + 1] = out[i * 3 + 1]; d[i * 4 + 2] = out[i * 3 + 2];
    d[i * 4 + 3] = 255;
  }
}

self.onmessage = (e) => {
  const { pixels, mask, w, h } = e.data;
  const d = new Uint8ClampedArray(pixels);
  diffusionFill(d, new Uint8Array(mask), w, h);
  self.postMessage({ pixels: d.buffer }, [d.buffer]);
};
