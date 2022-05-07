import os

from pathlib import Path


DEBUG = os.environ.get('DEBUG', False) == 'True'

BASE_DIR = Path(__file__).resolve().parent.parent

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOCALE_PATHS = ['movies/locale']
