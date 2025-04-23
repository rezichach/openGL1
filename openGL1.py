import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
import ctypes


def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    with open(vertex_filepath, "r") as f:
        vertex_src = f.read()

    with open(fragment_filepath, "r") as f:
        fragment_src = f.read()

    shader = compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER),
    )
    return shader


class Entity:
    def __init__(self, position: list[float], eulers: list[float]):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

    def update(self) -> None:
        self.eulers[1] += 0.25
        if self.eulers[1] > 360:
            self.eulers[1] -= 360

    def get_model_transform(self) -> np.ndarray:
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_axis_rotation(
                axis=[0, 1, 0],
                theta=np.radians(self.eulers[1]),
                dtype=np.float32,
            ),
        )
        return pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position), dtype=np.float32
            ),
        )


class Light:
    def __init__(self, position):
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.look_at = np.array([0, 0, 0], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
    
    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(
            eye=self.position,
            target=self.look_at,
            up=self.up,
            dtype=np.float32
        )


class Camera:
    def __init__(self, position, target):
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)

    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(
            eye=self.position,
            target=self.target,
            up=self.up,
            dtype=np.float32
        )


class App:
    def __init__(self):
        self._set_up_pygame()
        self._set_up_timer()
        self._set_up_opengl()
        self._create_assets()
        self._set_up_shadow_map()
        self._set_onetime_uniforms()
        self._get_uniform_locations()

    def _set_up_pygame(self) -> None:
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
        pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)

    def _set_up_timer(self) -> None:
        self.clock = pg.time.Clock()

    def _set_up_opengl(self) -> None:
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def _create_assets(self) -> None:
        self.cube = Entity(position=[0, 0.0, -2], eulers=[0, 0, 0])
        self.floor = Entity(position=[0, -0.5, 0], eulers=[0, 0, 0])
        self.cube_mesh = CubeMesh()
        self.floor_mesh = FloorMesh()
        self.wood_texture = Material("gfx/wall.png")
        self.floor_texture = Material("gfx/Ground.jfif")
        
        # Regular rendering shader
        self.shader = create_shader(
            vertex_filepath="shaders/vertex.txt", 
            fragment_filepath="shaders/fragment.txt"
        )
        
        # Shadow mapping shaders
        self.depth_shader = create_shader(
            vertex_filepath="shaders/depth_vertex.txt", 
            fragment_filepath="shaders/depth_fragment.txt"
        )
        
        self.shadow_shader = create_shader(
            vertex_filepath="shaders/shadow_vertex.txt", 
            fragment_filepath="shaders/shadow_fragment.txt"
        )
        
        self.camera = Camera(
            position=[0, 2, 5],
            target=[0, 0, -2]
        )
        
        # Add a light source for shadow casting
        self.light = Light(position=[2, 4, 2])

    def _set_up_shadow_map(self) -> None:
        # Shadow map resolution
        self.SHADOW_WIDTH = 1024
        self.SHADOW_HEIGHT = 1024
        
        # Create a framebuffer object for the depth map
        self.depth_map_FBO = glGenFramebuffers(1)
        
        # Create a 2D texture for the depth map
        self.depth_map = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_map)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, 
            self.SHADOW_WIDTH, self.SHADOW_HEIGHT, 0, 
            GL_DEPTH_COMPONENT, GL_FLOAT, None
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        border_color = [1.0, 1.0, 1.0, 1.0]
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border_color)
        
        # Attach the depth texture to the framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_FBO)
        glFramebufferTexture2D(
            GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth_map, 0
        )
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        # Light space projection matrix
        self.light_projection = pyrr.matrix44.create_orthogonal_projection_matrix(
            left=-10, right=10, bottom=-10, top=10, near=1.0, far=20.0, dtype=np.float32
        )

    def _set_onetime_uniforms(self) -> None:
        # Setup normal shader uniforms
        glUseProgram(self.shadow_shader)
        glUniform1i(glGetUniformLocation(self.shadow_shader, "diffuseTexture"), 0)
        glUniform1i(glGetUniformLocation(self.shadow_shader, "shadowMap"),      1)
        
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=640 / 480, near=0.1, far=100, dtype=np.float32
        )
        
        self.projectionMatrixLocation = glGetUniformLocation(self.shader, "projection")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        
        glUniformMatrix4fv(
            self.projectionMatrixLocation,
            1,
            GL_FALSE,
            projection_transform,
        )
        
        # Setup shadow shader uniforms
        glUseProgram(self.shadow_shader)
        glUniform1i(glGetUniformLocation(self.shadow_shader, "imageTexture"), 0)
        glUniform1i(glGetUniformLocation(self.shadow_shader, "shadowMap"), 1)
        
        glUniformMatrix4fv(
            glGetUniformLocation(self.shadow_shader, "projection"),
            1,
            GL_FALSE,
            projection_transform,
        )

    def _get_uniform_locations(self) -> None:
        # Regular shader locations
        glUseProgram(self.shader)
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        
        # Depth shader locations
        glUseProgram(self.depth_shader)
        self.depthModelLocation = glGetUniformLocation(self.depth_shader, "model")
        self.lightSpaceMatrixLocation = glGetUniformLocation(self.depth_shader, "lightSpaceMatrix")
        
        # Shadow shader locations
        glUseProgram(self.shadow_shader)
        self.shadowModelLocation = glGetUniformLocation(self.shadow_shader, "model")
        self.shadowViewLocation = glGetUniformLocation(self.shadow_shader, "view")
        self.lightPosLocation = glGetUniformLocation(self.shadow_shader, "lightPos")
        self.viewPosLocation = glGetUniformLocation(self.shadow_shader, "viewPos")
        self.lightSpaceMatrixLocShadow = glGetUniformLocation(self.shadow_shader, "lightSpaceMatrix")

    def _render_scene_depth(self, shader, model_loc):
        # Render cube for the depth map
        glUniformMatrix4fv(
            model_loc,
            1,
            GL_FALSE,
            self.cube.get_model_transform(),
        )
        self.cube_mesh.arm_for_drawing()
        self.cube_mesh.draw()
        
        # Render floor for the depth map
        glUniformMatrix4fv(
            model_loc,
            1,
            GL_FALSE,
            self.floor.get_model_transform(),
        )
        self.floor_mesh.arm_for_drawing()
        self.floor_mesh.draw()

    def _render_scene(self, shader, model_loc):
        # Render cube with texture
        glUniformMatrix4fv(
            model_loc,
            1,
            GL_FALSE,
            self.cube.get_model_transform(),
        )
        self.wood_texture.use()
        self.cube_mesh.arm_for_drawing()
        self.cube_mesh.draw()
        
        # Render floor with texture
        glUniformMatrix4fv(
            model_loc,
            1,
            GL_FALSE,
            self.floor.get_model_transform(),
        )
        self.floor_texture.use()
        self.floor_mesh.arm_for_drawing()
        self.floor_mesh.draw()

    def run(self) -> None:
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            self.cube.update()
            
            # 1. First render pass: render depth map from light's perspective
            light_view = self.light.get_view_matrix()
            light_space_matrix = pyrr.matrix44.multiply(
                self.light_projection, light_view
            )
            
            glViewport(0, 0, self.SHADOW_WIDTH, self.SHADOW_HEIGHT)
            glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_FBO)
            glClear(GL_DEPTH_BUFFER_BIT)

            glEnable(GL_POLYGON_OFFSET_FILL)          # ⬅️ add
            glPolygonOffset(2.0, 4.0) 
            
            # Use depth shader to create shadow map
            glUseProgram(self.depth_shader)
            glUniformMatrix4fv(
                self.lightSpaceMatrixLocation,
                1,
                GL_FALSE,
                light_space_matrix,
            )
            
            self._render_scene_depth(self.depth_shader, self.depthModelLocation)

            glDisable(GL_POLYGON_OFFSET_FILL)         # ⬅️ add
            
            # 2. Second render pass: render scene as normal with shadow mapping
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glViewport(0, 0, 640, 480)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            view_matrix = self.camera.get_view_matrix()
            
            # Use shadow shader for rendering with shadows
            glUseProgram(self.shadow_shader)
            
            # Set all the uniforms needed for shadow rendering
            glUniformMatrix4fv(
                self.shadowViewLocation,
                1,
                GL_FALSE,
                view_matrix,
            )
            
            glUniform3fv(
                self.lightPosLocation,
                1,
                self.light.position,
            )
            
            glUniform3fv(
                self.viewPosLocation,
                1,
                self.camera.position,
            )
            
            glUniformMatrix4fv(
                self.lightSpaceMatrixLocShadow,
                1,
                GL_FALSE,
                light_space_matrix,
            )
            
            # Bind shadow map texture
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.depth_map)

            # Render the scene with shadows
            self._render_scene(self.shadow_shader, self.shadowModelLocation)

            pg.display.flip()
            self.clock.tick(60)

    def quit(self) -> None:
        self.cube_mesh.destroy()
        self.floor_mesh.destroy()
        self.wood_texture.destroy()
        self.floor_texture.destroy()
        glDeleteProgram(self.shader)
        glDeleteProgram(self.depth_shader)
        glDeleteProgram(self.shadow_shader)
        glDeleteFramebuffers(1, [self.depth_map_FBO])
        glDeleteTextures(1, [self.depth_map])
        pg.quit()


