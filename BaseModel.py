# imports all the OpenGL libraries
from OpenGL.GL import *

#Imports all the necessary files
from matutils import *

from material import Material

from mesh import Mesh

from shaders import *
from texture import Texture

class BaseModel:
    '''
    Base class for all models, inherit from this to create new models
    '''

    def __init__(self, scene, M=poseMatrix(), mesh=Mesh(), color=[1., 1., 1.], primitive=GL_TRIANGLES, visible=True):
        '''
        Initialises the model data
        :param scene: the scene object
        :param M: the model matrix
        :param mesh: the mesh object
        :param color: the color of the model
        :param primitive: the primitive to use for drawing
        :param visible: whether the model is visible or not
        '''

        print('+ Initializing {}'.format(self.__class__.__name__))

        # if this flag is set to False, the model is not rendered and therefore not visible
        self.visible = visible

        # store the scene reference 
        self.scene = scene

        # store the type of primitive to draw 
        self.primitive = primitive

        # store the object's color (used if no texture is provided)
        self.color = color

        # store the shader program for rendering this model
        self.shader = None

        # store the mesh data
        self.mesh = mesh
        # checks if there is a exactly one texture
        if self.mesh.textures == 1:
            # if there is exactly one texture, add 'T-REX_NORMAL_4k.bmp' as an additional texture
            self.mesh.textures.append(Texture('T-REX_NORMAL_4k.bmp'))

        self.name = self.mesh.name

        # dictionary of VBOs
        self.vbos = {}

        # dictionary of attributes
        self.attributes = {}

        # store the position of the model in the scene
        self.M = M

        # store the identifier of the newly created VAO in self.vao
        self.vao = glGenVertexArrays(1)

        # this buffer will be used to store indices, if using shared vertex representation
        self.index_buffer = None

    def initialise_vbo(self, name, data):
        '''
        Initialises a VBO for the given attribute name and data array
        :param name: the name of the attribute
        :param data: the data array
        '''

        # outputs a message to the console if the function is called
        print('Initialising VBO for attribute {}'.format(name))

        # check if the data array is None
        if data is None:
            # if the data array is None, output a warning message to the console
            print('(W) Warning in {}.bind_attribute(): Data array for attribute {} is None!'.format(
                self.__class__.__name__, name))
            return

        # map the attribute name to its corresponding VBO index
        self.attributes[name] = len(self.vbos)
        
        # store the generated buffer ID in self.vbos under 'name'
        self.vbos[name] = glGenBuffers(1)

        # bind the buffer with ID self.vbos[name] to the GL_ARRAY_BUFFER target
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[name])

        # enable the attribute
        glEnableVertexAttribArray(self.attributes[name])

        # configures how OpenGL interprets vertex data
        glVertexAttribPointer(index=self.attributes[name], size=data.shape[1], type=GL_FLOAT, normalized=False,
                              stride=0, pointer=None)

        # sets the data into the buffer array
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)

    def bind_shader(self, shader):
        '''
        If a new shader is bound, we need to re-link it to ensure attributes are correctly linked.
        :param shader: the shader program to use for rendering this model
        '''

        # if the shader is not None and the shader name is not the same as the current shader name
        if self.shader is None or self.shader.name is not shader:
            # if the shader is a string
            if isinstance(shader, str):
                # create a new shader object
                self.shader = PhongShader(shader)
            else:
                # otherwise, set the shader to the passed shader
                self.shader = shader

            # bind all attributes and compile the shader
            self.shader.compile(self.attributes)

    def bind(self):
        '''
        This method stores the vertex data in a Vertex Buffer Object (VBO) that can be uploaded
        to the GPU at render time.
        '''

        # bind the VAO to retrieve all buffers and rendering context
        glBindVertexArray(self.vao)

        # if the mesh has no vertices, output a warning message to the console
        if self.mesh.vertices is None:
            print('(W) Warning in {}.bind(): No vertex array!'.format(self.__class__.__name__))

        # initialise vertex position VBO and link to shader program attribute
        self.initialise_vbo('position', self.mesh.vertices)
        self.initialise_vbo('normal', self.mesh.normals)
        self.initialise_vbo('color', self.mesh.colors)
        self.initialise_vbo('texCoord', self.mesh.textureCoords)
        self.initialise_vbo('tangent', self.mesh.tangents)
        self.initialise_vbo('binormal', self.mesh.binormals)

        # if indices are provided, put them in a buffer too
        if self.mesh.faces is not None:
            self.index_buffer = glGenBuffers(1)

            # bind the buffer named self.index_buffer to the GL_ELEMENT_ARRAY_BUFFER target
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            # creates a new data store for the currently bound buffer object
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.faces, GL_STATIC_DRAW)

        # unbind the VAO and VBO to avoid side effects
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, Mp=poseMatrix()):
        '''
        Renders the model using the provided shader program and model matrix
        :param Mp: the model matrix to use for rendering
        '''

        if self.visible:
            if self.mesh.vertices is None:
                print('(W) Warning in {}.draw(): No vertex array!'.format(self.__class__.__name__))

            # bind the Vertex Array Object so that all buffers are bound correctly and following operations affect them
            glBindVertexArray(self.vao)

            # setup the shader program and provide it the Model, View and Projection matrices to use
            # for rendering this model
            self.shader.bind(
                model=self,
                M=np.matmul(Mp, self.M)
            )
            # iterate over textures in self.mesh.textures
            for unit, tex in enumerate(self.mesh.textures):
                # activate the texture unit for current texture
                glActiveTexture(GL_TEXTURE0 + unit)
                # bind the texture to the current texture unit
                tex.bind()

            # check whether the data is stored as vertex array or index array
            if self.mesh.faces is not None:
                # draw the data in the buffer using the index array
                glDrawElements(self.primitive, self.mesh.faces.flatten().shape[0], GL_UNSIGNED_INT, None )
            else:
                # draw the data in the buffer using the vertex array ordering only.
                glDrawArrays(self.primitive, 0, self.mesh.vertices.shape[0])

            # unbind the shader to avoid side effects
            glBindVertexArray(0)

    def vbo__del__(self):
        '''
        Releases all the VBO objects when finished
        '''
        for vbo in self.vbos.items():
            glDeleteBuffers(1, vbo)

        glDeleteVertexArrays(1,self.vao.tolist())


class DrawModelFromMesh(BaseModel):
    '''
    Base class for all models, inherit from this to create new models
    '''

    def __init__(self, scene, M, mesh, name=None, shader=None, visible=True):
        '''
        Initialises the model data
        '''
        
        # call the constructor of the parent class
        BaseModel.__init__(self, scene=scene, M=M, mesh=mesh, visible=visible)
        
        if name is not None:
            self.name = name

        # if the number of columns in the index array is 3
        if self.mesh.faces.shape[1] == 3:
            # set the primitive to GL_TRIANGLES
            self.primitive = GL_TRIANGLES

        # if the number of columns in the index array is 4
        elif self.mesh.faces.shape[1] == 4:
            # set the primitive to GL_QUADS
            self.primitive = GL_QUADS

        else:
            # otherwise, output an error message to the console
            print('(E) Error in DrawModelFromObjFile.__init__(): index array must have 3 (triangles) or 4 (quads) columns, found {}!'.format(self.indices.shape[1]))

        # bind the model
        self.bind()

        # bind the shader if it is not None
        if shader is not None:
            self.bind_shader(shader)
