import os
import pymongo

from bandcamp_dl.bandcamp import Bandcamp
from bandcamp_dl.bandcampdownloader import BandcampDownloader
from py_bandcamp import BandCamper

DL_DIR = 'dls/'
DEFAULT_TEMPLATE = '%{artist}/%{album}/%{track} - %{title}'

bandcamp = Bandcamp()
bandcamper = BandCamper()


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


def tags():
    genres = db['tags'].find({'page_rows.to_dl': {'$exists': True}, 'page_rows.dl': {'$exists': False}})
    for g in genres:
        for row in g['page_rows']:
            print('Downloading', row['title'])
            urls, dl_dir = list(), os.path.join(DL_DIR, g['genre'], row['title'])
            os.makedirs(dl_dir, exist_ok=True)
            for to in row['to_dl']:
                albums = bandcamper.search_albums(to[1])
                if albums:
                    album = next(albums)
                    if g['genre'] in album['tags']:
                        print('Adding {} to download list ({})'.format(album['album_name'], album['length']))
                        urls.append(album['url'])
            bc_dl(urls, dl_dir)
            db['tags'].update_one({'page_rows': row}, {'$set': {'page_rows.$.dl': row['to_dl']}})


if __name__ == '__main__':
    c = pymongo.MongoClient()
    db = c['bandcamp']

    os.makedirs(DL_DIR, exist_ok=True)
    # TODO pass which genre as param
    # TODO integrate with tags.py
    tags()
