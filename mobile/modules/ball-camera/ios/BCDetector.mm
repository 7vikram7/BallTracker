#import "BCDetector.h"

// The shared C++ core lives in ../cpp (also used by Android and the Mac tests).
// Compiling it here (unity build) avoids pointing CocoaPods at files outside the pod folder.
#include "../cpp/ballcore.h"
#include "../cpp/ballcore.cpp"

static double num(NSDictionary *d, NSString *k, double dflt) {
    id v = d[k];
    return [v isKindOfClass:[NSNumber class]] ? [v doubleValue] : dflt;
}

static void triple(NSDictionary *d, NSString *k, int out[3]) {
    id v = d[k];
    if (![v isKindOfClass:[NSArray class]] || [v count] != 3) return;
    for (int i = 0; i < 3; i++) {
        id e = v[i];
        if ([e isKindOfClass:[NSNumber class]]) out[i] = [e intValue];
    }
}

static bc_config make_config(NSDictionary *d) {
    bc_config c;
    bc_default_config(&c);
    if (!d) return c;
    c.bin = (int)num(d, @"bin", c.bin);
    triple(d, @"hsv_low", c.hsv_low);
    triple(d, @"hsv_high", c.hsv_high);
    c.var_threshold = (float)num(d, @"var_threshold", c.var_threshold);
    c.var_init = (float)num(d, @"var_init", c.var_init);
    c.var_min = (float)num(d, @"var_min", c.var_min);
    c.var_max = (float)num(d, @"var_max", c.var_max);
    c.bg_history_s = num(d, @"bg_history_s", c.bg_history_s);
    c.bg_update_hz = num(d, @"bg_update_hz", c.bg_update_hz);
    c.fps = num(d, @"fps", c.fps);
    c.min_radius_px = num(d, @"min_radius_px", c.min_radius_px);
    c.max_radius_px = num(d, @"max_radius_px", c.max_radius_px);
    c.max_elongation = num(d, @"max_elongation", c.max_elongation);
    c.max_candidates = (int)num(d, @"max_candidates", c.max_candidates);
    id fl = d[@"flicker_compensation"];
    if ([fl isKindOfClass:[NSNumber class]]) c.flicker_compensation = [fl boolValue] ? 1 : 0;
    c.flicker_alpha = num(d, @"flicker_alpha", c.flicker_alpha);
    return c;
}

@implementation BCDetector {
    bc_detector *_d;
    bc_candidate _buf[64];
}

- (instancetype)initWithConfig:(NSDictionary<NSString *, id> *)config {
    if ((self = [super init])) {
        bc_config c = make_config(config);
        _d = bc_create(&c);
    }
    return self;
}

- (void)dealloc {
    bc_destroy(_d);
}

- (void)configure:(NSDictionary<NSString *, id> *)config {
    bc_config c = make_config(config);
    bc_configure(_d, &c);
}

- (void)reset {
    bc_reset(_d);
}

- (NSInteger)detectBGRA:(const uint8_t *)base width:(int)width height:(int)height bytesPerRow:(int)bytesPerRow
                   into:(float *)out maxCandidates:(int)maxCandidates {
    int maxc = maxCandidates < 64 ? maxCandidates : 64;
    int n = bc_detect(_d, base, width, height, bytesPerRow, BC_FMT_BGRA, _buf, maxc);
    if (n < 0) return 0;
    for (int i = 0; i < n; i++) {
        out[4 * i + 0] = _buf[i].u;
        out[4 * i + 1] = _buf[i].v;
        out[4 * i + 2] = _buf[i].radius_px;
        out[4 * i + 3] = _buf[i].score;
    }
    return n;
}

- (double)lastDetectMicros {
    return bc_last_detect_us(_d);
}

@end
