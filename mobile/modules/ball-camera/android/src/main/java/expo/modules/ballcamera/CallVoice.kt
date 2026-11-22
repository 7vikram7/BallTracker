package expo.modules.ballcamera

import android.content.Context
import android.media.AudioAttributes
import android.os.Handler
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.util.Log
import java.util.Locale

/**
 * Text-to-speech for the server's calls. The engine starts on the first call (takes ~0.5 s), so that
 * call is queued and spoken once it is ready; later calls cut off the previous one.
 *
 * Everything runs on the main thread: Expo calls [say] from the JS thread, and TextToSpeech is
 * created and used on the main looper (review of a9fbde6, P2-2). A failed start shuts the engine
 * down and the next call tries again; a missing US-English voice is logged, not silent.
 * Not yet checked on a device.
 */
object CallVoice {
  private const val TAG = "BallTrackerVoice"
  private val main = Handler(Looper.getMainLooper())
  private var tts: TextToSpeech? = null
  private var ready = false
  private var pending: String? = null

  fun say(ctx: Context, text: String) {
    val phrase = text.lowercase(Locale.US).replaceFirstChar { it.titlecase(Locale.US) }
    val app = ctx.applicationContext
    main.post { sayOnMain(app, phrase) }
  }

  private fun sayOnMain(app: Context, phrase: String) {
    val engine = tts
    if (engine == null) {
      pending = phrase
      tts = TextToSpeech(app) { status -> main.post { onInit(status) } }
      return
    }
    if (!ready) {
      pending = phrase
      return
    }
    engine.speak(phrase, TextToSpeech.QUEUE_FLUSH, null, "call")
  }

  private fun onInit(status: Int) {
    val engine = tts ?: return
    if (status != TextToSpeech.SUCCESS) {
      Log.w(TAG, "text-to-speech failed to start (status $status); will retry on the next call")
      engine.shutdown()
      tts = null
      return
    }
    val lang = engine.setLanguage(Locale.US)
    if (lang == TextToSpeech.LANG_MISSING_DATA || lang == TextToSpeech.LANG_NOT_SUPPORTED) {
      Log.w(TAG, "no US-English voice on this phone (result $lang); using the engine's default voice")
    }
    engine.setAudioAttributes(
      AudioAttributes.Builder()
        .setUsage(AudioAttributes.USAGE_ASSISTANCE_NAVIGATION_GUIDANCE)
        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
        .build()
    )
    ready = true
    pending?.let { engine.speak(it, TextToSpeech.QUEUE_FLUSH, null, "call") }
    pending = null
  }
}
