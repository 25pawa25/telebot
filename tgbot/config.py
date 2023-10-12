# any configuration should be stored here

import os

TOKEN = os.environ.get('TOKEN', 'token') # configure env if you need;

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'password')
POSTGRES_DATABASE = os.environ.get('POSTGRES_DB', 'db')
