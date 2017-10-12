# *** BEGIN LICENSE BLOCK ***
# Creative Commons 3.0 by-sa
#
# Full license: http://creativecommons.org/licenses/by-sa/3.0/
# Legal code: http://creativecommons.org/licenses/by-sa/3.0/legalcode
#
# You are free:
# * to Share  to copy, distribute and transmit the work
# * to Remix  to adapt the work
#
# Under the following conditions:
# * Attribution. You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work).
# * Share Alike. If you alter, transform, or build upon this work, you may distribute the resulting work only under the same, similar or a compatible license.
#
# * For any reuse or distribution, you must make clear to others the license terms of this work. The best way to do this is with a link to this web page.
# * Any of the above conditions can be waived if you get permission from the copyright holder.
# * Nothing in this license impairs or restricts the author's moral rights.
# *** END LICENSE BLOCK ***


bl_info = {
	"name": "Bolt / Thread",
	"author": "Sergio Moura",
	"version": (1, 0),
	"blender": (2, 7, 0),
	"location": "View3D > Object > Bolt Object",
	"description": "Adds a new bolt object",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object" }

import math;
import bpy;
from bpy.types import Operator;
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty, StringProperty;

# Returns a 3d vector given angle, radius and z (optional)
def point(ANGLE, RADIUS, DZ = 0):
	vert = [RADIUS * math.sin(ANGLE), RADIUS * math.cos(ANGLE), DZ]
	return vert


# actually creates the vertices and the faces for the bolt.
def create_bolt(RADIUS, SUBDIVISIONS, STEP, LOOPS, IDENT, SHOULDER):
	verts = []
	faces = []

	topcap = []
	shouldercap = []

	# ========= VERTS =========
	# cap
	for i in range(SUBDIVISIONS):
		# we start one loop BEFORE the other loops, so the 0 is one step before the others.
		deg = math.pi * 2 * (i - 1) / SUBDIVISIONS
		if (i == 0):
			verts.append(point(deg, RADIUS - IDENT))
		else:
			verts.append(point(deg, RADIUS))

	# 1st loop
	for i in range(SUBDIVISIONS):	
		deg = math.pi * 2 * i / SUBDIVISIONS
		space = (i + 1) * STEP / (SUBDIVISIONS * 2)
		verts.append(point(deg, RADIUS - IDENT, space))
		verts.append(point(deg, RADIUS, space * 2))

	# other loops
	disp = 0
	space = STEP / 2
	for j in range(1, LOOPS - 1):
		for i in range(SUBDIVISIONS):
			deg = math.pi * 2 * i / SUBDIVISIONS
			disp = disp + STEP / SUBDIVISIONS
			verts.append(point(deg, RADIUS - IDENT, disp + space))
			verts.append(point(deg, RADIUS, disp + space * 2))

	# last one
	lastdisp = disp + space * 2
	disp = disp + space
	topcap.append(len(verts) - 1)
	for i in range(SUBDIVISIONS - 1):
		disp = disp + (STEP / SUBDIVISIONS) / 2
		deg = math.pi * 2 * i / SUBDIVISIONS
		verts.append(point(deg, RADIUS - IDENT, disp))
		topcap.append(len(verts))
		verts.append(point(deg, RADIUS, lastdisp))

	# SHOULDER (vertices and faces)
	if (SHOULDER > 0):
		for i in range(SUBDIVISIONS):
			deg = math.pi * 2 * (i - 1) / SUBDIVISIONS
			shouldercap.append(len(verts))
			verts.append(point(deg, RADIUS, lastdisp + SHOULDER))
		faces.append([shouldercap[0], shouldercap[SUBDIVISIONS - 1], topcap[SUBDIVISIONS - 1], topcap[0]])
		for i in range (SUBDIVISIONS - 1):
			faces.append([shouldercap[i], shouldercap[i+1], topcap[i+1], topcap[i]])
			
	else:
		# when we are doing the head, this will come handy
		shouldercap = topcap


	# ========= FACES =========
	# cap / 1st loop
	# 	face count: 16 (SUBDIVISIONS * 2)
	# 	vertice count: 22 (SUBDIVISIONS * 3 - 2)
	faces.append([1, 0, SUBDIVISIONS])	
	faces.append([0, SUBDIVISIONS + 1, SUBDIVISIONS])

	for i in range(1, SUBDIVISIONS):
		i2 = (i - 1) * 2
		if (i == SUBDIVISIONS - 1):
			faces.append([0, i, SUBDIVISIONS + i2, SUBDIVISIONS + i2+2])
		else:
			faces.append([i+1, i, SUBDIVISIONS + i2, SUBDIVISIONS + i2+2])
		faces.append([SUBDIVISIONS + i2 + 2, SUBDIVISIONS + i2, SUBDIVISIONS + i2 + 1, SUBDIVISIONS + i2 + 3])

	# 2nd to n - 1
	lastcorner = 0
	nextcorner = SUBDIVISIONS + 1
	othercorner = 0
	vcount = SUBDIVISIONS * 3 - 2
	for j in range(1, LOOPS - 1):
		for i in range(SUBDIVISIONS):
			othercorner = nextcorner + vcount - SUBDIVISIONS - 1
			faces.append([nextcorner, lastcorner, othercorner, othercorner+2])
			faces.append([othercorner+2, othercorner, othercorner+1, othercorner+3])
			lastcorner = nextcorner
			nextcorner = nextcorner + 2


	# last one!
	eol = othercorner + 3 # stands for end of line
	for i in range(1, SUBDIVISIONS):
		othercorner = nextcorner + vcount - SUBDIVISIONS - 1
		faces.append([nextcorner, lastcorner, othercorner, othercorner + 2])
		faces.append([othercorner+2, othercorner, othercorner+1, othercorner+3])

		if (i == SUBDIVISIONS - 1):
			faces.append([eol, nextcorner, othercorner+2])
			faces.append([eol, othercorner+2, othercorner+3])
		lastcorner = nextcorner
		nextcorner = nextcorner + 2

	return verts, faces

class OBJECT_OT_add_bolt(Operator):
	"""Add an Bolt"""
	bl_idname = "mesh.add_bolt"
	bl_label = "Add Bolt"
	bl_description = "Create a new Bolt Object"
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}

	radius = FloatProperty(
		name = "radius",
		default = 1,
		min = 0,
		max = 50 )

	subdivisions = IntProperty(
		name = "subdivisions",
		default = 8,
		min = 0,
		max = 100 )

	step = FloatProperty(
		name = "step",
		default = 0.2,
		min = 3,
		max = 100 )

	loops = IntProperty(
		name = "loops",
		default = 5,
		min = 0,
		max = 100 )

	ident = FloatProperty(
		name = "ident",
		default = 0.1,
		min = 0,
		max = 100 )

	shoulder = FloatProperty(
		name = "shoulder",
		default = 0,
		min = 0,
		max = 100 )	

	def iterate(self):
		pass

	@staticmethod
	def add_obj(obdata, context):
		scene = context.scene
		obj_new = bpy.data.objects.new(obdata.name, obdata)
		base = scene.objects.link(obj_new)
		return obj_new,base

	def interpret(self, s, context):
		pass

	def execute(self, context):
		verts, faces = create_bolt(self.radius, self.subdivisions, self.step, self.loops, self.ident, self.shoulder);

		mesh = bpy.data.meshes.new('bolt')
		mesh.from_pydata(verts, [], faces)
		mesh.update()
		self.add_obj(mesh, context)
		return {'FINISHED'}

	def draw(self, context):  
		layout = self.layout

		box = layout.box()
		box.prop(self, 'radius')
		box = layout.box()
		box.prop(self, 'subdivisions')
		box = layout.box()
		box.prop(self, 'step')
		box = layout.box()
		box.prop(self, 'loops')
		box = layout.box()
		box.prop(self, 'ident')
		box = layout.box()
		box.prop(self, 'shoulder')

