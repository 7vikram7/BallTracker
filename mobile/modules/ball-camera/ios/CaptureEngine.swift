// Camera capture + on-phone ball detection for iOS.
//
// Frames go straight from AVFoundation to the C++ detector on a dedicated
// queue; JavaScript only receives small batches of results (every ~50 ms), a
// preview JPEG about once a second, and stats once a second.
//
// Settings that matter for line calling:
//   * fixed frame rate (activeVideoMin/MaxFrameDuration), up to 240 fps
//   * video stabilisation OFF (it warps each frame, which breaks the calibration)
//   * HDR off, main (1x) lens only
//   * optional fixed short shutter with ISO compensation (setExposure)
//   * frame timestamps converted to the host clock, which is also what now() returns

import AVFoundation
import CoreImage
import ImageIO
import UIKit

enum CaptureError: LocalizedError {
  case noCamera, permissionDenied, noFormat(String), configuration(String)
  var errorDescription: String? {
    switch self {
    case .noCamera: return "No back camera found"
    case .permissionDenied: return "Camera permission denied"
    case .noFormat(let s): return "Camera format not available: \(s)"
    case .configuration(let s): return "Camera configuration failed: \(s)"
    }
  }
}

struct StartConfig {
  var width = 1920
  var height = 1080
  var fps = 60
  var previewEverySec = 1.0
  var previewQuality = 0.7
  var batchMs = 50.0
  var detector: [String: Any]? = nil
}

