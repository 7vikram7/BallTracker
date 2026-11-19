import { requireNativeView } from 'expo';
import * as React from 'react';
import { Text, View, ViewProps } from 'react-native';

import { isSimulator } from './BallCameraModule';

const NativeView: React.ComponentType<ViewProps> | null = isSimulator ? null : requireNativeView('BallCamera');

/** Live camera preview. Shows a placeholder when running without the native module. */
export default function BallCameraView(props: ViewProps) {
  if (!NativeView) {
    return (
      <View {...props} style={[{ backgroundColor: '#111', alignItems: 'center', justifyContent: 'center' }, props.style]}>
        <Text style={{ color: '#888' }}>Simulated camera (native module not built in)</Text>
      </View>
    );
  }
  return <NativeView {...props} />;
}
