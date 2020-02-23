import sys

from config import options


def help():
    return """Usage:
To migrate or create the database:
    python api.py migrate [--option=value]

To start the server run:
    python api.py start_server [--option=value]
"""


def start_server():
    """This function will start the server on all of the ports defined as
    api_ports in the options"""
    from tornado import httpserver, ioloop, web
    from tornado.options import options


    class Application(web.Application):
    
        def __init__(self):
            from routes import ROUTES
            from controllers import ErrorHandler


            settings = {
                'debug': options.debug,
                'autoescape': None,
                'default_handler_class': ErrorHandler,
                'cookie_secret': 'secret CHANGE THIS',
                'static_path': options.static_path,
                'template_path': options.template_path,
            }

            web.Application.__init__(self, ROUTES, **settings)


    try:
        for port in options.ports:
            application = Application()
            http_server = httpserver.HTTPServer(application)

            print('API STARTED ON PORT: ', port)

            http_server.listen(port)

        ioloop.IOLoop.current().start()
    except Exception as e:
        print(e)


def migrate():
    """this function will run all of the migrations for the database
    tables"""
    from models import migrate_tables

    migrate_tables()


if __name__ == '__main__':
    args = sys.argv[1:]

    options.parse_command_line(args)

    if not len(args):
        print(help())
    elif args[0] == 'migrate':
        migrate()
    elif args[0] == 'start_server':
        start_server()
    else:
        print(help())
