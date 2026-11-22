import AVFoundation
import ExpoModulesCore

struct StartOptions: Record {
  @Field var width: Int = 1920
  @Field var height: Int = 1080
  @Field var fps: Int = 60
  @Field var previewEverySec: Double = 1.0
  @Field var previewQuality: Double = 0.7
  @Field var batchMs: Double = 50
  @Field var detector: [String: Any]? = nil
}

struct ExposureOptions: Record {
  @Field var mode: String = "auto"  // "auto" | "locked" | "shutter"
  @Field var shutterS: Double? = nil
  @Field var iso: Double? = nil
}

public class BallCameraModule: Module {
  private let engine = CaptureEngine.shared
  private let voice = CallVoice()

  public func definition() -> ModuleDefinition {
    Name("BallCamera")

    Events("onDetections", "onPreview", "onStats", "onError")

    OnCreate {
      self.engine.emit = { [weak self] name, body in
        self?.sendEvent(name, body)
      }
    }

    // Same clock as the frame timestamps (host clock), for the server's clock sync.
    Function("now") { () -> Double in
      CaptureEngine.hostNow()
    }

    AsyncFunction("getFormats") { () -> [[String: Any]] in
      self.engine.formats()
    }

    AsyncFunction("start") { (options: StartOptions, promise: Promise) in
      var c = StartConfig()
      c.width = options.width
      c.height = options.height
      c.fps = options.fps
      c.previewEverySec = options.previewEverySec
      c.previewQuality = options.previewQuality
      c.batchMs = options.batchMs
      c.detector = options.detector
      self.engine.start(c) { result in
        switch result {
        case .success(let info): promise.resolve(info)
        case .failure(let err): promise.reject("E_CAMERA", err.localizedDescription)
        }
      }
    }

    AsyncFunction("stop") { (promise: Promise) in
      self.engine.stop { promise.resolve(nil) }
    }

    Function("setDetectorConfig") { (config: [String: Any]) in
      self.engine.setDetectorConfig(config)
    }

    AsyncFunction("setExposure") { (options: ExposureOptions) -> [String: Any] in
      try self.engine.setExposure(mode: options.mode, shutterS: options.shutterS, iso: options.iso)
    }

    // Say a call ("OUT") out loud. Plays with the ring/silent switch on; other audio is ducked.
    Function("speak") { (text: String) in
      self.voice.say(text)
    }

    View(BallCameraView.self) {}
  }
}

/// Text-to-speech for the server's calls. One synthesizer, kept alive (a released one stops mid-word);
/// a new call cuts off the previous one.
/// Speaks the server's calls. The audio session is activated for every call, not once: a phone
/// call or Siri deactivates it, and calls would otherwise stay silent afterwards (review of
/// a9fbde6, P2-3). When speech ends it is deactivated again, so other audio stops being ducked.
/// Not yet checked on a device after an interruption.
/// @unchecked Sendable: every use of the synthesizer and the audio session is on the main queue.
final class CallVoice: NSObject, AVSpeechSynthesizerDelegate, @unchecked Sendable {
  private let synth = AVSpeechSynthesizer()
  private var categorySet = false

  override init() {
    super.init()
    synth.delegate = self
  }

  func say(_ text: String) {
    DispatchQueue.main.async {
      let session = AVAudioSession.sharedInstance()
      if !self.categorySet {
        // .playback: audible with the silent switch on; mixWithOthers + duckOthers: music dips, keeps playing.
        try? session.setCategory(.playback, mode: .voicePrompt, options: [.mixWithOthers, .duckOthers])
        self.categorySet = true
      }
      try? session.setActive(true)
      if self.synth.isSpeaking { self.synth.stopSpeaking(at: .immediate) }
      let u = AVSpeechUtterance(string: text.capitalized)
      u.rate = 0.5
      u.volume = 1.0
      u.voice = AVSpeechSynthesisVoice(language: "en-US")
      self.synth.speak(u)
    }
  }

  func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
    if !synthesizer.isSpeaking {
      try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }
  }
}
