# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader, Identity
from scrapy.loader.processors import TakeFirst, MapCompose, Compose
from w3lib.html import strip_html5_whitespace


class BcDailyPost(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    published = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    to_dl = scrapy.Field()


def normalize(v):
    return v.replace(u'\xa0', u' ')


class BcDailyPostLoader(ItemLoader):
    default_item_class = BcDailyPost
    default_input_processor = MapCompose(strip_html5_whitespace)
    default_output_processor = Compose(TakeFirst())

    title_out = Compose(TakeFirst(), normalize)
    tags_out = Identity()
    to_dl_out = Identity()
