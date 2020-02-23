from tornado import web

from models import Story, Scene


class BaseController(web.RequestHandler):

    @property
    def is_ajax(self):
        return ('X-Requested-With' in self.request.headers and
            self.request.headers['X-Requested-With'] == 'XMLHttpRequest')


class IndexController(BaseController):

    def get(self):
        home = self.render_string('index.html')

        return self.write(home)


class StoryController(BaseController):

    def get(self, story_id=None):
        # if there is no story_id grab the first one
        if story_id:
            story = Story.select().limit(1).get()
        else:
            story = Story.select().where(Story.id == story_id).get()

        page = self.render_string('story.html', story=story)
        self.write(page)


class SceneController(BaseController):

    def get(self, scene_id):
        scene = Scene.select().where(Scene.id == scene_id).get()
        content = self.render_string('scene.html', scene=scene.data)
        print(scene.data)
        if self.is_ajax:
            resp = {
                'content': content,
                'scent': scene,
            }

            return self.write(resp)

        return self.write(content)


class ErrorHandler:
    pass