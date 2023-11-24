# imports all the necessary files
from texture import *
from mesh import Mesh
from BaseModel import DrawModelFromMesh
from matutils import *
from shaders import *


class FlattenedCubeShader(BaseShaderProgram):
    '''
    Base class for rendering the flattened cube
    '''
    def __init__(self):
        '''
        Initialises the shader program
        '''

        # calls the constructor of the base class and gives it a name
        BaseShaderProgram.__init__(self, name='flattened_cube')

        # adds a uniform variable to the shader program
        self.add_uniform('sampler_cube')


class FlattenCubeMap(DrawModelFromMesh):
    '''
    A class for drawing the cube faces flattened on the screen#
    '''

    def __init__(self, scene, cube=None):
        '''
        Initialises the flattened cubemap
        :param scene: The scene object
        :param cube: The cube map texture to display
        '''

        # set the vertices of the flattened cube
        vertices = np.array([

            [-2.0, -1.0, 0.0],  # left face
            [-2.0,  0.0, 0.0],  
            [-1.0, -1.0, 0.0],  
            [-1.0,  0.0, 0.0],  

            [-1.0, -1.0, 0.0],  # front face
            [-1.0, 0.0, 0.0],   
            [0.0, -1.0, 0.0],  
            [0.0, 0.0, 0.0],    

            [0.0, -1.0, 0.0],   # right face, bottom left
            [0.0, 0.0, 0.0],    
            [1.0, -1.0, 0.0],   
            [1.0, 0.0, 0.0],    

            [1.0, -1.0, 0.0],   # back face
            [1.0, 0.0, 0.0],    
            [2.0, -1.0, 0.0],   
            [2.0, 0.0, 0.0],    

            [-1.0, 0.0, 0.0],   # top face
            [-1.0, 1.0, 0.0],   
            [0.0, 0.0, 0.0],   
            [0.0, 1.0, 0.0],   

            [-1.0, -2.0, 0.0],  # bottom face
            [-1.0, -1.0, 0.0],  
            [0.0, -2.0, 0.0],   
            [0.0, -1.0, 0.0],   

        ], dtype='f')/2  # scale down the cube size by half

        # set the faces of the flattened cube
        faces = np.zeros(vertices.shape, dtype=np.uint32)
        # Loop through each square face of the cube
        for f in range(int(vertices.shape[0]/4)):

            # First triangle of the face
            # Vertices: bottom left, top right, top left
            faces[2 * f + 0, :] = [0 + f*4, 3 + f*4, 1 + f*4]

            # Second triangle of the face
            # Vertices: bottom left, bottom right, top right
            faces[2 * f + 1, :] = [0 + f*4, 2 + f*4, 3 + f*4]

        # set the texture coordinates to index in the cube map texture
        textureCoords = np.array([
            [-1, +1, -1],  # left face
            [-1, -1, -1],
            [-1, +1, +1],
            [-1, -1, +1],

            [-1, +1, +1],  # front face
            [-1, -1, +1],
            [+1, +1, +1],
            [+1, -1, +1],

            [+1, +1, +1],  # right 
            [+1, -1, +1],
            [+1, +1, -1],
            [+1, -1, -1],

            [+1, +1, -1],  # back face 
            [+1, -1, -1],
            [-1, +1, -1],
            [-1, -1, -1],

            [-1, -1, +1],  # top face 
            [-1, -1, -1],
            [+1, -1, +1],
            [+1, -1, -1],

            [-1, +1, -1],  # bottom face 
            [-1, +1, +1],
            [+1, +1, -1],
            [+1, +1, +1],

        # use 32-bit floating point numbers for each element
        ], dtype='f')

        # create a mesh from the object
        mesh = Mesh(vertices=vertices, faces=faces, textureCoords=textureCoords)

        # add the CubeMap object if provided
        if cube is not None:
            mesh.textures.append(cube)

        # finishes initialising the mesh
        DrawModelFromMesh.__init__(self, scene=scene, M=poseMatrix(position=[0,0,+1]), mesh=mesh, shader=FlattenedCubeShader(), visible=False)

    def set(self, cube):
        '''
        Set the cube map to display
        :param cube: A CubeMap texture
        '''
        self.mesh.textures = [cube]


class CubeMap(Texture):
    '''
    Class for handling a cube map texture
    '''
    def __init__(self, name=None, files=None, wrap=GL_CLAMP_TO_EDGE, sample=GL_LINEAR, format=GL_RGBA, type=GL_UNSIGNED_BYTE):
        '''
        Initialise the cube map texture object
        :param name: The name of the folder containing the cube map images
        :param files: A dictionary containing the file name for each face.
        :param wrap: The wrap mode for the texture
        :param sample: The sampling mode for the texture
        :param format: The format of the texture
        :param type: The type of the texture
        '''
        self.name = name
        self.format = format
        self.type = type
        self.wrap = wrap
        self.sample = sample
        self.target = GL_TEXTURE_CUBE_MAP # we set the texture target as a cube map

        # this dictionary contains the file name for each face
        self.files = {
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X: 'left.bmp',
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z: 'back.bmp',
            GL_TEXTURE_CUBE_MAP_POSITIVE_X: 'right.bmp',
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: 'front.bmp',
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y: 'bottom.bmp',
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: 'top.bmp',
        }

        # generate the texture
        self.textureid = glGenTextures(1)

        # bind the texture
        self.bind()

        # if name is provided, load cube faces from images on disk
        if name is not None:
            self.set(name, files)

        # set what happens for texture coordinates outside [0,1]
        glTexParameteri(self.target, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_T, wrap)

        # set how sampling from the texture is done.
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, sample)
        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, sample)

        # unbind the texture
        self.unbind()

    def set(self, name, files=None):
        '''
        Load the cube's faces from images on the disk
        :param name: The folder in which the images are.
        :param files: A dictionary containing the file name for each face.
        '''
        
        # if files is provided, use it instead of the default
        if files is not None:
            self.files = files

        # iterate over key-value pairs in the 'files' dictionary
        for (key, value) in self.files.items():
            # print a message indicating which texture is being loaded
            print('Loading texture: texture/{}/{}'.format(name, value))

            # create an ImageWrapper object for the image file
            # the path is constructed using 'name' and 'value'
            img = ImageWrapper('{}/{}'.format(name, value))


            # convert the python image object to a plain byte array for passsing to OpenGL
            glTexImage2D(key, 0, self.format, img.width(), img.height(), 0, self.format, self.type, img.data(self.format))

    def update(self, scene):
        '''
        Used to update the texture, does not do anything at the moment, but could be extended for the environment mapping.
        '''
        pass

