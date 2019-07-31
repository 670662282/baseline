import logging

from handlers.base_handler import BaseHandler


class APINotFoundHandler(BaseHandler):
    def get(self):
        log = logging.getLogger()
        log.warning("hahaha")
        return self.write('no_found')
