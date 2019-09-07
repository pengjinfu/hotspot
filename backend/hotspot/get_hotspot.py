import datetime
import json
from abc import ABCMeta, abstractmethod

from celery import shared_task
from django.db.transaction import atomic
from django.utils.timezone import utc
from requests_html import HTMLSession
from http import cookiejar

from backend.settings.base import HOTSPOT_PERIODIC_TASK_PREFIX
from hotspot.constants import *
from hotspot.models import HotspotSource, Hotspot
from hotspot.serializers import HotspotSerializerStrategy
from utils import hump_2_underline


class Builder:
    __metaclass__ = ABCMeta

    def __init__(self):
        # To tmp Save Fetched Data
        self.tmp = []
        self.source = HotspotSource.objects.get(code=self.code)

    code = None
    uri = None

    @abstractmethod
    def get_data(self):
        pass

    def generate_single_data(self, title, uri, hotspot_source=None, **kwargs):
        # Update this function to reduce duplication code
        data = {
            'title': title,
            'uri': uri,
            'hotspot_source': hotspot_source,
            'extra': json.dumps(kwargs)
        }
        self.tmp.append(data)
        return data

    @classmethod
    def register(cls):
        @shared_task(name=f'{HOTSPOT_PERIODIC_TASK_PREFIX}_{hump_2_underline(cls.__name__.replace("Builder", ""))}')
        def task():
            Director(cls).build()


class Director:
    def __init__(self, builder):
        self.builder = builder()

    def build(self):
        with atomic():
            source = HotspotSource.objects.get(code=self.builder.code)
            last_fetch_data_time = datetime.datetime.utcnow().replace(tzinfo=utc)
            source.last_fetch_data_time = last_fetch_data_time
            source.save()

            data = self.builder.get_data()

            serializer = HotspotSerializerStrategy.Create(data=data[::-1], many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # Remove duplication data,
        # This operation not with atomic, otherwise will course error as follows.
        # MySQLdb._exceptions.OperationalError: (1213, 'Deadlock found when trying to get lock; try restarting transaction')
        for item in data:
            # TODO: THis will course timezone warning, not find appropriate method to deal with it.
            Hotspot.objects.filter(title=item['title'], created_time__gt=datetime.datetime.utcnow().replace(tzinfo=utc).date(), created_time__lte=last_fetch_data_time).delete()


def preprocessor_fetch_data(uri, **kwargs):
    session = HTMLSession()
    # noinspection PyUnresolvedReferences
    return session.get(uri, **kwargs).html


class WeiboBuilder(Builder):
    code = WEIBO_CODE

    def get_data(self):
        source = HotspotSource.objects.get(code=0)

        uri = 'https://s.weibo.com/top/summary'
        table = preprocessor_fetch_data(uri).find('tbody')[0]
        trs = table.find('tr')

        tmp = []

        # 不获取第一条, 第一条没有数量
        for tr in trs[1:]:
            content = tr.text.split('\n')
            *title, count = content[1].split(' ')
            href = tr.find("a", first=True).attrs["href"]
            if 'void' in href:
                href = tr.find("a", first=True).attrs["href_to"]
            hot_uri = f'https://s.weibo.com{href}'

            data = {
                'title': ' '.join(title),
                'uri': hot_uri,
                'extra': json.dumps({
                    'count': count,
                    'order': content[0]
                }),
                'hotspot_source': source.id
            }

            tmp.append(data)
        return tmp


class ZhihuBuilder(Builder):
    code = ZHIHU_CODE

    def get_data(self):
        source = HotspotSource.objects.get(code=1)
        uri = 'https://www.zhihu.com/hot'

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.3",
            "Referer": "https://www.zhihu.com/"
        }

        session = HTMLSession()
        session.cookies = cookiejar.LWPCookieJar(filename='./hotspot/utils/cookies.txt')
        session.cookies.load(ignore_discard=True)

        # TODO: 知乎必须要登录, 没法绕过, 后续添加验证码自动识别方案, 暂时写死cookie
        r = session.get(url=uri, headers=headers).html
        sections = r.find('#TopstoryContent > div > div > div.HotList-list', first=True).find('section')

        tmp = []

        for section in sections:
            order, _, desc, _, *t = section.text.split('\n')
            hot_uri = section.find('a', first=True).attrs['href']
            title = section.find('a', first=True).attrs['title']
            count = section.find('.HotItem-metrics', first=True).text.replace('分享', '')

            data = {
                'title': title,
                'uri': hot_uri,
                'extra': json.dumps({
                    'count': count,
                    'order': order,
                    'desc': desc
                }),
                'hotspot_source': source.id
            }

            tmp.append(data)

        return tmp


