import functools
import hashlib

from tornado import web

from config import options
from models import Story, Scene, SceneOption, User, UserGame


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
    def get(self, story_eyed=None, user_game_id=None):
        # if there is no story_id render the story select page
        user = self.session_user

        if story_eyed:
            story = Story.select().where(Story.eyed==story_eyed).get()
            scene = Scene.select().where(Scene.story==story,
                Scene.start_scene==True).get()
            page = self.render_string('story.html', story=story, scene=scene)

            try:
                if user_game_id is not None:
                    user_game = (UserGame.select()
                        .where(UserGame.id==user_game_id).get())
                else:
                    raise
            except:
                user_game = UserGame.create(user=user, story=story)

            self.set_game(user_game)

            return self.page(title='**STORYPAGE', content=page)

        stories = Story.get_user_stories(user_id=user.id)
        page = self.render_string('story_select.html', stories=stories)

        return self.page(title='*******SELECT STORY', content=page)


class SceneController(BaseController):

    @loggedin
    def get(self, option_eyed, scene_eyed, game_id=None):
        if game_id is not None:
            try:
                game = UserGame.select().where(UserGame.id==game_id).get()
                self.set_game(game)
            except:
                pass

        option = None
        scene = Scene.select().where(Scene.eyed == scene_eyed).get()
        user_game = self.session_game
        user = self.session_user

        if option_eyed and option_eyed not in ['0', '-']:
            option = SceneOption.select().where(
                SceneOption.eyed==option_eyed).get()
            user_game.add_last_seen(option, scene)

        data = scene.data_from_user(user, user_game)
        content = self.render_string('scene.html', scene=data)

        if self.is_ajax:
            resp = {
                'content': content.decode('utf-8'),
                'scene': data,
            }

            return self.write(resp)

        return self.page(title='**SCENEPAGE', content=content)


class ErrorHandler(BaseController):

    def get(self, *args, **kwargs):
        import pudb; pu.db

