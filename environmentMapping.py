# imports all the necessary files
from BaseModel import *

from mesh import *

from OpenGL.GL.framebufferobjects import *

from cubeMap import CubeMap

from shaders import *

from framebuffer import Framebuffer


class EnvironmentShader(BaseShaderProgram):
    '''
    Shader program for environment mapping.
    '''

    def __init__(self, name='environment', map=None):
        '''
        Initialises the shader program
        :param name: The name of the shader program
        :param map: The cube map texture to use
        '''

        # initialise base shader program
        BaseShaderProgram.__init__(self, name=name)
        # add shader uniform variables
        self.add_uniform('sampler_cube')
        # view-Model matrix
        self.add_uniform('VM')
        # inverse transpose of View-Model matrix
        self.add_uniform('VMiT')
        # transpose of View matrix
        self.add_uniform('VT')
        # cube map texture
        self.map = map

    def bind(self, model, M):
        '''
        Binds the shader program and sets uniforms
        :param model: The model to apply the shader to
        :param M: Model matrix
        '''    

        # use this shader program
        glUseProgram(self.program)
        # bind the cube map texture if available
        if self.map is not None:
            unit = len(model.mesh.textures)
            glActiveTexture(GL_TEXTURE0)
            self.map.bind()
            self.uniforms['sampler_cube'].bind(0)

        # retrieve matrices from the model and scene
        P = model.scene.P  # projection matrix
        V = model.scene.camera.V  # view matrix

        # set uniform variables for the shader
        self.uniforms['PVM'].bind(np.matmul(P, np.matmul(V, M)))  # projection-View-Model matrix
        self.uniforms['VM'].bind(np.matmul(V, M))  # view model matrix
        self.uniforms['VMiT'].bind(np.linalg.inv(np.matmul(V, M))[:3, :3].transpose())  # inverse transpose of VM
        self.uniforms['VT'].bind(V.transpose()[:3, :3])  # transpose of View matrix

class EnvironmentMappingTexture(CubeMap):
    '''
    A class for environment mapping textures
    '''
    def __init__(self, width=200, height=200):
        '''
        Initialises an environment mapping texture.
        :param width: Width of each face of the cube map.
        :param height: Height of each face of the cube map.
        '''

        # initialises the base CubeMap class
        CubeMap.__init__(self)
        
        # flag to indicate if environment map is complete
        self.done = False

        # dimensions of each cube face
        self.width = width
        self.height = height

        # dictionary of framebuffer objects for each face of the cube map
        self.fbos = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: Framebuffer(),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: Framebuffer()
        }

        t = 0.0
        # translation and rotation matrices for each cube face view
        self.views = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: np.matmul(translationMatrix([0, 0, t]), rotationMatrixY(-np.pi/2.0)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: np.matmul(translationMatrix([0, 0, t]), rotationMatrixY(+np.pi/2.0)),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: np.matmul(translationMatrix([0, 0, t]), rotationMatrixX(+np.pi/2.0)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: np.matmul(translationMatrix([0, 0, t]), rotationMatrixX(-np.pi/2.0)),
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: np.matmul(translationMatrix([0, 0, t]), rotationMatrixY(-np.pi)),
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: translationMatrix([0, 0, t]),
        }

        # set up the texture for each face
        # bind this cube map for operations
        self.bind()
        for (face, fbo) in self.fbos.items():
            # create texture image for each face
            glTexImage2D(face, 0, self.format, width, height, 0, self.format, self.type, None)
            # prepares framebuffer
            fbo.prepare(self, face)

        # unbind the cube map
        self.unbind()

    def update(self, scene):
        '''
        Updates the environment map with the current scene.
        :param scene: The scene to be reflected in the environment map.
        '''

        # skip update if already done
        if self.done:
            return

        # bind the cube map for update
        self.bind()

        # store the original projection matrix
        Pscene = scene.P

        # set a new projection matrix for environment mapping
        scene.P = frustumMatrix(-1.0, +1.0, -1.0, +1.0, 1.0, 20.0)

        # set viewport size for rendering each cube face
        glViewport(0, 0, self.width, self.height)


        # render each cube face
        for (face, fbo) in self.fbos.items():
            # bind the framebuffer for the current face
            fbo.bind()
            # set the view matrix for the current face
            scene.camera.V = self.views[face]
            # draw the scene reflections
            scene.draw_reflections()

            # update camera settings
            scene.camera.update()
            # unbind the framebuffer
            fbo.unbind()

        # resets the viewport to the original size
        glViewport(0, 0, scene.window_size[0], scene.window_size[1])
        # restore the original projection matrix
        scene.P = Pscene        
        # unbind the cube map
        self.unbind()