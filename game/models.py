from uuid import uuid4
import hashlib
from datetime import datetime

from tornado.options import options

import peeweedbevolve

from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model


def database():
    return MySQLDatabase(database=options.db_database, user=options.db_user,
        password=options.db_pass, host=options.db_host,
        port=options.db_port)


DATABASE = database()


def _uid_():
    return str(uuid4()).replace('-', '')


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
    eyed = CharField(unique=True, default=_uid_)
    title = CharField()
    description = TextField()
    image = TextField(null=True)
    image_mobile = TextField(null=True)
    sound_background = TextField(null=True)
    active = BooleanField(default=True)

    @classmethod
    def get_user_stories(cls, user_id):
        stories = Story.select()
        data = []

        for story in stories:
            story_data = story.data

            try:
                ug = (UserGame.select().where(UserGame.story==story,
                    UserGame.user_id==user_id)
                    .order_by(UserGame.date_completed.asc(),
                        UserGame.date_created.desc()))
                user_games = [us.data for us in ug]
            except:
                user_games = []

            story_data['UserGames'] = user_games
            data.append(story_data)

        return data


class Scene(BaseModel):
    id = AutoField()
    eyed = CharField(unique=True, default=_uid_)
    story = ForeignKeyField(Story, backref='scenes')
    done_scene = ForeignKeyField('self', null=True)
    title = CharField(null=True)
    content = TextField()
    order = IntegerField(default=0)
    start_scene = BooleanField(default=False)
    end_scene = BooleanField(default=False)
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
        next_scenes = set()
        data = super().data
        data['preload'] = {
            'images': set(),
            'audio': set(),
        }
        data['Options'] = []

        if self.image:
            data['preload']['images'].add(self.image)

        if self.image_mobile:
            data['preload']['images'].add(self.image_mobile)

        if self.sound_load:
            data['preload']['audio'].add(self.sound_load)

        if self.sound_unload:
            data['preload']['audio'].add(self.sound_unload)

        if self.sound_background:
            data['preload']['audio'].add(self.sound_background)

        options = (SceneOption
                   .select()
                   .where(SceneOption.scene_id == self.id)
                   .order_by(SceneOption.order))

        for option in options:
            data['Options'].append(option.data)

            if option.next_scene:
                next_scenes.add(option.next_scene)

        if next_scenes:
            ns = Scene.select().where(Scene.id.in_(next_scenes))\
                .order_by(Scene.order)

            for scene in ns:
                if scene.image:
                    data['preload']['images'].add(scene.image)

                if scene.image_mobile:
                    data['preload']['images'].add(scene.image_mobile)

                if scene.sound_load:
                    data['preload']['audio'].add(scene.sound_load)

                if scene.sound_unload:
                    data['preload']['audio'].add(scene.sound_unload)

                if scene.sound_background:
                    data['preload']['audio'].add(scene.sound_background)

        # fix sets so that data can be serialized
        data['preload']['images'] = list(data['preload']['images'])
        data['preload']['audio'] = list(data['preload']['audio'])

        return data

    def data_from_user(self, user, game):
        """this method will figure out which options the user has already seen
        if there are no options left, the scene's done_scene is chcked,
        if that doesnt exist, the game's end scene is returned"""
        data = self.data
        options_seen = game.options_seen.split(',')
        fixed_options = []

        for option in data['Options']:
            if option['eyed'] not in options_seen:
                fixed_options.append(option)

        if len(fixed_options) == 0 and not self.end_scene:
            if self.done_scene:
                done = Scene.select().where(Scene.id==self.done_scene).get()
                return done.data_from_user(user, game)
            else:
                end = Scene.select().where(Scene.story==game.story,
                    Scene.end_scene==True).get()
                game.date_completed = datetime.now()
                game.save()

                return end.data

        data['Options'] = fixed_options
        return data


class SceneOption(BaseModel):
    id = AutoField()
    eyed = CharField(unique=True, default=_uid_)
    scene = ForeignKeyField(Scene, backref='options')
    order = IntegerField(default=0)
    text = TextField()
    tool_tip = TextField(null=True)
    value = FloatField(default=0)
    next_scene = CharField()


class User(BaseModel):
    id = AutoField()
    username = CharField(unique=True)
    password = TextField()


class UserGame(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User)
    story = ForeignKeyField(Story)
    last_scene = TextField(null=True)
    options_seen = TextField(default='')
    options_score = TextField(default='')
    date_created = DateTimeField(default=datetime.now())
    date_update = TimestampField()
    date_completed = DateTimeField(null=True)

    def add_last_seen(self, option, scene):
        seen = [] if not self.options_seen else self.options_seen.split(',')

        if option.eyed not in seen:
            self.add_score(option)
            seen.append(option.eyed)

        seen = ','.join(seen)
        self.options_seen = seen
        self.last_scene = scene.eyed
        self.save()

    def add_score(self, option):
        seen = [] if not self.options_seen else self.options_seen.split(',')
        score = [] if not self.options_score else self.options_score.split(',')

        if option.eyed not in seen and option.value is not None:
            score.append(str(option.value))

            self.options_score = ','.join(score)
            self.save()

    @property
    def score(self):
        try:
            scores = map(float, self.options_score.split(','))

            return sum(scores)
        except:
            return 0

    @property
    def data(self):
        data = super().data
        data['Score'] = self.score

        try:
            data['LastScene'] = (Scene.select()
                .where(Scene.eyed==self.last_scene).get().data)
        except:
            data['LastScene'] = None

        try:
            data['LastOption'] = self.options_seen.split(',')[-1]
        except:
            data['LastOption'] = None

        return data

def create_tables():
    tables = [Story, Scene, SceneOption, User, UserGame]

    DATABASE.connect()
    DATABASE.create_tables(tables)


def migrate_tables():
    DATABASE.evolve()
