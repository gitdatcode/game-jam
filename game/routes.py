from controllers import (IndexController, StoryController, SceneController)

ROUTES = (
    (r'/', IndexController),
    (r'/story/([\w\-]+)', StoryController),
    (r'/scene/([\w\-]+)', SceneController),
)
