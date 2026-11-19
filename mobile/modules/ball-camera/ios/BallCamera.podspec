Pod::Spec.new do |s|
  s.name           = 'BallCamera'
  s.version        = '0.1.0'
  s.summary        = 'Camera capture with on-phone ball detection for BallTracker'
  s.description    = 'AVFoundation capture at up to 240 fps feeding the shared C++ ballcore detector.'
  s.author         = ''
  s.homepage       = 'https://example.invalid/balltracker'
  s.license        = { :type => 'Proprietary' }
  s.platforms      = { :ios => '16.4' }
  s.source         = { git: '' }
  s.static_framework = true

  s.dependency 'ExpoModulesCore'

  # BCDetector.mm compiles ../cpp/ballcore.cpp itself (unity build), so the
  # shared C++ stays in one place for iOS, Android and the Mac tests.
  s.source_files = '**/*.{h,m,mm,swift}'
  s.public_header_files = 'BCDetector.h'
  s.pod_target_xcconfig = {
    'DEFINES_MODULE' => 'YES',
    'CLANG_CXX_LANGUAGE_STANDARD' => 'c++17',
    # No fused multiply-add: keeps results identical to the Python reference.
    'OTHER_CPLUSPLUSFLAGS' => '$(inherited) -ffp-contract=off -O2',
  }
end
