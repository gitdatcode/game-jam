import os
import sys

from tornado.options import (options, define, parse_config_file,
    parse_command_line)


HERE = os.path.dirname(__file__)
CLIENT_DIR = os.path.abspath(os.path.join(HERE, '..', 'client'))
HOUR = 60 * 60
DAY = 24 * HOUR
debug = ['development', 'testing']

# check the local environment file to see which environment we're in
try:
    ENVIRONMENT = os.environ.get('datcode_environment', None)

    if not ENVIRONMENT:
        raise Exception()
except Exception:
    try:
        with open('{}/environment'.format(HERE), 'r') as f:
            ENVIRONMENT = f.readline().lower().strip()
    except Exception:
        ENVIRONMENT = 'development'


# app configuration
define('environment', ENVIRONMENT)
define('debug', True if ENVIRONMENT in debug else False)
define('autoreload', True if ENVIRONMENT in debug else False)
define('ports', [8877])
define('static_path', os.path.join(HERE, 'view', 'static'))
define('template_path', os.path.join(HERE, 'view', 'template'))
define('user_cookie_name', 'u')
define('user_game_name', 'ug')


# database config
define('db_host', 'localhost')
define('db_port', 3306)
define('db_user', 'root')
define('db_pass', '')
define('db_database', 'game_jam')


# load the local override config
local_override = os.path.join(HERE, '{}.config.py'.format(ENVIRONMENT))

if os.path.isfile(local_override):
    parse_config_file(local_override, final=False)


# load the cli flags to override pre-defined config settings
# remove app.py if it is the first arg. This is done because starting the sever
# by running python app.py start_server --arg=value is not parsable by
# tornado's parse_command_line function
args = sys.argv[:]

if args[0] == 'app.py':
    args = args[1:]

parse_command_line(args=args)
