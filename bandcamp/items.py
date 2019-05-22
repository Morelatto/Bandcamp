# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader, Identity
from scrapy.loader.processors import TakeFirst, MapCompose, Compose
from w3lib.html import strip_html5_whitespace


class BcDailyPost(scrapy.Item):
    title = scrapy.Field()
    published = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()


# TODO change name
class BcMusic(scrapy.Item):
    artist = scrapy.Field()
    album = scrapy.Field()
    track = scrapy.Field()
    track_number = scrapy.Field()
    artwork = scrapy.Field()
    url = scrapy.Field()


def normalize(v):
    return v.replace(u'\xa0', u' ')


class BcDailyPostLoader(ItemLoader):
    default_item_class = BcDailyPost
    default_input_processor = MapCompose(strip_html5_whitespace)
    default_output_processor = Compose(TakeFirst())

    title_out = Compose(TakeFirst(), normalize)
    tags_out = Identity()


class BcMusicLoader(ItemLoader):
    default_item_class = BcMusic
    default_input_processor = MapCompose(strip_html5_whitespace)
    default_output_processor = Compose(TakeFirst())
