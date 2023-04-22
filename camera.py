import glm

# -----------------------------------------------------------------------------------------------------------

class Camera:
    
    def __init__(self, app, fov=50, near=0.1, far=100, position=(0, 0, 4), speed=0.009, sensivity=0.07, yaw=-90, pitch=0):
        self.app = app

        self.fov = fov 
        self.near = near 
        self.far = far 
        self.position = glm.vec3(position)
        self.aspect_ratio = app.screen_width / app.screen_height

        self.speed = speed
        self.sensivity = sensivity

        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.yaw = yaw
        self.pitch = pitch

        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()

    def rotate(self, mouse_dx, mouse_dy):
        self.yaw += mouse_dx * self.sensivity
        self.pitch -= mouse_dy * self.sensivity
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def update(self, mouse_dx, mouse_dy, forward, backward, left, right, up, down):
        self.move(forward, backward, left, right, up, down)
        self.rotate(mouse_dx, mouse_dy)

        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self, forward, backward, left, right, up, down):
        velocity = self.speed * self.app.delta_time

        if forward:
            self.position += self.forward * velocity
        if backward:
            self.position -= self.forward * velocity
        if right:
            self.position += self.right * velocity
        if left:
            self.position -= self.right * velocity
        if up:
            self.position -= self.up * velocity
        if down:
            self.position += self.up * velocity

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)
        #return glm.lookAt(self.position, glm.vec3(0), self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.near, self.far)




















