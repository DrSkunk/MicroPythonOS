# WASM-compatible user C modules for c_mpos.
#
# Used when building with Emscripten (ports/webassembly Makefile).
# Pass this file to the build with: USER_C_MODULES=/path/to/micropython_wasm.mk
#
# Modules included here must be pure C with no platform-specific dependencies:
#   - quirc_decode + quirc library: pure C, compiles cleanly under emcc
#
# Modules excluded (and why):
#   - webcam.c:          uses Linux v4l2 (not available in Emscripten)
#   - adc_mic.c:         ESP-IDF ADC peripheral API
#   - pdm_mic.c:         ESP-IDF PDM / I2S peripheral API
#   - rvswd_module.c:    ESP32-specific JTAG/SWD bit-bang debugger
#   - secp256k1-embedded-ecdh: may contain x86-specific assembly intrinsics;
#                        use the pure-Python secp256k1.py already present in
#                        internal_filesystem/lib/ instead.

MOD_DIR := $(USERMOD_DIR)

SRC_USERMOD_C += $(MOD_DIR)/src/quirc_decode.c
SRC_USERMOD_C += $(MOD_DIR)/quirc/lib/identify.c
SRC_USERMOD_C += $(MOD_DIR)/quirc/lib/version_db.c
SRC_USERMOD_C += $(MOD_DIR)/quirc/lib/decode.c
SRC_USERMOD_C += $(MOD_DIR)/quirc/lib/quirc.c

# Force single-precision float maths in quirc (same as the ESP32 build).
CFLAGS_USERMOD += -DQUIRC_FLOAT_TYPE=float -DQUIRC_USE_TGMATH=1

# Size-optimised build (matches the webassembly port's -Os default).
CFLAGS_USERMOD += -Os
