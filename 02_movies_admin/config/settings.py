import os

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()


include(
    'components/database.py',
    'components/apps.py',
    'components/misc.py',
)

SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ['127.0.0.1']
