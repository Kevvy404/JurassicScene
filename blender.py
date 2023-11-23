# imports the libraries required
import numpy as np

# imports the other files required
from material import Material,MaterialLibrary
from mesh import Mesh

def process_line(line):
	'''
	A function that reads from a Blender3D object file
	'''

	label = None

	# split the line into a list of strings
	fields = line.split()
	# check if the list is empty
	if len(fields) == 0:
		# return None if the list is empty
		return None

	# check if the first element of the list is a hashtag (#)
	if fields[0] == '#':
		# if the first element of the list is a hashtag (#), then the line is a comment
		label = 'comment'
		return (label, fields[1:])

	# check if the first element of the list is a 'v'
	elif fields[0] == 'v':
		# if the first element of the list is a 'v', then the line is a vertex
		label = 'vertex'
		# if the length of the list is not 4, then the line is not a vertex
		if len(fields) != 4:
			# print an error message
			print('(E) Error, 3 entries expected for vertex')
			return None

	# check if the first element of the list is a 'vt'
	elif fields[0] == 'vt':
		# if the first element of the list is a 'vt', then the line is a vertex texture
		label = 'vertex texture'
		# if the length of the list is not 3, then the line is not a vertex texture
		if len(fields) != 3:
			# print an error message
			print('(E) Error, 2 entries expected for vertex texture')
			return None
	
	# check if the first element of the list is a 'vn'
	elif fields[0] == 'vn':
		# if the first element of the list is a 'vn', then the line is a normal
		label = 'normal'
		# if the length of the list is not 4, then the line is not a normal
		if len(fields) != 4:
			# print an error message
			print('(E) Error, 3 entries expected for normal')
			return None

	# check if the first element of the list is a 'mtllib'
	elif fields[0] == 'mtllib':
		# if the first element of the list is a 'mtllib', then the line is a material library
		label = 'material library'
		# if the length of the list is not 2, then the line is not a material library
		if len(fields) != 2:
			# print an error message
			print('(E) Error, material library file name missing')
			# and returns None
			return None
		else:
			# else return the label and the file name
			return (label, fields[1])

	# check if the first element of the list is a 'usemtl'
	elif fields[0] == 'usemtl':
		# if the first element of the list is a 'usemtl', then the line is a material
		label = 'material'
		# if the length of the list is not 2, then the line is not a material
		if len(fields) != 2:
			# print an error message
			print('(E) Error, material file name missing')
			# and returns None
			return None
		else:
			# else return the label and the file name
			return (label, fields[1])

	# check if the first element of the list is a 's'
	elif fields[0] == 's':
		label = 's???'
		return None

	# check if the first element of the list is a 'f'
	elif fields[0] == 'f':
		# if the first element of the list is a 'f', then the line is a face
		label = 'face'
		# if the length of the list is not 4 or 5, then the line is not a face
		if len(fields) != 4 and len(fields) != 5:
			# print an error message
			print('(E) Error, 3 or 4 entries expected for faces\n{}'.format(line))
			return None

		# return a tuple with the label and a list of lists containing parsed vertex data from fields
		return ( label, [ [np.uint32(i) for i in v.split('/')] for v in fields[1:] ] )

	else:
		print('(E) Unknown line: {}'.format(fields))
		return None

	# return a tuple with the label and a list of floating-point numbers converted from fields[1:] 
	return (label, [float(token) for token in fields[1:]])


