import dj_database_url
from .common import *

DEBUG = 'False'
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = [config('ALLOWED_HOSTS')]
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
