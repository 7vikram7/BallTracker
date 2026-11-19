package expo.modules.ballcamera

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Bitmap
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CaptureRequest
import android.os.BatteryManager
import android.os.Build
import android.os.PowerManager
import android.os.SystemClock
import android.util.Base64
import android.util.Range
import android.util.Size
import androidx.camera.camera2.interop.Camera2CameraControl
import androidx.camera.camera2.interop.Camera2CameraInfo
import androidx.camera.camera2.interop.Camera2Interop
import androidx.camera.camera2.interop.CaptureRequestOptions
import androidx.camera.camera2.interop.ExperimentalCamera2Interop
import androidx.camera.core.Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.core.resolutionselector.ResolutionSelector
import androidx.camera.core.resolutionselector.ResolutionStrategy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

data class StartConfig(
  val width: Int = 1280,
  val height: Int = 720,
  val fps: Int = 30,
  val previewEverySec: Double = 1.0,
  val previewQuality: Double = 0.7,
  val batchMs: Double = 50.0,
  val detector: Map<String, Any?>? = null,
)

/**
 * Camera capture + on-phone ball detection for Android (CameraX ImageAnalysis,
 * RGBA frames straight into the C++ detector on a background thread).
 *
 * Android phones generally can't deliver 120/240 fps frames to app code (the
 * high-speed modes only feed the screen and the video encoder), so Android
 * cameras run at 30-60 fps as helper cameras.
 */
@SuppressLint("UnsafeOptInUsageError")
@androidx.annotation.OptIn(ExperimentalCamera2Interop::class)
object CaptureEngine {
  var emit: ((String, Map<String, Any?>) -> Unit)? = null

  private val analysisExecutor = Executors.newSingleThreadExecutor()
  private val jpegExecutor = Executors.newSingleThreadExecutor()
  private var detector: NativeDetector? = null
  private var provider: ProcessCameraProvider? = null
  private var camera: Camera? = null
  private var preview: Preview? = null
  private var previewView: PreviewView? = null
  private var appContext: Context? = null

  @Volatile private var realtimeTimestamps = true
  @Volatile private var cfg = StartConfig()
  @Volatile private var pendingDetector: Map<String, Any?>? = null

  // Touched only on analysisExecutor.
  private var seq = 0
  private val batch = ArrayList<Map<String, Any?>>()
  private var batchStart = 0.0
  private var lastPreview = -1e9
  private val previewBusy = AtomicBoolean(false)
  private var statsStart = 0.0
  private var nProcessed = 0
  private var detectUs = 0.0
  private var lastSeqTs = 0L
  private var frameW = 0
  private var frameH = 0
  private val cands = FloatArray(64 * 4)
  private var rowBuf: ByteBuffer? = null

  /** Same clock as the frame timestamps (sensor time base). */
  fun now(): Double =
    if (realtimeTimestamps) SystemClock.elapsedRealtimeNanos() / 1e9 else System.nanoTime() / 1e9

  fun attachPreview(view: PreviewView) {
    previewView = view
    preview?.setSurfaceProvider(view.surfaceProvider)
  }

  fun detachPreview(view: PreviewView) {
    if (previewView === view) {
      previewView = null
      preview?.setSurfaceProvider(null)
    }
  }

