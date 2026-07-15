/**
 * Cross-tool image handoff.
 *
 * Lets one tool pass a result image to another without a re-upload: the source
 * stores a Blob in IndexedDB and navigates; the destination reads it once on
 * load. It's one-shot (read-and-clear) with a short TTL so a stale handoff can
 * never hijack an unrelated later visit to a tool page.
 */
const DB = 'clearbg-handoff';
const STORE = 'img';
const KEY = 'current';
const TTL_MS = 60000; // a handoff is only honoured within a minute of being set

function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

/** Store a blob for the next tool to pick up. Returns true on success. */
export async function putHandoff(blob, name = 'image.png') {
  try {
    const db = await openDb();
    await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).put({ blob, name, type: blob.type || 'image/png', ts: Date.now() }, KEY);
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
    db.close();
    return true;
  } catch {
    return false;
  }
}

/** Read-and-clear the pending handoff. Returns a fresh File, or null. */
export async function takeHandoff() {
  try {
    const db = await openDb();
    const rec = await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readwrite');
      const store = tx.objectStore(STORE);
      const get = store.get(KEY);
      get.onsuccess = () => { store.delete(KEY); resolve(get.result); };
      get.onerror = () => reject(get.error);
    });
    db.close();
    if (!rec || !rec.blob || Date.now() - rec.ts > TTL_MS) return null;
    return new File([rec.blob], rec.name, { type: rec.type });
  } catch {
    return null;
  }
}
