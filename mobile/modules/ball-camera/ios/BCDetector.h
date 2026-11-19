// Objective-C wrapper around the C++ ballcore detector, so Swift can call it.
#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

@interface BCDetector : NSObject

/// Detector settings as the server sends them (snake_case keys, EdgeDetectorConfig).
- (instancetype)initWithConfig:(nullable NSDictionary<NSString *, id> *)config;
- (void)configure:(nullable NSDictionary<NSString *, id> *)config;
- (void)reset;

/// Detect in a 32BGRA frame. Writes 4 floats per candidate (u, v, radius, score) into `out`.
/// Returns the number of candidates (<= maxCandidates).
- (NSInteger)detectBGRA:(const uint8_t *)base
                  width:(int)width
                 height:(int)height
            bytesPerRow:(int)bytesPerRow
                   into:(float *)out
          maxCandidates:(int)maxCandidates;

/// Microseconds spent in the last detect call.
- (double)lastDetectMicros;

@end

NS_ASSUME_NONNULL_END
