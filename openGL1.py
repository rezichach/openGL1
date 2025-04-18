import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D
import numpy as np
import ctypes 
from OpenGL.GL.shaders import compileProgram,compileShader

class app:
    


    def __init__(self):
        #initialize python
        pg.init()
        pg.font.init()
        pg.display.set_mode((640,480),pg.OPENGL|pg.DOUBLEBUF)
        self.clock=pg.time.Clock()
        #colosrs
        glClearColor(0.1, 0.1, 0.1, 1.0)
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)
        self.triangle = Triangle()
        
        self.offset_x = 0.0
        self.offset_y = 0.0

        self.mainLoop()
     
    def createShader(self, vertexFilepath, fragmentFilepath):
        with open(vertexFilepath, 'r') as f:
            vertex_src = f.read()

        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.read()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader   
    
    # def draw_buttons_gl(self):
    #     """
    #     Draw six 30×30‑pixel rectangles in the top‑right corner using OpenGL.
    #     We push / pop the fixed‑function matrices so the 3‑D projection is untouched.
    #     """
    #     glMatrixMode(GL_PROJECTION)
    #     glPushMatrix()
    #     glLoadIdentity()
    #     gluOrtho2D(0, 640, 480, 0)          # 0,0 = top‑left   (width, height)

    #     glMatrixMode(GL_MODELVIEW)
    #     glPushMatrix()
    #     glLoadIdentity()

    #     glDisable(GL_DEPTH_TEST)            # always on top
    #     glEnable(GL_BLEND)
    #     glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    #     labels = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']
    #     self.ui_quads = []                  # store rects for hit‑testing later

    #     for i, label in enumerate(labels):
    #         row, col = divmod(i, 2)         # 3 rows, 2 cols
    #         x = 540 + col * 40              # 640‑100
    #         y =  20 + row * 40
    #         w = h = 30

    #         # save quad corners for clicks
    #         self.ui_quads.append((label, (x, y, x + w, y + h)))

    #         # light‑grey button body
    #         glColor4f(0.8, 0.8, 0.8, 0.9)
    #         glBegin(GL_QUADS)
    #         glVertex2f(x    , y    )
    #         glVertex2f(x+w  , y    )
    #         glVertex2f(x+w  , y+h  )
    #         glVertex2f(x    , y+h  )
    #         glEnd()

    #         # thin dark border
    #         glColor4f(0.1, 0.1, 0.1, 1.0)
    #         glLineWidth(1)
    #         glBegin(GL_LINE_LOOP)
    #         glVertex2f(x    , y    )
    #         glVertex2f(x+w  , y    )
    #         glVertex2f(x+w  , y+h  )
    #         glVertex2f(x    , y+h  )
    #         glEnd()

    #     # ── restore previous matrices ──
    #     glPopMatrix()            # MODELVIEW
    #     glMatrixMode(GL_PROJECTION)
    #     glPopMatrix()
    #     glMatrixMode(GL_MODELVIEW)
    #     glEnable(GL_DEPTH_TEST)  # re‑enable for next 3‑D pass
    
    def mainLoop(self):
        running = True
        while(running):
            #events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
             #refresh
                    
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT]:
                self.offset_x -= 0.01
            if keys[pg.K_RIGHT]:
                self.offset_x += 0.01
            if keys[pg.K_UP]:
                self.offset_y += 0.01
            if keys[pg.K_DOWN]:
                self.offset_y -= 0.01

            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.shader)

            offset_location = glGetUniformLocation(self.shader, "offset")
            glUniform3f(offset_location, self.offset_x, self.offset_y, 0.0)

            glBindVertexArray(self.triangle.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count)

            pg.display.flip()
            
            #timing
            self.clock.tick(60)
        self.quit()
            
    def quit(self):
        self.triangle.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Triangle:
    def __init__(self):
        self.vertices = np.array([
        [ -0.5, -0.5,  0.0, 0.0, 0.0, 0.0],
        [ 0.5, -0.5, 0.0, 0.0, 1.0, 0.0],
        [0.0, 0.5, 0.0, 0.0, 0.0, 1.0]], dtype=np.float32)
        
        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
 

if __name__ == "__main__":
    app()
            
