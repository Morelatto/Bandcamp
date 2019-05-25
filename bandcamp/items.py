# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.loader import ItemLoader, Identity
from scrapy.loader.processors import TakeFirst, MapCompose, Compose, Join
from w3lib.html import replace_escape_chars, strip_html5_whitespace


class BcDailyPost(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    published = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    to_dl = scrapy.Field()


class BcTagPage(scrapy.Item):
    genre = scrapy.Field()
    summary = scrapy.Field()
    related_tags = scrapy.Field(input_processor=Identity(), output_processor=Identity())
    page_rows = scrapy.Field(input_processor=Identity(), output_processor=Identity())


# input/output_processor of Field from a sub-item not working
class BcTagPageRow(scrapy.Item):
    title = scrapy.Field()
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


class BcTagPageLoader(ItemLoader):
    default_item_class = BcTagPage
    default_input_processor = MapCompose(replace_escape_chars)
    default_output_processor = Compose(TakeFirst())

    summary_in = MapCompose(replace_escape_chars, lambda x: re.sub(' +', ' ', x))
    summary_out = Join()
