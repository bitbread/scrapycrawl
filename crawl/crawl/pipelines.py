# -*- coding: utf-8 -*-

from mongoengine import connect
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log
from crawl.items import SinaGlobalNewsArticle


class SinaGlobalNewsPipeline(object):

    def __init__(self):
        # connection = pymongo.MongoClient(
        #     settings['MONGODB_SERVER'],
        #     settings['MONGODB_PORT']
        # )
        # db = connection[settings['MONGODB_DB']]
        # self.collection = db[settings['MONGODB_COLLECTION']]
        connect(
            db=settings['MONGODB_DB'],
            host=settings['MONGODB_SERVER'],
            port=settings['MONGODB_PORT'],
            username=None,
            password=None,
        )

    def process_item(self, item, spider):
        if not item['id']:
            raise DropItem('Missing item id!')

        item_id = item['id']
        del item['id']  # 该字段仅用来查询id, 入库时要去除
        item['upsert'] = True
        SinaGlobalNewsArticle.objects(id=item_id).update(**item)
        log.msg('sina finance globalnews added into MongoDB!', level=log.DEBUG, spider=spider)
        return item

    @staticmethod
    def get_max_article_id():

        max_article = SinaGlobalNewsArticle.objects.only('id').order_by('-id').limit(1)
        if max_article:
            max_article_id = int(max_article[0]['id'])

        return max_article_id
