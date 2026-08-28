/**
 * Pure helpers for the /api/stats/ Worker.
 *
 * These live in their own module for one reason: index.js imports
 * `cloudflare:workers`, which plain Node cannot resolve, so nothing in it can be
 * imported by a test. Everything here is dependency-free, so
 * tests/stats.test.mjs exercises the exact code that ships instead of a copy of
 * it.
 */

// Counter keys are built from these whitelists and NEVER from raw client input,
// so a caller cannot mint arbitrary rows by posting a made-up tool name. (The
// storage is SQL with bound parameters now rather than a REST path, so this is
// no longer load-bearing for injection — it is load-bearing for keeping the
// table bounded and the breakdown meaningful.)
export const EVENTS = ['downloaded', 'processed'];

export const TOOLS = [
  'home', 'blur', 'ecommerce', 'sticker', 'passport',
  'instagram', 'crop', 'convert', 'compress', 'meme', 'favicon',
  'redact', 'exif', 'resize', 'watermark', 'gif', 'video_gif', 'video_converter',
  'qr', 'text_behind', 'pdf',
  'base64', 'palette', 'border', 'collage', 'screenshot',
  'remove_object', 'photo_filters', 'upscale', 'heic', 'pdf_to_image', 'ocr',
  'svg_to_png',
  // Added when the counter was rebuilt on Cloudflare: these four tools shipped
  // after the original whitelist was written, so every event they might have
  // reported was being dropped on the floor by the server.
  'word_to_pdf', 'pdf_to_word', 'pdf_tools', 'csv_excel',
];

/** Hard cap on a single report: it is a public, unauthenticated counter. */
export const MAX_N = 50;

/** Accepted POSTs per client IP per window, and the window length. */
export const POST_LIMIT = 60;
export const POST_WINDOW_MS = 60 * 1000;

/** A client-supplied `n` as a usable increment; anything unparseable is 1. */
export function clampCount(value) {
  const n = Number.parseInt(value, 10);
  if (!Number.isFinite(n)) return 1;
  return Math.max(1, Math.min(n, MAX_N));
}

/**
 * ISO-8601 week of `date` in UTC, e.g. `2026-W35`.
 *
 * UTC and Monday-based so the weekly bucket rolls over at the same instant for
 * everyone rather than following whoever happens to be looking at it. The keys
 * also sort lexicographically in chronological order, which is what lets the
 * weeks be listed or pruned with a plain string comparison.
 */
export function isoWeekKey(date = new Date()) {
  // Move to the Thursday of this ISO week: the ISO year is by definition the
  // calendar year that Thursday falls in, which is what makes the turn of the
  // year (Dec 29 - Jan 4) come out right.
  const thursday = new Date(Date.UTC(
    date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(),
  ));
  const weekday = thursday.getUTCDay() || 7;  // Mon=1 … Sun=7
  thursday.setUTCDate(thursday.getUTCDate() + 4 - weekday);

  const year = thursday.getUTCFullYear();
  const jan1 = Date.UTC(year, 0, 1);
  const week = Math.ceil(((thursday.getTime() - jan1) / 86400000 + 1) / 7);
  return `${year}-W${String(week).padStart(2, '0')}`;
}

/** Storage key for this week's counter. */
export function weekKey(date = new Date()) {
  return `w:${isoWeekKey(date)}`;
}

/**
 * Storage key for a per-tool/per-event counter, or null when either half is not
 * whitelisted — the caller drops the report rather than storing it.
 */
export function eventKey(event, tool) {
  return EVENTS.includes(event) && TOOLS.includes(tool) ? `evt:${event}:${tool}` : null;
}

/** Every per-tool/per-event key name, in a stable order, for the breakdown. */
export function breakdownNames() {
  const names = [];
  for (const event of [...EVENTS].sort()) {
    for (const tool of [...TOOLS].sort()) names.push(`${event}:${tool}`);
  }
  return names;
}
