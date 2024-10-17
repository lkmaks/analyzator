import os

basedir = os.path.abspath(os.path.dirname((__file__)))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ewirjiwqeojr322'
    print(os.environ.get('DATABASE_URL'), os.environ.get('DATABASE_PUBLIC_URL'))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True

