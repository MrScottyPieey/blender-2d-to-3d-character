bl_info = {
    "name": "2D to 3D Character Converter",
    "blender": (3, 0, 0),
    "version": (1, 0, 0),
    "location": "View3D > Sidebar > 2D to 3D Character",
    "description": "Convert flat 2D character artwork to 3D models with automatic texturing",
    "author": "MrScottyPieey",
    "category": "Modeling",
}

import bpy
from . import operators
from . import ui
from . import utils

classes = (
    operators.IMAGE_OT_LoadCharacter,
    operators.IMAGE_OT_Convert2DCharacterTo3D,
    operators.OBJECT_OT_AutoRig,
    ui.VIEW3D_PT_2DCharacterPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.character_image = bpy.props.PointerProperty(
        name="Character Image",
        type=bpy.types.Image
    )
    bpy.types.Scene.character_thickness = bpy.props.FloatProperty(
        name="Character Thickness",
        default=0.15,
        min=0.05,
        max=2.0
    )
    bpy.types.Scene.character_height = bpy.props.FloatProperty(
        name="Character Height",
        default=2.0,
        min=0.5,
        max=10.0
    )
    bpy.types.Scene.auto_rig = bpy.props.BoolProperty(
        name="Auto Rig",
        default=True
    )
    bpy.types.Scene.subdivision_levels = bpy.props.IntProperty(
        name="Subdivision Levels",
        default=2,
        min=0,
        max=5
    )
    bpy.types.Scene.add_bevel = bpy.props.BoolProperty(
        name="Add Bevel",
        default=True
    )
    bpy.types.Scene.smooth_shading = bpy.props.BoolProperty(
        name="Smooth Shading",
        default=True
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.character_image
    del bpy.types.Scene.character_thickness
    del bpy.types.Scene.character_height
    del bpy.types.Scene.auto_rig
    del bpy.types.Scene.subdivision_levels
    del bpy.types.Scene.add_bevel
    del bpy.types.Scene.smooth_shading

if __name__ == "__main__":
    register()
