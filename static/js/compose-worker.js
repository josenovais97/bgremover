/**
 * Compose/encode worker — runs the full-resolution export pipeline off the main
 * thread on an OffscreenCanvas, so downloading a large styled photo can't freeze
 * the tab (decode + shape mask + background + sticker convolution + encode are
 * all seconds of work on a big image).
 *
 * This is deliberately a faithful mirror of Card.compose() in app.js: the main
 * thread pre-decodes the sources into ImageBitmaps (transferable) and posts the
 * same parameters here. If anything about this drifts from compose(), the export
 * would differ from the on-card preview — tests/compose-parity guards that, and
 * app.js always falls back to the main-thread compose() if this worker fails.
 *
 * Message in : { id, format, quality, bg, crop, sticker, resize, maxDim,
 *                src, blur, image }  (src/blur/image are ImageBitmaps)
 * Message out: { id, blob } | { id, error }
 */
'use strict';

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const mk = (w, h) => new OffscreenCanvas(Math.max(1, w), Math.max(1, h));

function roundRectPath(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function applyShapeClip(ctx, shape, w, h) {
  if (shape === 'circle') {
    ctx.beginPath();
    ctx.ellipse(w / 2, h / 2, w / 2, h / 2, 0, 0, Math.PI * 2);
    ctx.clip();
  } else if (shape === 'rounded') {
    roundRectPath(ctx, 0, 0, w, h, Math.min(w, h) * 0.18);
    ctx.clip();
  }
}

function orientSource(img, rot = 0, flipH = false, flipV = false) {
  rot = ((rot % 360) + 360) % 360;
  if (!rot && !flipH && !flipV) return img;
  const iw = img.width;
  const ih = img.height;
  const swap = rot === 90 || rot === 270;
  const c = mk(swap ? ih : iw, swap ? iw : ih);
  const ctx = c.getContext('2d');
  ctx.translate(c.width / 2, c.height / 2);
  ctx.rotate((rot * Math.PI) / 180);
  ctx.scale(flipH ? -1 : 1, flipV ? -1 : 1);
  ctx.drawImage(img, -iw / 2, -ih / 2);
  return c;
}

function drawCover(ctx, img, w, h, scale = 1) {
  const iw = img.width;
  const ih = img.height;
  const s = Math.max(w / iw, h / ih) * scale;
  ctx.drawImage(img, (w - iw * s) / 2, (h - ih * s) / 2, iw * s, ih * s);
}

// Background painter. Blur/image sources arrive pre-decoded (srcs.blur/.image).
function paintBackground(ctx, w, h, spec, srcs) {
  if (typeof spec === 'string') {
    ctx.fillStyle = spec;
    ctx.fillRect(0, 0, w, h);
    return;
  }
  if (spec.type === 'gradient') {
    const a = ((spec.angle || 0) * Math.PI) / 180;
    const dx = Math.cos(a);
    const dy = Math.sin(a);
    const half = (Math.abs(dx) * w + Math.abs(dy) * h) / 2;
    const g = ctx.createLinearGradient(w / 2 - dx * half, h / 2 - dy * half, w / 2 + dx * half, h / 2 + dy * half);
    g.addColorStop(0, spec.from);
    g.addColorStop(1, spec.to);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
    return;
  }
  if (spec.type === 'blur' && srcs.blur) {
    ctx.save();
    ctx.filter = `blur(${Math.max(1, Math.round((spec.amount ?? 0.04) * Math.min(w, h)))}px)`;
    drawCover(ctx, srcs.blur, w, h, 1.15);
    ctx.restore();
    return;
  }
  if (spec.type === 'image' && srcs.image) {
    drawCover(ctx, srcs.image, w, h);
  }
}

function containInto(src, tw, th, format) {
  const t = mk(tw, th);
  const x = t.getContext('2d');
  if (format === 'image/jpeg') {
    x.fillStyle = '#ffffff';
    x.fillRect(0, 0, tw, th);
  }
  const s = Math.min(tw / src.width, th / src.height);
  const dw = src.width * s;
  const dh = src.height * s;
  x.drawImage(src, (tw - dw) / 2, (th - dh) / 2, dw, dh);
  return t;
}

function tintCanvas(src, color) {
  const c = mk(src.width, src.height);
  const x = c.getContext('2d');
  x.drawImage(src, 0, 0);
  x.globalCompositeOperation = 'source-in';
  x.fillStyle = color;
  x.fillRect(0, 0, c.width, c.height);
  return c;
}

function cropGeometry(iw, ih, crop) {
  const baseW = Math.min(iw, ih * crop.aspect);
  const baseH = baseW / crop.aspect;
  const z = Math.max(1, crop.z || 1);
  const sw = baseW / z;
  const sh = baseH / z;
  const halfU = sw / 2 / iw;
  const halfV = sh / 2 / ih;
  const u = clamp(crop.u ?? 0.5, halfU, 1 - halfU);
  const v = clamp(crop.v ?? 0.5, halfV, 1 - halfV);
  const sx = clamp(u * iw - sw / 2, 0, iw - sw);
  const sy = clamp(v * ih - sh / 2, 0, ih - sh);
  return { sx, sy, sw, sh, outW: Math.round(baseW), outH: Math.round(baseH) };
}

// Mirror of Card.compose()'s drawing pipeline (post-decode), on OffscreenCanvas.
function composeCanvas(p) {
  const { format, bg, crop, sticker, resize, maxDim } = p;
  const img = crop ? orientSource(p.src, crop.rot, crop.flipH, crop.flipV) : p.src;
  const iw = img.width;
  const ih = img.height;
  const geo = crop ? cropGeometry(iw, ih, crop) : { sx: 0, sy: 0, sw: iw, sh: ih, outW: iw, outH: ih };
  const shape = crop ? crop.shape : 'rect';
  const scale = maxDim ? Math.min(1, maxDim / Math.max(geo.outW, geo.outH)) : 1;
  const CW = Math.max(1, Math.round(geo.outW * scale));
  const CH = Math.max(1, Math.round(geo.outH * scale));

  const content = mk(CW, CH);
  const cc = content.getContext('2d');
  cc.save();
  applyShapeClip(cc, shape, CW, CH);
  cc.drawImage(img, geo.sx, geo.sy, geo.sw, geo.sh, 0, 0, CW, CH);
  cc.restore();

  let sprite = content;
  if (bg) {
    sprite = mk(CW, CH);
    const sc = sprite.getContext('2d');
    sc.save();
    applyShapeClip(sc, shape, CW, CH);
    paintBackground(sc, CW, CH, bg, { blur: p.blur, image: p.image });
    sc.drawImage(content, 0, 0);
    sc.restore();
  }

  const base = Math.min(CW, CH);
  const pad = sticker ? Math.round((sticker.pad || 0) * base) : 0;
  const ow = sticker && sticker.outline ? Math.max(1, Math.round((sticker.outlineW || 0.05) * base)) : 0;
  const shadowOn = !!(sticker && sticker.shadow);
  const sb = shadowOn ? Math.round((sticker.shadowBlur ?? 0.06) * base) : 0;
  const soff = shadowOn ? Math.round((sticker.shadowOff ?? 0.04) * base) : 0;
  const M = pad + ow + (shadowOn ? sb + soff : 0);

  const W = CW + 2 * M;
  const H = CH + 2 * M;
  let canvas = mk(W, H);
  const ctx = canvas.getContext('2d');
  if (format === 'image/jpeg') {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, W, H);
  }
  if (shadowOn) {
    ctx.save();
    ctx.shadowColor = sticker.shadowColor || 'rgba(0,0,0,0.45)';
    ctx.shadowBlur = sb;
    ctx.shadowOffsetY = soff;
    ctx.drawImage(sprite, M, M);
    ctx.restore();
  }
  if (ow > 0) {
    const sil = tintCanvas(sprite, sticker.outlineColor || '#ffffff');
    const steps = 32;
    for (let i = 0; i < steps; i++) {
      const a = (i / steps) * Math.PI * 2;
      ctx.drawImage(sil, M + Math.cos(a) * ow, M + Math.sin(a) * ow);
    }
  }
  ctx.drawImage(sprite, M, M);

  if (resize && (canvas.width !== resize.w || canvas.height !== resize.h)) {
    canvas = containInto(canvas, resize.w, resize.h, format);
  }
  return canvas;
}

self.onmessage = async (e) => {
  const { id } = e.data;
  try {
    const canvas = composeCanvas(e.data);
    const opts = { type: e.data.format };
    if (e.data.format !== 'image/png') opts.quality = e.data.quality;
    const blob = await canvas.convertToBlob(opts);
    self.postMessage({ id, blob });
  } catch (err) {
    self.postMessage({ id, error: String((err && err.message) || err) });
  }
};