  fun formats(context: Context): List<Map<String, Any?>> {
    val mgr = context.getSystemService(Context.CAMERA_SERVICE) as android.hardware.camera2.CameraManager
    val out = ArrayList<Map<String, Any?>>()
    for (id in mgr.cameraIdList) {
      val ch = mgr.getCameraCharacteristics(id)
      if (ch.get(CameraCharacteristics.LENS_FACING) != CameraCharacteristics.LENS_FACING_BACK) continue
      val map = ch.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP) ?: continue
      val maxFps = ch.get(CameraCharacteristics.CONTROL_AE_AVAILABLE_TARGET_FPS_RANGES)?.maxOfOrNull { it.upper } ?: 30
      for (s in map.getOutputSizes(android.graphics.ImageFormat.YUV_420_888) ?: emptyArray()) {
        out.add(mapOf("width" to s.width, "height" to s.height, "maxFps" to maxFps, "binned" to false))
      }
      break
    }
    return out
  }

  fun start(context: Context, owner: LifecycleOwner, c: StartConfig, done: (Result<Map<String, Any?>>) -> Unit) {
    appContext = context.applicationContext
    val future = ProcessCameraProvider.getInstance(context)
    future.addListener({
      try {
        val p = future.get()
        provider = p
        cfg = c
        analysisExecutor.execute {
          resetCounters()
          val d = detector ?: NativeDetector().also { detector = it }
          d.configure(c.detector ?: emptyMap(), c.fps)
        }
        val size = Size(c.width, c.height)
        val resolution = ResolutionSelector.Builder()
          .setResolutionStrategy(ResolutionStrategy(size, ResolutionStrategy.FALLBACK_RULE_CLOSEST_HIGHER_THEN_LOWER))
          .build()
        val ab = ImageAnalysis.Builder()
          .setResolutionSelector(resolution)
          .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
          .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
        Camera2Interop.Extender(ab)
          .setCaptureRequestOption(CaptureRequest.CONTROL_AE_TARGET_FPS_RANGE, Range(c.fps, c.fps))
          .setCaptureRequestOption(CaptureRequest.CONTROL_VIDEO_STABILIZATION_MODE,
            CaptureRequest.CONTROL_VIDEO_STABILIZATION_MODE_OFF)
        val analysis = ab.build()
        analysis.setAnalyzer(analysisExecutor) { image -> analyze(image) }
        val pv = Preview.Builder().setResolutionSelector(resolution).build()
        previewView?.let { pv.setSurfaceProvider(it.surfaceProvider) }
        preview = pv
        p.unbindAll()
        val cam = p.bindToLifecycle(owner, CameraSelector.DEFAULT_BACK_CAMERA, pv, analysis)
        camera = cam
        val src = Camera2CameraInfo.from(cam.cameraInfo)
          .getCameraCharacteristic(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE)
        realtimeTimestamps = src == CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME
        val res = analysis.resolutionInfo?.resolution ?: size
        done(Result.success(mapOf("width" to res.width, "height" to res.height, "fps" to c.fps,
          "format" to "${res.width}x${res.height} RGBA (CameraX)",
          "timestampSource" to if (realtimeTimestamps) "realtime" else "uptime")))
      } catch (e: Exception) {
        done(Result.failure(e))
      }
    }, ContextCompat.getMainExecutor(context))
  }

  fun stop(context: Context, done: () -> Unit) {
    ContextCompat.getMainExecutor(context).execute {
      provider?.unbindAll()
      camera = null
      preview = null
      analysisExecutor.execute {
        flushBatch()
        done()
      }
    }
  }

  fun setDetectorConfig(d: Map<String, Any?>) {
    pendingDetector = d
  }

  /** "auto" | "locked" | "shutter" (fixed exposure time, ISO given or 800). */
  fun setExposure(mode: String, shutterS: Double?, iso: Double?): Map<String, Any?> {
    val cam = camera ?: throw IllegalStateException("camera not started")
    val c2 = Camera2CameraControl.from(cam.cameraControl)
    val b = CaptureRequestOptions.Builder()
    when (mode) {
      "locked" -> {
        b.setCaptureRequestOption(CaptureRequest.CONTROL_AE_LOCK, true)
        b.setCaptureRequestOption(CaptureRequest.CONTROL_AWB_LOCK, true)
      }
      "shutter" -> {
        val ns = ((shutterS ?: 0.001) * 1e9).toLong()
        b.setCaptureRequestOption(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_OFF)
        b.setCaptureRequestOption(CaptureRequest.SENSOR_EXPOSURE_TIME, ns)
        b.setCaptureRequestOption(CaptureRequest.SENSOR_SENSITIVITY, (iso ?: 800.0).toInt())
        b.setCaptureRequestOption(CaptureRequest.SENSOR_FRAME_DURATION, (1e9 / cfg.fps).toLong())
        b.setCaptureRequestOption(CaptureRequest.CONTROL_AWB_LOCK, true)
      }
      else -> {}
    }
    c2.setCaptureRequestOptions(b.build())
    return mapOf("mode" to mode, "shutterS" to shutterS, "iso" to iso)
  }

  // ---- frames (analysisExecutor) ----

  private fun resetCounters() {
    seq = 0
    batch.clear()
    batchStart = 0.0
    lastPreview = -1e9
    statsStart = 0.0
    nProcessed = 0
    detectUs = 0.0
    lastSeqTs = 0L
  }

  private fun analyze(image: ImageProxy) {
    try {
      val d = detector ?: return
      pendingDetector?.let {
        d.configure(it, cfg.fps)
        pendingDetector = null
      }
      val t = image.imageInfo.timestamp / 1e9
      if (statsStart == 0.0) {
        statsStart = t
        batchStart = t
      }
      val plane = image.planes[0]
      val buf = plane.buffer
      val w = image.width
      val h = image.height
      val n = d.detect(buf, w, h, plane.rowStride, NativeDetector.FMT_RGBA, cands).coerceAtLeast(0)
      nProcessed++
      detectUs += d.lastMicros()
      frameW = w
      frameH = h
      val c = DoubleArray(n * 4) { cands[it].toDouble() }.toList()
      batch.add(mapOf("seq" to seq, "t" to t, "c" to c))
      seq++
      if ((t - batchStart) * 1000 >= cfg.batchMs) {
        flushBatch()
        batchStart = t
      }
      if (t - lastPreview >= cfg.previewEverySec && previewBusy.compareAndSet(false, true)) {
        lastPreview = t
        val bmp = toBitmap(buf, w, h, plane.rowStride)
        val s = seq - 1
        val q = (cfg.previewQuality * 100).toInt().coerceIn(10, 100)
        jpegExecutor.execute {
          try {
            val os = ByteArrayOutputStream()
            bmp.compress(Bitmap.CompressFormat.JPEG, q, os)
            emit?.invoke("onPreview", mapOf("seq" to s, "t" to t, "width" to w, "height" to h,
              "jpegBase64" to Base64.encodeToString(os.toByteArray(), Base64.NO_WRAP)))
          } finally {
            bmp.recycle()
            previewBusy.set(false)
          }
        }
      }
      if (t - statsStart >= 1.0) emitStats(t)
    } catch (e: Exception) {
      emit?.invoke("onError", mapOf("message" to (e.message ?: e.toString())))
    } finally {
      image.close()
    }
  }

  private fun toBitmap(buf: ByteBuffer, w: Int, h: Int, rowStride: Int): Bitmap {
    val bmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)  // memory layout is RGBA bytes
    buf.rewind()
    if (rowStride == w * 4) {
      bmp.copyPixelsFromBuffer(buf)
    } else {
      val packed = rowBuf?.takeIf { it.capacity() >= w * h * 4 } ?: ByteBuffer.allocateDirect(w * h * 4).also { rowBuf = it }
      packed.clear()
      val row = ByteArray(w * 4)
      for (y in 0 until h) {
        buf.position(y * rowStride)
        buf.get(row, 0, w * 4)
        packed.put(row)
      }
      packed.flip()
      bmp.copyPixelsFromBuffer(packed)
    }
    buf.rewind()
    return bmp
  }

  private fun flushBatch() {
    if (batch.isEmpty()) return
    emit?.invoke("onDetections", mapOf("width" to frameW, "height" to frameH, "frames" to ArrayList(batch)))
    batch.clear()
  }

  private fun emitStats(t: Double) {
    val dt = maxOf(t - statsStart, 1e-3)
    val ctx = appContext
    var thermal = "unknown"
    var battery = -1.0
    if (ctx != null) {
      if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        val pm = ctx.getSystemService(Context.POWER_SERVICE) as PowerManager
        thermal = when (pm.currentThermalStatus) {
          PowerManager.THERMAL_STATUS_NONE -> "nominal"
          PowerManager.THERMAL_STATUS_LIGHT, PowerManager.THERMAL_STATUS_MODERATE -> "fair"
          PowerManager.THERMAL_STATUS_SEVERE -> "serious"
          else -> "critical"
        }
      }
      val st = ctx.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
      val level = st?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
      val scale = st?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
      if (level >= 0 && scale > 0) battery = level.toDouble() / scale
    }
    emit?.invoke("onStats", mapOf("fpsCapture" to nProcessed / dt, "fpsProcessed" to nProcessed / dt,
      "detectMs" to if (nProcessed > 0) detectUs / nProcessed / 1000 else 0.0,
      "dropped" to 0, "thermal" to thermal, "battery" to battery))
    statsStart = t
    nProcessed = 0
    detectUs = 0.0
  }
}
