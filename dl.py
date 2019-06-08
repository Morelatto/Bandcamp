import json
import os
import pymongo

from bandcamp_dl.bandcamp import Bandcamp
from bandcamp_dl.bandcampdownloader import BandcampDownloader

DL_DIR = 'dls/'
os.makedirs(DL_DIR, exist_ok=True)

DEFAULT_TEMPLATE = '%{artist}/%{album}/%{track} - %{title}'

bandcamp = Bandcamp()

c = pymongo.MongoClient()
db = c['bandcamp']


def bc_dl(urls, base_dir=DL_DIR):
    downloader = BandcampDownloader(DEFAULT_TEMPLATE,
                                    base_dir,
                                    overwrite=False,
                                    embed_lyrics=True,
                                    grouping=False,
                                    embed_art=True,
                                    no_slugify=False,
                                    debugging=False,
                                    urls=urls)
    for url in urls:
        try:
            album = bandcamp.parse(url, lyrics=True)
            print('\nDownloading', url)
            downloader.start(album)
        except Exception as e:
            print('Failed to download', url, e)


def daily():
    posts = db['daily'].find({'to_dl': {'$exists': True}}).sort('published', -1)
    for p in posts:
        # TODO treat /music (AttributeError)
        bc_dl(p['to_dl'])
        db['daily'].update_one(p, {'$rename': {'to_dl': 'dl'}})


def tags(json_results):
    with open(json_results) as f:
        for collection in parse_scrapy_json(f.readlines()):
            urls = set()
            for release in collection['releases']:
                urls.add(release['url'])
            bc_dl(urls, os.path.join(DL_DIR, release['genre'], collection['name']))


# Scrapy creates invalid json
def parse_scrapy_json(file_lines):
    for line in file_lines:
        yield json.loads(line)
