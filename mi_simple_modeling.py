from __future__ import annotations
from typing import Any, List, Tuple, Optional, Dict, Union, Callable
import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    IntVectorProperty,
    PointerProperty,
    StringProperty,
)

# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


import bmesh
import array
# import blf
# import string

from bpy.types import Operator, AddonPreferences, Context, Event
#from bpy_extras import view3d_utils

import math
import mathutils as mathu
#import random
#from mathutils import Vector, Matrix


class MI_OT_SM_Symmetry(bpy.types.Operator):

    """Draw a line with the mouse"""
    bl_idname = "mira.sm_symmetry"
    bl_label = "MiraSymmetry"
    bl_description = "MiraSymmetry"
    bl_options = {'REGISTER', 'UNDO'}

    #taper_value: FloatProperty(default=0.0, min=-1000.0, max=1.0)

    sym_axis: EnumProperty(
        items=(('X', 'X', ''),
               ('Y', 'Y', ''),
               ('Z', 'Z', ''),
               ),
        default = 'X'
    )

    # deform_direction: EnumProperty(
        # items=(('Top', 'Top', ''),
               #('Bottom', 'Bottom', ''),
               #('Left', 'Left', ''),
               #('Right', 'Right', ''),
               #),
        # default = 'Top'
    #)


    def invoke(self, context: Context, event: Event):


        return self.execute(context)
        # else:
            # self.report({'WARNING'}, "View3D not found, cannot run operator")
            # return {'CANCELLED'}


    def execute(self, context: Context):

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        ref_obj = context.active_object
        verts_ref = [v for v in ref_obj.data.vertices if v.select]

        tmp_obj = bpy.data.objects.new("MIRA_TMP", ref_obj.data.copy())
        tmp_obj.matrix_world = ref_obj.matrix_world.copy()
        context.scene.collection.objects.link(tmp_obj)

        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.objects.active = tmp_obj
        tmp_obj.select_set(True)
        mesh_tmp = tmp_obj.data
        count = len(mesh_tmp.vertices)

        # Get all coordinates
        coords = array.array('f', [0.0] * (count * 3))
        mesh_tmp.vertices.foreach_get("co", coords)

        # Get selection
        select = array.array('i', [0] * count)
        mesh_tmp.vertices.foreach_get("select", select)

        if self.sym_axis == 'X':
            for i in range(count):
                if select[i]:
                    coords[i*3] = -coords[i*3]
        elif self.sym_axis == 'Y':
            for i in range(count):
                if select[i]:
                    coords[i*3 + 1] = -coords[i*3 + 1]
        elif self.sym_axis == 'Z':
            for i in range(count):
                if select[i]:
                    coords[i*3 + 2] = -coords[i*3 + 2]

        mesh_tmp.vertices.foreach_set("co", coords)
        mesh_tmp.update()

        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        tmp_obj.modifiers["Shrinkwrap"].wrap_method = 'NEAREST_VERTEX'
        bpy.context.object.modifiers["Shrinkwrap"].target = ref_obj
        bpy.ops.object.modifier_apply(modifier="Shrinkwrap")

        # Get vertices after shrinkwrap
        mesh_tmp = tmp_obj.data
        count_tmp = len(mesh_tmp.vertices)
        coords_tmp = array.array('f', [0.0] * (count_tmp * 3))
        mesh_tmp.vertices.foreach_get("co", coords_tmp)
        select_tmp = array.array('i', [0] * count_tmp)
        mesh_tmp.vertices.foreach_get("select", select_tmp)

        selected_coords_tmp = [Vector((coords_tmp[i*3], coords_tmp[i*3+1], coords_tmp[i*3+2])) for i in range(count_tmp) if select_tmp[i]]

        mesh_ref = ref_obj.data
        count_ref = len(mesh_ref.vertices)
        coords_ref = array.array('f', [0.0] * (count_ref * 3))
        mesh_ref.vertices.foreach_get("co", coords_ref)
        select_ref = array.array('i', [0] * count_ref)
        mesh_ref.vertices.foreach_get("select", select_ref)

        sel_idx = 0
        for i in range(count_ref):
            if select_ref[i]:
                new_co = selected_coords_tmp[sel_idx]
                coords_ref[i*3] = new_co.x
                coords_ref[i*3+1] = new_co.y
                coords_ref[i*3+2] = new_co.z
                sel_idx += 1

        if self.sym_axis == 'X':
            for i in range(count_ref):
                if select_ref[i]:
                    coords_ref[i*3] = -coords_ref[i*3]
        elif self.sym_axis == 'Y':
            for i in range(count_ref):
                if select_ref[i]:
                    coords_ref[i*3 + 1] = -coords_ref[i*3 + 1]
        elif self.sym_axis == 'Z':
            for i in range(count_ref):
                if select_ref[i]:
                    coords_ref[i*3 + 2] = -coords_ref[i*3 + 2]

        mesh_ref.vertices.foreach_set("co", coords_ref)
        mesh_ref.update()

        bpy.ops.object.delete(use_global=False)

        context.view_layer.objects.active = ref_obj
        ref_obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        return {'FINISHED'}




