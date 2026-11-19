cmake_minimum_required(VERSION 3.22.1)
project(ballcore_jni CXX)

# The shared C++ core (also compiled into the iOS app and the Mac tests).
set(BALLCORE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../../../cpp)

add_library(ballcore_jni SHARED
    ballcore_jni.cpp
    ${BALLCORE_DIR}/ballcore.cpp)
target_include_directories(ballcore_jni PRIVATE ${BALLCORE_DIR})
set_target_properties(ballcore_jni PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)
# -ffp-contract=off: no fused multiply-add, so results match the Python reference exactly.
target_compile_options(ballcore_jni PRIVATE -O2 -ffp-contract=off -Wall)
