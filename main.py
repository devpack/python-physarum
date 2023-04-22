import sys, random

import pygame as pg
import numpy as np
import moderngl as mgl
import glm
from array import array

from camera import Camera
from model import *
from config import *
from shader_program import ShaderProgram

# -----------------------------------------------------------------------------------------------------------

class App:

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        self.screen_width = screen_width
        self.screen_height = screen_height

        #
        print("SCREEN WIDTH =", SCREEN_WIDTH)
        print("SCREEN HEIGHT=", SCREEN_HEIGHT)

        print("X LOCAL  GROUPSIZE=", XGROUPSIZE)
        print("Y LOCAL  GROUPSIZE=", YGROUPSIZE)
        print("Z LOCAL  GROUPSIZE=", ZGROUPSIZE)
        print("X GLOBAL GROUPSIZE=", SCREEN_WIDTH // XGROUPSIZE)
        print("Y GLOBAL GROUPSIZE=", SCREEN_HEIGHT // YGROUPSIZE)
        print("Z GLOBAL GROUPSIZE=", 1)

        print("NB_BODY=",NB_BODY)

        #
        self.lastTime = time.time()
        self.currentTime = time.time()

        self.fps = FPSCounter()

        self.mode = MODE
        
        # pygame init
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 6)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg_flags = pg.OPENGL | pg.HWSURFACE | pg.DOUBLEBUF
        if FULLSCREEN:
            pg_flags |= pg.FULLSCREEN

        pg.display.set_mode((self.screen_width, self.screen_height), flags=pg_flags)

        # camera control: keys + mouse
        pg.event.set_grab(GRAB_MOUSE)
        pg.mouse.set_visible(True)
        self.u_scroll = 5.0

        self.forward = False
        self.backward = False
        self.right = False
        self.left = False
        self.up = False
        self.down = False

        self.mouse_x, self.mouse_y = 0, 0
        self.mouse_button_down = False

        # OpenGL context / options
        self.ctx = mgl.create_context()
        
        if self.mode == mgl.POINTS:
            self.ctx.enable_only(mgl.PROGRAM_POINT_SIZE | mgl.BLEND)

        #self.ctx.wireframe = True
        #self.ctx.front_face = 'cw'
        #self.ctx.enable(flags=mgl.DEPTH_TEST)
        #self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        #self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.ctx.enable(flags=mgl.BLEND)

        # time objects
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        self.num_frames = 0

        # quad
        quad = [
            # pos (x, y), uv coords (x, y)
            -1.0, 1.0, 0.0, 1.0,  # tl
            1.0, 1.0, 1.0, 1.0,   # tr
            -1.0, -1.0, 0.0, 0.0, # bl
            1.0, -1.0, 1.0, 0.0,  # br
        ]

        quad_buffer = self.ctx.buffer(data=np.array(quad, dtype='f4'))

        # vs / fs shaders
        self.all_shaders = ShaderProgram(self.ctx)

        self.nbody_program = self.all_shaders.get_program("nbody")
        self.quad_program  = self.all_shaders.get_program("quad")

        # compute shader
        with open(f'shaders/nbody_cs.glsl') as file:
            compute_shader_source = file.read()

        compute_shader_source = compute_shader_source.replace("XGROUPSIZE_VAL", str(XGROUPSIZE)) \
                                                     .replace("YGROUPSIZE_VAL", str(YGROUPSIZE)) \
                                                     .replace("ZGROUPSIZE_VAL", str(ZGROUPSIZE))

        self.compute_shader = self.ctx.compute_shader(compute_shader_source)

        self.set_uniform(self.compute_shader, "SCREEN_WIDTH", self.screen_width)
        self.set_uniform(self.compute_shader, "SCREEN_HEIGHT", self.screen_height)
        self.set_uniform(self.compute_shader, "RENDER_DEBUG", RENDER_DEBUG)
        self.set_uniform(self.compute_shader, "NB_BODY", NB_BODY)
        self.set_uniform(self.compute_shader, "SPEED_RATE", SPEED_RATE)
        self.set_uniform(self.compute_shader, "FADE_RATE", FADE_RATE)
        self.set_uniform(self.compute_shader, "TURN_SPEED", TURN_SPEED)
        self.set_uniform(self.compute_shader, "DIFFUSE_RATE", DIFFUSE_RATE)
        self.set_uniform(self.compute_shader, "SENSOR_ANGLE", SENSOR_ANGLE)
        self.set_uniform(self.compute_shader, "SENSOR_DIST", SENSOR_DIST)
        self.set_uniform(self.compute_shader, "SENSOR_SIZE", SENSOR_SIZE)
        self.set_uniform(self.compute_shader, "SENSOR_WEIGHT", SENSOR_WEIGHT)
        self.set_uniform(self.compute_shader, "COLOR", COLOR)
        self.set_uniform(self.compute_shader, "RANDOM_DIRECTION_STRENGTH", RANDOM_DIRECTION_STRENGTH)

        # Compute Shader uniforms
        try:
            self.compute_shader["out_texture"] = 0
        except:
            pass

        # out texture of compute shader
        self.texture = self.ctx.texture((int(self.screen_width/1), int(self.screen_height/1)), 4)
        self.texture.filter = mgl.NEAREST, mgl.NEAREST
        self.texture.bind_to_image(0, read=False, write=True)

        self.quad_program['tex'] = 0

        self.quad_vao = self.ctx.vertex_array(self.quad_program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

        #
        if 0:
            self.texture = self.ctx.texture((self.screen_width, self.screen_height), 3)
            self.texture.filter = (mgl.NEAREST, mgl.NEAREST)
            self.texture.swizzle = 'BGR'

            self.tex_data = b"\xaa\x33\x33" * self.screen_width * 32
            self.tex_data += b"\x00\x00\x00" * self.screen_width * (self.screen_height-32)
            self.texture.write(self.tex_data)

            self.texture.use(location=0)

        # camera
        self.camera = Camera(self, fov=FOV, near=NEAR, far=FAR, position=CAM_POS, speed=SPEED, sensivity=SENSITIVITY)

        self.bodies = Bodies(self, self.nbody_program)

        self.ctx.clear(color = (0.0, 0.0, 0.0))

    def destroy(self):
        self.all_shaders.destroy()
        self.bodies.destroy()

    def set_uniform(self, program, u_name, u_value):
        try:
            program[u_name] = u_value
        except KeyError:
            pass

    def get_fps(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:
            fps = f"PyGame World FPS: {self.fps.get_fps():3.0f}"
            cam_pos = f"CamPos: {int(self.camera.position.x)}, {int(self.camera.position.y)}, {int(self.camera.position.z)}"
            pg.display.set_caption(fps + " | " + cam_pos)

            self.lastTime = self.currentTime

        self.fps.tick()

    def check_events(self):

        for event in pg.event.get():

            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.destroy()
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.forward = True
                if event.key == pg.K_DOWN:
                    self.backward = True
                if event.key == pg.K_RIGHT:
                    self.right = True
                if event.key == pg.K_LEFT:
                    self.left = True
                if event.key == pg.K_LCTRL:
                    self.up = True
                if event.key == pg.K_LSHIFT:
                    self.down = True
                
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.forward = False
                if event.key == pg.K_DOWN:
                    self.backward = False
                if event.key == pg.K_RIGHT:
                    self.right = False
                if event.key == pg.K_LEFT:
                    self.left = False
                if event.key == pg.K_LCTRL:
                    self.up = False
                if event.key == pg.K_LSHIFT:
                    self.down = False
                    
            if event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_button_down = True

            if event.type == pg.MOUSEBUTTONUP:
                self.mouse_button_down = False

        # mouse camera control
        if self.mouse_button_down:
            mx, my = pg.mouse.get_pos()

            if self.mouse_x:
                self.mouse_dx = self.mouse_x - mx
            else:
                self.mouse_dx = 0

            if self.mouse_y:
                self.mouse_dy = self.mouse_y - my
            else:
                self.mouse_dy = 0

            self.mouse_x = mx
            self.mouse_y = my

        else:
            self.mouse_x = 0
            self.mouse_y = 0
            self.mouse_dx, self.mouse_dy = 0, 0

    def set_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def run(self):

        while True:
            # app.time used for object model motion
            self.set_time()

            # pygame events
            self.check_events()

            self.camera.update(self.mouse_dx, self.mouse_dy, self.forward, self.backward, self.left, self.right, self.up, self.down)

            self.ctx.clear(color=(0.0, 0.0, 0.0))

            self.set_uniform(self.compute_shader, "time", self.time)
            self.set_uniform(self.compute_shader, "delta_time", self.delta_time)

            self.bodies.ssbo_in.bind_to_storage_buffer(0)
            self.texture.bind_to_image(0, read=False, write=True)

            self.compute_shader.run(group_x= self.screen_width//XGROUPSIZE, group_y= self.screen_height//YGROUPSIZE, group_z=1)

            #self.ctx.memory_barrier()

            #outputs = np.frombuffer(self.bodies.ssbo_in.read(), dtype=np.float32)
            #print("outputs", outputs)

            self.texture.use(location=0)
            self.quad_vao.render(mode=mgl.TRIANGLE_STRIP)

            if RENDER_DEBUG:
                self.bodies.update()
                self.bodies.render()

            pg.display.flip()

            self.delta_time = self.clock.tick(MAX_FPS)

            self.get_fps()
            self.num_frames += 1

# -----------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App()
    app.run()

