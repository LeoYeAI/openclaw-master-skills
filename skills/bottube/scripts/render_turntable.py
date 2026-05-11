#!/usr/bin/env python3
"""Render a 360-degree turntable video from a GLB 3D model using Blender.

Usage:
    python3 render_turntable.py model.glb /tmp/frames/

Requires: Blender (blender) in PATH.
Outputs PNG frames to the given directory. Combine with ffmpeg:
    ffmpeg -y -framerate 30 -i /tmp/frames/%04d.png -t 6 \
      -c:v libx264 -pix_fmt yuv420p -an turntable.mp4
"""
import argparse
import os
import subprocess
import sys
import textwrap


def main():
    parser = argparse.ArgumentParser(description="Render GLB turntable via Blender")
    parser.add_argument("model", help="Path to .glb model file")
    parser.add_argument("output_dir", help="Directory for rendered PNG frames")
    parser.add_argument("--frames", type=int, default=180,
                        help="Number of frames (default: 180 = 6s at 30fps)")
    parser.add_argument("--resolution", type=int, default=720,
                        help="Render resolution (square, default: 720)")
    args = parser.parse_args()

    model_path = os.path.abspath(args.model)
    output_dir = os.path.abspath(args.output_dir)

    if not os.path.isfile(model_path):
        print(f"Error: model file not found: {model_path}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Blender Python script (written to temp file, not --python-expr)
    blender_script = textwrap.dedent(f"""\
        import bpy
        import math
        import mathutils

        # Clean scene
        bpy.ops.wm.read_factory_settings(use_empty=True)

        # Import model
        bpy.ops.import_scene.gltf(filepath="{model_path}")

        # Add camera on orbit
        cam = bpy.data.cameras.new("Camera")
        cam_obj = bpy.data.objects.new("Camera", cam)
        bpy.context.scene.collection.objects.link(cam_obj)
        bpy.context.scene.camera = cam_obj

        # Add light
        light = bpy.data.lights.new("Light", type="SUN")
        light.energy = 3
        light_obj = bpy.data.objects.new("Light", light)
        light_obj.location = (5, 5, 5)
        bpy.context.scene.collection.objects.link(light_obj)

        # Keyframe 360-degree camera orbit
        num_frames = {args.frames}
        for i in range(num_frames + 1):
            angle = (i / num_frames) * 2 * math.pi
            cam_obj.location = (3 * math.cos(angle), 3 * math.sin(angle), 1.5)
            cam_obj.keyframe_insert("location", frame=i)
            direction = mathutils.Vector((0, 0, 0)) - cam_obj.location
            cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            cam_obj.keyframe_insert("rotation_euler", frame=i)

        # Render settings
        scene = bpy.context.scene
        scene.render.resolution_x = {args.resolution}
        scene.render.resolution_y = {args.resolution}
        scene.frame_start = 0
        scene.frame_end = num_frames
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = "{output_dir}/"

        bpy.ops.render.render(animation=True)
    """)

    script_path = os.path.join(output_dir, "_render_script.py")
    with open(script_path, "w") as f:
        f.write(blender_script)

    print(f"Rendering {args.frames} frames at {args.resolution}x{args.resolution}...")
    result = subprocess.run(
        ["blender", "--background", "--python", script_path],
        capture_output=True, text=True
    )

    # Clean up temp script
    if os.path.exists(script_path):
        os.remove(script_path)

    if result.returncode != 0:
        print(f"Blender failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    frame_count = len([f for f in os.listdir(output_dir) if f.endswith(".png")])
    print(f"Done: {frame_count} frames in {output_dir}")


if __name__ == "__main__":
    main()
