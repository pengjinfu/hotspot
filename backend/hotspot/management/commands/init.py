from django_celery_beat.models import IntervalSchedule, PeriodicTask

import hotspot.get_hotspot

from django.core.management.base import BaseCommand

from backend.settings.base import HOTSPOT_PERIODIC_TASK_PREFIX
from hotspot.models import HotspotSource
from utils import hump_2_underline


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Generate Default Task...')
        builders = [i for i in dir(hotspot.get_hotspot) if i.endswith('Builder') and i != 'Builder']
        for item in builders:
            schedule, _ = IntervalSchedule.objects.get_or_create(every=60 * 30, period=IntervalSchedule.SECONDS)
            name = f"{HOTSPOT_PERIODIC_TASK_PREFIX}_{hump_2_underline(item.replace('Builder', ''))}"
            task, flag = PeriodicTask.objects.get_or_create(name=name, task=name)
            if flag:
                task.interval = schedule
                task.save()
        print('success')
