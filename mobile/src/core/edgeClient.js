// WebSocket client for `bt serve` (protocol 2, "edge" camera).
//
// Responsibilities: say hello, answer clock-sync pings with the native clock
// (the same clock the frame timestamps use), send detection batches and
// previews, pass server messages (config, calibration, calls, status) up, and
// reconnect by itself. No React, no native code: it runs in Node for tests.

import { packDetections, packPreview, PROTO_VERSION } from './protocol.js';

/** @typedef {import('./protocol.js').DetBatch} DetBatch */

/**
 * @typedef {object} EdgeClientOptions
 * @property {string} url                       ws://host:8080/ws/edge
 * @property {() => object} hello               fields for the hello message (name, width, height, fps, ...)
 * @property {() => number} now                 phone clock, seconds (must match frame timestamps)
 * @property {any} [WebSocketImpl]              defaults to globalThis.WebSocket
 * @property {(state: string) => void} [onConnection]  'connecting' | 'connected' | 'disconnected' | 'stopped'
 * @property {(msg: any) => void} [onMessage]   every JSON message from the server except ping
 * @property {number} [maxBufferedBytes]        drop detections above this send backlog
 * @property {number} [maxBufferedPreviewBytes] skip previews above this send backlog
 */

const BACKOFF_S = [0.5, 1, 2, 3, 5];

export class EdgeClient {
  /** @param {EdgeClientOptions} opts */
  constructor(opts) {
    this.opts = opts;
    this.WS = opts.WebSocketImpl || globalThis.WebSocket;
    this.maxBuffered = opts.maxBufferedBytes ?? 2_000_000;
    this.maxBufferedPreview = opts.maxBufferedPreviewBytes ?? 300_000;
    /** @type {any} */
    this.ws = null;
    this.state = 'stopped';
    this.stopped = true;
    this.attempt = 0;
    this.timer = null;
    this.welcome = null;
    this.stats = { sentFrames: 0, droppedFrames: 0, offlineFrames: 0, sentBatches: 0, previews: 0, bytes: 0, reconnects: 0, pongs: 0 };
  }

  start() {
    if (!this.stopped) return;
    this.stopped = false;
    this._connect();
  }

  stop() {
    this.stopped = true;
    if (this.timer) clearTimeout(this.timer);
    this.timer = null;
    const ws = this.ws;
    this.ws = null;
    if (ws) {
      try { ws.close(); } catch (_) { /* already closed */ }
    }
    this._setState('stopped');
  }

  get connected() {
    return !!this.ws && this.ws.readyState === 1 && this.state === 'connected';
  }

  /** Re-send hello (e.g. the frame rate or resolution changed). */
  resendHello() {
    if (this.connected) this._sendJson(this._hello());
  }

  /** @param {DetBatch} batch */
  sendDetections(batch) {
    const n = batch.frames.length;
    if (!n) return false;
    // Not connected (starting up, reconnecting): not a network problem, counted separately.
    if (!this.connected) {
      this.stats.offlineFrames += n;
      return false;
    }
    // Connected but the network can't keep up: these are the real Wi-Fi losses.
    if (this._buffered() > this.maxBuffered) {
      this.stats.droppedFrames += n;
      return false;
    }
    const buf = packDetections(batch);
    this.ws.send(buf);
    this.stats.sentFrames += n;
    this.stats.sentBatches += 1;
    this.stats.bytes += buf.byteLength;
    return true;
  }

  /**
   * @param {number} seq @param {number} t @param {number} width @param {number} height
   * @param {Uint8Array} jpeg
   */
  sendPreview(seq, t, width, height, jpeg) {
    if (!this.connected || this._buffered() > this.maxBufferedPreview) return false;
    const buf = packPreview(seq, t, width, height, jpeg);
    this.ws.send(buf);
    this.stats.previews += 1;
    this.stats.bytes += buf.byteLength;
    return true;
  }

  /** Informational stats shown on the dashboard's camera card.
   * @param {Record<string, unknown>} obj */
  sendStats(obj) {
    if (this.connected) this._sendJson({ type: 'stats', ...obj });
  }

  // --- internals -----------------------------------------------------------
  _hello() {
    return { type: 'hello', proto: PROTO_VERSION, mode: 'edge', ...this.opts.hello() };
  }

  _buffered() {
    const b = this.ws && this.ws.bufferedAmount;
    return typeof b === 'number' ? b : 0; // React Native may not report it
  }

  /** @param {string} s */
  _setState(s) {
    if (this.state === s) return;
    this.state = s;
    if (this.opts.onConnection) this.opts.onConnection(s);
  }

  /** @param {object} obj */
  _sendJson(obj) {
    try {
      this.ws.send(JSON.stringify(obj));
    } catch (_) { /* socket closing: the close handler reconnects */ }
  }

  _connect() {
    if (this.stopped) return;
    this._setState('connecting');
    let ws;
    try {
      ws = new this.WS(this.opts.url);
    } catch (e) {
      this._scheduleReconnect();
      return;
    }
    this.ws = ws;
    ws.binaryType = 'arraybuffer';
    ws.onopen = () => {
      if (ws !== this.ws) return;
      this.attempt = 0;
      this._sendJson(this._hello());
      this._setState('connected');
    };
    ws.onmessage = (/** @type {{data: unknown}} */ ev) => {
      if (ws !== this.ws || typeof ev.data !== 'string') return;
      let msg;
      try { msg = JSON.parse(ev.data); } catch (_) { return; }
      if (msg.type === 'ping') {
        // Answer immediately: the server's clock sync uses the round-trip time.
        this._sendJson({ type: 'pong', id: msg.id, tp: this.opts.now() });
        this.stats.pongs += 1;
        return;
      }
      if (msg.type === 'welcome') this.welcome = msg;
      if (this.opts.onMessage) this.opts.onMessage(msg);
    };
    ws.onerror = () => { /* onclose follows */ };
    ws.onclose = () => {
      if (ws !== this.ws) return;
      this.ws = null;
      if (this.stopped) return;
      this._setState('disconnected');
      this._scheduleReconnect();
    };
  }

  _scheduleReconnect() {
    if (this.stopped) return;
    const delay = BACKOFF_S[Math.min(this.attempt, BACKOFF_S.length - 1)];
    this.attempt += 1;
    this.stats.reconnects += 1;
    this.timer = setTimeout(() => {
      this.timer = null;
      this._connect();
    }, delay * 1000);
  }
}
