// CameraSession: the app's logic, independent of React and of the platform.
//
// Wires the native camera module (capture + on-phone detection) to the server
// connection, and keeps one state object the UI renders. The native module is
// injected, so tests drive it with a mock (test/mockNative.js).

import { Reducer } from './reducer.js';
import { EdgeClient } from './edgeClient.js';
import { ALGO, ALGO_VERSION, base64ToBytes } from './protocol.js';

/**
 * What the native module must provide (modules/ball-camera/src/BallCameraModule.ts).
 * @typedef {object} NativeCamera
 * @property {() => number} now
 * @property {(opts: {width: number, height: number, fps: number, previewEverySec?: number, previewQuality?: number, batchMs?: number, detector?: any}) => Promise<{width: number, height: number, fps: number, format?: string, timestampSource?: string}>} start
 * @property {() => Promise<void>} stop
 * @property {(cfg: object) => void} setDetectorConfig
 * @property {(opts: any) => Promise<any>} setExposure
 * @property {(event: any, fn: (payload: any) => void) => {remove: () => void}} addListener
 * @property {(text: string) => void} [speak]  say a call out loud (text-to-speech); absent in old builds
 */

/**
 * @typedef {object} SessionSettings
 * @property {string} url
 * @property {string} name
 * @property {number} width
 * @property {number} height
 * @property {number} fps
 * @property {number} [previewEverySec]
 * @property {number} [previewQuality]
 * @property {number} [batchMs]
 * @property {string} [device]
 * @property {string} [platform]
 * @property {string} [appVersion]
 * @property {object} [reduce]  phone-side data reduction settings (reducer.js); the server can override
 * @property {boolean} [speakCalls]  say the server's calls ("OUT", "FAULT") out loud (default true)
 */

/**
 * @typedef {object} SessionState
 * @property {'idle'|'starting'|'running'|'stopping'|'error'} phase
 * @property {string} connection  'connecting' | 'connected' | 'disconnected' | 'stopped'
 * @property {string|null} serverName
 * @property {boolean} calibrated
 * @property {{width: number, height: number, fps: number, format?: string, timestampSource?: string}|null} camera
 * @property {{fpsCapture: number, fpsProcessed: number, detectMs: number, dropped: number, thermal: string, battery?: number}} native
 * @property {{proc_fps?: number, fps_in?: number, drops?: number, rtt_ms?: number|null, latency_ms?: number|null, calibrated?: boolean}|null} server
 * @property {{sentFrames: number, droppedFrames: number, kbps: number}} link
 * @property {number} candidatesPerSec
 * @property {{text: string, at: number}|null} lastCall
 * @property {string|null} error
 * @property {string|null} ended  set when the server ended the session (Stop session on the dashboard)
 */

/** @returns {SessionState} */
export const initialState = () => ({
  phase: 'idle', // idle | starting | running | stopping | error
  connection: 'stopped',
  serverName: null,
  calibrated: false,
  camera: null, // {width, height, fps, format}
  native: { fpsCapture: 0, fpsProcessed: 0, detectMs: 0, dropped: 0, thermal: 'nominal', battery: -1 },
  server: null, // last status message: {proc_fps, fps_in, drops, rtt_ms, latency_ms}
  link: { sentFrames: 0, droppedFrames: 0, kbps: 0 },
  candidatesPerSec: 0,
  lastCall: null, // {text, at}
  error: null,
  ended: null, // the server's reason, when it ended the session
});

export class CameraSession {
  /**
   * @param {object} p
   * @param {NativeCamera} p.native
   * @param {SessionSettings} p.settings
   * @param {(state: SessionState) => void} [p.onState]
   * @param {any} [p.WebSocketImpl]
   * @param {() => number} [p.wallNow]  ms clock for rates (Date.now by default)
   */
  constructor({ native, settings, onState, WebSocketImpl, wallNow }) {
    this.native = native;
    this.settings = settings;
    this.onState = onState || (() => {});
    this.WebSocketImpl = WebSocketImpl;
    this.wallNow = wallNow || (() => Date.now());
    this.state = initialState();
    /** @type {{remove: () => void}[]} */
    this.subs = [];
    /** @type {EdgeClient | null} */
    this.client = null;
    this.detectorConfig = null;
    this.reducer = new Reducer(settings.reduce);
    this._rate = { t: this.wallNow(), bytes: 0, cands: 0 };
    this._lastStatsSent = 0;
  }

