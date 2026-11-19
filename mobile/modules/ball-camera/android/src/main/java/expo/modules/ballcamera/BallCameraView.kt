package expo.modules.ballcamera

import android.content.Context
import android.view.ViewGroup
import androidx.camera.view.PreviewView
import expo.modules.kotlin.AppContext
import expo.modules.kotlin.views.ExpoView

/** Live camera preview; the camera itself is owned by CaptureEngine. */
class BallCameraView(context: Context, appContext: AppContext) : ExpoView(context, appContext) {
  override val shouldUseAndroidLayout = true

  private val previewView = PreviewView(context).apply {
    scaleType = PreviewView.ScaleType.FIT_CENTER
    implementationMode = PreviewView.ImplementationMode.COMPATIBLE
  }

  init {
    addView(previewView, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
  }

  override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    CaptureEngine.attachPreview(previewView)
  }

  override fun onDetachedFromWindow() {
    CaptureEngine.detachPreview(previewView)
    super.onDetachedFromWindow()
  }
}
