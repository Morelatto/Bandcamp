# -*- coding: utf-8 -*-
import json
import scrapy

from bandcamp.items import BcTagCollection, BcRelease

BANDCAMP = 'bandcamp.com'

TO_SKIP = ['bc_dailys']


class TagSpider(scrapy.Spider):
    name = 'tags'
    allowed_domains = [BANDCAMP]
    custom_settings = {
        'FEED_URI': 'tag_results.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def __init__(self, tags='', **kwargs):
        super().__init__(**kwargs)
        self.tags = tags.split(';')

    def start_requests(self):
        for tag in self.tags:
            yield scrapy.Request('https://{}/tag/{}'.format(BANDCAMP, tag))

    def parse(self, response):
        json_data = response.css('#pagedata::attr(data-blob)').get()
        json_data = json.loads(json_data)

        for collection in json_data['hub']['tabs'][0]['collections']:
            if collection['name'] not in TO_SKIP:
                collection_item = BcTagCollection(name=collection['name'], releases=[])
                for release in collection['items']:
                    release_item = BcRelease()
                    release_item['artist'] = release['artist']
                    release_item['title'] = release['title']
                    release_item['description'] = release.get('blurb')
                    release_item['genre'] = release['genre']
                    release_item['featured_track'] = (release['featured_track_number'], release['featured_track_title'])
                    release_item['url'] = release['tralbum_url']
                    collection_item['releases'].append(release_item)
                yield collection_item
