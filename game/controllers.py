import functools
import hashlib

from tornado import web

from config import options
from models import Story, Scene, User, UserGame


def loggedin(method):
    """
    simple decorator used to see if there is session cookie set
    """
    @functools.wraps(method)
    def _method(self, *args, **kwargs):
        if self.user_id is not None:
            res = method(self, *args, **kwargs)

            return res

        return self.redirect('/login')

    return _method


class BaseController(web.RequestHandler):

    @property
    def is_ajax(self):
        return ('X-Requested-With' in self.request.headers and
            self.request.headers['X-Requested-With'] == 'XMLHttpRequest')

    def page(self, title, content):
        page = self.render_string('page.html', title=title, content=content)

        return self.write(page)

    @property
    def user_id(self):
        user = self.get_secure_cookie(options.user_cookie_name)

        if user:
            return int(user.decode('utf-8'))
        else:
            return None

    @property
    def game_id(self):
        user_game = self.get_secure_cookie(options.user_game_name)

        if user_game:
            return int(user_game.decode('utf-8'))
        else:
            return None

    @property
    def session_user(self):
        user_id = self.user_id

        if user_id:
            return User.select().where(User.id==user_id).get()

        return None

    @property
    def session_game(self):
        game_id = self.game_id

        if game_id:
            return UserGame.select().where(UserGame.id == game_id).get()

        return None

    def check_user_password(self, user, password):
        return hashlib.md5(password.encode('utf-8')).hexdigest()\
            == user.password

    def login(self, user_id):
        self.set_secure_cookie(options.user_cookie_name, str(user_id))
        self.redirect('/story')

    def set_game(self, user_game):
        self.set_secure_cookie(options.user_game_name, str(user_game.id))

    def continue_game(self):
        user = self.session_user


class IndexController(BaseController):

    def get(self):
        home = self.render_string('index.html')

        return self.page(title='**INDEXPAGE', content=home)


class LoginController(BaseController):

    def get(self, errors=None):
        errors = errors or {}
        login = self.render_string('login.html', errors=errors)

        return self.page(title='Login', content=login)

    def post(self):
        """simple login logic:
        if the username exists check the password
        else create a user with the supplied username and password
        redirect the user to the story select page
        if there are any errors, redirect back to the login form with errors
        """
        errors = []
        username = self.get_argument('username')
        password = self.get_argument('password')

        if not username:
            errors.append('username required')

        if not password:
            errors.append('password required')
        else:
            password = password.strip()

            if len(password) < 4:
                errors.append('password must be at least four characters')
            elif len(password) > 30:
                errors.append('password cannot be more than 30 characters')

        if errors:
            return self.get(errors=errors)

        try:
            user = User.select().where(User.username==username).get()
            found = self.check_user_password(user, password)

            if not found:
                invalid = ['invalid username/password combo',]
                return self.get(errors=invalid)

            self.login(user.id)
        except:
            # create a user
            pw = hashlib.md5(password.encode('utf-8')).hexdigest()
            user = User.create(username=username, password=pw)
            self.login(user.id)


class StoryController(BaseController):

    @loggedin
    def get(self, story_eyed=None):
        # if there is no story_id render the story select page
        if story_eyed:
            user = self.session_user
            story = Story.select().where(Story.eyed==story_eyed).get()
            scene = Scene.select().where(Scene.story==story,
                Scene.start_scene==True).get()
            user_game, _ = UserGame.get_or_create(user=user, story=story)
            page = self.render_string('story.html', story=story, scene=scene)
            self.set_game(user_game)

            return self.page(title='**STORYPAGE', content=page)

        stories = Story.select()
        page = self.render_string('story_select.html', stories=stories)

        return self.page(title='*******SELECT STORY', content=page)


class SceneController(BaseController):

    @loggedin
    def get(self, option_eyed, scene_eyed):
        scene = Scene.select().where(Scene.eyed == scene_eyed).get()
        content = self.render_string('scene.html', scene=scene.data)
        user_game = self.session_game

        if user_game.options_seen:
            seen = user_game.options_seen.split(',').append(scene.eyed)
        else:
            seen = [scene.eyed,]

        seen = ','.join(seen)
        user_game.options_seen = seen
        user_game.last_scene = scene.eyed
        user_game.save()

        if self.is_ajax:
            resp = {
                'content': content.decode('utf-8'),
                'scene': scene.data,
            }

            return self.write(resp)

        return self.page(title='**SCENEPAGE', content=content)


class ErrorHandler:
    pass
