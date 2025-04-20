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
        
        #colors
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        self.triangle = Triangle()
        self.wall_texture = Material("textures/wall.png")    
        
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

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)
            self.wall_texture.use()

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
        self.wall_texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Triangle:
    def __init__(self):
        # Format: position (3 floats), color (3 floats), texture coords (2 floats)
        self.vertices = np.array([
            # Position         # Color          # Texture coordinates
            [-0.5, -0.5, 0.0,  1.0, 1.0, 1.0,   0.0, 0.0],  # Bottom left
            [ 0.5, -0.5, 0.0,  1.0, 1.0, 1.0,   1.0, 0.0],  # Bottom right
            [ 0.0,  0.5, 0.0,  1.0, 1.0, 1.0,   0.5, 1.0]   # Top
        ], dtype=np.float32)
        
        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        # Color attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        
        # Texture coordinate attribute
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))  

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
 
class Material:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image = pg.image.load(filepath).convert()
        image_width, image_height = image.get_rect().size
        image_data = pg.image.tostring(image, "RGBA")

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

if __name__ == "__main__":
    app()
            
