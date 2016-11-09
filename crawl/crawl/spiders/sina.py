# coding: utf-8

import scrapy
import json
import datetime
from ..pipelines import SinaGlobalNewsPipeline
from ..common.utils import utc2datetime


class SinaGlobalNewsSpider(scrapy.Spider):
    # "增量"抓取新浪全球实时财经新闻
    name = "sina_globalnews_realtime"
    allowed_domains = ["sina.com"]

    pipeline = SinaGlobalNewsPipeline()
    max_globalnews_id = pipeline.get_max_article_id()
    # print max_globalnews_id
    start_urls = (
        'http://live.sina.com.cn/zt/api/f/get/finance/globalnews1/index.htm?format=json&id={'
        '0}&tag=0&pagesize=30&dire=f'.format(max_globalnews_id),
    )

    def parse(self, response):
        page_json = json.loads(response.body)
        assert page_json['result']['status']['code'] == 0

        for sel in page_json['result']['data']:
            item = {}
            item['id'] = sel.get('id')
            item['set__title'] = sel.get('title')
            item['set__content'] = sel.get('content')
            item['set__creator'] = sel.get('creator')
            item['set__published_at'] = utc2datetime(float(sel.get('created_at')))
            item['set__created_at'] = datetime.datetime.now()
            item['set__updated_at'] = datetime.datetime.now()
            yield item

