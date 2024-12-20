import os
from dotenv import load_dotenv

load_dotenv()


DB_LOGIN = os.getenv('DB_LOGIN')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DJ_SCRT_KEY = os.getenv('DJ_SCRT_KEY')

FROM_EMAIL_USER = os.getenv('FROM_EMAIL_USER')
FROM_EMAIL_PASSWORD = os.getenv('FROM_EMAIL_PASSWORD')
FROM_DEFAULT_EMAIL = os.getenv('FROM_DEFAULT_EMAIL')

GOOGLE_ID = os.getenv('GOOGLE_ID')
GOOGLE_SECRET = os.getenv('GOOGLE_SECRET')

YANDEX_ID = os.getenv('YANDEX_ID')
YANDEX_SECRET = os.getenv('YANDEX_SECRET')

AWS_KEY_ID = os.getenv('AWS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')