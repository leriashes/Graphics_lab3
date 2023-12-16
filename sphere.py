import numpy as np
import object3D


class Sphere(object3D.Object3D):
    def __init__(self, x, y, z, r, render, res=10):
        super().__init__(render)

        latitudes = [n * np.pi / res for n in range(1, res)] #вычисление "широт" (без полюсных)
        longitudes = [n * 2 * np.pi / res for n in range(res)] #вычисление "долгот"
        
        self.vertexes = [[x + r * np.sin(n) * np.sin(m), y - r * np.cos(m), z - r * np.cos(n) * np.sin(m), 1] for m in latitudes for n in longitudes]
        
        num_nodes = (res - 1) * res

        #добавление граней (кроме полюсных)
        num_nodes = res*(res-1)
        self.addFaces([(m + n, 
                               (m + res) % num_nodes + n,
                               (m + res) % res**2 + (n + 1) % res,
                               m + (n + 1) % res) 
                               for n in range(res) for m in range(0, num_nodes - res, res)])

        #добавление полюсов и треугольных граней вокруг них
        self.vertexes.append((x, y + r, z, 1))
        self.vertexes.append((x, y - r, z, 1))
        self.addFaces([(n, (n + 1) % res, num_nodes + 1) for n in range(res)])
        start_node = num_nodes - res
        self.addFaces([(num_nodes, start_node + (n + 1) % res, start_node + n) for n in range(res)])


