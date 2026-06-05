import bpy
import numpy as np
import bmesh
from mathutils import Vector

def create_character_from_image(image, thickness=0.15, height=2.0, subdivision_levels=2):
    """Create a 3D character model from a 2D image using silhouette extrusion"""
    
    # Convert image to numpy array
    img_array = image_to_numpy(image)
    
    # Extract silhouette with alpha channel
    silhouette, alpha_channel = extract_silhouette(img_array)
    
    # Create base mesh from silhouette
    mesh_obj = create_mesh_from_silhouette(silhouette, height, thickness)
    
    if mesh_obj is None:
        return None
    
    # Link to scene FIRST before applying modifiers
    bpy.context.collection.objects.link(mesh_obj)
    
    # Generate normal map from the image
    normal_map = generate_normal_map(img_array)
    
    # Create and apply material with texture and normal map
    apply_character_material(mesh_obj, image, alpha_channel, normal_map)
    
    # Apply UV mapping (now that object is linked)
    apply_uvs(mesh_obj, image)
    
    # Apply subdivision surface for smoother look
    if subdivision_levels > 0:
        apply_subdivision(mesh_obj, subdivision_levels)
    
    return mesh_obj


def image_to_numpy(image):
    """Convert Blender image to numpy array"""
    pixels = np.array(image.pixels[:])
    height, width = image.size[1], image.size[0]
    channels = image.channels
    
    if channels == 4:
        pixels = pixels.reshape((height, width, 4))
    elif channels == 3:
        pixels = pixels.reshape((height, width, 3))
    else:
        pixels = pixels.reshape((height, width))
    
    return pixels


def extract_silhouette(img_array):
    """Extract character silhouette and alpha from image"""
    
    alpha_channel = None
    
    if len(img_array.shape) == 3:
        if img_array.shape[2] == 4:
            # Use alpha channel
            alpha_channel = (img_array[:, :, 3] * 255).astype(np.uint8)
            silhouette = img_array[:, :, 3] > 0.1
        else:
            # Convert to grayscale
            silhouette = np.dot(img_array[:, :, :3], [0.299, 0.587, 0.114]) > 0.3
    else:
        silhouette = img_array > 0.3
    
    silhouette_uint8 = silhouette.astype(np.uint8) * 255
    
    return silhouette_uint8.astype(np.uint8), alpha_channel


def generate_normal_map(img_array):
    """Generate a normal map from the 2D image using Sobel edge detection"""
    
    # Convert to grayscale if needed
    if len(img_array.shape) == 3:
        if img_array.shape[2] >= 3:
            grayscale = np.dot(img_array[:, :, :3], [0.299, 0.587, 0.114])
        else:
            grayscale = img_array[:, :, 0]
    else:
        grayscale = img_array
    
    h, w = grayscale.shape
    
    # Simple Sobel edge detection for normal map
    # Sobel X kernel
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    # Sobel Y kernel
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    
    # Normalize grayscale to 0-1
    grayscale = grayscale.astype(np.float32) / 255.0
    
    # Apply Sobel filters
    gx = np.zeros_like(grayscale)
    gy = np.zeros_like(grayscale)
    
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            patch = grayscale[i-1:i+2, j-1:j+2]
            gx[i, j] = np.sum(patch * sobel_x)
            gy[i, j] = np.sum(patch * sobel_y)
    
    # Calculate normal map
    # Normal points outward from surface
    # X direction (left-right) from gx
    # Y direction (up-down) from gy
    # Z direction (depth) is always positive
    
    normal_map = np.zeros((h, w, 3), dtype=np.float32)
    
    # Set normal components
    normal_map[:, :, 0] = gx  # Red channel = X gradient
    normal_map[:, :, 1] = gy  # Green channel = Y gradient
    normal_map[:, :, 2] = np.ones((h, w)) * 0.5  # Blue channel = Z (depth)
    
    # Normalize the normal vectors
    magnitude = np.sqrt(normal_map[:, :, 0]**2 + normal_map[:, :, 1]**2 + normal_map[:, :, 2]**2)
    magnitude = np.maximum(magnitude, 0.001)  # Avoid division by zero
    
    normal_map[:, :, 0] /= magnitude
    normal_map[:, :, 1] /= magnitude
    normal_map[:, :, 2] /= magnitude
    
    # Convert from [-1, 1] range to [0, 1] range for storage
    normal_map = (normal_map + 1.0) / 2.0
    normal_map = (normal_map * 255).astype(np.uint8)
    
    return normal_map


