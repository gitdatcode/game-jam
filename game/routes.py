from controllers import (IndexController, LoginController, StoryController,
    SceneController)

ROUTES = (
    (r'/', IndexController),
    (r'/login', LoginController),

    # load story
    (r'/story(?:/([\w\-]+)?)?', StoryController),

    # load story by story.eyed and game.id
    # this is used to set the active game cookie
    (r'/story/([\w\-]+)/game/([\w]+)', StoryController),

    # load scene by option.eyed and scene.eyed
    (r'/option/([\w\-]+)/scene/([\w\-]+)', SceneController),

    # load scene by option.eyed and scene.eyed and game.id
    # this is used to set the active game cookie
    (r'/option/([\w\-]+)/scene/([\w\-]+)/game/([\w]+)', SceneController),
)
