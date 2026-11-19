// ballcore: C++ port of balltracker/edge_detection.py. Keep the two in step:
// any change here needs the same change there (and the parity test to pass).

#include "ballcore.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstring>
#include <new>
#include <vector>

namespace {

constexpr double kPi = 3.14159265358979323846;

struct Comp {
    int minx, miny, maxx, maxy;
    long long area, sumx, sumy;
};

inline bool gate_bgr(int b, int g, int r, const int lo[3], const int hi[3]) {
    const int v = std::max(std::max(b, g), r);
    const int mn = std::min(std::min(b, g), r);
    const int diff = v - mn;
    if (v < lo[2] || v > hi[2]) return false;
    if (v == 0) {
        if (lo[1] != 0) return false;
    } else {
        const int s255 = 255 * diff;
        if (s255 < lo[1] * v || s255 > hi[1] * v) return false;
    }
    if (diff == 0) return lo[0] == 0;
    int h6;
    if (v == r) h6 = 60 * (g - b);
    else if (v == g) h6 = 120 * diff + 60 * (b - r);
    else h6 = 240 * diff + 60 * (r - g);
    if (h6 < 0) h6 += 360 * diff;
    return h6 >= 2 * lo[0] * diff && h6 <= 2 * hi[0] * diff;
}

// Python round() semantics (half to even) for the integer config values.
inline int py_round(double x) { return static_cast<int>(std::nearbyint(x)); }

}  // namespace

struct bc_detector {
    bc_config cfg{};
    int update_every = 1, history = 1;
    // State
    int sw = 0, sh = 0, W = 0, H = 0;
    std::vector<uint8_t> small;   // sh*sw*3, BGR
    std::vector<float> mu;        // sh*sw*3
    std::vector<float> var;       // sh*sw
    std::vector<uint8_t> mask, dil;
    std::vector<int> labels, parent;
    bool have_bg = false;
    long long updates = 0, frame = 0;
    bool have_ref = false;
    double ref_mean[3] = {0, 0, 0};
    // ROI (full resolution, sampled at block corners)
    std::vector<uint8_t> roi;
    int roi_w = 0, roi_h = 0;
    double last_us = 0;

    void configure(const bc_config &c) {
        cfg = c;
        if (cfg.bin < 1) cfg.bin = 1;
        update_every = std::max(1, py_round(cfg.fps / cfg.bg_update_hz));
        history = std::max(1, py_round(cfg.bg_history_s * cfg.bg_update_hz));
        reset();
    }
    void reset() {
        have_bg = false;
        updates = frame = 0;
        have_ref = false;
        sw = sh = W = H = 0;
    }
    int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }
    void unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) return;
        if (a < b) parent[b] = a; else parent[a] = b;  // root = earliest label = first raster pixel
    }
    int detect(const uint8_t *px, int width, int height, int stride, int fmt, bc_candidate *out, int max_out);
};

extern "C" {

void bc_default_config(bc_config *c) {
    std::memset(c, 0, sizeof(*c));
    c->bin = 2;
    c->hsv_low[0] = 25; c->hsv_low[1] = 100; c->hsv_low[2] = 90;
    c->hsv_high[0] = 55; c->hsv_high[1] = 255; c->hsv_high[2] = 255;
    c->var_threshold = 24.0f;
    c->var_init = 15.0f;
    c->var_min = 4.0f;
    c->var_max = 75.0f;
    c->bg_history_s = 2.0;
    c->bg_update_hz = 60.0;
    c->fps = 60.0;
    c->min_radius_px = 1.5;
    c->max_radius_px = 80.0;
    c->max_elongation = 6.0;
    c->max_candidates = 12;
    c->flicker_compensation = 1;
    c->flicker_alpha = 0.02;
}

bc_detector *bc_create(const bc_config *cfg) {
    bc_detector *d = new (std::nothrow) bc_detector();
    if (!d) return nullptr;
    bc_config c;
    if (cfg) c = *cfg; else bc_default_config(&c);
    d->configure(c);
    return d;
}

void bc_destroy(bc_detector *d) { delete d; }
void bc_reset(bc_detector *d) { if (d) d->reset(); }
void bc_configure(bc_detector *d, const bc_config *cfg) { if (d && cfg) d->configure(*cfg); }
double bc_last_detect_us(const bc_detector *d) { return d ? d->last_us : 0.0; }

void bc_set_roi(bc_detector *d, const uint8_t *mask, int width, int height, int stride) {
    if (!d) return;
    if (!mask || width <= 0 || height <= 0) {
        d->roi.clear();
        d->roi_w = d->roi_h = 0;
        return;
    }
    d->roi.resize(static_cast<size_t>(width) * height);
    for (int y = 0; y < height; ++y) std::memcpy(&d->roi[static_cast<size_t>(y) * width], mask + static_cast<size_t>(y) * stride, width);
    d->roi_w = width;
    d->roi_h = height;
}

int bc_detect(bc_detector *d, const uint8_t *pixels, int width, int height, int stride_bytes, int format,
              bc_candidate *out, int max_out) {
    if (!d || !pixels || width <= 0 || height <= 0 || format < 0 || format > 3 || (max_out > 0 && !out)) return -1;
    auto t0 = std::chrono::steady_clock::now();
    int n = d->detect(pixels, width, height, stride_bytes, format, out, max_out);
    d->last_us = std::chrono::duration<double, std::micro>(std::chrono::steady_clock::now() - t0).count();
    return n;
}

}  // extern "C"

