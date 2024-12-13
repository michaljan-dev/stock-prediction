import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the main database app
SQLALCHEMY_DATABASE_URI = "mysql://username:password@h/dbname"
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Celery MySQL broker
CELERY_DATABASE_URI = "sqla+mysql://username:password@h/dbname"

# Protection agains CSRF
CSRF_ENABLED = True
# Accept all origins only for dev/test purposes
CORS_RESOURCES = {r"/*": {"origins": "*"}}
# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

# JWT
JWT_SECRET_KEY = "secrate-jwt"
JWT_ALGORITHM = "HS256"
JWT_VERIFY = True
JWT_VERIFY_EXPIRATION = False
JWT_ALLOW_REFRESH = True
