// Wire format between the app and `bt serve` (protocol 2).
// Mirror of balltracker/live/protocol.py: keep the two in step.
//
// Plain JavaScript with JSDoc types so it runs unchanged in React Native and
// in Node (tests). All binary values are little-endian.

export const PROTO_VERSION = 2;
export const ALGO = 'edge_color_motion';
export const ALGO_VERSION = '1.0.0';

const DETS_MAGIC = [0x42, 0x54, 0x44, 0x31]; // "BTD1"
const PREVIEW_MAGIC = [0x42, 0x54, 0x50, 0x31]; // "BTP1"
const DHDR = 10; // magic, u16 width, u16 height, u16 n_frames
const DFRM = 14; // u32 seq, f64 t_phone, u8 n_cands, u8 flags
const DCND = 16; // f32 u, v, radius, score
const PHDR = 20; // magic, u32 seq, f64 t_phone, u16 w, u16 h

/**
 * One processed frame: capture time on the phone clock (seconds) and the ball
 * candidates found in it, flattened as [u, v, r, score, u, v, r, score, ...].
 * @typedef {{ seq: number, t: number, c: number[] }} DetFrame
 */

/**
 * A batch of processed frames, as the native module emits it.
 * @typedef {{ width: number, height: number, frames: DetFrame[] }} DetBatch
 */

/**
 * @param {DetBatch} batch
 * @returns {ArrayBuffer}
 */
export function packDetections(batch) {
  const frames = batch.frames.slice(0, 65535);
  let size = DHDR;
  for (const f of frames) size += DFRM + DCND * Math.min(255, Math.floor(f.c.length / 4));
  const buf = new ArrayBuffer(size);
  const dv = new DataView(buf);
  DETS_MAGIC.forEach((b, i) => dv.setUint8(i, b));
  dv.setUint16(4, batch.width, true);
  dv.setUint16(6, batch.height, true);
  dv.setUint16(8, frames.length, true);
  let o = DHDR;
  for (const f of frames) {
    const n = Math.min(255, Math.floor(f.c.length / 4));
    dv.setUint32(o, f.seq >>> 0, true);
    dv.setFloat64(o + 4, f.t, true);
    dv.setUint8(o + 12, n);
    dv.setUint8(o + 13, 0);
    o += DFRM;
    for (let i = 0; i < n * 4; i++) {
      dv.setFloat32(o, f.c[i], true);
      o += 4;
    }
  }
  return buf;
}

/**
 * Inverse of packDetections (used by tests).
 * @param {ArrayBuffer} buf
 * @returns {DetBatch}
 */
export function unpackDetections(buf) {
  const dv = new DataView(buf);
  for (let i = 0; i < 4; i++) if (dv.getUint8(i) !== DETS_MAGIC[i]) throw new Error('bad detections magic');
  const width = dv.getUint16(4, true);
  const height = dv.getUint16(6, true);
  const n = dv.getUint16(8, true);
  const frames = [];
  let o = DHDR;
  for (let k = 0; k < n; k++) {
    const seq = dv.getUint32(o, true);
    const t = dv.getFloat64(o + 4, true);
    const nc = dv.getUint8(o + 12);
    o += DFRM;
    const c = [];
    for (let i = 0; i < nc * 4; i++) {
      c.push(dv.getFloat32(o, true));
      o += 4;
    }
    frames.push({ seq, t, c });
  }
  return { width, height, frames };
}

/**
 * Full-resolution preview JPEG (dashboard thumbnail and calibration snapshot).
 * @param {number} seq
 * @param {number} tPhone
 * @param {number} width
 * @param {number} height
 * @param {Uint8Array} jpeg
 * @returns {ArrayBuffer}
 */
export function packPreview(seq, tPhone, width, height, jpeg) {
  const buf = new ArrayBuffer(PHDR + jpeg.length);
  const dv = new DataView(buf);
  PREVIEW_MAGIC.forEach((b, i) => dv.setUint8(i, b));
  dv.setUint32(4, seq >>> 0, true);
  dv.setFloat64(8, tPhone, true);
  dv.setUint16(16, width, true);
  dv.setUint16(18, height, true);
  new Uint8Array(buf, PHDR).set(jpeg);
  return buf;
}

const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const B64_LOOKUP = (() => {
  const t = new Int16Array(256).fill(-1);
  for (let i = 0; i < 64; i++) t[B64.charCodeAt(i)] = i;
  return t;
})();

/**
 * Decode base64 (the native module hands JPEGs to JavaScript as base64).
 * @param {string} s
 * @returns {Uint8Array}
 */
export function base64ToBytes(s) {
  let len = s.length;
  while (len > 0 && (s[len - 1] === '=' || s[len - 1] === '\n')) len--;
  const out = new Uint8Array(Math.floor((len * 3) / 4));
  let o = 0, acc = 0, bits = 0;
  for (let i = 0; i < len; i++) {
    const v = B64_LOOKUP[s.charCodeAt(i)];
    if (v < 0) continue; // skip whitespace
    acc = (acc << 6) | v;
    bits += 6;
    if (bits >= 8) {
      bits -= 8;
      out[o++] = (acc >> bits) & 0xff;
    }
  }
  return o === out.length ? out : out.subarray(0, o);
}
