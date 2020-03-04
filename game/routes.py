from controllers import (IndexController, LoginController, StoryController,
    SceneController)

ROUTES = (
    (r'/', IndexController),
    (r'/login', LoginController),
    (r'/story(?:/([\w\-]+)?)?', StoryController),
    (r'/option/([\w\-]+)/scene/([\w\-]+)', SceneController),
)