def load_material_library(file_name):
    '''
    Load materials from a given file and create a material library.
	:param file_name: Name of the material file
	:return: Material library
    '''

	# initialise a new material library
    library = MaterialLibrary()
	# placeholder for the current material being processed
    material = None  

	# print a message for loading the material library
    print('-- Loading material library {}'.format(file_name))  

	# open the material file
    mtlfile = open(file_name)  
	# iterate over each line in the file
    for line in mtlfile:  
		# split the line into words
        fields = line.split()  
		 # check if the line is not empty
        if len(fields) != 0: 
			 # new material definition starts
            if fields[0] == 'newmtl': 
                if material is not None:
					# add the previous material to the library
                    library.add_material(material)  

				# create a new material with the name
                material = Material(fields[1]) 
				 # Print the material name
                print('Found material definition: {}'.format(material.name)) 

			# ambient colour
            elif fields[0] == 'Ka':  
				# set ambient colour
                material.Ka = np.array(fields[1:], 'f')  

			 # diffuse colour
            elif fields[0] == 'Kd': 
                material.Kd = np.array(fields[1:], 'f')  # Set diffuse colour

			# specular colour
            elif fields[0] == 'Ks': 
				# set specular colour
                material.Ks = np.array(fields[1:], 'f')  

			# specular exponent
            elif fields[0] == 'Ns':  
				# set specular exponent
                material.Ns = float(fields[1])  

			# dissolve (transparency)
            elif fields[0] == 'd':  
				# set transparency
                material.d = float(fields[1])  

			# transparency (alternative representation)
            elif fields[0] == 'Tr':  
				# calculate and set transparency
                material.d = 1.0 - float(fields[1])  

			 # illumination model
            elif fields[0] == 'illum': 
				# set illumination model
                material.illumination = int(fields[1])  

			# diffuse texture map
            elif fields[0] == 'map_Kd':  
				# set diffuse texture map
                material.texture = fields[1] 

	# add the last processed material to the library
    library.add_material(material)  

	# print a message for the completion of loading the material library
    print('- Done, loaded {} materials'.format(len(library.materials))) 

	# return the populated material library
    return library  

def load_obj_file(file_name):
	'''
	A function that loads a Blender3D object file and returns a list of meshes.
	:param file_name: Name of the Blender file
	:return: List of meshes
	'''
	print('Loading mesh(es) from Blender file: {}'.format(file_name))

	# list of vertices
	vlist = []
	# list of texture vectors	
	tlist = []	
	# list of polygonal faces
	flist = []
	# list of material names	
	mlist = []	
	# list of line numbers
	lnlist = []
	# mesh id is set to 0
	mesh_id = 0
	# list of meshes
	mesh_list = []

	# current material object
	material = None

	with open(file_name) as objfile:
		# count line number for easier error locating
		line_nb = 0 

		# loop over all lines in the file
		for line in objfile:
			# process the line
			data = process_line(line)

			# increment line number by 1
			line_nb += 1 

			# skip empty lines
			if data is None:
				continue
			
			elif data[0] == 'vertex':
				# append vertex coordinates to the vertex list
				vlist.append(data[1])

			elif data[0] == 'vertex texture':
				# append texture coordinates to the texture list
				tlist.append(data[1])
			
			elif data[0] == 'normal':
				# append normal vectors to the normal list
				vlist.append(data[1])

			elif data[0] == 'face':
				# check if the length of the list is 3
				if len(data[1]) == 3:
					# if the face is a triangle, add it directly to the face list
					# appends the face data to the list of faces
					flist.append(data[1])
					# appends the mesh id to the mesh list
					mesh_list.append(mesh_id)
					# appends the material to the material list
					mlist.append(material)
					# appends the line number to the line number list
					lnlist.append(line_nb)
				else:
					 # if the face has more than three vertices (e.g., a quad), split it into triangles
        			# first triangle
					face1 = [data[1][0], data[1][1], data[1][2]]
					# append the first triangle of a quad face to the list of faces
					flist.append(face1)
					# appends the mesh id to the mesh list
					mesh_list.append(mesh_id)
					# appends the material to the material list
					mlist.append(material)
					# appends the line number to the line number list
					lnlist.append(line_nb)

					# second triangle (for quads)
					face2 = [data[1][0], data[1][2], data[1][3]]
					# append the second triangle of a quad face to the list of faces
					flist.append(face2)
					# appends the mesh id to the mesh list
					mesh_list.append(mesh_id)
					# appends the material to the material list
					mlist.append(material)
					# appends the line number to the line number list
					lnlist.append(line_nb)

			elif data[0] == 'material library':
				# loads the material library
				library = load_material_library('models/{}'.format(data[1]))

			# material indicate a new mesh in the file, so we store the previous one if not empty and start
			# a new one.
			elif data[0] == 'material':
				# update the current material and increment the mesh ID
				material = library.names[data[1]]
				mesh_id += 1
				print('[l.{}] Loading mesh with material: {}'.format(line_nb, data[1]))

	# print a message for the completion of loading the mesh(es) from the Blender file
	print('File read. Found {} vertices and {} faces.'.format(len(vlist), len(flist)))

	# return the list of meshes
	return create_meshes_from_blender(vlist, flist, mlist, tlist, library, mesh_list, lnlist)


