import os

# Django settings for link5 project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Benjamin Tacquet', 'benjamin@tacquet.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': '', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

ugettext = lambda s: s
LANGUAGES = (
      ('en', ugettext('English')),
      ('fr', ugettext('French')),
      ('de', ugettext('German')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(os.path.dirname(__file__), 'static').replace('\\', '/'),
    #os.path.join(os.path.dirname(__file__), 'media').replace('\\', '/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd3t829tn=r(b3(4i#=!o6uxik-5035x9fy=d*c80hpm1*fs)4-'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'template').replace('\\', '/'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    "django.contrib.auth.context_processors.auth",
    #"django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
)

INSTALLED_APPS = (
    #'admintools_bootstrap',
    #'admin_tools.theming',
    #'admin_tools.menu',
    #'admin_tools.dashboard',
    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',

    'filebrowser',
    # Uncomment the next line to enable the admin:
    #'suit',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'rosetta',
    'sorl.thumbnail',

    'oembed',

    'link5app',
)

THUMBNAIL_BACKEND = 'sorl_backends.AutoFormatBackend'
# Used if the format cannot be automatically inferred (eg for a .gif image)
THUMBNAIL_FORMAT = 'JPEG'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
	'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logfile'),
            'maxBytes': 5000,
            'backupCount': 2,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


OEMBED = {
    'format': 'json',
    'maxwidth': '612',
    'width': '612',
}
LINK_PER_PAGE = 60
COMMENTS_PER_LINK = 3
FOLLOWER_PER_PAGE = 1
FOLLOWING_PER_PAGE = 1
MODERATION_LEVEL = -3
MAX_FOLLOW = 400
MAX_IMAGE = 15
MIM_IMAGE_SIZE = 2500



ANONYMOUS_POST = True
DEFAULT_USER = "Anonymous"
MAX_IMAGE_SIZE = 1*1024*1024

EMAIL_HOST = '' #ex: '127.0.0.1'

USER_MESSAGE_FROM = "" #ex: "Link5 <no-reply@xxxxx.com>"
CONTACT_FROM = "" #ex: "FromMe"
CONTACT_RECIPIENT = () #Tuple of emails

RECAPCHA_PRIVATE = "" # Please check recapcha to get private / public keys
RECAPCHA_PUBLIC  = ""

CACHES = {} # I use memcached, default configuration

INTERNAL_IPS = () # ex '127.0.0.1'

ALLOWED_HOSTS = "127.0.0.1"

try:
    from settings_local import *
except:
    pass
