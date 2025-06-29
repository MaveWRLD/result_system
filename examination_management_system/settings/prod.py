import dj_database_url
from .common import *

DEBUG = 'False'
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = []
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}
