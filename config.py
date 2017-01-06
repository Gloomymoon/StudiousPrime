import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a rather very hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    #BOOTSTRAP_SERVE_LOCAL = True
    CSS_SERVE_LOCAL = True
    JS_SERVE_LOCAL = True
    MAIL_SUBJECT_PREFIX = '[SutdiousPrime]'
    MAIL_SENDER = 'StudiousPrime Admin <admin@sutdiousprime.com>'
    MATERIAL_SERVE_LOCAL = True
    MATERIAL_QUERYSTRING_REVVING = False
    #ATH_ADMIN = os.environ.get('ATH_ADMIN')
    WORDS_PER_EXERCISE = [25, 15, 5, 3, 2, 0]   # word numbers by every level from 0 to 5, [0] means total
    WORDS_PER_PAGE = 10
    EXERCISES_PER_PAGE = 10
    USERS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'postgresql://postgres:778899@localhost/StudiousPrime'


class ProductionConfig(Config):
    CSS_SERVE_LOCAL = False
    JS_SERVE_LOCAL = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}
