import bpy

class VIEW3D_PT_2DCharacterPanel(bpy.types.Panel):
    bl_label = "2D to 3D Character"
    bl_idname = "VIEW3D_PT_2d_character"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "2D to 3D"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Image section
        layout.label(text="Character Image:", icon='IMAGE_DATA')
        layout.prop(scene, "character_image", text="")
        layout.operator("image.load_character", text="Load Character", icon='FILEBROWSER')
        
        # Model Settings section
        layout.separator()
        layout.label(text="Model Settings:", icon='CUBE')
        layout.prop(scene, "character_height", slider=True)
        layout.prop(scene, "character_thickness", slider=True)
        layout.prop(scene, "subdivision_levels", slider=True)
        
        # Appearance section
        layout.separator()
        layout.label(text="Appearance:", icon='SHADING_SOLID')
        layout.prop(scene, "smooth_shading")
        layout.prop(scene, "add_bevel")
        
        # Rigging section
        layout.separator()
        layout.label(text="Rigging:", icon='ARMATURE_DATA')
        layout.prop(scene, "auto_rig")
        
        # Convert button
        layout.separator()
        layout.operator("image.convert_character_to_3d", text="Convert to 3D", icon='MESH_CUBE')
        
        # Manual rig button
        if context.active_object and context.active_object.type == 'MESH':
            layout.separator()
            layout.operator("object.auto_rig", text="Manual Rig", icon='ARMATURE_DATA')
