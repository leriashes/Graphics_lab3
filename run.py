import pygame as pg
from object3D import *
from sphere import *
from camera import *
from projection import *

class Renderer:
    def __init__(self):
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = 1200, 700
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.create_objects()

    def create_objects(self):
        self.camera = Camera(self, [0, 0, -20])
        self.projection = Projection(self)
        self.object = Sphere(0, 0, 0, 5, self, res=60)

    def draw(self):
        self.screen.fill(pg.Color('dimgrey'))
        self.object.draw()

    def run(self):
        while True:
            self.draw()
            self.object.control()
            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            pg.display.set_caption('Лабораторная работа 3')
            pg.display.flip()
            self.clock.tick(self.FPS)


if __name__ == '__main__':
    app = Renderer()
    app.run()