#!/usr/bin/env python
import logging
import settings
import motor
import redis
from pymongo.errors import ConnectionFailure
from argparse import ArgumentTypeError
from logging.handlers import TimedRotatingFileHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.log import LogFormatter
from tornado.options import parse_command_line, define, options, parse_config_file
from tornado.web import Application
from handlers import logger
from urls import BASE_ROUTES

define("mongodb_url", default="mongodb://nexus:nexus@localhost:27017", help="Main user DB")
define("mongodb_name", default="nxg_app_base", help="DB name")
define("redis_url", default="redis://localhost:6379/0", multiple=False,
       help="Main user mem_cache servers")

define("auth_server", default="http://oauth.qavm.com:9420", help="auth_server")
define("openapi_server", default="http://api.qavm.com:9420", help="openapi_server")
define("app_host", default="http://nbad.qavm.app:8101", help="app_host")

define("auth_bypass", default=False, help="auth_bypass")
define("port", default=7777, help="port to listen on")
define("debug", default=True, help="debug")
define("config", type=str, help="path to config file",
       callback=lambda path: parse_config_file(path, final=False))


def parse_logging_level(name):
    """
    根据settings中的配置生成logging的level
    :param name:
    :return:
    """
    level = SUPPORT_LOGGING_LEVELS.get(name.upper(), None)
    if level is None:
        raise ArgumentTypeError("level %s is invalid (choose from '%s')"
                                % (name, "', '".join(SUPPORT_LOGGING_LEVELS.keys())))
    return level


define("log_level",
       default=logging.DEBUG,
       type=parse_logging_level,
       help="Set the Python log level. If 'none', tornado won't touch the logging configuration.",
       metavar="debug|info|warning|error|none")

fm = LogFormatter(fmt='[%(asctime)s]%(color)s[%(levelname)s]%(end_color)s[%(module)s:%(lineno)d] %(message)s',
                  datefmt='%Y-%m-%d %H:%M:%S')


SUPPORT_LOGGING_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}


def create_db_connection(mongodb_url, db_name):
    """
    创建 Mongodb 连接
    :param mongodb_url:
    :param db_name:
    :return:
    """
    try:
        logger.debug(f"conn mongodb: {mongodb_url}")
        return motor.MotorClient(mongodb_url)[db_name]
    except ConnectionFailure:
        logger.error('Could not connect to mongodb. exit')
        exit(1)
        return None


def create_redis_connection(url):
    """
    创建 Redis 连接
    :param url: redis_url
    :return:
    """
    try:
        logger.debug(f"conn redis: {url}")
        return redis.from_url(url)
    except redis.ConnectionError:
        logger.warning('Could not connect to redis.')
        return None


def main():
    db_conn = create_db_connection(options.mongodb_url, options.mongodb_name)
    redis_conn = create_redis_connection(options.redis_url)

    handlers = []
    for handler in BASE_ROUTES.values():
        handlers.extend(handler)

    app = Application(handlers=handlers, debug=options.debug, **settings.APPLICATION_SETTINGS)

    app.settings['db'] = db_conn
    app.settings['redis'] = redis_conn
    app.settings['auth_server'] = options.auth_server
    app.settings['auth_bypass'] = options.auth_bypass
    app.settings['openapi_server'] = options.openapi_server
    app.settings['app_host'] = options.app_host

    # app.listen(options.port)
    server = HTTPServer(app, xheaders=True)
    server.bind(options.port)
    server.start(1)
    IOLoop.current().start()


if __name__ == '__main__':
    parse_command_line()
    fm = LogFormatter(fmt='[%(asctime)s]%(color)s[%(levelname)s]%(end_color)s[%(module)s:%(lineno)d] %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = TimedRotatingFileHandler('temp.log', when="d", interval=1, backupCount=30)
    logger.addHandler(file_handler)
    logger.setLevel(options.log_level)
    for logHandler in logger.handlers:
        logHandler.setFormatter(fm)

    logger.debug('start')
    main()
