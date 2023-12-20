import pygame as pg
from matrixFunctions import *

class Camera:
    def __init__(self, render, position):
        self.render = render
        self.position = np.array([*position, 1.0])
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])
        self.h_fov = math.pi / 3
        self.v_fov = self.h_fov * (render.HEIGHT / render.WIDTH)
        self.near_plane = 0.1
        self.far_plane = 100
        self.moving_speed = 0.2
    

    def control(self):
        key = pg.key.get_pressed()
        if key[pg.K_a]:
            self.translate((-self.moving_speed, 0, 0))
        if key[pg.K_d]:
            self.translate((self.moving_speed, 0, 0))
        if key[pg.K_w]:
            self.translate((0, 0, self.moving_speed))
        if key[pg.K_s]:
            self.translate((0, 0, -self.moving_speed))
        if key[pg.K_q]:
            self.translate((0, -self.moving_speed, 0))
        if key[pg.K_e]:
            self.translate((0, self.moving_speed, 0))

        if key[pg.K_LEFT]:
            self.camera_yaw(-self.moving_speed / 100)
        if key[pg.K_RIGHT]:
            self.camera_yaw(self.moving_speed / 100)
        if key[pg.K_UP]:
            self.camera_pitch(self.moving_speed / 100)
        if key[pg.K_DOWN]:
            self.camera_pitch(-self.moving_speed / 100)

    def camera_pitch(self, angle):
        rotate = rotate_x(angle)
        self.forward = self.forward @ rotate
        self.right = self.right @ rotate
        self.up = self.up @ rotate

    def camera_yaw(self, angle):
        rotate = rotate_y(angle)
        self.forward = self.forward @ rotate
        self.right = self.right @ rotate
        self.up = self.up @ rotate

    def translate(self, pos):
        self.position = self.position @ translate(pos)

    def translate_matrix(self):
        x, y, z, w = self.position

        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [-x, -y, -z, 1]
        ])
    
    def rotate_matrix(self):
        rx, ry, rz, w = self.right
        fx, fy, fz, w = self.forward
        ux, uy, uz, w = self.up

        return np.array([
            [rx, ux, fx, 0],
            [ry, uy, fy, 0],
            [rz, uz, fz, 0],
            [0, 0, 0, 1]
        ])
    
    def camera_matrix(self):
        return self.translate_matrix() @ self.rotate_matrix()