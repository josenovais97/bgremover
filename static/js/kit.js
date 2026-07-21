/**
 * Shared browser kit — the helpers every tool page needs.
 *
 * Loaded as a CLASSIC script from base.html (not an ES module) on purpose:
 * Django's static storage does not rewrite ES-module import paths, so a local
 * `import` between tool modules breaks in production. A classic script that
 * publishes `window.CBG` sidesteps that entirely — it always runs before the
 * type="module" tool scripts, which are deferred by definition.
 *
 * Every tool used to carry its own private copy of $, $$, Toast, loadImage,
 * humanSize and the drag/drop/paste wiring. New tools should reach for CBG;
 * older self-contained modules are migrated as they're touched.
 */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  const Toast = {
    show(message, type = 'success') {
      const c = $('#toast-container');
      if (!c) return;
      const map = {
        success: ['bg-green-50 dark:bg-green-900/40 text-green-800 dark:text-green-200 border-green-200 dark:border-green-800', 'fa-circle-check text-green-500'],
        error: ['bg-red-50 dark:bg-red-900/40 text-red-800 dark:text-red-200 border-red-200 dark:border-red-800', 'fa-circle-exclamation text-red-500'],
      };
      const [cls, icon] = map[type] || map.success;
      const el = document.createElement('div');
      el.className = `pointer-events-auto flex items-center gap-3 px-5 py-3.5 rounded-xl border shadow-lg transition-all duration-300 translate-y-4 opacity-0 ${cls}`;
      el.setAttribute('role', 'alert');
      el.innerHTML = `<i class="fa-solid ${icon} text-lg"></i><span class="font-medium text-sm"></span>`;
      // textContent, not innerHTML: messages can include a user's file name.
      el.querySelector('span').textContent = message;
      c.appendChild(el);
      requestAnimationFrame(() => el.classList.remove('translate-y-4', 'opacity-0'));
      setTimeout(() => { el.classList.add('opacity-0', 'translate-y-4'); setTimeout(() => el.remove(), 300); }, 3600);
    },
  };

  const loadImage = (src) => new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });

  const humanSize = (b) =>
    (b < 1024 ? `${b} B` : b < 1048576 ? `${(b / 1024).toFixed(0)} KB` : `${(b / 1048576).toFixed(1)} MB`);

  const baseName = (name) => String(name || 'image').replace(/\.[^.]+$/, '');

  /** Save a Blob to the user's downloads under `name`. */
  function download(blob, name) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
  }

  /**
   * Wire a dropzone: click, keyboard, drag & drop, and clipboard paste.
   *
   * `onFiles` receives an array of image Files (already filtered). Pass
   * `multiple: false` to hand over only the first one.
   */
  function dropzone(el, { input, icon, browse, multiple = true, onFiles }) {
    if (!el || !input) return;
    const deliver = (list) => {
      const files = [...(list || [])].filter((f) => f && /^image\//.test(f.type));
      if (!files.length) { Toast.show('Please choose an image', 'error'); return; }
      onFiles(multiple ? files : [files[0]]);
    };
    const open = () => input.click();

    if (browse) browse.addEventListener('click', (e) => { e.stopPropagation(); open(); });
    el.addEventListener('click', open);
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
    });
    input.addEventListener('change', (e) => { deliver(e.target.files); input.value = ''; });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      el.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => el.addEventListener(evt, () => {
      el.classList.add('border-primary', 'bg-primary/5');
      if (icon) icon.classList.add('scale-110');
    }));
    ['dragleave', 'drop'].forEach((evt) => el.addEventListener(evt, () => {
      el.classList.remove('border-primary', 'bg-primary/5');
      if (icon) icon.classList.remove('scale-110');
    }));
    el.addEventListener('drop', (e) => deliver(e.dataTransfer.files));
    document.addEventListener('paste', (e) => {
      const items = [...(e.clipboardData?.items || [])].filter((i) => i.kind === 'file');
      if (items.length) deliver(items.map((i) => i.getAsFile()));
    });
  }

  /**
   * ZIP a list of {name, blob} entries and save it.
   *
   * JSZip is imported on demand (absolute CDN URL — allowed by the CSP and
   * cached by the service worker), so tools that never batch don't pay for it.
   */
  async function zipDownload(entries, zipName = 'clearbg.zip') {
    const { default: JSZip } = await import('https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm');
    const zip = new JSZip();
    const used = new Set();
    for (const { name, blob } of entries) {
      // Two source files can share a name; suffix collisions rather than
      // silently overwriting one of the user's results.
      let unique = name;
      for (let i = 2; used.has(unique); i++) unique = name.replace(/(\.[^.]+)$/, `-${i}$1`);
      used.add(unique);
      zip.file(unique, blob);
    }
    download(await zip.generateAsync({ type: 'blob' }), zipName);
  }

  /** Tiny localStorage-backed settings store, namespaced per tool. */
  function remember(ns) {
    const key = `clearbg:${ns}`;
    return {
      get() {
        try { return JSON.parse(localStorage.getItem(key)) || {}; } catch { return {}; }
      },
      set(patch) {
        try { localStorage.setItem(key, JSON.stringify({ ...this.get(), ...patch })); } catch { /* private mode */ }
      },
    };
  }

  window.CBG = { $, $$, Toast, loadImage, humanSize, baseName, download, dropzone, zipDownload, remember };
})();
