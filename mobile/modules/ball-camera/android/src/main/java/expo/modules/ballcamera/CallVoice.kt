package expo.modules.ballcamera

import android.content.Context
import android.media.AudioAttributes
import android.speech.tts.TextToSpeech
import java.util.Locale

/**
 * Text-to-speech for the server's calls. The engine starts on the first call (takes ~0.5 s), so that
 * call is queued and spoken once it is ready; later calls cut off the previous one.
 */
object CallVoice {
  private var tts: TextToSpeech? = null
  private var ready = false
  private var pending: String? = null

  @Synchronized
  fun say(ctx: Context, text: String) {
    val phrase = text.lowercase(Locale.US).replaceFirstChar { it.titlecase(Locale.US) }
    val engine = tts
    if (engine == null) {
      pending = phrase
      tts = TextToSpeech(ctx.applicationContext) { status -> onInit(status) }
      return
    }
    if (!ready) {
      pending = phrase
      return
    }
    engine.speak(phrase, TextToSpeech.QUEUE_FLUSH, null, "call")
  }

  @Synchronized
  private fun onInit(status: Int) {
    val engine = tts ?: return
    if (status != TextToSpeech.SUCCESS) {
      tts = null  // try again on the next call
      return
    }
    engine.language = Locale.US
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
