import bpy
import os
from . import utils

class IMAGE_OT_LoadCharacter(bpy.types.Operator):
    bl_idname = "image.load_character"
    bl_label = "Load Character Image"
    bl_description = "Load a 2D character image with transparency"
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to the character image file (PNG recommended for transparency)",
        subtype="FILE_PATH"
    )
    
    filter_image: bpy.props.BoolProperty(
        name="Filter Images",
        default=True,
        options={'HIDDEN'}
    )
    
    filter_glob: bpy.props.StringProperty(
        default="*.png;*.jpg;*.jpeg;*.bmp",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        scene = context.scene
        if os.path.exists(self.filepath):
            image = bpy.data.images.load(self.filepath)
            scene.character_image = image
            self.report({'INFO'}, f"Loaded character: {image.name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "File not found")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class IMAGE_OT_Convert2DCharacterTo3D(bpy.types.Operator):
    bl_idname = "image.convert_character_to_3d"
    bl_label = "Convert Character to 3D"
    bl_description = "Convert 2D character to 3D model with texturing"
    
    def execute(self, context):
        scene = context.scene
        
        if not scene.character_image:
            self.report({'ERROR'}, 'Please load a character image first')
            return {'CANCELLED'}
        
        try:
            # Create 3D character model
            character_obj = utils.create_character_from_image(
                scene.character_image,
                scene.character_thickness,
                scene.character_height,
                scene.subdivision_levels
            )
            
            if character_obj is None:
                self.report({'ERROR'}, 'Failed to create character model')
                return {'CANCELLED'}
            
            # Link to scene
            bpy.context.collection.objects.link(character_obj)
            bpy.context.view_layer.objects.active = character_obj
            character_obj.select_set(True)
            
            # Apply modifiers
            if scene.smooth_shading:
                utils.apply_smooth_shading(character_obj)
            
            if scene.add_bevel:
                utils.apply_bevel(character_obj)
            
            # Auto rig if enabled
            if scene.auto_rig:
                utils.create_basic_armature(character_obj)
                self.report({'INFO'}, 'Character created, textured and rigged successfully')
            else:
                self.report({'INFO'}, 'Character created and textured successfully')
            
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f'Conversion failed: {str(e)}')
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}


class OBJECT_OT_AutoRig(bpy.types.Operator):
    bl_idname = "object.auto_rig"
    bl_label = "Auto Rig Character"
    bl_description = "Automatically rig the character with humanoid bones"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'
    
    def execute(self, context):
        obj = context.active_object
        
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, 'Please select a mesh object')
            return {'CANCELLED'}
        
        try:
            utils.create_basic_armature(obj)
            self.report({'INFO'}, 'Character rigged successfully')
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f'Rigging failed: {str(e)}')
            return {'CANCELLED'}
