/*
 * ballcore: on-phone ball detection (C API, shared by iOS, Android and the Mac tests).
 *
 * A C++ port of balltracker/edge_detection.py (the reference). Same steps, same
 * integer maths and float32 operation order, so results match the Python
 * implementation; tests/test_ballcore_parity.py checks this on recorded video.
 *
 * Build with -ffp-contract=off (no fused multiply-add), otherwise ARM compilers
 * fuse a*b+c and the background model drifts from the reference by rounding.
 *
 * Thread safety: one bc_detector per camera, used from one thread at a time.
 */
#ifndef BALLCORE_H
#define BALLCORE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BC_ALGO "edge_color_motion"
#define BC_ALGO_VERSION "1.0.0"

/* Pixel layouts accepted by bc_detect (8 bits per channel, interleaved). */
enum { BC_FMT_BGRA = 0, BC_FMT_RGBA = 1, BC_FMT_BGR = 2, BC_FMT_RGB = 3 };

typedef struct {
    int bin;                 /* k x k binning before detection (1, 2, 4) */
    int hsv_low[3];          /* OpenCV HSV units: H 0-180, S 0-255, V 0-255 */
    int hsv_high[3];
    float var_threshold;     /* foreground if d2 > var_threshold * var */
    float var_init, var_min, var_max;
    double bg_history_s;     /* background memory (seconds) */
    double bg_update_hz;     /* background update rate, independent of fps */
    double fps;              /* nominal capture rate */
    double min_radius_px, max_radius_px, max_elongation;
    int max_candidates;
    int flicker_compensation;
    double flicker_alpha;
} bc_config;

typedef struct {
    float u, v;              /* full-resolution pixel coordinates (pixel centres at integers) */
    float radius_px;
    float score;             /* 0..1 shape quality */
    float area_px;           /* blob area in full-resolution pixels */
    float elongation;
} bc_candidate;

typedef struct bc_detector bc_detector;

void bc_default_config(bc_config *cfg);
bc_detector *bc_create(const bc_config *cfg);
void bc_destroy(bc_detector *d);
/* Forget the background model (call after the camera moves or the format changes). */
void bc_reset(bc_detector *d);
/* Replace the configuration; resets the background model. */
void bc_configure(bc_detector *d, const bc_config *cfg);
/* Optional search mask at full resolution (255 = search). mask == NULL clears it. */
void bc_set_roi(bc_detector *d, const uint8_t *mask, int width, int height, int stride);
/*
 * Detect ball candidates in one frame. Returns the number written to `out`
 * (at most max_out, sorted by score, best first), or -1 on bad arguments.
 */
int bc_detect(bc_detector *d, const uint8_t *pixels, int width, int height, int stride_bytes, int format,
              bc_candidate *out, int max_out);
/* Microseconds spent in the last bc_detect call (for the app's stats). */
double bc_last_detect_us(const bc_detector *d);

#ifdef __cplusplus
}
#endif

#endif /* BALLCORE_H */
