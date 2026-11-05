import os
import sys
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv("DEBUG") == 'True' else False


STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
# Проверка на наличие ключа (чтобы сервер упал при запуске, если ключ не задан, а не выдавал ошибку 500 в процессе)
if not STRIPE_SECRET_KEY:
    raise ValueError("STRIPE_SECRET_KEY не найден в переменных окружения. Проверьте файл .env")

ALLOWED_HOSTS = []


AUTH_USER_MODEL = 'users.CustomUser'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_countries',
    'django_filters',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'drf_yasg',
    'users',
    'materials',
    'django_celery_beat',
]

SPECTACULAR_SETTINGS = {
    'TITLE': 'API Documentation', # Заголовок для документации
    'DESCRIPTION': 'Описание вашего API', # Описание (опционально)
    'VERSION': '1.0.0', # Версия вашего API
    'SERVE_INCLUDE_SCHEMA': False, # Не показывать сырую схему OpenAPI на главной странице (опционально)
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # ← вот это "закрывает" всё
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# Настройки срока действия токенов
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('NAME'),
        'USER': os.getenv('USER'),
        'PASSWORD': os.getenv('PASSWORD'),
        'HOST': os.getenv('HOST'),
        'PORT': os.getenv('PORT'),
        'TEST': {
            'NAME': 'drfhw',
        },
    }
}

# Для тестов.
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Медиатека (Media)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',  # адрес фронтенд-сервера
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

CORS_ALLOW_ALL_ORIGINS = False

# Настройки для Celery
CELERY_BEAT_SCHEDULE = {
    'task-name': {
        'task': 'myapp.tasks.my_task',  # Путь к задаче
        'schedule': timedelta(minutes=10),  # Расписание выполнения задачи (например, каждые 10 минут)
    },
}

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')


# Запрещаем выполнение произвольного кода через задачи. Только JSON.
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# Воркер подтвердит получение задачи только после ее успешного выполнения.
# Если воркер упадет во время работы, задача вернется в очередь.
CELERY_ACKS_LATE = True

# Если соединение с брокером оборвется, воркер будет пытаться переподключиться
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = None # Бесконечное количество попыток

# Результаты задач будут храниться в Redis 1 час (3600 секунд), затем удалятся для экономии места
CELERY_RESULT_EXPIRES = 3600

CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Настройка для вывода писем в консоль
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Настройки для тестов
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


    # Заставляет Celery выполнять задачи синхронно (в том же потоке) без Redis
    CELERY_TASK_ALWAYS_EAGER = True
    # Игнорирует подключение к брокеру во время тестов
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'


CELERY_BEAT_SCHEDULE = {
    'block_inactive_users_every_day': {
        'task': 'users.tasks.block_inactive_users',
        # Вариант 1. Запуск раз в сутки в полночь
        'schedule': crontab(hour=0, minute=0),

        # Вариант 2. Для локального тестирования (запуск каждые 30 секунд)
        # 'schedule': 30.0,
    },
}