  /** @param {Partial<SessionState>} patch */
  _set(patch) {
    this.state = { ...this.state, ...patch };
    this.onState(this.state);
  }

  async start() {
    if (this.state.phase === 'running' || this.state.phase === 'starting') return;
    const s = this.settings;
    this._set({ phase: 'starting', error: null });
    this.subs.push(this.native.addListener('onDetections', (b) => this._onDetections(b)));
    this.subs.push(this.native.addListener('onPreview', (p) => this._onPreview(p)));
    this.subs.push(this.native.addListener('onStats', (st) => this._onNativeStats(st)));
    this.subs.push(this.native.addListener('onError', (/** @type {any} */ e) => this._set({ error: String(e && e.message || e) })));
    let cam;
    try {
      cam = await this.native.start({
        width: s.width, height: s.height, fps: s.fps,
        previewEverySec: s.previewEverySec ?? 2.0,
        previewQuality: s.previewQuality ?? 0.7,
        batchMs: s.batchMs ?? 50,
        detector: this.detectorConfig || undefined,
      });
    } catch (/** @type {any} */ e) {
      this._unsubscribe();
      this._set({ phase: 'error', error: `Camera: ${e && e.message || e}` });
      return;
    }
    this._set({ phase: 'running', camera: cam });
    this.client = new EdgeClient({
      url: s.url,
      WebSocketImpl: this.WebSocketImpl,
      now: () => this.native.now(),
      hello: () => ({
        name: s.name, device: s.device || 'unknown', platform: s.platform || 'unknown',
        // ts_source: the clock the native side says its frame times are on (Android checks it)
        width: cam.width, height: cam.height, fps: cam.fps, ts_source: `app:${cam.timestampSource || 'sensor'}`,
        algo: ALGO, algo_version: ALGO_VERSION, app_version: s.appVersion || 'dev',
        reduce: this.reducer.cfg.enabled,
      }),
      onConnection: (c) => this._set({ connection: c }),
      onMessage: (m) => this._onServer(m),
    });
    this.client.start();
  }

  async stop() {
    if (this.state.phase === 'idle') return;
    this._set({ phase: 'stopping' });
    const rest = this.reducer.flush();
    if (this.client && rest.length && this.state.camera) {
      this.client.sendDetections({ width: this.state.camera.width, height: this.state.camera.height, frames: rest });
    }
    this._unsubscribe();
    if (this.client) this.client.stop();
    this.client = null;
    try {
      await this.native.stop();
    } catch (_) { /* already stopped */ }
    this._set({ phase: 'idle', connection: 'stopped' });
  }

  /** Lock a short shutter (ISO raised to keep brightness), or go back to auto. */
  /** @param {{mode: 'auto'|'locked'|'shutter', shutterS?: number, iso?: number}} opts */
  async setExposure(opts) {
    return this.native.setExposure(opts);
  }

  _unsubscribe() {
    for (const s of this.subs) {
      try { s.remove(); } catch (_) { /* ignore */ }
    }
    this.subs = [];
  }

  /** @param {any} m  a JSON message from the server */
  _onServer(m) {
    switch (m.type) {
      case 'welcome':
        this._set({ serverName: m.name, calibrated: !!m.calibrated });
        break;
      case 'config':
        if (m.reduce) this.reducer.configure(m.reduce);
        if (m.detector) {
          // The server owns the detector settings (ball colour etc.); the frame
          // rate is what the camera actually runs at.
          const fps = this._fpsActual || (this.state.camera ? this.state.camera.fps : m.detector.fps);
          this.detectorConfig = { ...m.detector, fps };
          this.native.setDetectorConfig(this.detectorConfig);
        }
        break;
      case 'calibration':
        this._set({ calibrated: !!m.camera });
        break;
      case 'status':
        this._set({ server: m, calibrated: !!m.calibrated });
        break;
      case 'call':
        this._set({ lastCall: { text: m.text, at: this.wallNow() } });
        // Every phone says the call, so players hear it wherever they are on the court.
        if (m.text && this.settings.speakCalls !== false && this.native.speak) {
          try { this.native.speak(String(m.text)); } catch (_) { /* no speech on this phone */ }
        }
        break;
      case 'session_end':
        // Stop session on the dashboard: stop the camera and don't reconnect (the server is going away).
        this._set({ ended: m.reason || 'The session was ended from the dashboard.' });
        this.stop();
        break;
      default:
        break;
    }
  }