final class CaptureEngine: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
  static let shared = CaptureEngine()

  let session = AVCaptureSession()
  private let sessionQueue = DispatchQueue(label: "balltracker.session")
  private let videoQueue = DispatchQueue(label: "balltracker.video", qos: .userInteractive)
  private let jpegQueue = DispatchQueue(label: "balltracker.jpeg", qos: .utility)
  private let output = AVCaptureVideoDataOutput()
  private var device: AVCaptureDevice?
  private let detector = BCDetector(config: nil)
  private lazy var ciContext = CIContext(options: [.cacheIntermediates: false])

  /// Event sink, set by the module: (event name, payload).
  var emit: ((String, [String: Any]) -> Void)?

  // Everything below is touched only on videoQueue.
  private var seq: UInt32 = 0
  private var batch: [[String: Any]] = []
  private var batchStart = 0.0
  private var cfg = StartConfig()
  private var lastPreview = -1e9
  private var previewBusy = false
  private var statsStart = 0.0
  private var nCaptured = 0
  private var nProcessed = 0
  private var nDropped = 0
  private var detectUs = 0.0
  private var frameW = 0
  private var frameH = 0
  private var cands = [Float](repeating: 0, count: 64 * 4)
  private var running = false
  private var battery = -1.0  // read on the main thread (UIKit), used on videoQueue

  /// Host clock in seconds: the clock frame timestamps are converted to.
  static func hostNow() -> Double {
    CMClockGetTime(CMClockGetHostTimeClock()).seconds
  }

  // MARK: formats

  func formats() -> [[String: Any]] {
    guard let dev = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back) else { return [] }
    var seen = Set<String>()
    var out: [[String: Any]] = []
    for f in dev.formats {
      let d = CMVideoFormatDescriptionGetDimensions(f.formatDescription)
      let maxFps = f.videoSupportedFrameRateRanges.map { $0.maxFrameRate }.max() ?? 0
      let key = "\(d.width)x\(d.height)@\(Int(maxFps))"
      if seen.insert(key).inserted {
        out.append(["width": Int(d.width), "height": Int(d.height), "maxFps": maxFps,
                    "binned": f.isVideoBinned])
      }
    }
    return out
  }

  private func pickFormat(_ dev: AVCaptureDevice, width: Int, height: Int, fps: Int) -> AVCaptureDevice.Format? {
    let ok = dev.formats.filter { f in
      let d = CMVideoFormatDescriptionGetDimensions(f.formatDescription)
      guard Int(d.width) == width, Int(d.height) == height else { return false }
      return f.videoSupportedFrameRateRanges.contains { $0.minFrameRate <= Double(fps) && Double(fps) <= $0.maxFrameRate }
    }
    // Prefer full-range YUV (420f), not binned (sharper), lowest max fps that still fits.
    func rank(_ f: AVCaptureDevice.Format) -> (Int, Int, Double) {
      let sub = CMFormatDescriptionGetMediaSubType(f.formatDescription)
      let full = sub == kCVPixelFormatType_420YpCbCr8BiPlanarFullRange ? 0 : 1
      let maxFps = f.videoSupportedFrameRateRanges.map { $0.maxFrameRate }.max() ?? 0
      return (f.isVideoBinned ? 1 : 0, full, maxFps)
    }
    return ok.min { rank($0) < rank($1) }
  }

  // MARK: start / stop

  func start(_ c: StartConfig, completion: @escaping (Result<[String: Any], Error>) -> Void) {
    AVCaptureDevice.requestAccess(for: .video) { granted in
      guard granted else { return completion(.failure(CaptureError.permissionDenied)) }
      self.sessionQueue.async {
        do {
          let info = try self.configure(c)
          self.videoQueue.sync {
            self.cfg = c
            self.resetCounters()
            if let d = c.detector { self.detector.configure(self.withFps(d, c.fps)) }
            else { self.detector.configure(["fps": c.fps]) }
            self.running = true
          }
          self.session.startRunning()
          DispatchQueue.main.async {
            UIApplication.shared.isIdleTimerDisabled = true
            UIDevice.current.isBatteryMonitoringEnabled = true
          }
          completion(.success(info))
        } catch {
          completion(.failure(error))
        }
      }
    }
  }

  func stop(completion: @escaping () -> Void) {
    sessionQueue.async {
      if self.session.isRunning { self.session.stopRunning() }
      self.videoQueue.sync {
        self.flushBatch()
        self.running = false
      }
      DispatchQueue.main.async {
        UIApplication.shared.isIdleTimerDisabled = false
        completion()
      }
    }
  }

  private func configure(_ c: StartConfig) throws -> [String: Any] {
    guard let dev = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back) else {
      throw CaptureError.noCamera
    }
    guard let format = pickFormat(dev, width: c.width, height: c.height, fps: c.fps) else {
      throw CaptureError.noFormat("\(c.width)x\(c.height) at \(c.fps) fps")
    }
    session.beginConfiguration()
    defer { session.commitConfiguration() }
    session.sessionPreset = .inputPriority  // we choose the format ourselves
    for i in session.inputs { session.removeInput(i) }
    for o in session.outputs { session.removeOutput(o) }
    let input: AVCaptureDeviceInput
    do { input = try AVCaptureDeviceInput(device: dev) } catch {
      throw CaptureError.configuration(error.localizedDescription)
    }
    guard session.canAddInput(input) else { throw CaptureError.configuration("cannot add camera input") }
    session.addInput(input)
    output.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
    output.alwaysDiscardsLateVideoFrames = true
    output.setSampleBufferDelegate(self, queue: videoQueue)
    guard session.canAddOutput(output) else { throw CaptureError.configuration("cannot add video output") }
    session.addOutput(output)
    if let conn = output.connection(with: .video), conn.isVideoStabilizationSupported {
      conn.preferredVideoStabilizationMode = .off
    }
    do {
      try dev.lockForConfiguration()
      dev.activeFormat = format
      let dur = CMTime(value: 1, timescale: CMTimeScale(c.fps))
      dev.activeVideoMinFrameDuration = dur
      dev.activeVideoMaxFrameDuration = dur
      if format.isVideoHDRSupported {
        dev.automaticallyAdjustsVideoHDREnabled = false
        dev.isVideoHDREnabled = false
      }
      if dev.isFocusModeSupported(.continuousAutoFocus) { dev.focusMode = .continuousAutoFocus }
      if dev.isExposureModeSupported(.continuousAutoExposure) { dev.exposureMode = .continuousAutoExposure }
      dev.unlockForConfiguration()
    } catch {
      throw CaptureError.configuration(error.localizedDescription)
    }
    device = dev
    let d = CMVideoFormatDescriptionGetDimensions(format.formatDescription)
    return ["width": Int(d.width), "height": Int(d.height), "fps": c.fps,
            "format": "\(d.width)x\(d.height) max \(Int(format.videoSupportedFrameRateRanges.map { $0.maxFrameRate }.max() ?? 0)) fps\(format.isVideoBinned ? " binned" : "")",
            "minShutterS": format.minExposureDuration.seconds, "maxIso": format.maxISO, "minIso": format.minISO]
  }

  private func withFps(_ d: [String: Any], _ fps: Int) -> [String: Any] {
    var m = d
    m["fps"] = fps
    return m
  }

  func setDetectorConfig(_ d: [String: Any]) {
    videoQueue.async {
      self.detector.configure(self.withFps(d, self.cfg.fps))
    }
  }

  // MARK: exposure

  /// mode "auto": continuous AE/AF/AWB. "locked": freeze the current values.
  /// "shutter": fixed exposure time (shutterS), ISO raised to keep the brightness (or `iso`).
  func setExposure(mode: String, shutterS: Double?, iso: Double?) throws -> [String: Any] {
    guard let dev = device else { throw CaptureError.configuration("camera not started") }
    try dev.lockForConfiguration()
    defer { dev.unlockForConfiguration() }
    switch mode {
    case "locked":
      if dev.isExposureModeSupported(.locked) { dev.exposureMode = .locked }
      if dev.isWhiteBalanceModeSupported(.locked) { dev.whiteBalanceMode = .locked }
      if dev.isFocusModeSupported(.locked) { dev.focusMode = .locked }
    case "shutter":
      let f = dev.activeFormat
      let want = shutterS ?? 0.001
      let dur = min(max(want, f.minExposureDuration.seconds), f.maxExposureDuration.seconds)
      let curDur = dev.exposureDuration.seconds
      let targetIso = iso ?? Double(dev.iso) * (curDur > 0 ? curDur / dur : 1)
      let isoC = Float(min(max(targetIso, Double(f.minISO)), Double(f.maxISO)))
      dev.setExposureModeCustom(duration: CMTime(seconds: dur, preferredTimescale: 1_000_000), iso: isoC, completionHandler: nil)
      if dev.isWhiteBalanceModeSupported(.locked) { dev.whiteBalanceMode = .locked }
      if dev.isFocusModeSupported(.locked) { dev.focusMode = .locked }
      return ["mode": mode, "shutterS": dur, "iso": Double(isoC), "isoLimited": Double(isoC) < targetIso - 1]
    default:
      if dev.isExposureModeSupported(.continuousAutoExposure) { dev.exposureMode = .continuousAutoExposure }
      if dev.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) { dev.whiteBalanceMode = .continuousAutoWhiteBalance }
      if dev.isFocusModeSupported(.continuousAutoFocus) { dev.focusMode = .continuousAutoFocus }
    }
    return ["mode": mode, "shutterS": dev.exposureDuration.seconds, "iso": Double(dev.iso)]
  }

  // MARK: frames (videoQueue)

  private func resetCounters() {
    seq = 0
    batch.removeAll()
    batchStart = 0
    lastPreview = -1e9
    statsStart = 0
    nCaptured = 0
    nProcessed = 0
    nDropped = 0
    detectUs = 0
  }

  private func hostTime(_ sb: CMSampleBuffer) -> Double {
    let pts = CMSampleBufferGetPresentationTimeStamp(sb)
    let clock: CMClock?
    if #available(iOS 15.4, *) { clock = session.synchronizationClock } else { clock = session.masterClock }
    guard let c = clock else { return pts.seconds }
    return CMSyncConvertTime(pts, from: c, to: CMClockGetHostTimeClock()).seconds
  }

  func captureOutput(_ output: AVCaptureOutput, didOutput sb: CMSampleBuffer, from connection: AVCaptureConnection) {
    guard running, let pb = CMSampleBufferGetImageBuffer(sb) else { return }
    let t = hostTime(sb)
    nCaptured += 1
    if statsStart == 0 { statsStart = t; batchStart = t }

    CVPixelBufferLockBaseAddress(pb, .readOnly)
    let w = CVPixelBufferGetWidth(pb), h = CVPixelBufferGetHeight(pb), stride = CVPixelBufferGetBytesPerRow(pb)
    var n = 0
    if let base = CVPixelBufferGetBaseAddress(pb) {
      let p = base.assumingMemoryBound(to: UInt8.self)
      n = cands.withUnsafeMutableBufferPointer { buf in
        detector.detectBGRA(p, width: Int32(w), height: Int32(h), bytesPerRow: Int32(stride),
                            into: buf.baseAddress!, maxCandidates: 64)
      }
    }
    CVPixelBufferUnlockBaseAddress(pb, .readOnly)
    nProcessed += 1
    detectUs += detector.lastDetectMicros()
    frameW = w
    frameH = h

    var c = [Double]()
    c.reserveCapacity(n * 4)
    for i in 0..<(n * 4) { c.append(Double(cands[i])) }
    batch.append(["seq": Int(seq), "t": t, "c": c])
    seq &+= 1
    if (t - batchStart) * 1000 >= cfg.batchMs { flushBatch(); batchStart = t }

    if t - lastPreview >= cfg.previewEverySec && !previewBusy {
      lastPreview = t
      previewBusy = true
      let image = CIImage(cvPixelBuffer: pb)
      let s = Int(seq &- 1), q = cfg.previewQuality
      jpegQueue.async {
        let opts = [CIImageRepresentationOption(rawValue: kCGImageDestinationLossyCompressionQuality as String): q]
        if let cs = CGColorSpace(name: CGColorSpace.sRGB),
           let data = self.ciContext.jpegRepresentation(of: image, colorSpace: cs, options: opts) {
          self.emit?("onPreview", ["seq": s, "t": t, "width": w, "height": h,
                                   "jpegBase64": data.base64EncodedString()])
        }
        self.videoQueue.async { self.previewBusy = false }
      }
    }

    if t - statsStart >= 1.0 { emitStats(t) }
  }

  func captureOutput(_ output: AVCaptureOutput, didDrop sb: CMSampleBuffer, from connection: AVCaptureConnection) {
    nDropped += 1
  }

  private func flushBatch() {
    guard !batch.isEmpty else { return }
    emit?("onDetections", ["width": frameW, "height": frameH, "frames": batch])
    batch.removeAll(keepingCapacity: true)
  }

  private func emitStats(_ t: Double) {
    let dt = max(t - statsStart, 1e-3)
    let thermal: String
    switch ProcessInfo.processInfo.thermalState {
    case .nominal: thermal = "nominal"
    case .fair: thermal = "fair"
    case .serious: thermal = "serious"
    case .critical: thermal = "critical"
    @unknown default: thermal = "unknown"
    }
    DispatchQueue.main.async { self.battery = Double(UIDevice.current.batteryLevel) }  // -1 if unknown
    emit?("onStats", ["fpsCapture": Double(nCaptured + nDropped) / dt, "fpsProcessed": Double(nProcessed) / dt,
                      "detectMs": nProcessed > 0 ? detectUs / Double(nProcessed) / 1000 : 0,
                      "dropped": nDropped, "thermal": thermal, "battery": battery])
    statsStart = t
    nCaptured = 0
    nProcessed = 0
    nDropped = 0
    detectUs = 0
  }
}
