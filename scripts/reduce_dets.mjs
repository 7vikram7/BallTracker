// Run the phone-side reducer (mobile/src/core/reducer.js) over a recorded dets.jsonl.
// node scripts/reduce_dets.mjs in.jsonl out.jsonl [t0 [dur]]   (env RCFG = reducer config JSON)
import fs from 'node:fs';
import readline from 'node:readline';
import { Reducer } from '../mobile/src/core/reducer.js';
const [inp, outp, t0s, durs] = process.argv.slice(2);
const t0 = t0s ? Number(t0s) : -Infinity, t1 = durs ? t0 + Number(durs) : Infinity;
const red = new Reducer(JSON.parse(process.env.RCFG || '{}'));
const out = fs.createWriteStream(outp);
const meta = new Map();
let batch = [];
const emit = (fs_) => { for (const f of fs_) { const m = meta.get(f.seq); const c = []; for (let i = 0; i < f.c.length; i += 4) c.push(f.c.slice(i, i + 4)); out.write(JSON.stringify({ ...m, c }) + '\n'); meta.delete(f.seq); } };
const rl = readline.createInterface({ input: fs.createReadStream(inp) });
for await (const line of rl) {
  const d = JSON.parse(line);
  if (d.ts < t0) continue;
  if (d.ts > t1) break;
  meta.set(d.seq, { seq: d.seq, tp: d.tp, ts: d.ts, w: d.w, h: d.h });
  batch.push({ seq: d.seq, t: d.tp, c: d.c.flat() });
  if (batch.length >= 6) { emit(red.push(batch)); batch = []; }
}
emit(red.push(batch)); emit(red.flush()); out.end();
console.error(JSON.stringify(red.stats));
