# imports the matutils file 
from matutils import *

class Camera:
    '''
    A class to represent a camera in 3D space.
    '''

    def __init__(self):
        '''
        A constructor for the Camera class.
        '''
        self.V = np.identity(4)
        # azimuth angle
        self.phi = 0.
        # zenith angle               
        self.psi = 0.
        # distance of the camera to the centre point               
        self.distance = 5. 
        # position of the centre       
        self.center = [0., 0., 0.]
        # calculate the view matrix  
        self.update()               

    def update(self):
        '''
        A function to update the camera view matrix from parameters.
        '''
        # calculate the translation matrix for the view center
        T0 = translationMatrix(self.center)

        # calculate the rotation matrix from the angles phi and psi angles.
        R = np.matmul(rotationMatrixX(self.psi), rotationMatrixY(self.phi))

        # calculate translation for the camera distance to the center point
        T = translationMatrix([0., 0., -self.distance])

        # calculate the view matrix
        self.V = np.matmul(np.matmul(T, R), T0)