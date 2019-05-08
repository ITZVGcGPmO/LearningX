import io
from tkinter import *
# /pillow library\
import PIL.Image
import PIL.ImageTk

import os
from os.path import isfile
import json
from urllib.request import urlopen, Request, urlretrieve
from urllib.error import HTTPError
from multiprocessing import Pool
from threading import Thread
from subprocess import check_output
import re
from random import randint
def ms_skinprocess(x):
    if not isfile(f'skins/{x["id"]}.png'):
        print(f'processing skin ms {x["id"]}')
        urlretrieve(x['url'], f'skins/{x["id"]}.png')
        open(f'dataset/sfw/ol-{x["id"]}.png', 'wb').write(check_output(['php', 'render.php', f'{x["id"]}.png', 'front', 'true']))
        open(f'dataset/sfw/{x["id"]}.png', 'wb').write(check_output(['php', 'render.php', f'{x["id"]}.png', 'front', 'false']))
    return(f'{x["id"]}.png')

def nskinprocess(x):
    if x['model'] == 'Player' and x['id'] != None:
        if not isfile(f'skins/{x["id"]}.png'):
            print(f'processing skin ns {x["id"]}')
            urlretrieve(x['url_direct'], f'skins/{x["id"]}.png')
            open(f'dataset/nsfw/ol-{x["id"]}.png', 'wb').write(check_output(['php', 'render.php', f'{x["id"]}.png', 'front', 'true']))
            open(f'dataset/nsfw/{x["id"]}.png', 'wb').write(check_output(['php', 'render.php', f'{x["id"]}.png', 'front', 'false']))
        return(f'{x["id"]}.png')

procpool=Pool(processes=32)
ns_regex = re.compile(r'data = ({.*})',)
for tag in ['nudes', 'sexy']:
    nxpg = ''
    try:
        while True:
            url = f'https://minecraft.novaskin.me/gallery/tag/{tag}?next={nxpg}'
            print(f'downloading list from {url}')
            data = json.loads(ns_regex.search(urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode())[1])
            procpool.map(nskinprocess, data['skins'])
            nxpg = data['pagination']['next']
    except HTTPError:
        pass
counter = 1
nsfwamnt = len(os.listdir('dataset/nsfw'))
while page*64 < nsfwamnt:
    pgdt = json.loads(urlopen(f'https://api.mineskin.org/get/list/{page}?size=64').read().decode())
    procpool.map(ms_skinprocess, pgdt['skins'])
    page = page+1


while True:
    getNewData()