import json
from abc import ABCMeta, abstractmethod

from django.db.transaction import atomic
from django.utils.timezone import now
from requests_html import HTMLSession
from http import cookiejar

from hotspot.constants import *
from hotspot.models import HotspotSource
from hotspot.serializers import HotspotSerializerStrategy


class Builder:
    __metaclass__ = ABCMeta

    code = None

    @abstractmethod
    def get_data(self):
        pass

    @staticmethod
    def generate_single_data(title, uri, hotspot_source=None, **kwargs):
        return {
            'title': title,
            'uri': uri,
            'hotspot_source': hotspot_source,
            'extra': json.dumps(kwargs)
        }


class Director:
    def __init__(self, builder):
        self.builder = builder

    def build(self):
        with atomic():
            # update last fetch data time
            source = HotspotSource.objects.get(code=self.builder.code)
            copied_last_fetch_data_time = source.last_fetch_data_time
            source.last_fetch_data_time = now()
            source.save()

            data = self.builder.get_data()

            serializer = HotspotSerializerStrategy.Create(data=data[::-1], many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()


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


def test():
    Director(ThePaperBuilder()).build()
