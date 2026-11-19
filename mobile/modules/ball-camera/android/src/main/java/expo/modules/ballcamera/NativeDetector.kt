package expo.modules.ballcamera

import java.nio.ByteBuffer

/** Kotlin side of the shared C++ detector (cpp/ballcore.cpp via ballcore_jni.cpp). */
class NativeDetector {
  companion object {
    init {
      System.loadLibrary("ballcore_jni")
    }
    const val FMT_RGBA = 1
  }

  private var handle: Long = nativeCreate()

  /** Detector settings as the server sends them (snake_case keys, EdgeDetectorConfig). */
  fun configure(cfg: Map<String, Any?>, fps: Int) {
    fun num(k: String, d: Double) = (cfg[k] as? Number)?.toDouble() ?: d
    fun triple(k: String, d: IntArray): IntArray {
      val v = cfg[k] as? List<*> ?: return d
      if (v.size != 3) return d
      return IntArray(3) { (v[it] as? Number)?.toInt() ?: d[it] }
    }
    val lo = triple("hsv_low", intArrayOf(25, 100, 90))
    val hi = triple("hsv_high", intArrayOf(55, 255, 255))
    val flicker = when (val f = cfg["flicker_compensation"]) {
      is Boolean -> if (f) 1 else 0
      is Number -> if (f.toInt() != 0) 1 else 0
      else -> 1
    }
    val ints = intArrayOf(num("bin", 2.0).toInt(), lo[0], lo[1], lo[2], hi[0], hi[1], hi[2],
      num("max_candidates", 12.0).toInt(), flicker)
    val dbls = doubleArrayOf(num("var_threshold", 24.0), num("var_init", 15.0), num("var_min", 4.0),
      num("var_max", 75.0), num("bg_history_s", 2.0), num("bg_update_hz", 60.0), fps.toDouble(),
      num("min_radius_px", 1.5), num("max_radius_px", 80.0), num("max_elongation", 6.0),
      num("flicker_alpha", 0.02))
    nativeConfigure(handle, ints, dbls)
  }

  /** @param out 4 floats per candidate (u, v, radius, score). Returns the candidate count. */
  fun detect(buf: ByteBuffer, width: Int, height: Int, rowStride: Int, format: Int, out: FloatArray): Int =
    nativeDetect(handle, buf, width, height, rowStride, format, out)

  fun lastMicros(): Double = nativeLastMicros(handle)

  fun reset() = nativeReset(handle)

  fun release() {
    if (handle != 0L) {
      nativeDestroy(handle)
      handle = 0L
    }
  }

  private external fun nativeCreate(): Long
  private external fun nativeDestroy(h: Long)
  private external fun nativeConfigure(h: Long, ints: IntArray, dbls: DoubleArray): Boolean
  private external fun nativeDetect(h: Long, buf: ByteBuffer, w: Int, hgt: Int, stride: Int, fmt: Int, out: FloatArray): Int
  private external fun nativeLastMicros(h: Long): Double
  private external fun nativeReset(h: Long)
}
