# Hardware / display initialisation for the WebAssembly (Emscripten) target.
#
# MicroPython sets sys.platform = "webassembly" for this port.
#
# ── Current state ───────────────────────────────────────────────────────────
# The lvgl_micropython make.py does not yet have a "webassembly" build target,
# so the initial WASM build is plain MicroPython (no LVGL).  In that case
# mpos/main.py will fail at "import lvgl as lv" before it ever calls this
# board module, which is expected and handled gracefully by the outer
# internal_filesystem/main.py try/except block.
#
# ── Future state (LVGL + Emscripten) ────────────────────────────────────────
# When lvgl_micropython gains Emscripten support (compiling with emcc and
# Emscripten's SDL2 port via -s USE_SDL=2), this board module will be
# executed.  At that point:
#   - lcd_bus.SDLBus / sdl_display.SDLDisplay are the same drivers used by the
#     linux.py board module; Emscripten maps SDL2 calls to a <canvas> element.
#   - Mouse / touch events from the browser are forwarded to LVGL via the SDL
#     pointer driver already present in lvgl_micropython.
#   - No audio or camera hardware is available; those managers are skipped.
#
# To serve the resulting .wasm / .mjs / index.html files a web server must
# include the following headers so SharedArrayBuffer (needed for pthreads) is
# allowed:
#   Cross-Origin-Opener-Policy: same-origin
#   Cross-Origin-Embedder-Policy: require-corp

import sys

print(f"webassembly.py: sys.platform={sys.platform}")

# ── Display ──────────────────────────────────────────────────────────────────
# Same resolution as the Waveshare ESP32-S3-Touch-LCD-2 and Fri3d 2026 badge.
TFT_HOR_RES = 320
TFT_VER_RES = 240

try:
    import lcd_bus
    import lvgl as lv
    import sdl_display

    import mpos.ui

    bus = lcd_bus.SDLBus(flags=0)
    buf1 = bus.allocate_framebuffer(TFT_HOR_RES * TFT_VER_RES * 2, 0)

    mpos.ui.main_display = sdl_display.SDLDisplay(
        data_bus=bus,
        display_width=TFT_HOR_RES,
        display_height=TFT_VER_RES,
        frame_buffer1=buf1,
        color_space=lv.COLOR_FORMAT.RGB565,
    )
    mpos.ui.main_display.init()

    # ── Pointer input (browser mouse / touch → SDL → LVGL) ──────────────────
    import sdl_pointer
    from mpos import InputManager

    mouse = sdl_pointer.SDLPointer()
    InputManager.register_indev(mouse)

    print("webassembly.py: display and pointer initialised via SDL2 (Emscripten)")

except ImportError as e:
    # LVGL / SDL not available in plain MicroPython WASM builds.
    print(f"webassembly.py: LVGL/SDL not available ({e}); display skipped")
    print("webassembly.py: MicroPython WASM REPL is available via the browser console")

# ── Battery (simulated) ──────────────────────────────────────────────────────
try:
    from mpos import BatteryManager

    def _adc_to_voltage(adc_value):
        return adc_value * (3.3 / 4095) * 2

    BatteryManager.init_adc(999, _adc_to_voltage)
except Exception as e:
    print(f"webassembly.py: BatteryManager init skipped: {e}")

# ── Audio: not available in the browser without additional Web Audio API ─────
# AudioManager is intentionally not initialised here.

# ── Camera: not available (no V4L2, getUserMedia requires JS glue code) ──────
# CameraManager is intentionally not initialised here.

# ── Network: handled entirely by the browser; no network module needed ───────
# WifiService already detects the absence of the "network" MicroPython module
# and falls back to desktop/simulated mode automatically.

print("webassembly.py finished")
