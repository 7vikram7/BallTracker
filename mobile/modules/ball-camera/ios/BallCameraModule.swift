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

    View(BallCameraView.self) {}
  }
}