def create_normal_map_image(name, normal_map_array):
    """Create a Blender image from normal map array"""
    
    h, w = normal_map_array.shape[:2]
    
    # Create image
    img = bpy.data.images.new(name, width=w, height=h)
    
    # Prepare pixel data (RGBA format)
    pixels = np.zeros((h, w, 4), dtype=np.float32)
    pixels[:, :, :3] = normal_map_array.astype(np.float32) / 255.0  # RGB
    pixels[:, :, 3] = 1.0  # Alpha
    
    # Flatten and assign to image
    img.pixels[:] = pixels.flatten()
    
    return img


def create_mesh_from_silhouette(silhouette, height=2.0, thickness=0.15):
    """Create 3D mesh from 2D silhouette using extrusion"""
    
    mesh = bpy.data.meshes.new("Character_Mesh")
    obj = bpy.data.objects.new("Character", mesh)
    
    h, w = silhouette.shape
    
    # Find contour points from silhouette
    contour = extract_contour(silhouette)
    
    if not contour or len(contour) < 4:
        return None
    
    # Create vertices from contour
    vertices = []
    
    for x, y in contour:
        vx = (x / w) * 2 - 1
        vy = (y / h) * height
        
        # Front face
        vertices.append((vx, -thickness/2, vy))
        # Back face
        vertices.append((vx, thickness/2, vy))
    
    if len(vertices) < 4:
        return None
    
    # Create faces
    faces = []
    n = len(vertices) // 2
    
    for i in range(n - 1):
        v0 = i * 2
        v1 = (i + 1) * 2
        v2 = (i + 1) * 2 + 1
        v3 = i * 2 + 1
        
        faces.append((v0, v1, v2, v3))
    
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    
    return obj


def extract_contour(silhouette):
    """Extract contour points from silhouette using simple edge detection"""
    h, w = silhouette.shape
    contour = []
    
    # Find boundary pixels
    for y in range(h):
        for x in range(w):
            if silhouette[y, x] > 128:
                # Check if it's on the edge
                is_edge = False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = y + dy, x + dx
                        if ny < 0 or ny >= h or nx < 0 or nx >= w:
                            is_edge = True
                        elif silhouette[ny, nx] <= 128:
                            is_edge = True
                
                if is_edge:
                    contour.append((x, y))
    
    # Reduce points for cleaner mesh
    if len(contour) > 200:
        step = len(contour) // 200
        contour = contour[::step]
    
    return contour


def apply_uvs(obj, image):
    """Apply UV mapping to character"""
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    try:
        # Create UV map if it doesn't exist
        if not obj.data.uv_layers:
            obj.data.uv_layers.new()
        
        # Switch to edit mode and UV unwrap
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.object.mode_set(mode='OBJECT')
    except Exception as e:
        print(f"UV mapping error: {e}")
        # Don't fail completely if UV fails
        bpy.ops.object.mode_set(mode='OBJECT')


def apply_character_material(obj, image, alpha_channel, normal_map_array):
    """Apply material with the character image texture and normal map"""
    
    mat = bpy.data.materials.new(name="Character_Material")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    mat.shadow_method = 'HASHED'
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    # Create normal map image
    normal_map_img = create_normal_map_image("Normal_Map", normal_map_array)
    
    # Create nodes
    img_node = nodes.new('ShaderNodeTexImage')
    img_node.image = image
    img_node.label = "Color"
    
    normal_img_node = nodes.new('ShaderNodeTexImage')
    normal_img_node.image = normal_map_img
    normal_img_node.label = "Normal Map"
    
    normal_node = nodes.new('ShaderNodeNormalMap')
    normal_node.inputs['Strength'].default_value = 1.0
    
    bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_node.inputs['Specular'].default_value = 0.1
    bsdf_node.inputs['Roughness'].default_value = 0.8
    
    output_node = nodes.new('ShaderNodeOutputMaterial')
    
    # Connect nodes for color
    links.new(img_node.outputs['Color'], bsdf_node.inputs['Base Color'])
    
    # Connect nodes for normal map
    links.new(normal_img_node.outputs['Color'], normal_node.inputs['Color'])
    links.new(normal_node.outputs['Normal'], bsdf_node.inputs['Normal'])
    
    # Connect alpha if available
    if alpha_channel is not None:
        links.new(img_node.outputs['Alpha'], bsdf_node.inputs['Alpha'])
    
    # Connect to output
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    # Add material to object
    obj.data.materials.append(mat)


