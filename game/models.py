from tornado.options import options

import peeweedbevolve

from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model


def database():
    return MySQLDatabase(database=options.db_database, user=options.db_user,
        password=options.db_pass, host=options.db_host,
        port=options.db_port)


DATABASE = database()


class BaseModel(Model):
    __recurse_data_relationships__ = False

    class Meta:
        database = DATABASE

    @property
    def data(self):
        return model_to_dict(self,
            recurse=self.__recurse_data_relationships__)


class Story(BaseModel):
    id = AutoField()
    title = CharField()
    description = TextField()
    image = TextField(null=True)
    image_mobile = TextField(null=True)
    sound_background = TextField(null=True)
    active = BooleanField(default=True)


class Scene(BaseModel):
    id = AutoField()
    story = ForeignKeyField(Story, backref='scenes')
    title = CharField(null=True)
    content = TextField()
    order = IntegerField(default=0)
    image = TextField(null=True)
    image_mobile = TextField(null=True)
    sound_load = TextField(null=True)
    sound_unload = TextField(null=True)
    sound_background = TextField(null=True)
    css = TextField(null=True)
    js = TextField(null=True)

    @property
    def data(self):
        """this should collect the scene, its options, and all of the options'
        scene's image and audio assets to allow the front-end to preload them
        """
        next_scenes = []
        data = super().data
        data['preload'] = {
            'images': [],
            'audio': [],
        }
        data['Options'] = []

        if 'image' in data and data['image'] is not None:
            data['preload']['images'].append(data['image'])

        if 'image_mobile' in data and data['image_mobile'] is not None:
            data['preload']['images'].append(data['image_mobile'])

        if 'sound_load' in data and data['sound_load'] is not None:
            data['preload']['audio'].append(data['sound_load'])

        if 'sound_unload' in data and data['sound_unload'] is not None:
            data['preload']['audio'].append(data['sound_unload'])

        if 'sound_background' in data and data['sound_background'] is not None:
            data['preload']['audio'].append(data['sound_background'])

        options = (SceneOption
                   .select()
                   .where(SceneOption.scene_id == self.id)
                   .order_by(SceneOption.order))

        for option in options:
            data['Options'].append(option.data)

            if option.next_scene:
                next_scenes.append(option.next_scene)

        if next_scenes:
            ns = Scene.select().where(Scene.id.in_(next_scenes))\
                .order_by(Scene.order)

            for scene in ns:
                if scene.image:
                    data['preload']['images'].append(scene.image)

                if scene.image_mobile:
                    data['preload']['images'].append(scene.image_mobile)

                if scene.sound_load:
                    data['preload']['audio'].append(scene.sound_load)

                if scene.sound_unload:
                    data['preload']['audio'].append(scene.sound_unload)

                if scene.sound_background:
                    data['preload']['audio'].append(scene.sound_background)

        return data


class SceneOption(BaseModel):
    id = AutoField()
    scene = ForeignKeyField(Scene, backref='options')
    order = IntegerField(default=0)
    text = TextField()
    tool_tip = TextField(null=True)
    value = FloatField(default=0)
    next_scene = IntegerField()


def create_tables():
    tables = [Story, Scene, SceneOption]

    DATABASE.connect()
    DATABASE.create_tables(tables)


def migrate_tables():
    DATABASE.evolve()
