import os
import shutil

import bpy
from bpy.types import Operator, Scene
from PIL import Image

bl_info = {
    'name': 'Rendering GIF animations',
    'category': 'Render',
    'author': 'Lady Blizzardess',
    'version': (1, 0),
    'blender': (2, 80, 0),
    'location': 'Properties > Output',
    'description': 'Creating animated gifs',
    'warning': 'You need a PIL library for your python.',
    'doc_url': ''
}


class CreateGif(Operator):
    bl_idname = 'render.create_gif'
    bl_label = 'Create .gif'
    bl_description = ('Write an animation to a gif file with choosen properties\n'
                      'WARNING: It will take a lot of time and memory, don\'t forget save your project.')
    bl_options = {'REGISTER'}

    def execute(self, context):
        file_path = context.scene.render.filepath
        gif_name = context.scene.gifaddon_file_name
        optimize = context.scene.gifaddon_optimize
        duration = int(round(1000 / context.scene.render.fps))
        loop = context.scene.gifaddon_loop
        save_frames = context.scene.gifaddon_save_frames

        tmp_path = file_path + 'tmp\\'
        shutil.rmtree(tmp_path, ignore_errors=True)
        os.mkdir(tmp_path)
        context.scene.render.filepath, old_path = tmp_path, context.scene.render.filepath

        bpy.ops.render.render(animation=True)

        frames_names = os.listdir(tmp_path)
        frames_names.sort()
        frames = []
        for frame in frames_names:
            frames.append(Image.open(tmp_path + frame))

        frames[0].save(f'{file_path}{gif_name}.gif',
                       save_all=True,
                       append_images=frames[1:],
                       transparency=0,
                       optimize=optimize,
                       duration=duration,
                       loop=loop)

        if save_frames:
            os.rename(tmp_path, f'{file_path}{gif_name}-frames')
        else:
            shutil.rmtree(tmp_path, ignore_errors=True)
        context.scene.render.filepath = old_path
        return {'FINISHED'}


class CreateGifPanel(bpy.types.Panel):
    bl_idname = 'create_gif'
    bl_label = 'Record animation in .gif'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'gifaddon_file_name')
        row = layout.row()
        row.prop(context.scene, 'gifaddon_loop')
        split = layout.split()
        col = split.column()
        col.prop(context.scene, 'gifaddon_optimize')
        col = split.column(align=True)
        col.prop(context.scene, 'gifaddon_save_frames')
        row = layout.row()
        row.operator('render.create_gif')


def register():
    bpy.utils.register_class(CreateGif)
    bpy.utils.register_class(CreateGifPanel)

    Scene.gifaddon_file_name = bpy.props.StringProperty(
        name='File name',
        default='Animation'
    )
    Scene.gifaddon_optimize = bpy.props.BoolProperty(
        name='Optimize',
        description='Remove unused colors to get a smaller output file'
    )
    Scene.gifaddon_loop = bpy.props.IntProperty(
        name='Loop',
        description='The number of cycles that our GIF animation will perform.\n0 means infinite cycle.',
        min=0,
        max=10
    )
    Scene.gifaddon_save_frames = bpy.props.BoolProperty(
        name='Save frames',
        description='Save all render frames to separate directory.'
    )


def unregister():
    bpy.utils.unregister_class(CreateGifPanel)
    bpy.utils.unregister_class(CreateGif)
    del bpy.types.Scene.gifaddon_file_name
    del bpy.types.Scene.gifaddon_optimize
    del bpy.types.Scene.gifaddon_loop
    del bpy.types.Scene.gifaddon_save_frames