def add_object_button(self, context):
	self.layout.operator(
		OBJECT_OT_add_bolt.bl_idname,
		text = "Add Bolt",
		icon = 'PLUGIN' )

def register():
	bpy.utils.register_class(OBJECT_OT_add_bolt)
	bpy.types.INFO_MT_mesh_add.append(add_object_button)

def unregister():
	bpy.utils.unregister_class(OBJECT_OT_add_bolt)
	bpy.types.INFO_MT_mesh_add.remove(add_object_button)

if __name__ == "__main__":
	register()



# Check if vertice is an outer edge.
def is_outer(OFFSET, EDGE, SUBDIVISIONS, VCOUNT):
	v1 = EDGE.v1.index - OFFSET
	v2 = EDGE.v2.index - OFFSET
	if ((v1 < 0) or (v2 < 0)):
		return False
	eol = VCOUNT - SUBDIVISIONS * 2 + 1
	v1_found = False
	v2_found = False
	
	if ((v1 == 0) or (v1 == eol)):
		v1_found = True
	
	if ((v2 == 0) or (v2 == eol)):
		v2_found = True
	
	idx = SUBDIVISIONS + 1
	while ((v1_found == False) or (v2_found == False)):
		if (idx > VCOUNT):
			return False
		if (v1 == idx):
			v1_found = True
		if (v2 == idx):
			v2_found = True
	
		idx = idx + 2
	
	return True

def is_inner(OFFSET, EDGE, SUBDIVISIONS, VCOUNT):
	v1 = EDGE.v1.index - OFFSET
	v2 = EDGE.v2.index - OFFSET
	if ((v1 < 0) or (v2 < 0)):
		return False
	eol = VCOUNT - SUBDIVISIONS * 2 + 1
	v1_found = False
	v2_found = False
	
	if ((v1 == 0) or (v1 == eol)):
		v1_found = True
	
	if ((v2 == 0) or (v2 == eol)):
		v2_found = True
	
	idx = SUBDIVISIONS
	while ((v1_found == False) or (v2_found == False)):
		if (idx > VCOUNT):
			return False
		if (v1 == idx):
			v1_found = True
		if (v2 == idx):
			v2_found = True
	
		idx = idx + 2
	
	return True

def is_cap(OFFSET, EDGE, SUBDIVISIONS, VCOUNT):
	v1 = EDGE.v1.index - OFFSET
	v2 = EDGE.v2.index - OFFSET

	if ((v1 < 0) or (v2 < 0)):
		return False

	eol = VCOUNT - SUBDIVISIONS * 2 + 1

	v1_found = False
	v2_found = False

	for i in range(SUBDIVISIONS):
		nx = eol + i*2
		if ((v1 == i) or (v1 == nx)):
			v1_found = True
		if ((v2 == i) or (v2 == nx)):
			v2_found = True

	if ((v1_found == False) or (v2_found == False)):
		return False

	return True
