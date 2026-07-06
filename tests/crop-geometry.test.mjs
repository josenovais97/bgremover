/**
 * Unit tests for the pure crop-geometry math in static/js/app.js.
 *
 * app.js is a browser ES module (it imports from a CDN and touches `document`),
 * so it can't be imported directly under Node. Instead we extract the two pure,
 * dependency-free helpers — `clamp` and `cropGeometry` — straight from the
 * source text and evaluate them. That keeps a single source of truth: the test
 * exercises exactly the code the app ships, and fails loudly if the function is
 * renamed or its shape changes.
 *
 * Run: node tests/crop-geometry.test.mjs   (exit code 0 = pass)
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(here, '..', 'static', 'js', 'app.js'), 'utf8');

function extract(re, label) {
  const m = src.match(re);
  if (!m) throw new Error(`Could not find ${label} in app.js — did it get renamed?`);
  return m[0];
}

// `const clamp = (...) => ...;`  and  `function cropGeometry(...) { ... }`.
// cropGeometry's body has no nested block braces, so the first line-start `}`
// closes the function.
const clampSrc = extract(/const clamp = [^\n]+;/, 'clamp');
const geomSrc = extract(/function cropGeometry\([\s\S]*?\n}/, 'cropGeometry');

const cropGeometry = new Function(`${clampSrc}\n${geomSrc}\nreturn cropGeometry;`)();

let failures = 0;
function check(name, cond) {
  console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}`);
  if (!cond) failures++;
}

function within(iw, ih, g) {
  return (
    g.sx >= -1e-9 &&
    g.sy >= -1e-9 &&
    g.sx + g.sw <= iw + 1e-6 &&
    g.sy + g.sh <= ih + 1e-6 &&
    g.outW > 0 &&
    g.outH > 0
  );
}

const cases = [
  ['circle centered on landscape', 1200, 800, { aspect: 1, z: 1, u: 0.5, v: 0.5 }],
  ['circle zoomed 3x', 1200, 800, { aspect: 1, z: 3, u: 0.5, v: 0.5 }],
  ['drag far past edges clamps', 1200, 800, { aspect: 1, z: 1, u: 5, v: -5 }],
  ['16:9 on portrait source', 600, 1000, { aspect: 16 / 9, z: 1, u: 0.5, v: 0.5 }],
  ['9:16 on landscape source', 1600, 900, { aspect: 9 / 16, z: 1.5, u: 0.5, v: 0.5 }],
  ['4:5 at max zoom off-centre', 1000, 1000, { aspect: 4 / 5, z: 5, u: 0.9, v: 0.1 }],
  ['tiny source stays in bounds', 3, 7, { aspect: 1, z: 1, u: 0.5, v: 0.5 }],
];

for (const [name, iw, ih, crop] of cases) {
  const g = cropGeometry(iw, ih, crop);
  check(`${name}: sampling rect within bounds`, within(iw, ih, g));
  check(`${name}: output aspect preserved`, Math.abs(g.outW / g.outH - crop.aspect) < 0.02);
}

// Zooming in must sample a strictly smaller region than zoom = 1.
const z1 = cropGeometry(1200, 800, { aspect: 1, z: 1, u: 0.5, v: 0.5 });
const z2 = cropGeometry(1200, 800, { aspect: 1, z: 2, u: 0.5, v: 0.5 });
check('zoom shrinks the sampled region', z2.sw < z1.sw && z2.sh < z1.sh);

// Missing u/v/z default to a centred, un-zoomed crop rather than NaN.
const dflt = cropGeometry(1000, 1000, { aspect: 1 });
check('missing u/v/z defaults to a valid centred crop', within(1000, 1000, dflt) && dflt.outW === 1000);

console.log(`\n${failures ? `${failures} FAILED` : 'All geometry tests passed'}`);
process.exit(failures ? 1 : 0);
