from .common import *

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
# DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.postgresql",
#        "NAME": config("DB_NAME"),
#        "HOST": config("DB_HOST"),
#        "USER": config("DB_USER"),
#        "PASSWORD": config("DB_PASSWORD"),
#    }
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "result_system_postgres_9w5n",
        "HOST": "dpg-d2gp6eruibrs73eioitg-a.oregon-postgres.render.com",
        "USER": "result_system_postgres_9w5n_user",
        "PASSWORD": "rqQcGU7xhOSNRVSJbPBlJ8ciVBsgoGWY",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 2525
