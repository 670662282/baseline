from asyncio import sleep
from handlers.base_handler import BaseHandler


class HelpInfoHandler(BaseHandler):

    async def get_help_info(self, **kwargs):
        await sleep(1)
        kwargs.setdefault('access_token', 'default token')
        return self.write_json(f'test get help info, {kwargs.get("access_token")}')

    async def post_help_info(self, **kwargs):
        await sleep(1)
        kwargs.setdefault('access_token', 'default token')
        return self.write_json(f'test post help info, {kwargs.get("access_token")}')
