import { CameraView, useCameraPermissions } from 'expo-camera';
import { useState } from 'react';
import { Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { isSimulator } from '../../modules/ball-camera';
import { toEdgeUrl } from '../core/serverAddress.js';
import { AppSettings, FRAME_RATES, RESOLUTIONS } from '../settings';

type Props = { initial: AppSettings; notice?: string | null; onStart: (s: AppSettings) => void };

export default function ConnectScreen({ initial, notice, onStart }: Props) {
  const [s, setS] = useState<AppSettings>(initial);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [permission, requestPermission] = useCameraPermissions();
  // Keep content clear of the notch / Dynamic Island / Android cut-out and system bars.
  const ins = useSafeAreaInsets();
  const pad = { paddingTop: 24 + ins.top, paddingBottom: 24 + ins.bottom, paddingLeft: 24 + ins.left, paddingRight: 24 + ins.right };
  const url = toEdgeUrl(s.address);
  const androidHighFps = Platform.OS === 'android' && s.fps > 60;

  async function ensureCamera(): Promise<boolean> {
    if (permission?.granted) return true;
    const r = await requestPermission();
    if (!r.granted) setError('Camera permission is needed. Allow it in Settings.');
    return r.granted;
  }

  async function start() {
    setError(null);
    if (!url) return setError('Enter the server address shown by `bt serve` (or scan the dashboard QR code).');
    if (!s.name.trim()) return setError('Give this camera a name that says where it is mounted, e.g. baseline-A-left.');
    if (!(await ensureCamera())) return;
    onStart({ ...s, name: s.name.trim() });
  }

  if (scanning) {
    return (
      <View style={{ flex: 1, backgroundColor: '#000' }}>
        <CameraView
          style={{ flex: 1 }}
          facing="back"
          barcodeScannerSettings={{ barcodeTypes: ['qr'] }}
          onBarcodeScanned={({ data }) => {
            if (toEdgeUrl(data)) {
              setS((p) => ({ ...p, address: data }));
              setScanning(false);
            }
          }}
        />
        <Pressable style={[styles.button, styles.cancel, { bottom: 24 + ins.bottom }]} onPress={() => setScanning(false)}>
          <Text style={styles.buttonText}>Cancel</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={[styles.content, pad]}>
      <Text style={styles.title}>BallTracker camera</Text>
      {isSimulator && (
        <Text style={styles.warn}>Native camera module not built in: this run uses a simulated camera.</Text>
      )}

      <Text style={styles.label}>Server (Mac running `bt serve`)</Text>
      <View style={styles.row}>
        <TextInput
          style={[styles.input, { flex: 1 }]}
          value={s.address}
          onChangeText={(address) => setS({ ...s, address })}
          placeholder="192.168.0.247"
          placeholderTextColor="#666"
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
        />
        <Pressable
          style={[styles.button, styles.small]}
          onPress={async () => {
            if (await ensureCamera()) setScanning(true);
          }}
        >
          <Text style={styles.buttonText}>Scan QR</Text>
        </Pressable>
      </View>
      <Text style={styles.hint}>{url ? `→ ${url}` : 'Address or QR from the dashboard'}</Text>

      <Text style={styles.label}>Camera name (its mounting position)</Text>
      <TextInput
        style={styles.input}
        value={s.name}
        onChangeText={(name) => setS({ ...s, name })}
        placeholder="baseline-A-left"
        placeholderTextColor="#666"
        autoCapitalize="none"
        autoCorrect={false}
      />

      <Text style={styles.label}>Resolution</Text>
      <View style={styles.row}>
        {RESOLUTIONS.map(([w, h]) => (
          <Chip key={w} label={`${w}×${h}`} on={s.width === w && s.height === h} onPress={() => setS({ ...s, width: w, height: h })} />
        ))}
      </View>

      <Text style={styles.label}>Frame rate</Text>
      <View style={styles.row}>
        {FRAME_RATES.map((f) => (
          <Chip key={f} label={`${f} fps`} on={s.fps === f} onPress={() => setS({ ...s, fps: f })} />
        ))}
      </View>
      <Text style={styles.hint}>
        {androidHighFps
          ? 'Most Android phones can only process up to 60 fps; choose 30 or 60.'
          : 'iPhone: 120 or 240 fps gives the best accuracy. Use bright light.'}
      </Text>

      <Text style={styles.label}>Calls</Text>
      <View style={styles.row}>
        <Chip label="Say calls out loud" on={s.speakCalls !== false} onPress={() => setS({ ...s, speakCalls: true })} />
        <Chip label="Silent" on={s.speakCalls === false} onPress={() => setS({ ...s, speakCalls: false })} />
      </View>
      <Text style={styles.hint}>Every phone set to speak says “Out” when the server calls one. Turn the media volume up.</Text>

      {notice && <Text style={styles.notice}>{notice}</Text>}
      {error && <Text style={styles.error}>{error}</Text>}
      <Pressable style={[styles.button, styles.start]} onPress={start}>
        <Text style={styles.buttonText}>Start camera</Text>
      </Pressable>
      <Text style={styles.hint}>
        Mount the phone in landscape, then calibrate it once on the dashboard (Calibrate on this camera's card).
      </Text>
    </ScrollView>
  );
}

function Chip({ label, on, onPress }: { label: string; on: boolean; onPress: () => void }) {
  return (
    <Pressable onPress={onPress} style={[styles.chip, on && styles.chipOn]}>
      <Text style={[styles.chipText, on && { color: '#000' }]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#0b0b0b' },
  content: { padding: 24, gap: 8 },
  title: { color: '#fff', fontSize: 24, fontWeight: '700', marginBottom: 8 },
  label: { color: '#ddd', fontSize: 14, marginTop: 10 },
  hint: { color: '#888', fontSize: 12 },
  warn: { color: '#e0b000', fontSize: 13 },
  error: { color: '#ff6b6b', fontSize: 14, marginTop: 8 },
  notice: { color: '#7fd3ff', fontSize: 14, marginTop: 8 },
  row: { flexDirection: 'row', gap: 8, alignItems: 'center', flexWrap: 'wrap' },
  input: { backgroundColor: '#1c1c1c', color: '#fff', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 10, fontSize: 16 },
  button: { backgroundColor: '#2d6cdf', borderRadius: 8, paddingVertical: 12, paddingHorizontal: 18, alignItems: 'center' },
  small: { paddingVertical: 10 },
  start: { marginTop: 16, backgroundColor: '#1f9d55' },
  cancel: { position: 'absolute', bottom: 24, alignSelf: 'center' },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  chip: { borderWidth: 1, borderColor: '#555', borderRadius: 16, paddingVertical: 6, paddingHorizontal: 12 },
  chipOn: { backgroundColor: '#d4f542', borderColor: '#d4f542' },
  chipText: { color: '#ddd' },
});
