
import logging
import pickle
import asyncio
from hashlib import md5
from functools import wraps
from time import time

logger = logging.getLogger('cache')


def cached(expire_in=86400, key_prefix=None):
    """Cache 装饰器
    :param expire_in: 过期时间，单位是：秒
    :param key_prefix: 在 Redis 中存储时使用的 Key 前缀，默认是：app_base
    :return:
    """
    def decorator(asyncfunc):
        @wraps(asyncfunc)
        async def wrapper(self, *args, **kw):
            future = asyncio.Future()
            if not self.redis_conn:
                logger.debug('redis is none, calling %s to fetch data.' % asyncfunc.__name__)
                future.set_result(await asyncfunc(self, *args, **kw))
                return future.result()

            prefix = 'app_base' if key_prefix is None else f'app_base_{key_prefix}'
            new_key = f'{prefix}_{generate_key(*args, **kw)}_{int(time() // expire_in * expire_in)}'
            logger.debug(f'redis key is: {new_key}')

            data = self.redis_conn.get(new_key)
            if data is None:
                logger.debug('data in cache is none, calling %s to fetch data.' % asyncfunc.__name__)
                future.set_result(await asyncfunc(self, *args, **kw))
                result = future.result()
                logger.debug('return data is %s.' % result)

                if is_fail_result(result):
                    return result
                logger.debug('save data to cache. data: %s' % result)
                self.redis_conn.set(new_key, pickle.dumps(result), ex=expire_in)
            else:
                logger.debug('fetch data in cache.')
                data = pickle.loads(data)

            return data
        return wrapper
    return decorator


def is_fail_result(result):
    """
    :param result: 当结构为空或者返回码不等于0或者 result key的值为空 返回True
    :return:
    """
    if result is None:
        return True
    if isinstance(result, dict) and (result.get('code') != 0 and result.get('result') is None):
        logger.debug('result is fail, so no set in redis')
        return True


def generate_key(*args, **kw):
    """
    生成 Redis 的 Key
    :param args:
    :param kw:
    :return:
    """
    key = pickle.dumps((args, kw))
    return md5(key).hexdigest()