def create_meshes_from_blender(vlist, flist, mlist, tlist, library, mesh_list, lnlist):
	'''
	Creates a list of meshes from the Blender file.
	:param vlist: List of vertices
	:param flist: List of faces
	:param mlist: List of materials
	:param tlist: List of texture vectors
	:param library: Material library
	:param mesh_list: List of mesh IDs
	:param lnlist: List of line numbers
	:return: List of meshes
	'''

	fstart = 0
	mesh_id = 1
	meshes = []

	# create a numpy array from the vertex list
	varray = np.array(vlist, dtype='f')

	# and all texture vectors
	tarray = np.array(tlist, dtype='f')

	# start with the first material
	material = mlist[fstart]

	for f in range(len(flist)):
		# new mesh is denoted by change in material
		if mesh_id != mesh_list[f]: 
			print('Creating new mesh %i, faces %i-%i, line %i, with material %i: %s' % (mesh_id, fstart, f, lnlist[fstart], mlist[fstart], library.materials[mlist[fstart]].name))
			try:
				# create a new mesh
				mesh = create_mesh(varray, tarray, flist, fstart, f, library, material)
				# append the new mesh to the list of meshes
				meshes.append(mesh)
			except Exception as e:
				print('(W) could not load mesh!')
				print(e)
				raise
			
			# update the mesh ID and material
			mesh_id = mesh_list[f]

			# start the next mesh
			fstart = f
			material = mlist[fstart]

	# add the last mesh
	try:
		meshes.append(create_mesh(varray, tarray, flist, fstart, len(flist), library, material))
	except:
		print('(W) could not load mesh!')
		raise

	print('--- Created {} mesh(es) from Blender file.'.format(len(meshes)))
	# return the list of meshes
	return meshes


def create_mesh(varray, tarray, flist, fstart, f, library, material):
	'''
	Creates a mesh from the Blender file.
	:param varray: Array of vertices
	:param tarray: Array of texture vectors
	:param flist: List of faces
	:param fstart: Start index of faces
	:param f: End index of faces
	:param library: Material library
	:param material: Material
	:return: Mesh
	'''

	# select faces for this mesh
	farray = np.array(flist[fstart:f], dtype=np.uint32)

	# and vertices
	vmax = np.max(farray[:, :, 0].flatten())
	vmin = np.min(farray[:, :, 0].flatten()) - 1

	# fix blender texture intexing
	textures = fix_blender_textures(tarray, farray, varray)
	if textures is not None:
		textures = textures[vmin:vmax, :]

	# returns a mesh created from the vertex array, face array, material and texture coordinates
	return Mesh(
			vertices=varray[vmin:vmax, :],
			faces=farray[:, :, 0] - vmin - 1,
			material=library.materials[material],
			textureCoords=textures
		)


def fix_blender_textures(textures, faces, vertices):
	'''
	Fixes Blender texture indexing for compatibility with OpenGL
	:param textures: Original Blender texture UV values
	:param faces: Blender faces multiple-index
	:return: a new texture array indexed according to vertices.
	'''

	if faces.shape[2] == 1:
		print('(W) No texture indices provided, setting texture coordinate array as None!')
		return None

	# Initialise a new texture array with zeros, sized for vertices and 2D texture coordinates
	new_textures = np.zeros((vertices.shape[0], 2), dtype='f')

	# iterate over each face
	for f in range(faces.shape[0]):
		# iterate over each vertex in the face
		for j in range(faces.shape[1]):
			# map the texture coordinate to the corresponding vertex
            # blender indices are 1-based, hence the '-1' adjustment
			new_textures[faces[f, j, 0], :] = textures[faces[f, j, 1] -1, :]

	# return the new texture array
	return new_textures
