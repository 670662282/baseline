import json

from tornado.escape import json_decode
from tornado.web import RequestHandler, HTTPError
from handlers import logger, HTTP_ERRORS


class BaseHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def initialize(self):
        self.json_args = dict()

    def db_conn(self):
        """Returns database connection abstraction
        If no database connection is available, raises an AttributeError
        """
        if not self.settings.get('db'):
            raise AttributeError("No database connection found.")
        return self.settings.get('db')

    def redis_conn(self):
        """Returns redis connection abstraction
        If no redis connection is available, raises an AttributeError
        """
        if not self.settings.get('redis'):
            raise AttributeError("No redis connection found.")
        return self.settings.get('redis')

    def prepare(self):
        """Called at the beginning of a request before  `get`/`post`/etc.

        Override this method to perform common initialization regardless
        of the request method.

        Asynchronous support: Decorate this method with `.gen.coroutine`
        or use ``async def`` to make it asynchronous (the
        `asynchronous` decorator cannot be used on `prepare`).
        If this method returns a `.Future` execution will not proceed
        until the `.Future` is done.

        .. version added:: 3.1
           Asynchronous support.
        """
        if self.request.body and self.request.headers.get("Content-Type", "").startswith("application/json"):
            try:
                logger.debug(f"json_args:{self.request.body}")
                self.json_args = json_decode(self.request.body)
                self.request.arguments.update(self.json_args)
            except ValueError:
                self.write_error(405, msg='Unable to parse JSON.')  # Bad RequestHandler

    async def get(self):
        logger.debug("route path: BaseHandler -> get")
        return await self._dispatch('get')

    async def post(self):
        logger.debug("route path: BaseHandler -> post")
        return await self._dispatch('post')

    async def put(self):
        logger.debug("route path: BaseHandler -> put")
        return await self._dispatch('put')

    async def delete(self):
        logger.debug("route path: BaseHandler -> delete")
        return await self._dispatch('delete')

    async def _dispatch(self, method):
        kwargs = {}
        # Sanitize argument lists:
        if self.request.arguments:
            kwargs = self._delist_arguments(self.request.arguments)
        path = self.request.uri.split('?')[0]
        path_segs = path.split('/')
        if len(path_segs) < 2:
            logger.debug("len(path_segs) < 2")
            raise HTTPError(**HTTP_ERRORS['status_404'])

        method = f"{method}_{path_segs[-1]}"
        logger.debug("path: %s, method: %s" % (path, method))

        func = getattr(self, method, None)
        if callable(func):
            return await func(**kwargs)
        else:
            logger.debug("func no callable")
            if self.is_exist_supported_method(path_segs[-1]):
                    raise HTTPError(**HTTP_ERRORS['status_405'])

            raise HTTPError(**HTTP_ERRORS['status_404'])

    def is_exist_supported_method(self, method_name):
        for method in self.SUPPORTED_METHODS:
            if callable(getattr(self, f"{method.lower()}_{method_name}", None)):
                return True
        return False

    def get_current_user(self):
        """
        Override to determine the current user from, e.g., a cookie.
        This method may not be a coroutine.
        """
        return self._current_user

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    def _delist_arguments(self, arguments):
        logger.debug(f"before_args:{arguments}")
        # for arg, value in arguments.items():
        #     logger.debug(f'{type(value)}')
        #     if isinstance(value, list):
        #         arguments[arg] = [v.decode("utf-8").strip() if isinstance(v, bytes) else v.strip() for v in value]

        def decode_(v):
            return self.decode_argument(v).strip()
        arguments = {k: list(map(decode_, v)) for k, v in arguments.items()}

        logger.debug(f"after_args:{arguments}")
        return arguments

    def write_error(self, status_code, **kwargs):
        return self.write_json(None, status_code, kwargs.get('msg') or self._reason)

    def write_error_msg(self, data):
        return self.write_json(None, data['code'], data['msg'])

    def write_json(self, data, status_code=0, msg='success.'):
        result = {'code': status_code, 'msg': msg}
        if data is not None:
            result['result'] = data
        self.finish(json.dumps(result))