  /** @param {import('./protocol.js').DetBatch} batch */
  _onDetections(batch) {
    if (!this.client) return;
    let n = 0;
    for (const f of batch.frames) n += f.c.length / 4;
    this._rate.cands += n;
    // The phone sees every frame; the server gets still clutter removed and full frame rate only
    // around bounces / hits (see reducer.js).
    const frames = this.reducer.push(batch.frames);
    if (frames.length) this.client.sendDetections({ ...batch, frames });
  }

  /** @param {{seq: number, t: number, width: number, height: number, jpegBase64: string}} p */
  _onPreview(p) {
    if (!this.client) return;
    const bytes = base64ToBytes(p.jpegBase64);
    this.client.sendPreview(p.seq, p.t, p.width, p.height, bytes);
  }

  /**
   * The camera may deliver fewer frames than asked (field test 3: a Samsung asked for 120 gave 58).
   * The detector's background model is tuned by frame rate, so after 3 s below 85% of the asked
   * rate it is re-tuned to the measured one (review of defed68, TODO-23).
   * @param {number | undefined} fps
   */
  _noteFps(fps) {
    const asked = this.state.camera ? this.state.camera.fps : 0;
    if (!asked || fps === undefined || !(fps > 0)) return;
    /** @type {number[]} */
    const seen = [...(this._fpsSeen || []), fps].slice(-3);
    this._fpsSeen = seen;
    const low = this._fpsSeen.length === 3 && this._fpsSeen.every((f) => f < 0.85 * asked);
    if (!low) return;
    const med = [...this._fpsSeen].sort((a, b) => a - b)[1];
    if (this._fpsActual && Math.abs(med - this._fpsActual) <= 0.15 * this._fpsActual) return;
    this._fpsActual = Math.round(med);
    if (this.detectorConfig) {
      this.detectorConfig = { ...this.detectorConfig, fps: this._fpsActual };
      this.native.setDetectorConfig(this.detectorConfig);
    }
  }

  /** @param {{fpsCapture: number, fpsProcessed: number, detectMs: number, dropped: number, thermal: string, battery?: number, tsSource?: string, detectErrors?: number}} st */
  _onNativeStats(st) {
    this._noteFps(st.fpsCapture);
    const now = this.wallNow();
    const dt = Math.max(1e-3, (now - this._rate.t) / 1000);
    const cs = this.client ? this.client.stats : { sentFrames: 0, droppedFrames: 0, bytes: 0 };
    const kbps = ((cs.bytes - this._rate.bytes) * 8) / 1000 / dt;
    const candidatesPerSec = this._rate.cands / dt;
    this._rate = { t: now, bytes: cs.bytes, cands: 0 };
    this._set({
      native: { ...this.state.native, ...st },
      link: { sentFrames: cs.sentFrames, droppedFrames: cs.droppedFrames, kbps },
      candidatesPerSec,
    });
    if (this.client && now - this._lastStatsSent >= 1000) {
      this._lastStatsSent = now;
      this.client.sendStats({
        fps_capture: st.fpsCapture, fps_processed: st.fpsProcessed, detect_ms: st.detectMs,
        ...(this._fpsActual ? { fps_detector: this._fpsActual } : {}),
        phone_drops: st.dropped, thermal: st.thermal, battery: st.battery,
        ...(st.tsSource ? { ts_source: `app:${st.tsSource}` } : {}),
        ...(st.detectErrors ? { detect_errors: st.detectErrors } : {}),
        link_dropped: cs.droppedFrames, kbps: Math.round(kbps),
        reduce: { ...this.reducer.stats },
      });
    }
  }
}
