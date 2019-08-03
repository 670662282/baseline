port = 8989
#mysql_host = 'mydb.example.com:3306'
# Both lists and comma-separated strings are allowed for
# multiple=True.
# memcache_hosts = ['cache1.example.com:11011','cache2.example.com:11011']
# memcache_hosts = 'cache1.example.com:11011,cache2.example.com:11011'

# app base common config
APP_BASE_AUTH_TYPE = "authorization_code"

openapi_server = "http://api.qavm.com:9420"
auth_server = "http://oauth.qavm.com:9420"
app_host = "http://nbad.qavm.app:8101"

mongodb_url = "mongodb://nexus:nexus@localhost:27017"
mongodb_name = "nxg_app_base"
redis_url = "redis://localhost:6379/0"


APPLICATION_SETTINGS = {
    "cookie_secret": "d3bbd7479bc952e1dd1f32e48320a619",
    "xsrf_cookies": False,
    "compress_response": True
}

# You can generate the key by the following website:
# https://asecuritysite.com/encryption/keygen
AES_KEY = 'your 32 byte aes key'
TOKEN_TIMEOUT = 60 * 60 * 24 * 30