class Config(object):
    POST_PER_PAGE=2

class ProdConfig(Config):
    pass

class DevConfig(Config):
    DEBUG = True
    SECRET_KEY='h\x0e\xc2\x16:mx\xa1\x86\xb3\x84Zp\xc0\xdfw\x8cP\x92\x96-#\x1aO'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
