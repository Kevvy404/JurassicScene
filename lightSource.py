# imports the library numpy as np
import numpy as np

class LightSource:
    '''
    Class for a light source in a 3D scene. It contains properties for ambient, diffuse, 
    and specular illumination, and can be positioned within the scene.
    '''
    def __init__(self, scene, position=[2.,2.,0.], Ia=[0.2,0.2,0.2], Id=[0.9,0.9,0.9], Is=[1.0,1.0,1.0]):
        '''
        Initialise the light source with its properties.
        :param scene: The scene to which the light belongs.
        :param position: The 3D position of the light source.
        :param Ia: Ambient illumination (RGB).
        :param Id: Diffuse illumination (RGB).
        :param Is: Specular illumination (RGB).
        '''

        # set the position as a numpy array
        self.position = np.array(position, 'f')
        self.Ia = Ia  # ambient illumination 
        self.Id = Id  # diffuse illumination
        self.Is = Is  # specular illumination

    def update(self, position=None):
        '''
        Update the position of the light source
        :param position: New position for the light source
        '''

        # update position if provided
        if position is not None:
            self.position = position
