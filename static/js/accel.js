/**
 * Shared inference configuration for @imgly/background-removal.
 *
 * Every tool page runs the same model, so the choice of execution backend lives
 * here rather than being re-derived (and re-decided differently) in each one.
 *
 * WebGPU is the one knob that speeds up inference without trading away model
 * quality: given an adapter, the library runs the same full-precision weights on
 * the `webgpu` execution provider instead of the WASM CPU backend. It also
 * unlocks `proxyToWorker`, which the library honours ONLY on the GPU path — that
 * moves inference off the main thread, so the page stays responsive for the
 * whole job instead of locking up the way the WASM path does.
 *
 * Choosing the backend is a one-way door, deliberately: onnxruntime-web ships
 * two incompatible builds (`.jsep` for WebGPU, plain for WASM), and the library
 * caches whichever module it imported first for the lifetime of the page along
 * with the matching wasm binary path. A GPU session that fails therefore cannot
 * be retried on the CPU in the same page — the cached module would be handed the
 * wrong binary. So we remember the failure and take the CPU path from the next
 * load onward.
 */

const GPU_OFF_KEY = 'bgr_gpu_off';   // set once a GPU session has actually failed here
const RELOAD_KEY = 'bgr_gpu_fb';     // guards against a reload loop within one tab
const PROVEN_KEY = 'bgr_proven';     // set once a removal has actually finished here

let resolved = null;
let usingGpu = false;

/** True once the resolved config asked for the GPU backend. */
export const isGpu = () => usingGpu;

/**
 * Has this visitor ever completed a removal on this device?
 *
 * The flag is what separates "someone deciding whether this site works" from
 * "someone who already knows it does", which is the only input to the model
 * choice below.
 */
function proven() {
  try { return !!localStorage.getItem(PROVEN_KEY); } catch { return false; }
}

/**
 * Record that a removal completed, so later visits earn the full-quality model.
 * Called from app.js the moment a cut-out lands on screen.
 */
export function markRemovalSucceeded() {
  try { localStorage.setItem(PROVEN_KEY, '1'); } catch { /* private mode: stay on the light model */ }
}

/**
 * Which model this page will use. Resolved ONCE at module load, not per call.
 *
 * Two things force that. The library memoises its parsed config on the first
 * call (see `removalConfig`), so a name that changed mid-page would be ignored
 * by inference but still believed by the download badge — the badge would
 * advertise a size nobody was downloading. And `markRemovalSucceeded()` fires
 * during the very first run, so a live-evaluated version would flip the moment
 * it succeeded and mislabel the download already in flight.
 *
 * The choice itself is a first-impression trade. Full `isnet` needs cross-origin
 * isolation for the multi-threaded WASM backend, but it costs ~190 MB — and a
 * first-time visitor pays that *before* their first result, on the one page that
 * has to convince them the site works at all. Ironically the isolated browsers
 * that got the biggest download were the best-supported ones (desktop Chrome),
 * so the strongest traffic got the worst first run. So the first removal on a
 * device uses the quantised model at ~56 MB, and the full weights are fetched
 * only once someone has seen a result and come back. Quality on the light model
 * is close enough that most visitors never notice; a 190 MB wait before any
 * output is something everyone notices.
 */
const MODEL = (self.crossOriginIsolated && proven()) ? 'isnet' : 'isnet_quint8';

const modelName = () => MODEL;

/**
 * Roughly how much the first run downloads, in MB — model weights plus the
 * onnxruntime binary, which is the whole one-time cost the user waits through.
 *
 * Measured from the CDN's resources.json: the chunks are served raw, with no
 * gzip or brotli, so these are the real bytes on the wire and not a compressed
 * estimate. isnet 176 MB / isnet_quint8 44 MB; the ORT wasm is 12 MB, or 23 MB
 * for the .jsep build the WebGPU path needs. Quoted against the smaller runtime
 * because the backend is not known yet when the badge first appears.
 */
export const downloadMb = () => (modelName() === 'isnet' ? 190 : 56);

async function gpuAvailable() {
  if (!navigator.gpu) return false;
  try {
    if (localStorage.getItem(GPU_OFF_KEY)) return false; // failed here before
  } catch { /* private mode: fall through and probe */ }
  try {
    // The same check the library makes; doing it ourselves keeps the decision
    // in one place and lets us record failures against it.
    return (await navigator.gpu.requestAdapter()) !== null;
  } catch {
    return false;
  }
}

/**
 * The removal config for this page, resolved once.
 *
 * Must be awaited before the FIRST removeBackground/preload call and reused for
 * every later one: the library memoises its parsed config on
 * JSON.stringify(config), so whatever shape reaches it first is the shape it
 * keeps. `extra` is only read on that first call.
 */
export function removalConfig(extra) {
  resolved ??= (async () => {
    const config = {
      // Full-quality 'isnet' only where the page is cross-origin isolated
      // (COOP+COEP, set per-route by SecurityHeadersMiddleware, so the WASM
      // runtime can use its multi-threaded + SIMD backend) AND the visitor has
      // completed a removal here before. Without isolation (e.g. Safari) the
      // quantized 'isnet_quint8' also keeps the main thread from stalling long
      // enough to trip the browser's "page not responding" prompt. See MODEL.
      model: modelName(),
      ...extra,
    };
    if (await gpuAvailable()) {
      config.device = 'gpu';
      config.proxyToWorker = true;
      usingGpu = true;
    }
    return config;
  })();
  return resolved;
}

/**
 * Record that the GPU path is unusable here and, when it is free to do so,
 * reload straight into the CPU path.
 *
 * `hasWork` is false during idle warm-up — nothing is on screen to lose, so the
 * reload is invisible and the user never learns the GPU attempt happened. Once
 * there is work on screen a reload would discard it, so we only leave the flag
 * for next time and let the caller surface the error.
 *
 * Returns true if a reload was triggered.
 */
export function markGpuFailed(hasWork) {
  if (!usingGpu) return false;
  try { localStorage.setItem(GPU_OFF_KEY, '1'); } catch { /* nothing we can do */ }
  let reload = false;
  try {
    reload = !hasWork && !sessionStorage.getItem(RELOAD_KEY);
    if (reload) sessionStorage.setItem(RELOAD_KEY, '1');
  } catch { reload = false; }
  if (reload) location.reload();
  return reload;
}
