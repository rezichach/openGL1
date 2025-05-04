import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
import ctypes


# Menu system class
class MenuSystem:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((800, 600))
        pg.display.set_caption("OpenGL Demo - Menu")
        self.clock = pg.time.Clock()
        self.font_large = pg.font.SysFont('Arial', 48)
        self.font = pg.font.SysFont('Arial', 32)
        self.background_color = (25, 50, 95)  # Dark blue background
        self.button_color = (40, 80, 170)  # Medium blue for buttons
        self.button_hover_color = (70, 120, 230)  # Lighter blue for hover
        self.text_color = (255, 255, 255)  # Keep white text for good contrast
        
    def create_button(self, text, rect, hover=False):
        color = self.button_hover_color if hover else self.button_color
        pg.draw.rect(self.screen, color, rect, border_radius=8)
        pg.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=8)
        text_surface = self.font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def show_controls(self):
        running = True
        controls = [
            "W/S/A/D - Move in X-Z plane",
            "UP/DOWN - Move up/down",
            "T/G - Rotate X axis (pitch)",
            "H/F - Rotate Y axis (yaw)",
            "Y/R - Rotate Z axis (roll)",
            "SPACE - Toggle shadow map view",
            "ESC - Return to menu"
        ]
        
        while running:
            self.screen.fill(self.background_color)
            
            # Title
            title = self.font_large.render("Controls", True, self.text_color)
            title_rect = title.get_rect(center=(400, 60))
            self.screen.blit(title, title_rect)
            
            # Controls list
            for i, control in enumerate(controls):
                text = self.font.render(control, True, self.text_color)
                self.screen.blit(text, (150, 150 + i * 50))
            
            # Back button
            back_rect = pg.Rect(300, 500, 200, 50)
            mouse_pos = pg.mouse.get_pos()
            hover = back_rect.collidepoint(mouse_pos)
            self.create_button("Back", back_rect, hover)
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    return False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if back_rect.collidepoint(event.pos):
                        running = False
            
            pg.display.flip()
            self.clock.tick(60)
        
        return True
    
    def run(self):
        running = True
        
        while running:
            self.screen.fill(self.background_color)
            
            # Title
            title = self.font_large.render("OpenGL Demo", True, self.text_color)
            title_rect = title.get_rect(center=(400, 100))
            self.screen.blit(title, title_rect)
            
            # Buttons
            start_rect = pg.Rect(300, 200, 200, 50)
            controls_rect = pg.Rect(300, 300, 200, 50)
            quit_rect = pg.Rect(300, 400, 200, 50)
            
            mouse_pos = pg.mouse.get_pos()
            start_hover = start_rect.collidepoint(mouse_pos)
            controls_hover = controls_rect.collidepoint(mouse_pos)
            quit_hover = quit_rect.collidepoint(mouse_pos)
            
            self.create_button("Start", start_rect, start_hover)
            self.create_button("Controls", controls_rect, controls_hover)
            self.create_button("Quit", quit_rect, quit_hover)
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if start_rect.collidepoint(event.pos):
                        return True
                    elif controls_rect.collidepoint(event.pos):
                        if not self.show_controls():
                            return False
                    elif quit_rect.collidepoint(event.pos):
                        return False
            
            pg.display.flip()
            self.clock.tick(60)


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
    def __init__(self, position: list[float], eulers: list[float], scale: list[float] = [1.0, 1.0, 1.0]):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)
        self.move_speed = 0.1  # Movement speed per frame
        self.rotation_speed = 2.0  # Rotation speed per frame

    def update(self) -> None:
        # No automatic rotation
        pass
        
    def rotate_x(self, angle) -> None:
        self.eulers[0] += angle
        if self.eulers[0] > 360:
            self.eulers[0] -= 360
        elif self.eulers[0] < 0:
            self.eulers[0] += 360
            
    def rotate_y(self, angle) -> None:
        self.eulers[1] += angle
        if self.eulers[1] > 360:
            self.eulers[1] -= 360
        elif self.eulers[1] < 0:
            self.eulers[1] += 360
    
    def rotate_z(self, angle) -> None:
        self.eulers[2] += angle
        if self.eulers[2] > 360:
            self.eulers[2] -= 360
        elif self.eulers[2] < 0:
            self.eulers[2] += 360
    
    def move(self, direction) -> None:
        # direction should be a normalized vector
        self.position += direction * self.move_speed

    def get_model_transform(self) -> np.ndarray:
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        
        # Apply rotation on all axes
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_x_rotation(
                theta=np.radians(self.eulers[0]),
                dtype=np.float32,
            ),
        )
        
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_y_rotation(
                theta=np.radians(self.eulers[1]),
                dtype=np.float32,
            ),
        )
        
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_z_rotation(
                theta=np.radians(self.eulers[2]),
                dtype=np.float32,
            ),
        )
        
        # Apply translation
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position), dtype=np.float32
            ),
        )
        
        # Apply scale
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_scale(
                scale=np.array(self.scale), dtype=np.float32
            ),
        )
        
        return model_transform


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
        # Don't initialize pygame again, as the menu already did this
        # pg.init()
        # Just set the OpenGL attributes and switch to OpenGL mode
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
        # Use the same size as the menu for consistency
        pg.display.set_mode((800, 600), pg.OPENGL | pg.DOUBLEBUF)
        pg.display.set_caption("OpenGL Demo - Running")

    def _set_up_timer(self) -> None:
        self.clock = pg.time.Clock()

    def _set_up_opengl(self) -> None:
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def _create_assets(self) -> None:
        # Create just one spinning cube in the middle
        self.main_cube = Entity(position=[0, 0, 0], eulers=[0, 0, 0], scale=[0.5, 0.5, 0.5])
        
        # Floor positioned at y=0
        self.floor = Entity(position=[0, -0.5, 0], eulers=[0, 0, 0])
        
        self.cube_mesh = CubeMesh()
        self.floor_mesh = FloorMesh()
        self.quad_mesh = QuadMesh()  # Added quad mesh for debug visualization
        self.wood_texture = Material("openGL1/gfx/wall.png")
        self.floor_texture = Material("openGL1/gfx/Ground.jfif")
        
        # Regular rendering shader
        self.shader = create_shader(
            vertex_filepath="openGL1/shaders/vertex.txt", 
            fragment_filepath="openGL1/shaders/fragment.txt"
        )
        
        # Shadow mapping shaders
        self.depth_shader = create_shader(
            vertex_filepath="openGL1/shaders/depth_vertex.txt", 
            fragment_filepath="openGL1/shaders/depth_fragment.txt"
        )
        
        self.shadow_shader = create_shader(
            vertex_filepath="openGL1/shaders/shadow_vertex.txt", 
            fragment_filepath="openGL1/shaders/shadow_fragment.txt"
        )
        
        # Create debug depth shader for visualizing shadow map
        self.debug_depth_shader = create_shader(
            vertex_filepath="openGL1/shaders/debug_quad_vertex.txt", 
            fragment_filepath="openGL1/shaders/debug_fragment.txt"
        )
        
        self.camera = Camera(
            position=[0, 2, 5],
            target=[0, 0, 0]
        )
        
        # Light positioned at the left side
        self.light = Light(position=[-2.0, 4.0, -1.0])
        
        # Flag to toggle shadow map visualization
        self.show_depth_map = False

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
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=800 / 600, near=0.1, far=100, dtype=np.float32
        )
        
        # Setup regular shader uniform locations
        glUseProgram(self.shader)
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
        glUniform1i(glGetUniformLocation(self.shadow_shader, "diffuseTexture"), 0)
        glUniform1i(glGetUniformLocation(self.shadow_shader, "shadowMap"), 1)
        
        glUniformMatrix4fv(
            glGetUniformLocation(self.shadow_shader, "projection"),
            1,
            GL_FALSE,
            projection_transform,
        )
        
        # Setup debug depth shader uniforms
        glUseProgram(self.debug_depth_shader)
        glUniform1i(glGetUniformLocation(self.debug_depth_shader, "depthMap"), 0)

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
        
        # Debug depth shader locations
        glUseProgram(self.debug_depth_shader)
        self.near_plane_loc = glGetUniformLocation(self.debug_depth_shader, "near_plane")
        self.far_plane_loc = glGetUniformLocation(self.debug_depth_shader, "far_plane")

    def _render_scene_depth(self, shader, model_loc):
        # Render only the main cube for the depth map
        glUniformMatrix4fv(
            model_loc,
            1,
            GL_FALSE,
            self.main_cube.get_model_transform(),
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
        # Render main cube with texture
        glUniformMatrix4fv(
            model_loc,
            1,
            GL_FALSE,
            self.main_cube.get_model_transform(),
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
        keys = {}  # Dictionary to track which keys are currently pressed
        
        while running:
            # Process events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        # Toggle shadow map visualization with spacebar
                        self.show_depth_map = not self.show_depth_map
                    elif event.key == pg.K_ESCAPE:
                        # Return to menu when ESC is pressed
                        running = False
                    # Track key presses
                    keys[event.key] = True
                elif event.type == pg.KEYUP:
                    # Stop tracking released keys
                    keys[event.key] = False
            
            # Handle continuous key presses for movement (X-Z plane)
            if keys.get(pg.K_w, False):
                self.main_cube.move(np.array([0, 0, -1]))  # Forward (negative Z)
            if keys.get(pg.K_s, False):
                self.main_cube.move(np.array([0, 0, 1]))   # Backward (positive Z)
            if keys.get(pg.K_a, False):
                self.main_cube.move(np.array([-1, 0, 0]))  # Left (negative X)
            if keys.get(pg.K_d, False):
                self.main_cube.move(np.array([1, 0, 0]))   # Right (positive X)
            
            # Handle up/down movement with arrow keys
            if keys.get(pg.K_UP, False):
                self.main_cube.move(np.array([0, 1, 0]))   # Up (positive Y)
            if keys.get(pg.K_DOWN, False):
                self.main_cube.move(np.array([0, -1, 0]))  # Down (negative Y)
            
            # Handle pitch (X-axis rotation) with T/G
            if keys.get(pg.K_t, False):
                self.main_cube.rotate_x(self.main_cube.rotation_speed)  # Pitch up (look up)
            if keys.get(pg.K_g, False):
                self.main_cube.rotate_x(-self.main_cube.rotation_speed)  # Pitch down (look down)
                
            # Handle yaw (Y-axis rotation) with H/F
            if keys.get(pg.K_h, False):
                self.main_cube.rotate_y(self.main_cube.rotation_speed)  # Yaw right (turn right)
            if keys.get(pg.K_f, False):
                self.main_cube.rotate_y(-self.main_cube.rotation_speed)  # Yaw left (turn left)
                
            # Handle roll (Z-axis rotation) with Y/R
            if keys.get(pg.K_y, False):
                self.main_cube.rotate_z(self.main_cube.rotation_speed)  # Roll right
            if keys.get(pg.K_r, False):
                self.main_cube.rotate_z(-self.main_cube.rotation_speed)  # Roll left
            
            # 1. First render pass: render depth map from light's perspective
            light_view = self.light.get_view_matrix()
            
            # Set up near and far planes for the light's perspective
            near_plane = 1.0
            far_plane = 30.0  # Increased from 7.5 to cover the entire floor
            
            # Create light space matrix
            self.light_projection = pyrr.matrix44.create_orthogonal_projection_matrix(
                left=-10, right=10, bottom=-10, top=10, near=near_plane, far=far_plane, dtype=np.float32
            )
            
            # Fix matrix multiplication order - view first, then projection
            light_space_matrix = pyrr.matrix44.multiply(
                light_view, self.light_projection
            )
            
            glViewport(0, 0, self.SHADOW_WIDTH, self.SHADOW_HEIGHT)
            glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_FBO)
            glClear(GL_DEPTH_BUFFER_BIT)

            # Disable face culling entirely for depth map generation
            glDisable(GL_CULL_FACE)
            glEnable(GL_POLYGON_OFFSET_FILL)
            glPolygonOffset(1.0, 1.0)  # Adjusted to balanced values
            
            # Use depth shader to create shadow map
            glUseProgram(self.depth_shader)
            glUniformMatrix4fv(
                self.lightSpaceMatrixLocation,
                1,
                GL_FALSE,
                light_space_matrix,
            )
            
            self._render_scene_depth(self.depth_shader, self.depthModelLocation)

            glDisable(GL_POLYGON_OFFSET_FILL)
            glDisable(GL_CULL_FACE)
            
            # 2. Second render pass: render scene as normal with shadow mapping
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glViewport(0, 0, 800, 600)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # If showing depth map for debugging
            if self.show_depth_map:
                glUseProgram(self.debug_depth_shader)
                glUniform1f(self.near_plane_loc, near_plane)
                glUniform1f(self.far_plane_loc, far_plane)
                
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, self.depth_map)
                
                self.quad_mesh.arm_for_drawing()
                self.quad_mesh.draw()
            else:
                # Normal rendering with shadows
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
        self.quad_mesh.destroy()  # Added quad mesh destruction
        self.wood_texture.destroy()
        self.floor_texture.destroy()
        glDeleteProgram(self.shader)
        glDeleteProgram(self.depth_shader)
        glDeleteProgram(self.shadow_shader)
        glDeleteProgram(self.debug_depth_shader)  # Added debug shader destruction
        glDeleteFramebuffers(1, [self.depth_map_FBO])
        glDeleteTextures(1, [self.depth_map])
        # Don't quit pygame here - we'll do that after returning from the app
        # pg.quit()


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
        -25,0,-25,   0,1,0,   0,0,
         25,0,-25,   0,1,0,   25,0,
         25,0, 25,   0,1,0,   25,25,
         25,0, 25,   0,1,0,   25,25,
        -25,0, 25,   0,1,0,   0,25,
        -25,0,-25,   0,1,0,   0,0,
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


class QuadMesh:
    def __init__(self):
        verts = (
        #  x,  y,  z,    u, v
        -1.0,  1.0, 0.0, 0.0, 1.0,
        -1.0, -1.0, 0.0, 0.0, 0.0,
         1.0,  1.0, 0.0, 1.0, 1.0,
         1.0, -1.0, 0.0, 1.0, 0.0,
        )
        self.vertex_count = 4
        verts = np.array(verts, dtype=np.float32)

        stride = 5*4  # 5 floats per vertex, 4 bytes per float
        self.vao = glGenVertexArrays(1); glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)  # position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)  # uv
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

    def arm_for_drawing(self): glBindVertexArray(self.vao)
    def draw(self):            glDrawArrays(GL_TRIANGLE_STRIP, 0, self.vertex_count)
    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,)); glDeleteBuffers(1,(self.vbo,))


# Main application execution
if __name__ == "__main__":
    # Show menu first
    menu = MenuSystem()
    start_app = menu.run()
    
    if start_app:
        # Initialize and run OpenGL application
        my_app = App()
        my_app.run()
        my_app.quit()
    
    # Always quit pygame at the end
    pg.quit()