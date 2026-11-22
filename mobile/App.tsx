import { StatusBar } from 'expo-status-bar';
import { useEffect, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import CameraScreen from './src/screens/CameraScreen';
import ConnectScreen from './src/screens/ConnectScreen';
import { AppSettings, loadSettings, saveSettings } from './src/settings';

export default function App() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    loadSettings().then(setSettings);
  }, []);

  if (!settings) {
    return (
      <View style={{ flex: 1, backgroundColor: '#000', justifyContent: 'center' }}>
        <ActivityIndicator />
      </View>
    );
  }
  return (
    <SafeAreaProvider>
      <StatusBar hidden />
      {streaming ? (
        <CameraScreen
          settings={settings}
          onExit={(n) => {
            setNotice(n ?? null);
            setStreaming(false);
          }}
        />
      ) : (
        <ConnectScreen
          initial={settings}
          notice={notice}
          onStart={(s) => {
            setNotice(null);
            setSettings(s);
            saveSettings(s);
            setStreaming(true);
          }}
        />
      )}
    </SafeAreaProvider>
  );
}