int bc_detector::detect(const uint8_t *px, int width, int height, int stride, int fmt, bc_candidate *out, int max_out) {
    const bc_config &c = cfg;
    const int k = c.bin;
    const int ch = (fmt == BC_FMT_BGRA || fmt == BC_FMT_RGBA) ? 4 : 3;
    const bool rgb = (fmt == BC_FMT_RGBA || fmt == BC_FMT_RGB);
    const int ib = rgb ? 2 : 0, ir = rgb ? 0 : 2;  // byte offsets of blue / red
    const int nsw = width / k, nsh = height / k;
    if (nsw < 8 || nsh < 8) return 0;
    if (nsw != sw || nsh != sh || width != W || height != H) {
        sw = nsw; sh = nsh; W = width; H = height;
        const size_t np = static_cast<size_t>(sw) * sh;
        small.assign(np * 3, 0);
        mu.assign(np * 3, 0.f);
        var.assign(np, 0.f);
        mask.assign(np, 0);
        dil.assign(np, 0);
        labels.assign(np, 0);
        have_bg = false;
        updates = frame = 0;
        have_ref = false;
    }
    const size_t np = static_cast<size_t>(sw) * sh;

    // 1. Bin k x k, round half up, into BGR.
    const int kk = k * k, half = kk / 2;
    for (int y = 0; y < sh; ++y) {
        uint8_t *dst = &small[static_cast<size_t>(y) * sw * 3];
        for (int x = 0; x < sw; ++x) {
            unsigned sb = 0, sg = 0, sr = 0;
            for (int dy = 0; dy < k; ++dy) {
                const uint8_t *row = px + static_cast<size_t>(y * k + dy) * stride + static_cast<size_t>(x * k) * ch;
                for (int dx = 0; dx < k; ++dx) {
                    const uint8_t *p = row + dx * ch;
                    sb += p[ib]; sg += p[1]; sr += p[ir];
                }
            }
            dst[3 * x + 0] = static_cast<uint8_t>((sb + half) / kk);
            dst[3 * x + 1] = static_cast<uint8_t>((sg + half) / kk);
            dst[3 * x + 2] = static_cast<uint8_t>((sr + half) / kk);
        }
    }

    // 2. Flicker compensation (float64 means, float32 LUT, floor).
    if (c.flicker_compensation) {
        unsigned long long s[3] = {0, 0, 0};
        for (size_t i = 0; i < np; ++i) {
            s[0] += small[3 * i]; s[1] += small[3 * i + 1]; s[2] += small[3 * i + 2];
        }
        double m[3], gain[3];
        for (int j = 0; j < 3; ++j) m[j] = static_cast<double>(s[j]) / static_cast<double>(np) + 1e-3;
        if (!have_ref) {
            for (int j = 0; j < 3; ++j) ref_mean[j] = m[j];
            have_ref = true;
        }
        bool skip = true;
        for (int j = 0; j < 3; ++j) {
            gain[j] = ref_mean[j] / m[j];
            if (!(std::fabs(gain[j] - 1.0) < 0.01)) skip = false;
        }
        const double a = c.flicker_alpha;
        for (int j = 0; j < 3; ++j) ref_mean[j] = (1 - a) * ref_mean[j] + a * m[j];
        if (!skip) {
            uint8_t lut[3][256];
            for (int j = 0; j < 3; ++j) {
                const float g = static_cast<float>(gain[j]);
                for (int i = 0; i < 256; ++i) {
                    float v = static_cast<float>(i) * g;
                    if (v > 255.0f) v = 255.0f;
                    lut[j][i] = static_cast<uint8_t>(v);
                }
            }
            for (size_t i = 0; i < np; ++i) {
                small[3 * i] = lut[0][small[3 * i]];
                small[3 * i + 1] = lut[1][small[3 * i + 1]];
                small[3 * i + 2] = lut[2][small[3 * i + 2]];
            }
        }
    }

    // 3-4. Colour gate, foreground test, background update.
    const bool first = !have_bg;
    const bool update_frame = (frame % update_every) == 0;
    bool do_update = false;
    float a = 0.f;
    if (update_frame) {
        ++updates;
        a = static_cast<float>(1.0 / static_cast<double>(std::min<long long>(updates, history)));
        do_update = updates > 1;
    }
    ++frame;
    const float vt = c.var_threshold, vmin = c.var_min, vmax = c.var_max;
    const bool use_roi = !roi.empty() && roi_w == W && roi_h == H;
    bool any = false;
    for (size_t i = 0; i < np; ++i) {
        const uint8_t *p = &small[3 * i];
        float *m = &mu[3 * i];
        const float x0 = p[0], x1 = p[1], x2 = p[2];
        if (first) {
            m[0] = x0; m[1] = x1; m[2] = x2;
            var[i] = c.var_init;
            mask[i] = 0;
            continue;
        }
        const bool col = gate_bgr(p[0], p[1], p[2], c.hsv_low, c.hsv_high);
        if (!col && !do_update) {
            mask[i] = 0;
            continue;
        }
        const float d0 = x0 - m[0], d1 = x1 - m[1], d2c = x2 - m[2];
        const float d2 = (d0 * d0 + d1 * d1) + d2c * d2c;
        bool fg = d2 > vt * var[i];
        uint8_t mk = (col && fg) ? 1 : 0;
        if (mk && use_roi) {
            const int y = static_cast<int>(i / sw), x = static_cast<int>(i % sw);
            if (roi[static_cast<size_t>(y * k) * W + static_cast<size_t>(x * k)] == 0) mk = 0;
        }
        mask[i] = mk;
        any |= mk != 0;
        if (do_update) {
            m[0] = m[0] + a * (x0 - m[0]);
            m[1] = m[1] + a * (x1 - m[1]);
            m[2] = m[2] + a * (x2 - m[2]);
            float nv = var[i] + a * (d2 - var[i]);
            nv = std::min(std::max(nv, vmin), vmax);
            var[i] = nv;
        }
    }
    have_bg = true;
    if (!any) return 0;

    // 5. Dilate with a 3x3 cross.
    for (int y = 0; y < sh; ++y) {
        for (int x = 0; x < sw; ++x) {
            const size_t i = static_cast<size_t>(y) * sw + x;
            uint8_t v = mask[i];
            if (!v) {
                if ((x > 0 && mask[i - 1]) || (x + 1 < sw && mask[i + 1]) || (y > 0 && mask[i - sw]) ||
                    (y + 1 < sh && mask[i + sw]))
                    v = 1;
            }
            dil[i] = v;
        }
    }

    // 6. 8-connected components (two-pass union-find).
    parent.clear();
    parent.push_back(0);
    for (int y = 0; y < sh; ++y) {
        for (int x = 0; x < sw; ++x) {
            const size_t i = static_cast<size_t>(y) * sw + x;
            if (!dil[i]) { labels[i] = 0; continue; }
            int best = 0;
            const int nb[4] = {
                x > 0 ? labels[i - 1] : 0,
                (x > 0 && y > 0) ? labels[i - sw - 1] : 0,
                y > 0 ? labels[i - sw] : 0,
                (x + 1 < sw && y > 0) ? labels[i - sw + 1] : 0,
            };
            for (int q = 0; q < 4; ++q) if (nb[q] && (!best || nb[q] < best)) best = nb[q];
            if (!best) {
                best = static_cast<int>(parent.size());
                parent.push_back(best);
            } else {
                for (int q = 0; q < 4; ++q) if (nb[q]) unite(best, nb[q]);
            }
            labels[i] = best;
        }
    }
    const int nl = static_cast<int>(parent.size());
    std::vector<int> root_index(nl, -1);
    std::vector<Comp> comps;
    for (int y = 0; y < sh; ++y) {
        for (int x = 0; x < sw; ++x) {
            const int l = labels[static_cast<size_t>(y) * sw + x];
            if (!l) continue;
            const int r = find(l);
            int ci = root_index[r];
            if (ci < 0) {
                ci = root_index[r] = static_cast<int>(comps.size());
                comps.push_back({x, y, x, y, 0, 0, 0});
            }
            Comp &cp = comps[ci];
            cp.minx = std::min(cp.minx, x); cp.maxx = std::max(cp.maxx, x);
            cp.miny = std::min(cp.miny, y); cp.maxy = std::max(cp.maxy, y);
            cp.area += 1; cp.sumx += x; cp.sumy += y;
        }
    }
    // Components were created in raster order of their first pixel (OpenCV's label order).

    // 7. Filter and refine at full resolution.
    const double min_area = std::max(1.0, kPi * std::pow(c.min_radius_px / k, 2) * 0.3);
    const double max_area = kPi * std::pow(c.max_radius_px / k, 2) * 3;
    const int pad = 3;
    std::vector<bc_candidate> cands;
    for (const Comp &cp : comps) {
        const int bx = cp.minx, by = cp.miny, bw = cp.maxx - cp.minx + 1, bh = cp.maxy - cp.miny + 1;
        const double area = static_cast<double>(cp.area);
        if (area < min_area || area > max_area) continue;
        if (bx <= 2 || by <= 2 || bx + bw >= sw - 2 || by + bh >= sh - 2) continue;
        const double elong = static_cast<double>(std::max(bw, bh)) / static_cast<double>(std::max(1, std::min(bw, bh)));
        if (elong > c.max_elongation) continue;
        const int X0 = std::max(0, (bx - pad) * k), Y0 = std::max(0, (by - pad) * k);
        const int X1 = std::min(W, (bx + bw + pad) * k), Y1 = std::min(H, (by + bh + pad) * k);
        long long cnt = 0, sx = 0, sy = 0;
        for (int y = Y0; y < Y1; ++y) {
            const uint8_t *row = px + static_cast<size_t>(y) * stride;
            for (int x = X0; x < X1; ++x) {
                const uint8_t *p = row + static_cast<size_t>(x) * ch;
                if (gate_bgr(p[ib], p[1], p[ir], c.hsv_low, c.hsv_high)) {
                    ++cnt; sx += x - X0; sy += y - Y0;
                }
            }
        }
        double u, v, r;
        if (cnt == 0) {
            u = (static_cast<double>(cp.sumx) / area + 0.5) * k - 0.5;
            v = (static_cast<double>(cp.sumy) / area + 0.5) * k - 0.5;
            r = 1.0;
        } else {
            u = static_cast<double>(sx) / static_cast<double>(cnt) + X0;
            v = static_cast<double>(sy) / static_cast<double>(cnt) + Y0;
            r = std::sqrt(static_cast<double>(cnt) / kPi);
        }
        if (!(c.min_radius_px * 0.5 <= r && r <= c.max_radius_px * 1.5)) continue;
        const double fill = area / static_cast<double>(std::max(1, bw * bh));
        const double score = std::min(std::max(0.5 * fill / 0.785 + 0.5 / elong, 0.0), 1.0);
        cands.push_back({static_cast<float>(u), static_cast<float>(v), static_cast<float>(r), static_cast<float>(score),
                         static_cast<float>(area * k * k), static_cast<float>(elong)});
    }
    std::stable_sort(cands.begin(), cands.end(), [](const bc_candidate &p, const bc_candidate &q) { return p.score > q.score; });
    const int n = std::min<int>({static_cast<int>(cands.size()), c.max_candidates, max_out});
    for (int i = 0; i < n; ++i) out[i] = cands[i];
    return n;
}
