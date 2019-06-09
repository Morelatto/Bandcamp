import json
import multiprocessing
import os
import pymongo

from bandcamp_dl import bandcamp
from bandcamp_dl.bandcampdownloader import BandcampDownloader

DL_DIR = 'dls/'
os.makedirs(DL_DIR, exist_ok=True)

DEFAULT_TEMPLATE = '%{artist}/%{album}/%{track} - %{title}'

c = pymongo.MongoClient()
db = c['bandcamp']

MAX_PROCESSES = 4


# TODO retry failed
def parse_album(url):
    try:
        return bandcamp.parse(url)
    except Exception as e:
        print('Failed to parse album', url, e)


def bc_dl(urls, base_dir=DL_DIR):
    pool = multiprocessing.Pool(MAX_PROCESSES)
    downloader = BandcampDownloader(DEFAULT_TEMPLATE,
                                    base_dir,
                                    overwrite=False,
                                    embed_lyrics=True,
                                    grouping=False,
                                    embed_art=True,
                                    no_slugify=False,
                                    debugging=False,
                                    urls=urls)
    albums = pool.imap_unordered(parse_album, urls)
    for album in albums:
        if album:
            print('Downloading album', album['title'])
            downloader.download_album(album)


def daily():
    posts = db['daily'].find({'to_dl': {'$exists': True}}).sort('published', -1)
    for p in posts:
        # TODO treat /music urls (AttributeError)
        bc_dl(p['to_dl'])
        db['daily'].update_one(p, {'$rename': {'to_dl': 'dl'}})


def tags(json_results):
    print('Starting downloads')
    with open(json_results) as f:
        for collection in parse_scrapy_json(f.readlines()):
            urls = set()
            for release in collection['releases']:
                urls.add(release['url'])
            bc_dl(urls, os.path.join(DL_DIR, release['genre'], collection['name']))
    print('Finished downloading. Total', len(urls))


# Scrapy creates invalid json
def parse_scrapy_json(file_lines):
    for line in file_lines:
        yield json.loads(line)
