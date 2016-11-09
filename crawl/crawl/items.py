# coding: utf-8

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from mongoengine import *


class SinaGlobalNewsArticle(Document):
    # define the fields for your item here like:
    kind = 'K_SINA_GLOBALNEWS_ARTICLE'
    kind_cn = u'新浪全球实时财经新闻'

    id = StringField(primary_key=True)
    title = StringField()
    content = StringField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    published_at = DateTimeField()
    creator = StringField()

    meta = {
        'collection': 'item_sina_globalnews_article',
        'indexes': ['updated_at', 'created_at', 'published_at'],
        'strict': False,
    }
