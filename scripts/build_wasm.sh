#!/bin/bash
# Build the shared C++ ball detector for the browser phone page (WebAssembly).
#   scripts/build_wasm.sh            -> balltracker/live/static/ballcore.wasm
# Needs wasi-sdk (https://github.com/WebAssembly/wasi-sdk); set WASI_SDK or install to ~/.local/toolchains.
set -euo pipefail
cd "$(dirname "$0")/.."
WASI_SDK="${WASI_SDK:-$(ls -d "$HOME"/.local/toolchains/wasi-sdk-* 2>/dev/null | tail -1)}"
[ -x "$WASI_SDK/bin/clang++" ] || { echo "wasi-sdk not found (set WASI_SDK)"; exit 1; }
SRC=mobile/modules/ball-camera/cpp
OUT=balltracker/live/static/ballcore.wasm
"$WASI_SDK/bin/clang++" --target=wasm32-wasip1 -std=c++17 -O3 -ffp-contract=off -fno-exceptions -fno-rtti \
  -mexec-model=reactor -Wl,--strip-all \
  -o "$OUT" "$SRC/ballcore.cpp" "$SRC/ballcore_wasm.cpp"
echo "built $OUT ($(wc -c < "$OUT" | tr -d ' ') bytes)"
