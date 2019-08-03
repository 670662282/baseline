from common.cache import cached
from handlers.base_handler import BaseHandler


class HelpInfoHandler(BaseHandler):

    async def get_help_info(self, **kwargs):
        help_info = await self._help()
        kwargs.setdefault('access_token', 'default token')
        return self.write_json(f'{help_info}, {kwargs.get("access_token")}')

    async def post_help_info(self, **kwargs):
        help_info = await self._help()
        kwargs.setdefault('access_token', 'default token')
        return self.write_json(f'{help_info}, {kwargs.get("access_token")}')

    @cached(expire_in=86400)
    async def _help(self):
        return {'code': 0, 'result': 'success'}