class BaiduBuilder(Builder):
    code = BAIDU_CODE

    def get_data(self):
        source = HotspotSource.objects.get(code=2)
        uri = 'http://top.baidu.com/buzz?b=1&c=513&fr=topbuzz_b341_c513'
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.3",
            'Host': 'top.baidu.com',
            'Upgrade-Insecure-Requests': '1'
        }
        r = preprocessor_fetch_data(uri, headers=headers).find('table', first=True).find('tr')

        tmp = []

        for item in r[1:]:
            first = item.find('.first', first=True)
            if first is None:
                continue
            order = first.text
            title = item.find('.keyword', first=True).find('a', first=True).text
            hot_uri = item.find('.keyword', first=True).find('a', first=True).attrs['href']
            count = item.find('.last', first=True).text

            data = {
                'title': title,
                'uri': hot_uri,
                'extra': json.dumps({
                    'count': count,
                    'order': order,
                }),
                'hotspot_source': source.id
            }

            tmp.append(data)

        return tmp


class HupuBxjBuilder(Builder):
    code = HUPU_BXJ_CODE

    def get_data(self):
        source = HotspotSource.objects.get(code=HUPU_BXJ_CODE)
        uri = 'https://bbs.hupu.com/all-gambia'
        r = preprocessor_fetch_data(uri)

        tmp = []

        for item in r.find('#container > div > div.bbsHotPit', first=True).find('.textSpan'):
            *title, count = item.text.split()
            target = item.find('a', first=True).attrs['href']
            data = {
                'title': ' '.join(title),
                'uri': f'https://bbs.hupu.com/{target}',
                'extra': json.dumps({
                    'count': count
                }),
                'hotspot_source': source.id
            }
            tmp.append(data)
        return tmp


class BaiduTiebaBuilder(Builder):
    code = BAIDU_TIEBA_CODE

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        uri = 'http://tieba.baidu.com/hottopic/browse/topicList'
        r = json.loads(preprocessor_fetch_data(uri).text)['data']['bang_topic']['topic_list']
        tmp = []
        for item in r:
            data = {
                'title': item['topic_name'],
                'uri': item['topic_url'],
                'extra': json.dumps({
                    'count': item['discuss_num'],
                    'e': item
                }),
                'hotspot_source': source.id
            }
            tmp.append(data)
        return tmp


class ZhihuDailyBuilder(Builder):
    code = ZHIHU_DAILY_CODE

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        uri = 'http://daily.zhihu.com/'
        r = preprocessor_fetch_data(uri)
        tmp = []
        for item in r.find('.row .box'):
            title = item.find('a', first=True).text
            target = f'http://daily.zhihu.com/{item.find("a", first=True).attrs["href"]}'
            data = {
                'title': title,
                'uri': target,
                'hotspot_source': source.id,
                'extra': json.dumps({
                    'count': ''
                })
            }
            tmp.append(data)
        return tmp


class ThePaperBuilder(Builder):
    code = THE_PAPER_CODE

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        uri = 'https://www.thepaper.cn/'
        r = preprocessor_fetch_data(uri)
        tmp = []
        for item in r.find('#listhot0', first=True).find('a'):
            data = self.generate_single_data(
                item.text,
                f'https://www.thepaper.cn/{item.attrs["href"]}',
                hotspot_source=source.id,
                count=''
            )
            tmp.append(data)

        return tmp


class WYNewBuilder(Builder):
    code = WY_NEW_CODE
    uri = 'http://news.163.com/special/0001386F/rank_whole.html'

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        r = preprocessor_fetch_data(self.uri)
        tmp = []
        for item in r.find('.tabContents', first=True).find('tr')[1:]:
            a = item.find('a', first=True)
            if a is None: continue
            data = self.generate_single_data(
                a.text,
                a.attrs['href'],
                hotspot_source=source.id,
                count=item.find('.cBlue', first=True).text
            )
            tmp.append(data)
        return tmp


