/** Detector settings, as the server sends them (EdgeDetectorConfig in balltracker/edge_detection.py). */
export type DetectorConfig = {
  bin?: number;
  hsv_low?: [number, number, number];
  hsv_high?: [number, number, number];
  var_threshold?: number;
  var_init?: number;
  var_min?: number;
  var_max?: number;
  bg_history_s?: number;
  bg_update_hz?: number;
  fps?: number;
  min_radius_px?: number;
  max_radius_px?: number;
  max_elongation?: number;
  max_candidates?: number;
  flicker_compensation?: boolean;
  flicker_alpha?: number;
};

export type StartOptions = {
  width: number;
  height: number;
  fps: number;
  previewEverySec?: number;
  previewQuality?: number;
  batchMs?: number;
  detector?: DetectorConfig;
};

export type StartResult = {
  width: number;
  height: number;
  fps: number;
  format?: string;
  minShutterS?: number;
  minIso?: number;
  maxIso?: number;
  timestampSource?: string;
};

export type CameraFormat = { width: number; height: number; maxFps: number; binned: boolean };

export type ExposureOptions = { mode: 'auto' | 'locked' | 'shutter'; shutterS?: number; iso?: number };
export type ExposureState = { mode: string; shutterS?: number | null; iso?: number | null; isoLimited?: boolean };

/** One processed frame: capture time (phone clock, s) and candidates flattened [u, v, r, score, ...]. */
export type DetFrame = { seq: number; t: number; c: number[] };
export type DetectionsEvent = { width: number; height: number; frames: DetFrame[] };
export type PreviewEvent = { seq: number; t: number; width: number; height: number; jpegBase64: string };
export type StatsEvent = {
  fpsCapture: number;
  fpsProcessed: number;
  detectMs: number;
  dropped: number;
  thermal: 'nominal' | 'fair' | 'serious' | 'critical' | 'unknown';
  battery?: number;
};

export type BallCameraEvents = {
  onDetections: (e: DetectionsEvent) => void;
  onPreview: (e: PreviewEvent) => void;
  onStats: (e: StatsEvent) => void;
  onError: (e: { message: string }) => void;
};