# ───────────── CubeMesh with normals (pos 3 ‖ normal 3 ‖ uv 2) ─────────────
class CubeMesh:
    def __init__(self):
        verts = (
        #  x,  y,  z,    nx, ny, nz,    u, v          ← 8 floats/vertex
        # front face  (-Z)
        -0.5,-0.5,-0.5,   0, 0,-1,      0,0,
         0.5,-0.5,-0.5,   0, 0,-1,      1,0,
         0.5, 0.5,-0.5,   0, 0,-1,      1,1,
         0.5, 0.5,-0.5,   0, 0,-1,      1,1,
        -0.5, 0.5,-0.5,   0, 0,-1,      0,1,
        -0.5,-0.5,-0.5,   0, 0,-1,      0,0,
        # back face   (+Z)
        -0.5,-0.5, 0.5,   0, 0, 1,      0,0,
         0.5,-0.5, 0.5,   0, 0, 1,      1,0,
         0.5, 0.5, 0.5,   0, 0, 1,      1,1,
         0.5, 0.5, 0.5,   0, 0, 1,      1,1,
        -0.5, 0.5, 0.5,   0, 0, 1,      0,1,
        -0.5,-0.5, 0.5,   0, 0, 1,      0,0,
        # left face   (-X)
        -0.5, 0.5, 0.5,  -1, 0, 0,      1,0,
        -0.5, 0.5,-0.5,  -1, 0, 0,      1,1,
        -0.5,-0.5,-0.5,  -1, 0, 0,      0,1,
        -0.5,-0.5,-0.5,  -1, 0, 0,      0,1,
        -0.5,-0.5, 0.5,  -1, 0, 0,      0,0,
        -0.5, 0.5, 0.5,  -1, 0, 0,      1,0,
        # right face  (+X)
         0.5, 0.5, 0.5,   1, 0, 0,      1,0,
         0.5, 0.5,-0.5,   1, 0, 0,      1,1,
         0.5,-0.5,-0.5,   1, 0, 0,      0,1,
         0.5,-0.5,-0.5,   1, 0, 0,      0,1,
         0.5,-0.5, 0.5,   1, 0, 0,      0,0,
         0.5, 0.5, 0.5,   1, 0, 0,      1,0,
        # bottom face (-Y)
        -0.5,-0.5,-0.5,   0,-1, 0,      0,1,
         0.5,-0.5,-0.5,   0,-1, 0,      1,1,
         0.5,-0.5, 0.5,   0,-1, 0,      1,0,
         0.5,-0.5, 0.5,   0,-1, 0,      1,0,
        -0.5,-0.5, 0.5,   0,-1, 0,      0,0,
        -0.5,-0.5,-0.5,   0,-1, 0,      0,1,
        # top face    (+Y)
        -0.5, 0.5,-0.5,   0, 1, 0,      0,1,
         0.5, 0.5,-0.5,   0, 1, 0,      1,1,
         0.5, 0.5, 0.5,   0, 1, 0,      1,0,
         0.5, 0.5, 0.5,   0, 1, 0,      1,0,
        -0.5, 0.5, 0.5,   0, 1, 0,      0,0,
        -0.5, 0.5,-0.5,   0, 1, 0,      0,1,
        )
        self.vertex_count = len(verts)//8
        verts = np.array(verts, dtype=np.float32)

        stride = 8*4
        self.vao = glGenVertexArrays(1); glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)  # position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)  # normal
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)  # uv
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))

    def arm_for_drawing(self): glBindVertexArray(self.vao)
    def draw(self):            glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,)); glDeleteBuffers(1,(self.vbo,))

# ───────────── FloorMesh with normals ─────────────
class FloorMesh:
    def __init__(self):
        verts = (
        #  x, y,  z,    nx, ny, nz,    u, v
        -5,0,-5,   0,1,0,   0,0,
         5,0,-5,   0,1,0,   5,0,
         5,0, 5,   0,1,0,   5,5,
         5,0, 5,   0,1,0,   5,5,
        -5,0, 5,   0,1,0,   0,5,
        -5,0,-5,   0,1,0,   0,0,
        )
        self.vertex_count = len(verts)//8
        verts = np.array(verts, dtype=np.float32)

        stride = 8*4
        self.vao = glGenVertexArrays(1); glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))

    def arm_for_drawing(self): glBindVertexArray(self.vao)
    def draw(self):            glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,)); glDeleteBuffers(1,(self.vbo,))


class Material:
    def __init__(self, filepath: str):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert_alpha()
        image_width, image_height = image.get_rect().size
        img_data = pg.image.tostring(image, "RGBA", True)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            image_width,
            image_height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img_data,
        )
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))


my_app = App()
my_app.run()
my_app.quit()

