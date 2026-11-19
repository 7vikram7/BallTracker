import * as Device from 'expo-device';
import { useKeepAwake } from 'expo-keep-awake';
import * as ScreenOrientation from 'expo-screen-orientation';
import { useEffect, useRef, useState } from 'react';
import { Platform, Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import BallCamera, { BallCameraView } from '../../modules/ball-camera';
import { displayHost, toEdgeUrl } from '../core/serverAddress.js';
import { CameraSession, initialState } from '../core/session.js';
import { AppSettings } from '../settings';

type Props = { settings: AppSettings; onExit: () => void };
type SessionState = import("../core/session.js").SessionState;

const EXPOSURES = [
  { label: 'Auto exposure', opts: { mode: 'auto' as const } },
  { label: 'Shutter 1/1000', opts: { mode: 'shutter' as const, shutterS: 1 / 1000 } },
  { label: 'Shutter 1/2000', opts: { mode: 'shutter' as const, shutterS: 1 / 2000 } },
  { label: 'Locked', opts: { mode: 'locked' as const } },
];

export default function CameraScreen({ settings, onExit }: Props) {
  useKeepAwake();
  const [st, setSt] = useState<SessionState>(initialState());
  const [expIdx, setExpIdx] = useState(0);
  const [expInfo, setExpInfo] = useState<string | null>(null);
  const [flash, setFlash] = useState<string | null>(null);
  const session = useRef<CameraSession | null>(null);
  const url = toEdgeUrl(settings.address) ?? '';
  // In landscape the notch / Dynamic Island / Android cut-out sits on a side edge: keep text and buttons clear.
  const ins = useSafeAreaInsets();

  useEffect(() => {
    // One fixed landscape orientation: frames and calibration must not rotate mid-session.
    ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.LANDSCAPE_RIGHT).catch(() => {});
    const s = new CameraSession({
      native: BallCamera,
      settings: {
        url, name: settings.name, width: settings.width, height: settings.height, fps: settings.fps,
        device: `${Device.manufacturer ?? ''} ${Device.modelName ?? ''}`.trim(), platform: Platform.OS,
        appVersion: '0.1.0',
      },
      onState: setSt,
    });
    session.current = s;
    s.start();
    return () => {
      s.stop();
      ScreenOrientation.unlockAsync().catch(() => {});
    };
  }, []);

  // Flash the call ("OUT" / "FAULT") for 1.5 s.
  useEffect(() => {
    if (!st.lastCall?.text) return;
    setFlash(st.lastCall.text);
    const t = setTimeout(() => setFlash(null), 1500);
    return () => clearTimeout(t);
  }, [st.lastCall?.at]);

  async function cycleExposure() {
    const next = (expIdx + 1) % EXPOSURES.length;
    try {
      const r: any = await session.current?.setExposure(EXPOSURES[next].opts);
      setExpIdx(next);
      setExpInfo(r?.shutterS ? `1/${Math.round(1 / r.shutterS)} s, ISO ${Math.round(r.iso ?? 0)}${r.isoLimited ? ' (too dark: max ISO)' : ''}` : null);
    } catch (e: any) {
      setExpInfo(String(e?.message ?? e));
    }
  }

  const n = st.native;
  const warnings: string[] = [];
  if (st.phase === 'error' && st.error) warnings.push(st.error);
  if (st.connection !== 'connected' && st.phase === 'running') warnings.push(`Not connected to ${displayHost(url)}: retrying…`);
  if (st.connection === 'connected' && !st.calibrated) warnings.push('Not calibrated: click Calibrate on this camera in the dashboard.');
  if (n.fpsCapture > 0 && n.fpsProcessed < 0.9 * n.fpsCapture) warnings.push('Phone can’t keep up: lower the frame rate.');
  if (n.thermal === 'serious' || n.thermal === 'critical') warnings.push('Phone is hot: shade it or lower the frame rate.');
  if (st.link.droppedFrames > 0 && st.connection === 'connected') warnings.push(`${st.link.droppedFrames} frames not sent (Wi-Fi).`);

  return (
    <View style={styles.screen}>
      <BallCameraView style={StyleSheet.absoluteFill} />

      <View style={[styles.hud, { top: 12 + ins.top, left: 16 + ins.left, right: 16 + ins.right }]} pointerEvents="none">
        <Text style={styles.hudTitle}>
          {settings.name} · {st.camera ? `${st.camera.width}×${st.camera.height} @ ${st.camera.fps}` : 'starting…'}
        </Text>
        <Text style={[styles.hudLine, { color: st.connection === 'connected' ? '#7CFC00' : '#ffb000' }]}>
          {st.connection} · {displayHost(url)}
          {st.server?.rtt_ms != null ? ` · rtt ${st.server.rtt_ms.toFixed(0)} ms` : ''}
          {st.calibrated ? ' · calibrated' : ''}
        </Text>
        <Text style={styles.hudLine}>
          camera {n.fpsCapture.toFixed(0)} fps · processed {n.fpsProcessed.toFixed(0)} fps · detect {n.detectMs.toFixed(1)} ms
        </Text>
        <Text style={styles.hudLine}>
          ball candidates {st.candidatesPerSec.toFixed(0)}/s · uplink {st.link.kbps.toFixed(0)} kbit/s · {n.thermal}
          {n.battery != null && n.battery >= 0 ? ` · battery ${(n.battery * 100).toFixed(0)}%` : ''}
        </Text>
        {warnings.map((w) => (
          <Text key={w} style={styles.warn}>{w}</Text>
        ))}
      </View>

      {flash && (
        <View style={styles.flash} pointerEvents="none">
          <Text style={styles.flashText}>{flash}</Text>
        </View>
      )}

      <View style={[styles.bar, { bottom: 16 + ins.bottom, right: 16 + ins.right }]}>
        <Pressable style={styles.btn} onPress={cycleExposure}>
          <Text style={styles.btnText}>{EXPOSURES[expIdx].label}</Text>
          {expInfo && <Text style={styles.btnSub}>{expInfo}</Text>}
        </Pressable>
        <Pressable
          style={[styles.btn, { backgroundColor: '#8b1e1e' }]}
          onPress={async () => {
            await session.current?.stop();
            onExit();
          }}
        >
          <Text style={styles.btnText}>Stop</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000' },
  hud: { position: 'absolute', top: 12, left: 16, right: 16, gap: 2 },
  hudTitle: { color: '#fff', fontSize: 16, fontWeight: '700', textShadowColor: '#000', textShadowRadius: 3 },
  hudLine: { color: '#eee', fontSize: 13, textShadowColor: '#000', textShadowRadius: 3 },
  warn: { color: '#ffd166', fontSize: 13, fontWeight: '600', textShadowColor: '#000', textShadowRadius: 3 },
  flash: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(200,0,0,0.35)' },
  flashText: { color: '#fff', fontSize: 96, fontWeight: '900' },
  bar: { position: 'absolute', bottom: 16, right: 16, flexDirection: 'row', gap: 12 },
  btn: { backgroundColor: 'rgba(30,30,30,0.85)', borderRadius: 10, paddingVertical: 10, paddingHorizontal: 16, alignItems: 'center' },
  btnText: { color: '#fff', fontSize: 15, fontWeight: '600' },
  btnSub: { color: '#bbb', fontSize: 11, marginTop: 2 },
});
