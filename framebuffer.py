# imports all the OpenGL libraries
from OpenGL.GL import *

class Framebuffer:
    '''
    Class for handling off-screen rendering using a framebuffer object
    This allows rendering directly to a texture
    '''

    def __init__(self, attachment=GL_COLOR_ATTACHMENT0, texture=None):
        '''
        Initialises a new framebuffer object
        :param attachment: The attachment point for the texture (e.g., color, depth)
        :param texture: The texture to which rendering will be directed
        ''' 

        # define the attachment point
        self.attachment = attachment
        # generate a framebuffer object
        self.fbo = glGenFramebuffers(1)

        # prepare the framebuffer with the given texture
        if texture is not None:
            self.prepare(texture)

    def bind(self):
        '''
        Bind this framebuffer for rendering
        '''

        # bind the FBO
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

    def unbind(self):
        '''
        Unbind the framebuffer, reverting to default framebuffer
        '''

        # unbind the FBO
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def prepare(self, texture, target=None, level=0):
        '''
        Prepare the framebuffer by linking it to a texture
        :param texture: The texture to render to
        :param target: The rendering target, defaults to texture's target
        :param level: Mipmap level, usually 0 (the base level)
        '''
        if target is None:
            # default to texture's target
            target = texture.target

        # bind framebuffer for setup
        self.bind()
        # link the texture to the framebuffer
        glFramebufferTexture2D(GL_FRAMEBUFFER, self.attachment, target, texture.textureid, level)

        # special handling for depth attachment
        if self.attachment == GL_DEPTH_ATTACHMENT:
            # no color buffer is drawn
            glDrawBuffer(GL_NONE)
            # no color buffer is read
            glReadBuffer(GL_NONE)

        # unbind the framebuffer
        self.unbind()