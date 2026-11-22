package expo.modules.ballcamera

import androidx.lifecycle.LifecycleOwner
import expo.modules.kotlin.Promise
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import expo.modules.kotlin.records.Field
import expo.modules.kotlin.records.Record

class StartOptions : Record {
  @Field val width: Int = 1280
  @Field val height: Int = 720
  @Field val fps: Int = 30
  @Field val previewEverySec: Double = 1.0
  @Field val previewQuality: Double = 0.7
  @Field val batchMs: Double = 50.0
  @Field val detector: Map<String, Any?>? = null
}

class ExposureOptions : Record {
  @Field val mode: String = "auto"
  @Field val shutterS: Double? = null
  @Field val iso: Double? = null
}

class BallCameraModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("BallCamera")

    Events("onDetections", "onPreview", "onStats", "onError")

    OnCreate {
      CaptureEngine.emit = { name, body -> sendEvent(name, body) }
    }

    Function("now") {
      CaptureEngine.now()
    }

    AsyncFunction("getFormats") {
      val ctx = appContext.reactContext ?: throw IllegalStateException("no context")
      CaptureEngine.formats(ctx)
    }

    AsyncFunction("start") { options: StartOptions, promise: Promise ->
      val ctx = appContext.reactContext
      val owner = appContext.currentActivity as? LifecycleOwner
      if (ctx == null || owner == null) {
        promise.reject("E_NO_ACTIVITY", "No foreground activity to attach the camera to", null)
        return@AsyncFunction
      }
      val cfg = StartConfig(options.width, options.height, options.fps, options.previewEverySec,
        options.previewQuality, options.batchMs, options.detector)
      CaptureEngine.start(ctx, owner, cfg) { result ->
        result.fold(
          onSuccess = { promise.resolve(it) },
          onFailure = { promise.reject("E_CAMERA", it.message ?: it.toString(), it) },
        )
      }
    }

    AsyncFunction("stop") { promise: Promise ->
      val ctx = appContext.reactContext
      if (ctx == null) {
        promise.resolve(null)
        return@AsyncFunction
      }
      CaptureEngine.stop(ctx) { promise.resolve(null) }
    }

    Function("setDetectorConfig") { config: Map<String, Any?> ->
      CaptureEngine.setDetectorConfig(config)
    }

    AsyncFunction("setExposure") { options: ExposureOptions ->
      CaptureEngine.setExposure(options.mode, options.shutterS, options.iso)
    }

    // Say a call ("OUT") out loud (Android text-to-speech, media volume).
    Function("speak") { text: String ->
      val ctx = appContext.reactContext ?: return@Function
      CallVoice.say(ctx, text)
    }

    View(BallCameraView::class) {}
  }
}
