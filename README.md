# Hotspot

获取各种网站的热点头条的后台程序, 采用Django作为开发框架, 利用多线程定时任务获取数据

# 环境配置

- Python 3.7
- Django 2.2
- MySQL 5.7
- Redis server 5.0.3

# 参数配置

`backend/settings/secret_settings.py`
```python
# 含义见Django文档
SECRET_KEY = ''

# 数据库配置, 详细可以参考Django文档
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hotspot_db',
        'USER': 'db_username',
        'PASSWORD': 'db_password',
        'HOST': '127.0.0.1',
        'PORT': '',
        "TEST_CHARSET": "utf8",
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0;",
            'charset': 'utf8mb4'
        },
    }
}
```

# 安装教程

- 安装依赖 `pip install -r requirements.txt`
- `tar -xzvf django-extensions-2.1.5.tar.gz`
- `python django-extensions-2.1.5/setup.py install `
- 启动Redis `redis-server`
- 启动Celery `celery -A backend worker -l info -c 2`
- 启动定时任务 `celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

# API

## 获取热点

- uri: /api/hotspot/hotspot-source/?hotspot_source=1

```json
{
    "id": 1,
    "last_fetch_data_time": "2019-08-27T19:55:52.465713+08:00",
    "hotspot_set": [
        {
            "id": 1570,
            "extra": "2467982",
            "title": "2019收入最高女歌手",
            "uri": "https://s.weibo.com/weibo?q=%232019%E6%94%B6%E5%85%A5%E6%9C%80%E9%AB%98%E5%A5%B3%E6%AD%8C%E6%89%8B%23&Refer=top"
        }
    ],
    "name": "微博",
    "desc": "微博热搜",
    "icon": "https://img.t.sinajs.cn/t4/appstyle/searchpc/css/pc/img/icon_wb.png",
    "code": 0,
    "source_uri": "https://s.weibo.com/top/summary"
}
```
