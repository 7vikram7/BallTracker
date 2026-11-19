// JNI bridge: expo.modules.ballcamera.NativeDetector <-> ballcore (C API).
#include <jni.h>

#include "ballcore.h"

namespace {
inline bc_detector *H(jlong h) { return reinterpret_cast<bc_detector *>(h); }

// ints:    bin, hsv_low[3], hsv_high[3], max_candidates, flicker_compensation           (9)
// doubles: var_threshold, var_init, var_min, var_max, bg_history_s, bg_update_hz, fps,
//          min_radius_px, max_radius_px, max_elongation, flicker_alpha                  (11)
bool fill(JNIEnv *env, jintArray ints, jdoubleArray dbls, bc_config *c) {
    bc_default_config(c);
    if (!ints || !dbls || env->GetArrayLength(ints) < 9 || env->GetArrayLength(dbls) < 11) return false;
    jint i[9];
    jdouble d[11];
    env->GetIntArrayRegion(ints, 0, 9, i);
    env->GetDoubleArrayRegion(dbls, 0, 11, d);
    c->bin = i[0];
    for (int k = 0; k < 3; ++k) { c->hsv_low[k] = i[1 + k]; c->hsv_high[k] = i[4 + k]; }
    c->max_candidates = i[7];
    c->flicker_compensation = i[8];
    c->var_threshold = static_cast<float>(d[0]);
    c->var_init = static_cast<float>(d[1]);
    c->var_min = static_cast<float>(d[2]);
    c->var_max = static_cast<float>(d[3]);
    c->bg_history_s = d[4];
    c->bg_update_hz = d[5];
    c->fps = d[6];
    c->min_radius_px = d[7];
    c->max_radius_px = d[8];
    c->max_elongation = d[9];
    c->flicker_alpha = d[10];
    return true;
}
}  // namespace

extern "C" {

JNIEXPORT jlong JNICALL Java_expo_modules_ballcamera_NativeDetector_nativeCreate(JNIEnv *, jobject) {
    return reinterpret_cast<jlong>(bc_create(nullptr));
}

JNIEXPORT void JNICALL Java_expo_modules_ballcamera_NativeDetector_nativeDestroy(JNIEnv *, jobject, jlong h) {
    bc_destroy(H(h));
}

JNIEXPORT jboolean JNICALL Java_expo_modules_ballcamera_NativeDetector_nativeConfigure(JNIEnv *env, jobject, jlong h,
                                                                                      jintArray ints, jdoubleArray dbls) {
    bc_config c;
    if (!fill(env, ints, dbls, &c)) return JNI_FALSE;
    bc_configure(H(h), &c);
    return JNI_TRUE;
}

// buf: direct ByteBuffer (ImageProxy plane 0, RGBA_8888). out: 4 floats per candidate.
JNIEXPORT jint JNICALL Java_expo_modules_ballcamera_NativeDetector_nativeDetect(JNIEnv *env, jobject, jlong h,
                                                                               jobject buf, jint width, jint height,
                                                                               jint stride, jint format, jfloatArray out) {
    const uint8_t *px = static_cast<const uint8_t *>(env->GetDirectBufferAddress(buf));
    if (!px || !out) return -1;
    const jsize cap = env->GetArrayLength(out) / 4;
    bc_candidate c[64];
    const int maxc = cap < 64 ? static_cast<int>(cap) : 64;
    const int n = bc_detect(H(h), px, width, height, stride, format, c, maxc);
    if (n <= 0) return n;
    jfloat tmp[64 * 4];
    for (int i = 0; i < n; ++i) {
        tmp[4 * i + 0] = c[i].u;
        tmp[4 * i + 1] = c[i].v;
        tmp[4 * i + 2] = c[i].radius_px;
        tmp[4 * i + 3] = c[i].score;
    }
    env->SetFloatArrayRegion(out, 0, n * 4, tmp);
    return n;
}

JNIEXPORT jdouble JNICALL Java_expo_modules_ballcamera_NativeDetector_nativeLastMicros(JNIEnv *, jobject, jlong h) {
    return bc_last_detect_us(H(h));
}

JNIEXPORT void JNICALL Java_expo_modules_ballcamera_NativeDetector_nativeReset(JNIEnv *, jobject, jlong h) {
    bc_reset(H(h));
}

}  // extern "C"
