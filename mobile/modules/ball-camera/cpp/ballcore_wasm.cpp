// WebAssembly entry points for the browser phone page (balltracker/live/static/edge-worker.js).
// Built by scripts/build_wasm.sh into balltracker/live/static/ballcore.wasm.
//
// Flat, pointer-and-number API (no structs across the boundary):
//   bcw_alloc / bcw_free             scratch memory for frames and results
//   bcw_create / bcw_destroy
//   bcw_configure(det, vals, n)      vals = 20 doubles, same order as the Android JNI bridge:
//       bin, hsv_low[3], hsv_high[3], max_candidates, flicker_compensation,
//       var_threshold, var_init, var_min, var_max, bg_history_s, bg_update_hz, fps,
//       min_radius_px, max_radius_px, max_elongation, flicker_alpha
//   bcw_detect(det, px, w, h, stride, fmt, out, max) -> n; out = 4 floats per candidate (u, v, r, score)
//   bcw_last_us(det)

#include <cstdlib>

#include "ballcore.h"

#define EXPORT(name) extern "C" __attribute__((export_name(#name)))

EXPORT(bcw_alloc) void *bcw_alloc(int n) { return std::malloc(static_cast<size_t>(n)); }
EXPORT(bcw_free) void bcw_free(void *p) { std::free(p); }
EXPORT(bcw_create) bc_detector *bcw_create() { return bc_create(nullptr); }
EXPORT(bcw_destroy) void bcw_destroy(bc_detector *d) { bc_destroy(d); }
EXPORT(bcw_reset) void bcw_reset(bc_detector *d) { bc_reset(d); }
EXPORT(bcw_last_us) double bcw_last_us(bc_detector *d) { return bc_last_detect_us(d); }

EXPORT(bcw_configure) int bcw_configure(bc_detector *d, const double *v, int n) {
    if (!d || !v || n < 20) return 0;
    bc_config c;
    bc_default_config(&c);
    c.bin = static_cast<int>(v[0]);
    for (int k = 0; k < 3; ++k) {
        c.hsv_low[k] = static_cast<int>(v[1 + k]);
        c.hsv_high[k] = static_cast<int>(v[4 + k]);
    }
    c.max_candidates = static_cast<int>(v[7]);
    c.flicker_compensation = v[8] != 0 ? 1 : 0;
    c.var_threshold = static_cast<float>(v[9]);
    c.var_init = static_cast<float>(v[10]);
    c.var_min = static_cast<float>(v[11]);
    c.var_max = static_cast<float>(v[12]);
    c.bg_history_s = v[13];
    c.bg_update_hz = v[14];
    c.fps = v[15];
    c.min_radius_px = v[16];
    c.max_radius_px = v[17];
    c.max_elongation = v[18];
    c.flicker_alpha = v[19];
    bc_configure(d, &c);
    return 1;
}

EXPORT(bcw_detect) int bcw_detect(bc_detector *d, const uint8_t *px, int w, int h, int stride, int fmt, float *out, int max) {
    bc_candidate c[64];
    const int maxc = max < 64 ? max : 64;
    const int n = bc_detect(d, px, w, h, stride, fmt, c, maxc);
    for (int i = 0; i < n; ++i) {
        out[4 * i + 0] = c[i].u;
        out[4 * i + 1] = c[i].v;
        out[4 * i + 2] = c[i].radius_px;
        out[4 * i + 3] = c[i].score;
    }
    return n;
}
