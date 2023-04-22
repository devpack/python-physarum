import time, collections
import moderngl as mgl

# ----------------------------------------------------------------------------------------------------------------------

FULLSCREEN    = 0
SCREEN_WIDTH  = 1920
SCREEN_HEIGHT = 1080
FONT_SIZE     = 32
MAX_FPS       = 60

RENDER_DEBUG  = 0 # directly plot the particles (not using the texture)

XGROUPSIZE = 32
YGROUPSIZE = 1
ZGROUPSIZE = 1

NB_BODY       = 20000
SPEED_RATE    = 0.0002
TURN_SPEED    = 0.062
FADE_RATE     = 0.0005
DIFFUSE_RATE  = 0.1
SENSOR_ANGLE  = 60.0
SENSOR_DIST   = 30.0
SENSOR_SIZE   = 1
SENSOR_WEIGHT = 1.0
RANDOM_DIRECTION_STRENGTH = 0.05

COLOR         = (0.3, 0.5, 1.0)

# ----------------------------------------------------------------------------------------------------------------------

# drawing mode
#MODE = mgl.LINE_STRIP
MODE = mgl.POINTS
#MODE = mgl.TRIANGLES

# ----------------------------------------------------------------------------------------------------------------------

# camera
CAM_POS = (0, 0, 20)
FOV = 50
NEAR = 0.1
FAR = 2000
SPEED = 0.01
SENSITIVITY = 0.07

GRAB_MOUSE = False

# ----------------------------------------------------------------------------------------------------------------------

class FPSCounter:
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        t1 = time.perf_counter()
        dt = t1 - self.time
        self.time = t1
        self.frame_times.append(dt)

    def get_fps(self):
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return len(self.frame_times) / sum(self.frame_times)
