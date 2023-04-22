from config import *
import pygame as pg
import numpy as np
import moderngl as mgl
import glm, math
import pywavefront
import random, copy

# -----------------------------------------------------------------------------------------------------------

class Bodies:

    def __init__(self, app, program):
        self.app = app
        self.ctx = app.ctx

        self.program = program

        self.m_model = glm.mat4()

        self.set_uniform(self.program, "m_model", self.m_model)
        self.set_uniform(self.program, "m_proj",  self.app.camera.m_proj)
        self.set_uniform(self.program, "m_view",  self.app.camera.m_view)

        # Body
        # {
        #    vec4 pos;  // x, y, z, w
        #    vec4 dat; // angle, ID, nop, nop
        # };

        particles_array = self.get_particles()
        self.ssbo_in    = self.ctx.buffer(data    = particles_array)

        self.vao        = self.ctx.vertex_array(self.program, [(self.ssbo_in, '4f 4x4', 'in_position')])

    def set_uniform(self, program, u_name, u_value):
        try:
            program[u_name].write(u_value)
        except KeyError:
            pass

    def update(self):
        self.set_uniform(self.program, "m_model", self.m_model)
        self.set_uniform(self.program, "m_view", self.app.camera.m_view)

    def render(self):
        self.vao.render(mgl.POINTS)

    def destroy(self):
        self.ssbo_in.release()
        self.vao.release()

    def get_particles(self):

        # Body
        # {
        #    vec4 pos;  // x, y, z, w
        #    vec4 dat;  // angle, ID, nop, nop
        # };

        bodies = []
        for i in range(0, NB_BODY):
            #posx, posy, posz = self.pickball(1.0)
            posx, posy, posz = 0.0, 0.0, 0.0
            posx, posy, posz = random.uniform(-0.99, 0.99), random.uniform(-0.99, 0.99), random.uniform(-0.99, 0.99)

            bodies.extend((posx, posy, posz, 1.0))

            bodies.extend((random.uniform(0.0, 6.2831853), i, 0.0, 0.0))

        vertex_data = np.asarray(bodies, dtype='f4') #vertex_data = np.array(bodies, dtype='f4')

        #print("vertex_data=", vertex_data)

        return vertex_data

    def pickball(self, radius):

        while True:
            rsq = 0.0

            posx = random.uniform(-1.0, 1.0)
            posy = random.uniform(-1.0, 1.0)
            posz = random.uniform(-1.0, 1.0)

            rsq = (posx * posx) + (posy * posy) + (posz * posz)

            if rsq <= 1.0:
                break

        posx = posx * radius
        posy = posy * radius
        posz = posz * radius

        return posx, posy, posz