class WeiXinBuilder(Builder):
    code = WEIXIN_CODE
    uri = 'https://weixin.sogou.com/?pid=sogou-wsse-721e049e9903c3a7&kw='

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        r = preprocessor_fetch_data(self.uri)
        tmp = []
        for item in r.find('.news-list li'):
            if item.find('h3 a', first=True).text == '': continue
            data = self.generate_single_data(
                item.find('h3 a', first=True).text,
                item.find('h3 a', first=True).attrs['href'],
                hotspot_source=source.id,
                count=''
            )
            tmp.append(data)
        return tmp


class ChiphellBuilder(Builder):
    code = CHIPHELL_CODE
    uri = 'https://www.chiphell.com/'

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        r = preprocessor_fetch_data(self.uri)
        for item in r.find('#frameZ3L5I7 li'):
            self.generate_single_data(
                item.text,
                f"https://www.chiphell.com/{item.find('a', first=True).attrs['href']}",
                hotspot_source=source.id,
                count=''
            )
        return self.tmp


class ItHomeBuilder(Builder):
    code = IT_HOME_CODE
    uri = 'https://www.ithome.com/'

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        r = preprocessor_fetch_data(self.uri)
        for item in r.find('.hot-list .bx ul li'):
            a = item.find('a', first=True)
            self.generate_single_data(
                a.attrs['title'],
                a.attrs['href'],
                hotspot_source=source.id,
                count=''
            )
        return self.tmp


class LssdjtBuilder(Builder):
    uri = 'http://www.lssdjt.com/'
    code = LSSDJT_CODE

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        r = preprocessor_fetch_data(self.uri)
        for item in r.find('.gong'):
            a = item.find('a', first=True)
            self.generate_single_data(
                item.text,
                f"http://www.lssdjt.com{a.attrs['href']}",
                hotspot_source=source.id,
                count=''
            )
        return self.tmp


class QDailyBuilder(Builder):
    code = QDAILY_CODE
    uri = 'https://www.qdaily.com/tags/29.html'

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        r = preprocessor_fetch_data(self.uri)
        for item in r.find('.packery-item'):
            self.generate_single_data(
                item.find('h3', first=True).text,
                f"https://www.qdaily.com{item.find('a', first=True).attrs['href']}",
                hotspot_source=source.id,
                count=''
            )
        return self.tmp


class V2EXBuilder(Builder):
    code = V2EX_CODE
    uri = 'https://www.v2ex.com/?tab=hot'

    def get_data(self):
        source = HotspotSource.objects.get(code=self.code)
        r = preprocessor_fetch_data(self.uri)
        for item in r.find('.cell.item'):
            self.generate_single_data(
                item.find('.item_title', first=True).text,
                f"https://www.v2ex.com/{item.find('.item_title', first=True).find('a', first=True).attrs['href']}",
                hotspot_source=source.id,
                count=item.find('.count_livid', first=True).text
            )
        return self.tmp


class TianyaBuilder(Builder):
    code = TIANYA_CODE
    uri = 'http://bbs.tianya.cn/list.jsp?item=funinfo&grade=3&order=1'

    def get_data(self):
        r = preprocessor_fetch_data(self.uri)
        for item in r.find('table tr')[1:]:
            a = item.find('a', first=True)
            self.generate_single_data(
                a.text,
                f"http://bbs.tianya.cn{a.attrs['href']}",
                self.source.id,
                count=item.find('td')[2].text
            )
        return self.tmp


class GithubBuilder(Builder):
    code = GITHUB_CODE
    uri = 'https://github.com/trending'

    def get_data(self):
        r = preprocessor_fetch_data(self.uri)
        for item in r.find('.Box article')[1:]:
            self.generate_single_data(
                item.find('.lh-condensed a', first=True).text,
                f"https://github.com{item.find('.lh-condensed a', first=True).attrs['href']}",
                hotspot_source=self.source.id,
                count=item.find('.muted-link.d-inline-block.mr-3', first=True).text
            )
        return self.tmp


def test():
    Director(GithubBuilder).build()
