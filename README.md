# blender-2d-to-3d-character
This blender plugin let's characters 2D convert flat to 3D plugin.


Features:
✅ 2D to 3D Conversion - Converts flat character images to 3D models using silhouette extraction ✅ Automatic Texturing - Applies the original image as texture to the 3D model with proper UV mapping ✅ Alpha Channel Support - Preserves transparency from PNG images ✅ Smooth Shading - Auto-applies smooth shading for polished look ✅ Bevel Edges - Adds subtle edge bevels for detail ✅ Subdivision Levels - Increases smoothness with configurable subdivision surfaces ✅ Auto Rigging - Creates a complete humanoid skeleton with 20+ bones ✅ Character Armature - Full body rig with spine, limbs, and head controls

Files Included:
__init__.py - Main plugin initialization
operators.py - Image loading and conversion operators
ui.py - User interface panel
utils.py - All conversion and rigging logic with OpenCV integration
How to Use:
Install the plugin in Blender's addons folder
Enable it in Preferences → Add-ons
Open the "2D to 3D Character" panel in the 3D View sidebar
Load a character image (PNG with transparency works best)
Adjust settings (height, thickness, smoothness)
Click "Convert to 3D"
Your character is automatically textured and rigged!

✅ Blender 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
✅ Blender 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
✅ Latest Blender versions
