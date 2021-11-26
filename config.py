class Config(object):
    """
    Main Configuration for Go Out Safe API Gateway
    """
    DEBUG = False
    TESTING = False

    # configuring microservices endpoints
    import os

    REQUESTS_TIMEOUT_SECONDS = float(os.getenv("REQUESTS_TIMEOUT_SECONDS", 5))

    # configuring redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis_cache')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
    REDIS_DB = os.getenv('REDIS_DB', '0')
    REDIS_URL = 'redis://%s:%s/%s' % (
        REDIS_HOST,
        REDIS_PORT,
        REDIS_DB
    )

    # users microservice
    USERS_MS_PROTO = os.getenv('USERS_MS_PROTO', 'http')
    USERS_MS_HOST = os.getenv('USERS_MS_HOST', 'localhost')
    USERS_MS_PORT = os.getenv('USERS_MS_PORT', 5000)
    USERS_MS_URL = '%s://%s:%s' % (USERS_MS_PROTO, USERS_MS_HOST, USERS_MS_PORT)

    # notifications
    NOTIFICATIONS_MS_PROTO = os.getenv('NOTIFICATIONS_MS_PROTO', 'http')
    NOTIFICATIONS_MS_HOST = os.getenv('NOTIFICATIONS_MS_HOST', 'localhost')
    NOTIFICATIONS_MS_PORT = os.getenv('NOTIFICATIONS_MS_PORT', 5001)
    NOTIFICATIONS_MS_URL = '%s://%s:%s' % (NOTIFICATIONS_MS_PROTO, NOTIFICATIONS_MS_HOST, NOTIFICATIONS_MS_PORT)

    # Configuring sessions
    SESSION_TYPE = 'redis'

    # secret key
    SECRET_KEY = os.getenv('APP_SECRET_KEY', b'isreallynotsecretatall')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_EXTENSIONS = ["jpg", "jpeg", "png"]
    UPLOAD_FOLDER = os.path.join("/static", "assets")


class DebugConfig(Config):
    """
    This is the main configuration object for application.
    """
    DEBUG = True
    TESTING = False


class DevConfig(DebugConfig):
    """
    This is the main configuration object for application.
    """
    pass


class TestConfig(Config):
    """
    This is the main configuration object for application.
    """
    TESTING = True

    import os
    SECRET_KEY = os.urandom(24)
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = True


class ProdConfig(Config):
    """
    This is the main configuration object for application.
    """
    TESTING = False
    DEBUG = False

    import os
    SECRET_KEY = os.getenv('APP_SECRET_KEY', os.urandom(24))


