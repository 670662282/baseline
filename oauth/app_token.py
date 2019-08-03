# -*- coding: utf-8 -*-

import time
from handlers import logger

__author__ = 'tengfei.wang'


def app_token(data):
    app_token_info = {}
    if 'app_id' in data:
        app_token_info['app_id'] = data['app_id']
    if 'customer_id' in data:
        app_token_info['customer_id'] = data['customer_id']
    if 'access_token' in data:
        app_token_info['access_token'] = data['access_token']
    if 'expires_in' in data:
        app_token_info['expires_in'] = data['expires_in']
    if 'refresh_token' in data:
        app_token_info['refresh_token'] = data['refresh_token']
    if 'scope' in data:
        app_token_info['scope'] = data['scope']
    if 'is_first_install' in data:
        app_token_info['is_first_install'] = data['is_first_install']
    if 'status' in data:
        app_token_info['status'] = data['status']
    if 'access_token_ctime' in data:
        app_token_info['access_token_ctime'] = data['access_token_ctime']
    if 'refresh_token_ctime' in data:
        app_token_info['refresh_token_ctime'] = data['refresh_token_ctime']
    if 'ctime' in data:
        app_token_info['ctime'] = data['ctime']
    if 'uninstall_time' in data:
        app_token_info['uninstall_time'] = data['uninstall_time']
    return app_token_info


"""
model for nx_app_user_token
    storage app-customer token information 
"""


class AppToken(object):

    def __init__(self, db=None):
        self.db = db
        self.collection = db.nx_app_user_token

    async def async_insert(self, data=None):
        """
        插入
        :param data:
        :return:
        """
        logger.debug("insert nx_app_user_token: %s" % data)
        result = await self.collection.insert_one(app_token(data))
        logger.debug('result %s' % repr(result.inserted_id))
        return result

    def insert(self, data=None):
        """
        插入
        :param data:
        :return:
        """
        logger.debug("insert nx_app_user_token: %s" % data)
        result = self.collection.insert_one(app_token(data))
        logger.debug('result %s' % repr(result.inserted_id))
        return result

    async def get_access_token(self, customer_id):
        logger.debug("get nx_app_user_token: { customer_id: %s }" % customer_id)
        doc = await self.collection.find_one({'customer_id': customer_id})
        logger.debug("return document: " + str(doc))
        if doc:
            return doc['access_token']
        return None

    async def async_get_token_by_cid_aid(self, app_id, customer_id):
        logger.debug("get nx_app_user_token: { customer_id: %s, app_id: %s, status: 0 }" % (customer_id, app_id))
        doc = await self.collection.find_one({'app_id': app_id, 'customer_id': customer_id, 'status': 0})
        logger.debug("return document: " + str(doc))
        return doc

    def get_token_by_cid_aid(self, app_id, customer_id):
        logger.debug("get nx_app_user_token: { customer_id: %s, app_id: %s }" % (customer_id, app_id))
        doc = self.collection.find_one({'app_id': app_id, 'customer_id': customer_id, 'status': 0})

        logger.debug("return document: " + str(doc))
        print(dict(doc))
        return dict(str(doc))

    async def get_token(self, data=None):
        logger.debug("get nx_app_user_token: %s" % data)
        data['status'] = 0
        if data:
            doc = self.collection.find(app_token(data))
        else:
            doc = self.collection.find()
        docs = await doc.to_list(None)
        logger.debug("return document:" + str(docs))
        return docs

    async def async_update(self, app_id, customer_id, data=None):
        document = await self.collection.update_one({'app_id': app_id, 'customer_id': customer_id, 'status': 0},
                                                    {'$set': app_token(data)})
        logger.debug(
            "update nx_app_user_token: app_id %s, customer %s -> %s, ret: %s" % (app_id, customer_id, data, document))
        return True

    def update(self, app_id, customer_id, data=None):
        document = self.collection.update_one({'app_id': app_id, 'customer_id': customer_id, 'status': 0},
                                              {'$set': app_token(data)})
        logger.debug(
            "update nx_app_user_token: app_id %s, customer %s -> %s, ret: %s" % (app_id, customer_id, data, document))
        return True


if __name__ == '__main__':
    app = AppToken()
    app_info = {
        "spe_uid": 343,
        "spe_gid": 5,
        "access_token": 'GOPS4KQNTH2TVVT4K3IQVAPYOM',
        "expires_in": '7200',
        "refresh_token": 'G7D2LT4U2ACWDZCT2BTTK32PKU',
        "scope": 'install_login',
        "ctime": int(time.time()),
        "mtime": int(time.time())
    }
    asd = app.insert(app_info)
    print(asd)
