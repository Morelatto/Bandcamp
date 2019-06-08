import json
import os
import pymongo

from bandcamp_dl.bandcamp import Bandcamp
from bandcamp_dl.bandcampdownloader import BandcampDownloader
from py_bandcamp import BandCamper
from unidecode import unidecode

DL_DIR = 'dls/'
os.makedirs(DL_DIR, exist_ok=True)

DEFAULT_TEMPLATE = '%{artist}/%{album}/%{track} - %{title}'

bandcamp = Bandcamp()
bandcamper = BandCamper()

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
        album = bandcamp.parse(url, lyrics=True)
        print('\nDownloading', url)
        downloader.start(album)


def daily():
    posts = db['daily'].find({'to_dl': {'$exists': True}}).sort('published', -1)
    for p in posts:
        # TODO treat /music (AttributeError)
        bc_dl(p['to_dl'])
        db['daily'].update_one(p, {'$rename': {'to_dl': 'dl'}})


def tags(json_results):
    with open(json_results) as f:
        for res in parse_scrapy_json(f.readlines()):
            urls = list()
            for release in res['all_releases']:
                album_url = search_url(release['album'])
                if album_url:
                    urls.append(album_url)
            bc_dl(urls)


def search_url(album):
    try:
        albums = bandcamper.search_albums(unidecode(album))
        if albums:
            album = next(albums)
            print('Adding {} to download list ({})'.format(album['album_name'], album['length']))
            return album['url']
        else:
            print('No search results found for album', album)
    except Exception as e:
        print('Failed to search for album', album, e)


# Scrapy creates invalid json
def parse_scrapy_json(file_lines):
    for line in file_lines:
        yield json.loads(line)
