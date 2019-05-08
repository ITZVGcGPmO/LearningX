
import os
import json
from urllib.request import urlopen, Request, urlretrieve
from urllib.error import HTTPError
from multiprocessing import Pool
import re
from random import randint
def ms_skinprocess(x):
    urlretrieve(x['url'], f'dataset/skins/{x["id"]}.png')
    addToClsfy(f'dataset/skins/{x["id"]}.png')

def ns_skinprocess(x):
    if x['model'] == 'Player':
        urlretrieve(x['url_direct'], f'dataset/skins/{x["id"]}.png')
        addToClsfy(f'dataset/skins/{x["id"]}.png')
def ns_dlskins(url):
    global ns_regex
    global threadpool
    print(f'crawl {url}')
    get = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
    if get.getcode() == 404:
        return('')
    else:
        data = json.loads(ns_regex.search(get.read().decode())[1])
        threadpool.map(ns_skinprocess, data['skins'])
        return(data['pagination']['next'])

def getNewData():
    global ns_nxpg
    global ns_taglist
    global threadpool
    if len(os.listdir('dataset/sfw')) > len(os.listdir('dataset/nsfw')):
        for tg in ns_taglist.copy():
            ns_nxpg=ns_dlskins(f'https://minecraft.novaskin.me/gallery/tag/{tg}?next={ns_nxpg}')
            if ns_nxpg == '':
                ns_taglist.pop(0)
            else: # if the server returned 404, remove old tag and try new tag, else break loop
                break
    else:
        pgdt = json.loads(urlopen(f'https://api.mineskin.org/get/list/{randint(1,256)}?size=64').read().decode())
        threadpool.map(ms_skinprocess, pgdt['skins'])

threadpool=Pool(processes=16)
ns_regex = re.compile(r'data = ({.*})',)
ns_taglist = ['nudes', 'sexy']
ns_nxpg = ''
