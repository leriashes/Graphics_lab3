import cv2
import numpy as np
import time
import math

WIND_X = 1600
WIND_Y = 800

class Object:
    def __init__ (self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def get_coords (self):
        return [self.x, self.y, self.z]
    
    def change_coord (self, coord, val, increment = False):
        if (coord == "x"):
            if (increment == True):
                self.x += val            
            else:
                self.x = val

        if (coord == "y"):
            if (increment == True):
                self.y += val            
            else:
                self.y = val

        if (coord == "z"):
            if (increment == True):
                self.z += val            
            else:
                self.z = val

    def draw (self, canvas):
        pass

class Light(Object):
    def __init__ (self, x_, y_, z_, color_ = (255, 255, 255)):
        Object.__init__ (self, x_, y_, z_)
        
        self.color = color_
    
    def get_color (self):
        return self.color
    
    def draw (self, canvas):
        canvas.draw_3d_circle ([self.x, self.y, self.z], 10, (250, 250, 250))
        #pass

class Surface (Object):
    def __init__ (self, x_, y_, z_):
        Object.__init__ (self, x_, y_, z_)
    
    def draw (self, canvas):
        self.render (canvas)
    
    def render (self, canvas):
        pass
    
    def iterate_elements (self):
        pass
    
    def calc_element_lightening (self):
        pass
    
    def _dotproduct (self, v1, v2):
        return sum ((a * b) for a, b in zip (v1, v2))

    def _length(self, v):
        return math.sqrt (self._dotproduct (v, v))

    def _cos (self, v1, v2):
        return self._dotproduct (v1, v2) / ((self._length (v1) * self._length (v2)) + 0.00001)
    
    def _subtr (self, v1, v2):
        return [a - b for a, b in zip (v1, v2)]

    def _add (self, v1, v2):
        return [a + b for a, b in zip (v1, v2)]
    
    def _norm_3_points (self, p1, p2, p3):
        u = self._subtr (p2, p1)
        v = self._subtr (p3, p1)
        
        n = [u [1] * v [2] - u [2] * v [1],
             u [2] * v [0] - u [0] * v [2],
             u [0] * v [1] - u [1] * v [0]]
        
        return n
    
    def _rotate_2d_vec (self, x, y, radians):
        xx = x * math.cos(radians) + y * math.sin(radians)
        yy = -x * math.sin(radians) + y * math.cos(radians)

        return xx, yy

class Sphere_pix(Surface):
    def __init__ (self, x_, y_, z_, r_, color_ = (100, 100, 255)):
        Object.__init__ (self, x_, y_, z_)
        
        self.r     = r_
        self.color = color_
    
    def iterate_elements (self):
        result = []
        
        for i in range (int (- self.r / self.z), int (self.r / self.z)):
            for j in range (int (- self.r / self.z), int (self.r / self.z)):
                dist_2d = self._length ((i, j))
                
                if (dist_2d < self.r / self.z):
                    n = []
                    
                    n.append (i * self.z)
                    n.append (j * self.z)
                    n.append (math.sqrt ((self.r)**2 - (dist_2d * self.z)**2))
                    
                    result.append ((self.x / self.z + i, self.y / self.z + j, n))
        
        return result
    
    def draw (self, canvas, emitter):
        self.render (canvas, emitter)
    
    def render (self, canvas, emitter):
        for i, j, n in self.iterate_elements ():
            pix_color = self.calc_lightening (n, emitter)
            
            canvas [int (j), int (i), :] = pix_color
    
    def calc_lightening (self, n, emitter):
        p_vec = [self.x + n [0], self.y + n [1], self.z + n [2]]
        vec = self._subtr (emitter.get_coords (), p_vec)
        cos = max (self._cos (n, vec), 0)
        
        result = [int (channel * cos) for channel in self.color]
        
        return result

class Triangle(Surface):
    def __init__ (self, p1_, p2_, p3_, color_ = (100, 100, 255)):
        Object.__init__ (self, p1_ [0], p1_ [1], p1_ [2])
        
        self.p1 = p1_
        self.p2 = p2_
        self.p3 = p3_
        
        self.color = color_
    
    def draw (self, canvas, emitter, shift = [0, 0, 0]):
        self.render (canvas, emitter, shift)
    
    def render (self, canvas, emitter, shift = [0, 0, 0]):
        n = self._norm_3_points (self.p1, self.p2, self.p3)
        
        tr_color = self.calc_lightening (n, emitter)
        
        #canvas.draw_3d_line (self.p1, self.p2, self.color)
        #canvas.draw_3d_line (self.p1, self.p3, self.color)
        #canvas.draw_3d_line (self.p2, self.p3, self.color)
        
        canvas.draw_3d_triangle (self._add (self.p1, shift),
                                 self._add (self.p2, shift),
                                 self._add (self.p3, shift),
                                 tr_color)
    
    def calc_lightening (self, n, emitter):
        p_vec = [self.x + n [0], self.y + n [1], self.z + n [2]]
        vec = self._subtr (emitter.get_coords (), p_vec)
        cos = max (self._cos (n, vec), 0)
        #print (cos)
        
        result = [int (channel * cos) for channel in self.color]
        
        return result

class Triangle_mesh (Surface):
    def __init__ (self, x_, y_, z_):
        Surface.__init__ (self, x_, y_, z_)
        
        self.triangles = []
        #self.generate_triangulation ()
        
    def generate_triangulation (self):
        sample_triangle = Triangle ((0.6, 0.7, 1.2), (0.5, 0.7, 1.25), (-0.5, -0.9, 1.3))
        
        self.triangles.append (sample_triangle)
        
    def draw (self, canvas, emitter):
        for tr in sorted (self.triangles, key = lambda tr: tr.p1 [2]):
            tr.draw (canvas, emitter, [self.x, self.y, self.z])

    #obj.rotate ("z", rot_step, increment = True)
    
    def rotate (self, axis, step, increment = True):
        for tr in self.triangles:
            for p in [tr.p1, tr.p2, tr.p3]:
                #l = math.sqrt (p [1]**2 + p [2]**2)
                #cos = self._cos ([0, 1], [p [1], p [2]])
                #angle = math.acos (cos)
                #new_angle = angle + step
                #p [1] = l * math.sin (new_angle)
                #p [2] = l * math.cos (new_angle)
                
                p [1], p [2] = self._rotate_2d_vec (p [1], p [2],
                    step)
    
class Sphere_tri (Triangle_mesh):
    def __init__ (self, x_, y_, z_, r_, color_, stripes_num_):
        Triangle_mesh.__init__ (self, x_, y_, z_)
        
        self.r     = r_
        self.color = color_
        
        self.stripes_num = stripes_num_
        self.generate_triangulation ()
        
    def generate_triangulation (self):
        h_step = 2 * self.r / self.stripes_num
        angle_step = 2 * math.pi / self.stripes_num
        
        for i in range (self.stripes_num):
            for j in range (self.stripes_num):
                stripe_rad_curr = math.sqrt (self.r**2 - \
                    (- self.r + i * h_step)**2)
                
                stripe_rad_next = math.sqrt (self.r**2 - \
                    (- self.r + (i + 1) * h_step)**2)
                
                #stripe_rad_curr = self.r
                #stripe_rad_next = self.r
                
                p1 = [stripe_rad_curr * math.sin (j * angle_step),
                      stripe_rad_curr * math.cos (j * angle_step),
                      - self.r + i * h_step]
                
                p2 = [stripe_rad_curr * math.sin ((j + 1) * angle_step),
                      stripe_rad_curr * math.cos ((j + 1) * angle_step),
                      - self.r + i * h_step]
                
                p3 = [stripe_rad_next * math.sin (j * angle_step),
                      stripe_rad_next * math.cos (j * angle_step),
                      - self.r + (i + 1) * h_step]
                
                p4 = [stripe_rad_next * math.sin ((j + 1) * angle_step),
                      stripe_rad_next * math.cos ((j + 1) * angle_step),
                      - self.r + (i + 1) * h_step]
                
                p5 = list (p2)
                p6 = list (p3)
                
                new_triangle_1 = Triangle (p1, p3, p2,\
                    color_ = self.color)
                new_triangle_2 = Triangle (p4, p5, p6, \
                    color_ = self.color)

                if (i > 0):
                    self.triangles.append (new_triangle_1)
                
                if (i < self.stripes_num - 1):
                    self.triangles.append (new_triangle_2)

class Canvas:
    def __init__ (self, xsz_, ysz_, zsz_, centerx_, centery_):
        self.xsz = xsz_
        self.ysz = ysz_
        self.zsz = zsz_
        self.centerx = centerx_
        self.centery = centery_
        
        self.canvas = np.ones ((WIND_Y, WIND_X, 3), np.uint8) * 55
        
    def get_canvas (self):
        return self.canvas
    
    def refresh (self):
        self.canvas = np.ones ((WIND_Y, WIND_X, 3), np.uint8) * 55
    
    def _transform_point (self, p):
        x = int ((p [0] / p [2] + self.centerx) * WIND_X / self.xsz)
        y = int ((p [1] / p [2] + self.centery) * WIND_Y / self.ysz)
        
        return x, y
    
    def draw_3d_line (self, p1, p2, color, thickness = 1):
        x1, y1 = self._transform_point (p1)
        x2, y2 = self._transform_point (p2)
        
        cv2.line (self.canvas, (x1, y1), (x2, y2), color, thickness)
    
    def draw_3d_triangle (self, p1, p2, p3, color):
        x1, y1 = self._transform_point (p1)
        x2, y2 = self._transform_point (p2)
        x3, y3 = self._transform_point (p3)
        
        contour = np.array ([(x1, y1), (x2, y2), (x3, y3)])
        
        cv2.drawContours (self.canvas, [contour], 0, color, -1)
        
    def draw_3d_circle (self, p, r, color):
        x, y = self._transform_point (p)
        
        cv2.circle (self.canvas, (x, y), int (r / p [2]), color)
    
    #def draw_space_box (self):
        
    def put_text (self, text, x, y, color = (100, 25, 130)):
        cv2.putText (self.canvas, text, (x, y),
            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)


emitter = Light(0.6, 0, 1.5)

# spheres = [Sphere (300, 350, 1, 250),
#            Sphere (500, 450, 1, 150, color_ = (250, 24, 100)),
#            Sphere (650, 250, 1, 100, color_ = (25, 240, 10)),
#            Sphere (750, 150, 1, 100, color_ = (125, 200, 10)),
#            Sphere (850, 345, 1, 100, color_ = (225, 240, 10)),
#            Sphere (950, 125, 1, 100, color_ = (250, 20, 255))]

canvas = Canvas(2, 1, 10, 1, 0)

#objects = [Triangle_mesh (0, 0, 1.5)]

objects = [Sphere_tri (0,0, 1.6, 0.4, (100, 200, 70), 20),
           #Sphere_tri (0.3,   0.1,  1.4, 0.5, (200, 20, 170), 10),
           #Sphere_tri (-0.2,  0.2,    1.3, 0.6, (10, 130, 120), 36)
           ]

to_refresh = True

light_step = 0.2
rot_step   = 0.1

while (True):
    k = cv2.waitKey (50) & 0xFF
    
    if (k != 255):
        to_refresh = True
    
    if (k == ord ('q')):
        break
    
    if (k == ord ('d')):
        emitter.change_coord ("x", light_step, increment = True)

    if (k == ord ('a')):
        emitter.change_coord ("x", -light_step, increment = True)

    if (k == ord ('s')):
        emitter.change_coord ("y", light_step, increment = True)

    if (k == ord ('w')):
        emitter.change_coord ("y", -light_step, increment = True)

    if (k == ord ('r')):
        emitter.change_coord ("z", light_step, increment = True)

    if (k == ord ('f')):
        emitter.change_coord ("z", -light_step, increment = True)
    
    if (k == ord ('t')):
        for obj in objects:
            obj.rotate ("z", rot_step, increment = True)
    
    if (to_refresh == True):
        to_refresh = False
        canvas.refresh ()
        
        #print ("rendering...")
        
        before_time = time.time()
        
        for obj in objects:
            obj.draw(canvas, emitter)
        
        #print ("rendered in ", str (time.time () - before_time) [:6], "seconds")
        
        emitter.draw (canvas)
    
    light_info_str  = "light: " + str (emitter.get_coords ())
    #sphere_info_str = "sphere: " + str (sphere.get_coords ())
    
    canvas.put_text(light_info_str, 20, 30)
    cv2.imshow ("Lab 3", canvas.get_canvas ())

cv2.waitKey(0)
cv2.destroyAllWindows()