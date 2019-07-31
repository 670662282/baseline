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

define("mongodb_hosts", default="127.0.0.1:27017", help="Main user DB")
define("redis_host", default="127.0.0.1:6834", multiple=False,
       help="Main user memcache servers")
define("port", default=7777, help="port to listen on")
define("cache", default=True, help="port to listen on")
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


def create_db_connection(mongodb_host, db_name):
    """
    创建 Mongodb 连接
    :param mongodb_host:
    :param db_name:
    :return:
    """
    try:
        return motor.MotorClient(mongodb_host)[db_name]
    except ConnectionFailure:
        logger.error('Could not connect to mongodb. exit')
        exit(1)
        return None


def create_redis_connection(redis_host, redis_port, redis_password=''):
    """
    创建 Redis 连接
    :param redis_host:
    :param redis_port:
    :param redis_password:
    :return:
    """
    try:
        if redis_password:
            redis_conn = redis.Redis(
                connection_pool=redis.ConnectionPool(host=redis_host, port=redis_port, db=0, password=redis_password))
        else:
            redis_conn = redis.Redis(connection_pool=redis.ConnectionPool(host=redis_host, port=redis_port, db=0))
        return redis_conn
    except redis.ConnectionError:
        logger.warning('Could not connect to redis.')
        return None


def main():
    handlers = []

    for handler in BASE_ROUTES.values():
        handlers.extend(handler)
    app = Application(handlers=handlers, debug=options.debug, **settings.APPLICATION_SETTINGS)
    print(options.debug)
    print(options.port)
    app.settings['cache'] = options.cache
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
    logger.warning('xxxx')
    logger.debug('xxxx')
    main()
