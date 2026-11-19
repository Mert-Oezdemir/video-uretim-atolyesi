"""30 saniyelik dikey kamera 'exploded view' animasyonu.
Blender 5.1+; sadece bpy ve Python standart kutuphanesi kullanir.

calistir:
  blender -b --python blender/scenes/camera_exploded.py -- --render still --quality preview --output outputs
  blender -b --python blender/scenes/camera_exploded.py -- --render animation --quality preview --output outputs
"""
import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def cli():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", choices=("still", "animation", "none"), default="still")
    parser.add_argument("--quality", choices=("preview", "final"), default="preview")
    parser.add_argument("--output", default="outputs")
    return parser.parse_args(args)


def material(name, color, metal=0.0, rough=0.3, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1.0)
    node.inputs["Metallic"].default_value = metal
    node.inputs["Roughness"].default_value = rough
    if emission:
        node.inputs["Emission Color"].default_value = (*color, 1.0)
        node.inputs["Emission Strength"].default_value = emission
    return mat


def bevel(obj, width=0.04, segments=3):
    mod = obj.modifiers.new("CNC rounded edges", "BEVEL")
    mod.width = width
    mod.segments = segments
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def cube(name, loc, scale, mat, rounded=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if rounded:
        bevel(obj, rounded)
    return obj


def cylinder(name, x, radius, depth, mat, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth,
        location=(x, 0, 0), rotation=(0, math.pi / 2, 0)
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel(obj, 0.018)
    return obj


def torus(name, x, major, minor, mat):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=80, minor_segments=12,
        location=(x, 0, 0), rotation=(0, math.pi / 2, 0),
        major_radius=major, minor_radius=minor
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def explode(obj, distance, twist=0.0):
    home = obj.location.copy()
    start_rot = obj.rotation_euler.copy()
    for frame, offset, rotation in (
        (1, 0.0, 0.0),
        (76, 0.0, 0.0),
        (235, distance, twist),
        (480, distance, twist),
        (635, 0.0, 0.0),
        (720, 0.0, 0.0),
    ):
        obj.location = home + Vector((offset, 0, 0))
        obj.rotation_euler = start_rot.copy()
        obj.rotation_euler.x += rotation
        obj.keyframe_insert(data_path="location", frame=frame)
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def point(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def area_light(name, loc, power, color, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.color = color
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(light)
    light.location = loc
    point(light, (0, 0, 0))
    return light


def camera_rig():
    cam_data = bpy.data.cameras.new("Cinematic 65mm")
    cam = bpy.data.objects.new("Cinematic orbit camera", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 9.5
    for frame, loc in (
        (1, (5.8, -12.0, 5.0)),
        (235, (4.2, -11.0, 4.8)),
        (480, (4.5, -11.4, 5.2)),
        (720, (5.8, -12.0, 5.0)),
    ):
        cam.location = loc
        point(cam, (0.0, 0.0, -0.1))
        cam.keyframe_insert(data_path="location", frame=frame)
        cam.keyframe_insert(data_path="rotation_euler", frame=frame)


def build_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, 720
    scene.render.fps = 24
    scene.render.resolution_x, scene.render.resolution_y = 1080, 1920
    scene.render.resolution_percentage = 100
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.world.color = (0.02, 0.025, 0.05)
    if scene.world.use_nodes:
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.012, 0.018, 0.035, 1)
            bg.inputs["Strength"].default_value = 0.5

    graphite = material("Graphite anodized", (0.045, 0.055, 0.075), 0.85, 0.22)
    dark = material("Lens barrel black", (0.012, 0.018, 0.025), 0.68, 0.25)
    titanium = material("Brushed titanium", (0.38, 0.43, 0.49), 0.85, 0.25)
    copper = material("Copper traces", (0.72, 0.27, 0.09), 0.82, 0.28)
    glass = material("Coated optic", (0.02, 0.27, 0.36), 0.4, 0.09)
    green = material("PCB", (0.025, 0.16, 0.13), 0.25, 0.32)
    glow = material("Blue micro LED", (0.05, 0.65, 0.86), 0.1, 0.3, 1.8)

    # Floating camera chassis and the central image sensor.
    chassis = cube("Camera diecast chassis", (-1.03, 0, 0), (1.75, 2.15, 2.45), graphite, 0.22)
    grip = cube("Rubber side grip", (-1.09, -1.10, -0.18), (1.45, 0.34, 1.60), dark, 0.13)
    cylinder("Mount housing", -0.07, 0.94, 0.22, titanium)
    sensor = cube("Exposed image sensor", (0.11, 0, 0), (0.09, 0.72, 0.58), glass, 0.025)
    explode(sensor, 0.40)

    board = cube("Logic PCB", (-2.18, 0, 0.05), (0.10, 1.67, 1.8), green, 0.025)
    explode(board, -1.25)
    for i in range(10):
        y = (i % 5 - 2) * 0.28
        z = (i // 5 - 0.5) * 0.55
        chip = cube("IC chip %02d" % i, (-2.31, y, z), (0.065, 0.20, 0.22), dark, 0.012)
        explode(chip, -1.25)

    # Lens elements, multiple independent parts travel along the X axis.
    barrel = cylinder("Outer barrel", 0.77, 0.88, 0.68, dark)
    explode(barrel, 0.83, 0.06)
    for index, x in enumerate((1.18, 1.43, 1.70)):
        optic = cylinder("Lens glass %d" % (index + 1), x, 0.74 - index * 0.06, 0.07, glass)
        explode(optic, 1.16 + 0.42 * index)
        rim = torus("Lens ring %d" % (index + 1), x, 0.77 - index * 0.06, 0.045, titanium)
        explode(rim, 1.16 + 0.42 * index, 0.11)
    torus("Front gold accent", 1.90, 0.82, 0.035, copper)
    front = cylinder("Front protective optic", 1.98, 0.73, 0.045, glass)
    explode(front, 2.45)
    lens_cap = torus("Retaining ring", 2.05, 0.84, 0.055, graphite)
    explode(lens_cap, 2.62, 0.08)
    for i in range(8):
        a = i / 8 * math.tau
        bolt = cube(
            "Mount screw %02d" % i,
            (-0.04, math.cos(a) * 0.90, math.sin(a) * 0.90),
            (0.07, 0.075, 0.075), titanium, 0.01,
        )
        explode(bolt, 0.3)
    for i in range(4):
        led = cube("Indicator %d" % i, (-1.05, -1.29, -0.61 + 0.22 * i),
                   (0.07, 0.06, 0.09), glow, 0.008)
        explode(led, -0.10)

    # Ground and a little atmospheric depth; no external assets.
    floor = cube("Matte display platform", (0.5, 0, -2.15), (10.0, 8.0, 0.15), dark, 0.08)
    random.seed(31)
    for i in range(40):
        x = random.uniform(-4.1, 4.1)
        y = random.uniform(-3.2, 2.5)
        z = random.uniform(-1.6, 3.0)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4,
                                             radius=random.uniform(0.005, 0.022),
                                             location=(x, y, z))
        bpy.context.object.name = "Floating dust %02d" % i
        bpy.context.object.data.materials.append(glow if i % 4 == 0 else titanium)

    area_light("Warm overhead softbox", (2, -4, 7), 950, (1.0, 0.73, 0.48), 5.0)
    area_light("Cool blue rim", (-4, 2, 4), 1250, (0.30, 0.61, 1.0), 4.5)
    area_light("Front fill", (3, -8, -1), 560, (0.82, 0.91, 1.0), 6.0)
    camera_rig()
    scene.view_settings.view_transform = "AgX"
    scene.frame_set(1)
    return scene


def main():
    args = cli()
    out = Path(args.output).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    scene = build_scene()
    if args.quality == "preview":
        scene.render.resolution_percentage = 35
        scene.cycles.samples = 12
    else:
        scene.render.resolution_percentage = 100
        scene.cycles.samples = 64

    blend_path = out / "camera_exploded.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    if args.render == "still":
        scene.frame_set(235)
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(out / "camera_exploded_preview.png")
        bpy.ops.render.render(write_still=True)
    elif args.render == "animation":
        scene.frame_set(1)
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
        scene.render.filepath = str(out / "camera_exploded.mp4")
        bpy.ops.render.render(animation=True)
    print("Cikti klasoru:", out)


if __name__ == "__main__":
    main()