def apply_smooth_shading(obj):
    """Apply smooth shading to character"""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    
    # Enable auto smooth
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = 0.5236  # 30 degrees in radians


def apply_bevel(obj, amount=0.01):
    """Apply bevel modifier for edge detail"""
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = amount
    bevel.segment = 2
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = 0.5236  # 30 degrees


def apply_subdivision(obj, levels=2):
    """Apply subdivision surface modifier for smoothness"""
    subdiv = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subdiv.levels = levels
    subdiv.render_levels = levels + 1
    subdiv.quality = 3


def create_basic_armature(obj):
    """Create a basic humanoid armature for character rigging"""
    
    # Create armature
    armature = bpy.data.armatures.new("Character_Armature")
    arm_obj = bpy.data.objects.new("Armature", armature)
    bpy.context.collection.objects.link(arm_obj)
    
    # Enter edit mode to create bones
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Define basic humanoid skeleton
    bones_data = [
        ("Root", (0, 0, 0), (0, 0, 0.1)),
        ("Pelvis", (0, 0, 0.1), (0, 0, 0.4)),
        ("Spine", (0, 0, 0.4), (0, 0, 0.75)),
        ("Chest", (0, 0, 0.75), (0, 0, 1.0)),
        ("Neck", (0, 0, 1.0), (0, 0, 1.2)),
        ("Head", (0, 0, 1.2), (0, 0, 1.5)),
        ("ShoulderL", (0, 0, 1.0), (-0.3, 0, 1.0)),
        ("ArmL", (-0.3, 0, 1.0), (-0.6, 0, 0.8)),
        ("ForearmL", (-0.6, 0, 0.8), (-0.8, 0, 0.6)),
        ("HandL", (-0.8, 0, 0.6), (-0.9, 0, 0.5)),
        ("ShoulderR", (0, 0, 1.0), (0.3, 0, 1.0)),
        ("ArmR", (0.3, 0, 1.0), (0.6, 0, 0.8)),
        ("ForearmR", (0.6, 0, 0.8), (0.8, 0, 0.6)),
        ("HandR", (0.8, 0, 0.6), (0.9, 0, 0.5)),
        ("ThighL", (0, 0, 0.4), (-0.15, 0, 0.1)),
        ("ShinL", (-0.15, 0, 0.1), (-0.15, 0, -0.2)),
        ("FootL", (-0.15, 0, -0.2), (-0.15, 0, -0.3)),
        ("ThighR", (0, 0, 0.4), (0.15, 0, 0.1)),
        ("ShinR", (0.15, 0, 0.1), (0.15, 0, -0.2)),
        ("FootR", (0.15, 0, -0.2), (0.15, 0, -0.3)),
    ]
    
    for bone_name, head, tail in bones_data:
        bone = armature.edit_bones.new(bone_name)
        bone.head = head
        bone.tail = tail
    
    # Set up parent relationships
    armature.edit_bones["Pelvis"].parent = armature.edit_bones["Root"]
    armature.edit_bones["Spine"].parent = armature.edit_bones["Pelvis"]
    armature.edit_bones["Chest"].parent = armature.edit_bones["Spine"]
    armature.edit_bones["Neck"].parent = armature.edit_bones["Chest"]
    armature.edit_bones["Head"].parent = armature.edit_bones["Neck"]
    
    for limb in ["L", "R"]:
        armature.edit_bones[f"Shoulder{limb}"].parent = armature.edit_bones["Chest"]
        armature.edit_bones[f"Arm{limb}"].parent = armature.edit_bones[f"Shoulder{limb}"]
        armature.edit_bones[f"Forearm{limb}"].parent = armature.edit_bones[f"Arm{limb}"]
        armature.edit_bones[f"Hand{limb}"].parent = armature.edit_bones[f"Forearm{limb}"]
        
        armature.edit_bones[f"Thigh{limb}"].parent = armature.edit_bones["Pelvis"]
        armature.edit_bones[f"Shin{limb}"].parent = armature.edit_bones[f"Thigh{limb}"]
        armature.edit_bones[f"Foot{limb}"].parent = armature.edit_bones[f"Shin{limb}"]
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add armature modifier to character
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    armature_mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    armature_mod.object = arm_obj
    
    # Set armature as parent
    with bpy.context.temp_override(object=obj):
        bpy.ops.object.parent_set(type='ARMATURE')
