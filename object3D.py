from turtle import color
import pygame as pg
from matrixFunctions import *

class Object3D:
    def __init__(self, render, color):
        self.render = render
        self.color = color

        self.start = False
        self.x = 1
        self.y = 1
        self.z = 1
        self.t = 0


        self.moving_speed = 0.02
        self.rotation_speed = 0.01

        self.vertexes = []

        self.edges = []
        self.faces = []

        self.movement_flag, self.draw_vertexes = True, True
        self.label = ''

    def addFaces(self, face_list):
        for node_list in face_list:
            num_nodes = len(node_list)
            if all((node < len(self.vertexes) for node in node_list)):
                self.faces.append([node_list, np.array(self.color, np.uint8)])
                self.addEdges([(node_list[n - 1], node_list[n]) for n in range(num_nodes)])

    def addEdges(self, edge_list):
        self.edges += [edge for edge in edge_list if edge not in self.edges]

    def remap(self, val, low1, high1, low2, high2):
        return low2 + (val - low1) * (high2 - low2) / (high1 - low1)

    def draw(self):
        if (self.start):
            if (self.t < 30000):
                time_n = max(self.remap(self.t, 0, 30000, 0, 1), 0)
                s = (1 - time_n)
                s *= s
                s *= s
                s = 1 - s
                nx = 1 + self.remap(s, 0, 1, 0, self.x - 1)
                self.x /= nx
                ny = 1 + self.remap(s, 0, 1, 0, self.y - 1)
                self.y /= ny
                nz = 1 + self.remap(s, 0, 1, 0, self.z - 1)
                self.z /= nz
                self.dilatate((nx, ny, nz))
                self.t += 1
            else:
                self.start = False

        self.screen_projection()


    def control(self):
        key = pg.key.get_pressed()

        if key[pg.K_i]:
            self.rotate_x((self.rotation_speed))
        if key[pg.K_k]:
            self.rotate_x((-self.rotation_speed))
        if key[pg.K_j]:
            self.rotate_y((self.rotation_speed))
        if key[pg.K_l]:
            self.rotate_y((-self.rotation_speed))
        if key[pg.K_u]:
            self.rotate_z((self.rotation_speed))
        if key[pg.K_o]:
            self.rotate_z((-self.rotation_speed))


    def movement(self):
        if self.movement_flag:
            self.rotate_y(pg.time.get_ticks() % 0.005)

    def screen_projection(self):
        vertexes = self.vertexes @ self.render.camera.camera_matrix()
        vertexes = vertexes @ self.render.projection.projection_matrix
        vertexes /= vertexes[:, -1].reshape(-1, 1)
        vertexes[(vertexes > 3) | (vertexes < -3)] = 0
        vertexes = vertexes @ self.render.projection.to_screen_matrix
        vertexes = vertexes[:, :3]

        for face in self.faces:
            color = face[1]
            towards_us = np.dot(np.cross((vertexes[face[0][1]] - vertexes[face[0][0]])[:3], (vertexes[face[0][2]] - vertexes[face[0][0]])[:3]), np.array([0, 0, 1]))
                    
            #отображение только тех граней, которые обращены к камере
            if towards_us > 0:
                normal = np.cross((np.array(self.vertexes[face[0][1]]) - np.array(self.vertexes[face[0][0]]))[:3], (np.array(self.vertexes[face[0][2]]) - np.array(self.vertexes[face[0][0]]))[:3])
                cosTheta = np.dot(normal, np.array([1, 2, -1])) / np.linalg.norm(normal) / np.linalg.norm(np.array([1, 2, -1]))
             
                if cosTheta <= 0 or cosTheta >= math.pi / 2:
                    shade = 0.2 * color
                else:
                    shade = (cosTheta * 0.8 + 0.2) * color
                pg.draw.polygon(self.render.screen, shade, [(vertexes[node][0], vertexes[node][1]) for node in face[0]], 0)
             
                
    def translate(self, pos):
        self.vertexes = self.vertexes @ translate(pos)

    def dilatate(self, coefs):
        self.vertexes = self.vertexes @ dilatate(coefs)

    def scale(self, scale_to):
        self.vertexes = self.vertexes @ scale(scale_to)

    def rotate_x(self, angle):
        self.vertexes = self.vertexes @ rotate_x(angle)

    def rotate_y(self, angle):
        self.vertexes = self.vertexes @ rotate_y(angle)

    def rotate_z(self, angle):
        self.vertexes = self.vertexes @ rotate_z(angle)
