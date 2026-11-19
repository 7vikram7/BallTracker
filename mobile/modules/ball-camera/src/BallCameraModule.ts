import { NativeModule, requireOptionalNativeModule } from 'expo';

import { SimCamera } from '../../../src/core/simCamera';
import type {
  BallCameraEvents,
  CameraFormat,
  DetectorConfig,
  ExposureOptions,
  ExposureState,
  StartOptions,
  StartResult,
} from './BallCamera.types';

declare class BallCameraNative extends NativeModule<BallCameraEvents> {
  /** Seconds on the same clock as frame timestamps. */
  now(): number;
  getFormats(): Promise<CameraFormat[]>;
  start(options: StartOptions): Promise<StartResult>;
  stop(): Promise<void>;
  setDetectorConfig(config: DetectorConfig): void;
  setExposure(options: ExposureOptions): Promise<ExposureState>;
}

export type BallCameraApi = Pick<BallCameraNative, 'now' | 'getFormats' | 'start' | 'stop' | 'setDetectorConfig' | 'setExposure'> & {
  addListener<E extends keyof BallCameraEvents>(event: E, fn: BallCameraEvents[E]): { remove(): void };
  isSimulator?: boolean;
};

const native = requireOptionalNativeModule<BallCameraNative>('BallCamera');

/**
 * The native camera module, or a simulated camera when the native code isn't
 * built in (Expo Go): the simulator lets you test connecting to the server.
 */
const BallCamera: BallCameraApi = (native as unknown as BallCameraApi) ?? (new SimCamera() as unknown as BallCameraApi);

export const isSimulator = native == null;
export default BallCamera;
