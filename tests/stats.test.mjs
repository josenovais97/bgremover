/**
 * Unit tests for the /api/stats/ counter helpers (worker/lib.mjs).
 *
 * Unlike the other two suites here, nothing has to be scraped out of the source
 * text: worker/lib.mjs exists precisely so the pure parts of the endpoint can be
 * imported. worker/index.mjs itself cannot be (it imports `cloudflare:workers`),
 * so the Durable Object is covered by `wrangler dev --local` rather than here.
 *
 * The ISO-week key is the part most worth pinning down. It decides which bucket
 * "this week" reads from, and it is wrong in the ways calendar code is always
 * wrong — at the turn of the year, and only for a few days a year, long after
 * anyone would connect the bad number to the cause.
 *
 * Run: node tests/stats.test.mjs   (exit code 0 = pass)
 */
import {
  MAX_N, TOOLS,
  breakdownNames, clampCount, eventKey, isoWeekKey, weekKey,
} from '../worker/lib.mjs';

let failures = 0;
function check(name, cond) {
  console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}`);
  if (!cond) failures++;
}

const week = (iso) => isoWeekKey(new Date(`${iso}T12:00:00Z`));

// Year boundaries, where an ISO week belongs to the year of its Thursday and so
// disagrees with the calendar year. Verified against `date -d … +%G-W%V`.
const boundaries = [
  ['2026-01-01', '2026-W01'],  // Thursday — its own week's Thursday
  ['2025-12-29', '2026-W01'],  // Monday, but the week's Thursday is in 2026
  ['2025-12-28', '2025-W52'],  // the Sunday before it, still the old year
  ['2021-01-01', '2020-W53'],  // Friday of a 53-week year
  ['2023-01-01', '2022-W52'],  // Sunday belongs to the previous year's last week
  ['2024-12-30', '2025-W01'],
  ['2026-08-28', '2026-W35'],
];
for (const [date, expected] of boundaries) {
  check(`${date} is ${expected}`, week(date) === expected);
}

// Every day of one ISO week must land in the same bucket, Monday through Sunday
// — a bucket that rolls over mid-week would split a week's count in two.
const monday = week('2026-08-24');
const sameWeek = ['2026-08-24', '2026-08-25', '2026-08-26', '2026-08-27',
                  '2026-08-28', '2026-08-29', '2026-08-30'];
check('Mon-Sun share one bucket', sameWeek.every((d) => week(d) === monday));
check('the next Monday starts a new bucket', week('2026-08-31') !== monday);

// The keys are compared as strings when weeks are listed or pruned, so they have
// to sort in chronological order.
check('week keys sort chronologically',
  week('2025-12-28') < week('2026-01-01') && weekKey(new Date('2026-08-28')) === 'w:2026-W35');

// Time of day must not matter: the key is derived from the UTC date alone.
check('same day, different hours, same key',
  isoWeekKey(new Date('2026-08-28T00:00:00Z')) === isoWeekKey(new Date('2026-08-28T23:59:59Z')));

// `n` is client-supplied on a public, unauthenticated endpoint.
check('n is clamped to MAX_N', clampCount(9999) === MAX_N);
check('n below 1 becomes 1', clampCount(0) === 1 && clampCount(-5) === 1);
check('garbage n becomes 1', clampCount(undefined) === 1 && clampCount('abc') === 1
  && clampCount(null) === 1 && clampCount({}) === 1);
check('a normal n is untouched', clampCount(3) === 3 && clampCount('7') === 7);

// Only whitelisted pairs get a key; anything else is dropped rather than stored,
// which is what keeps the table bounded and the breakdown readable.
check('a whitelisted pair gets a key', eventKey('processed', 'home') === 'evt:processed:home');
check('an unknown tool is dropped', eventKey('processed', 'flushall') === null);
check('an unknown event is dropped', eventKey('deleted', 'home') === null);
check('a missing tool is dropped', eventKey('processed', undefined) === null);

// The tool ids the client can send come from static/js/stats.js; a tool listed
// there but missing here is a count that vanishes on arrival.
check('the four late-added tools are whitelisted',
  ['word_to_pdf', 'pdf_to_word', 'pdf_tools', 'csv_excel'].every((t) => TOOLS.includes(t)));

// The breakdown is zero-filled from the whitelists, so its shape does not change
// with the data.
const names = breakdownNames();
check('breakdown covers every event x tool', names.length === 2 * TOOLS.length);
check('breakdown names are unique', new Set(names).size === names.length);
check('breakdown is in a stable sorted order',
  names.join() === [...names].sort().join());

console.log(`\n${failures ? `${failures} FAILED` : 'All stats tests passed'}`);
process.exit(failures ? 1 : 0);
