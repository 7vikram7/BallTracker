import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

export type AppSettings = {
  address: string; // as typed or scanned; converted with toEdgeUrl()
  name: string; // camera name = its mounting position, e.g. "baseline-A-left"
  width: number;
  height: number;
  fps: number;
};

// Android: most phones can't hand more than 30-60 fps to app code; iPhone: 120 is a safe start.
export const DEFAULTS: AppSettings = Platform.OS === 'android'
  ? { address: '', name: '', width: 1280, height: 720, fps: 30 }
  : { address: '', name: '', width: 1920, height: 1080, fps: 120 };

export const RESOLUTIONS: [number, number][] = [
  [1280, 720],
  [1920, 1080],
];
export const FRAME_RATES = [30, 60, 120, 240];

const KEY = 'balltracker.settings.v1';

export async function loadSettings(): Promise<AppSettings> {
  try {
    const raw = await AsyncStorage.getItem(KEY);
    return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : DEFAULTS;
  } catch {
    return DEFAULTS;
  }
}

export async function saveSettings(s: AppSettings): Promise<void> {
  try {
    await AsyncStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    // not fatal: settings just won't be remembered
  }
}
