import AVFoundation
import ExpoModulesCore
import UIKit

/// Live camera preview (the capture session is owned by CaptureEngine).
class BallCameraView: ExpoView {
  private let previewLayer = AVCaptureVideoPreviewLayer(session: CaptureEngine.shared.session)

  required init(appContext: AppContext? = nil) {
    super.init(appContext: appContext)
    backgroundColor = .black
    previewLayer.videoGravity = .resizeAspect
    layer.addSublayer(previewLayer)
    // The preview's connection only exists once the capture session has its camera input, which
    // happens after this view is laid out. Re-apply the rotation whenever the session starts,
    // otherwise the preview stays in the default portrait rotation.
    NotificationCenter.default.addObserver(
      self, selector: #selector(sessionStarted), name: AVCaptureSession.didStartRunningNotification,
      object: CaptureEngine.shared.session)
  }

  deinit {
    NotificationCenter.default.removeObserver(self)
  }

  @objc private func sessionStarted() {
    DispatchQueue.main.async { [weak self] in self?.updateOrientation() }
  }

  override func didMoveToWindow() {
    super.didMoveToWindow()
    updateOrientation()
  }

  override func layoutSubviews() {
    super.layoutSubviews()
    previewLayer.frame = bounds
    updateOrientation()
  }

  private func updateOrientation() {
    guard let conn = previewLayer.connection,
          let io = window?.windowScene?.interfaceOrientation else { return }
    // The app is locked to landscape; match the preview to whichever landscape it is.
    if #available(iOS 17.0, *) {
      let angle: CGFloat
      switch io {
      case .landscapeRight: angle = 0
      case .landscapeLeft: angle = 180
      case .portraitUpsideDown: angle = 270
      default: angle = 90
      }
      if conn.isVideoRotationAngleSupported(angle) { conn.videoRotationAngle = angle }
    } else {
      let o: AVCaptureVideoOrientation
      switch io {
      case .landscapeRight: o = .landscapeRight
      case .landscapeLeft: o = .landscapeLeft
      case .portraitUpsideDown: o = .portraitUpsideDown
      default: o = .portrait
      }
      if conn.isVideoOrientationSupported { conn.videoOrientation = o }
    }
  }
}
