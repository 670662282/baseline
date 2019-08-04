# -*- coding: utf-8 -*-
import json
from time import time
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from common.constant import APP_STATUS_NORMAL
from common.lib.uuid import get_uuid
from common.result_code import PARAM_NOT_FOUND, PARAM_INVALID, SERVER_ERROR, NOT_FOUND, REMOTE_SERVER_ERROR
from handlers import logger, OAUTH_APPS
from handlers.base_handler import BaseHandler
from oauth.app_token import AppToken

__author__ = 'tengfei.wang'

"""
oauth model
    proved info for UI
    oauth for apps
    proved token for open API
"""


class OAuth2Handler(BaseHandler):
    token_keep_time = 60 * 90
    day = 60 * 60 * 24
    month = day * 29

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.app_token = AppToken(self.db_conn)
        self.app_host = self.settings['app_host']
        self.oauth_host = self.settings['auth_server']

    """
    get oauth status step 1
    """

    async def get_app_oauth_info(self, **kwargs):
        """ get app oauth status
        :param kwargs: app_name
               customer_id
        :return: {'status': status, 'is_first_install': is_first_install}
        """

        customer_id = kwargs.get('customer_id')
        app_name = kwargs.get('app_name')

        if not customer_id or not app_name:
            logger.error('request param not found')
            return self.write_error_msg(PARAM_NOT_FOUND)

        if OAUTH_APPS.get(app_name) is None:
            logger.error('app %s not found' % app_name)
            return self.write_error_msg(PARAM_INVALID)

        try:
            request_data = await self._get_app_oauth_info(app_name, customer_id)
            logger.info(f'oauth info is : {request_data}')
            return self.write_json(request_data)
        except Exception as e:
            logger.error(f'get base info error:{e}')
            return self.write_error_msg(SERVER_ERROR)

    async def _get_app_oauth_info(self, app_name, customer_id):
        status = 0
        is_first_install = 0
        app_token = await self.app_token.async_get_token_by_cid_aid(OAUTH_APPS[app_name]['app_id'], customer_id)
        if app_token:
            is_first_install = app_token['is_first_install']
            refresh_token_ctime = app_token['refresh_token_ctime']
            logger.info(
                f'refresh token has used {int((time() - refresh_token_ctime)) / self.day:{0.2}} days')
            if not self._is_need_refreshed(app_token):
                status = 1
        return {'status': status, 'is_first_install': is_first_install}

    def _is_need_refreshed(self, app_token):
        if (int(time() - app_token['refresh_token_ctime'])) <= self.month:
            return False
        return True

    """
    get oauth curl  step 2
    """

    async def get_oauth_url(self, **kwargs):
        """get app oauth information and connect url
        :param kwargs: app_name
                       customer_id
                       xspe
                       fe_url
        :return: {'status': status, 'is_first_install': is_first_install, 'oauth_url': oauth_url}
        """

        fe_url = kwargs.get('fe_url')
        xspe = kwargs.get('xspe')
        customer_id = kwargs.get('customer_id')
        app_name = kwargs.get('app_name')
        if not customer_id or not fe_url or not xspe or not app_name:
            logger.error('request param not found')
            return self.write_error_msg(PARAM_NOT_FOUND)

        if not OAUTH_APPS.get(app_name):
            logger.error('app %s not found' % app_name)
            return self.write_error_msg(PARAM_INVALID)

        try:
            oauth_info = await self._get_app_oauth_info(app_name, customer_id)
            app_info = OAUTH_APPS[app_name]
            state_value = {'app_id': app_info['app_id'], 'customer_id': customer_id, 'app_name': app_name,
                           'fe_url': fe_url, 'is_first_install': oauth_info['is_first_install']}
            state = get_uuid()
            self.redis_conn.set(state, str(state_value), 60)

            oauth_url = f'{self.oauth_host}/oauth/connect?app_id={app_info["app_id"]}' \
                        f'&response_type=code' \
                        f'&scope=install_login' \
                        f'&state={state}' \
                        f'&xspe={xspe}' \
                        f'&customer_id={customer_id}' \
                        f'&redirect_uri={self.app_host}{app_info["redirect_uri"]}'

            oauth_info.update({'oauth_url': oauth_url})
            logger.info(f'oauth info is: {oauth_info}')
            return self.write_json(oauth_info)
        except Exception as e:
            logger.error(f'get oauth url error:{e}')
            return self.write_error_msg(SERVER_ERROR)

    """
    callback for oauth  step 3
    """

    async def get_callback(self, **kwargs):
        """
        :param kwargs:
                 code
                 state
        :return: redirect to fe_url
        """
        re_state = kwargs.get("state")
        code = kwargs.get("code")

        try:
            state_value = self.redis_conn.get(re_state)
            logger.info('state value is %s:' % state_value)
        except Exception as e:
            logger.error(f'get state from redis error: {e}')
            return self.write_error_msg(SERVER_ERROR)

        self.redis_conn.delete(re_state)
        if not state_value:
            return self.write_error_msg(PARAM_INVALID)

        dict_state_value = eval(state_value)

        app_id = dict_state_value['app_id']
        app_info = OAUTH_APPS[dict_state_value['app_name']]

        url = f"{self.oauth_host}/oauth/access_token?app_id={app_id}&secret={app_info['secret']}&code={code}"
        logger.info(f'begin: {url}')
        request = HTTPRequest(url, method="POST", allow_nonstandard_methods=True)
        try:
            http_response = await AsyncHTTPClient().fetch(request)
        except Exception as e:
            logger.error(f'ger refresh token error: {e}')
            return self.write_error_msg(REMOTE_SERVER_ERROR)

        token_result = json.loads(str(http_response.body, encoding='utf-8'))
        if token_result.get('code') != 0:
            return self.write_json(None, status_code=token_result.get('code', ''), msg=token_result.get('msg', ''))
        logger.info(f'remote result is: {token_result}')

        customer_id = dict_state_value['customer_id']
        try:
            app_token = token_result.get('result')
            app_token['app_id'] = app_id
            app_token['customer_id'] = customer_id
            app_token['is_first_install'] = dict_state_value['is_first_install']
            # app status used for customer uninstall, app 0: install 1:uninstall
            app_token['status'] = APP_STATUS_NORMAL
            app_token['access_token_ctime'] = int(time())
            app_token['refresh_token_ctime'] = int(time())

            db_app_token = await self.app_token.async_get_token_by_cid_aid(app_id=app_id, customer_id=customer_id)
            logger.info(f'db_app_token: {db_app_token}')

            try:
                await self._save_app_token(dict_state_value, app_token, db_app_token)
            except Exception as e:
                logger.error(f'save app_token error :{e}')
                return self.write_error_msg(SERVER_ERROR)

            return self.redirect(dict_state_value['fe_url'])
        except Exception as e:
            logger.error('get token error: %s' % str(e))
            return self.write_error_msg(SERVER_ERROR)

    async def _save_app_token(self, dict_state_value, app_token, db_app_token):
        """save app token: update it if exist, insert if not exist
        :param app_id:
        :param app_token:
        :param customer_id:
        :param db_app_token:
        :return:
        """
        access_token_key = f"{dict_state_value['app_id']}-{dict_state_value['customer_id']}"
        if not db_app_token:
            app_token['ctime'] = int(time())
            await self.app_token.async_insert(app_token)
        else:
            await self.app_token.async_update(dict_state_value['app_id'], dict_state_value['customer_id'], app_token)
        self.redis_conn.set(access_token_key, app_token['access_token'], self.token_keep_time)

    """
    update app is_first_install status step 4
    """
    async def check_first_install(self, **kwargs):
        """ check is first install
        :param kwargs:
                 app_name
                 customer_id
                 is_first_install   only 0 or 1
        :return: update result
        """
        app_name = kwargs.get('app_name')
        customer_id = kwargs.get('customer_id')
        is_first_install = kwargs.get('is_first_install')

        if not app_name or not customer_id or not is_first_install:
            return self.write_error_msg(PARAM_NOT_FOUND)

        app_info = OAUTH_APPS[app_name]
        if not app_info:
            logger.error('app not found')
            return self.write_error_msg(PARAM_INVALID)

        is_first_install = int(is_first_install)
        if is_first_install != 0 and is_first_install != 1:
            return self.write_error_msg(PARAM_INVALID)

        try:
            app_token = await self.app_token.async_get_token_by_cid_aid(app_info['app_id'], customer_id)
            if not app_token:
                return self.write_error_msg(NOT_FOUND)
            app_token['is_first_install'] = is_first_install
            await self.app_token.async_update(app_info['app_id'], customer_id, app_token)
            return self.write_json(None)
        except Exception as e:
            logger.error('get data from mongo error :%s' % e)
            return self.write_error_msg(SERVER_ERROR)

    def _is_expired(self, app_token):
        """ expired time is one and half hours
        :param app_token:
        :return:
        """
        if (int(time()) - app_token['access_token_ctime']) >= self.token_keep_time:
            return True
        return False

    async def get_token(self, app_id, customer_id):
        """refresh access_token
        :param app_id:
        :param customer_id:
        :return: access_token
        """
        if not app_id or not customer_id:
            logger.error('app_id or customer_id not exist')
            return None

        access_token_key = f'{app_id}-{customer_id}'
        try:
            access_token = self.redis_conn.get(access_token_key)
            if access_token:
                logger.info(f'get token from redis:{access_token}')
                return str(access_token, encoding='utf-8')

            app_token = await self.app_token.async_get_token_by_cid_aid(app_id, customer_id)
            if not app_token:
                return None
            if not self._is_expired(app_token):
                logger.info('get token from mongo ' + app_token['access_token'])
                return app_token['access_token']
        except Exception as e:
            logger.error('get data from mongo error :%s' % e)
            return None

        refresh_url = f"{self.oauth_host}/oauth/refresh_token?app_id={app_id}&grant_type=refresh_token" \
            f"&refresh_token={app_token['refresh_token']}"

        logger.info('refresh_url: {refresh_url}')
        request = HTTPRequest(refresh_url, method="POST", allow_nonstandard_methods=True)

        try:
            http_response = await AsyncHTTPClient().fetch(request)
            result = json.loads(str(http_response.body, encoding='utf-8'))
            logger.info('remote result is: {result}')

            if result.get('code') != 0:
                logger.error(f'get access token error: {result}')
                return None

            app_token['access_token'] = result['result']['access_token']
            app_token['access_token_ctime'] = int(time())
            await self.app_token.async_update(app_id, customer_id, app_token)

            self.redis_conn.set(access_token_key, app_token['access_token'], self.token_keep_time)
            logger.info(f'get token from mongodb: {app_token["access_token"]}')
            return app_token['access_token']

        except Exception as e:
            logger.error(f"get refresh token error: {e}")
            return None
