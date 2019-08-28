from celery import shared_task

from hotspot.get_hotspot import *


@shared_task
def task_weibo():
    Director(WeiboBuilder()).build()


@shared_task
def task_zhihu():
    Director(ZhihuBuilder()).build()


@shared_task
def task_baidu():
    Director(BaiduBuilder()).build()


@shared_task
def task_hupu_bxj():
    Director(HupuBxjBuilder()).build()


@shared_task
def task_baidu_tieba():
    Director(BaiduTiebaBuilder()).build()


@shared_task
def task_zhihu_daily():
    Director(ZhihuDailyBuilder()).build()


@shared_task
def task_zhe_paper():
    Director(ThePaperBuilder()).build()
