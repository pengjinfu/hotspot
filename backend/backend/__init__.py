# import pymysql
# To Update django version of 2.2 thus, should use MySQLdb. otherwise will get django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3.
from .celery import app as celery_app

# pymysql.install_as_MySQLdb()

__all__ = ('celery_app',)
