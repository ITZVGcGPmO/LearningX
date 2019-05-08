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
import re
from random import randint
def ms_skinprocess(x):
    urlretrieve(x['url'], f'dataset/skins/{x["id"]}.png')
    return(f'dataset/skins/{x["id"]}.png')

def ns_skinprocess(x):
    if x['model'] == 'Player':
        urlretrieve(x['url_direct'], f'dataset/skins/{x["id"]}.png')
        return(f'dataset/skins/{x["id"]}.png')
def ns_dlskins(url):
    global ns_regex
    print(f'crawl {url}')
    get = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
    if get.getcode() == 404:
        return('')
    else:
        data = json.loads(ns_regex.search(get.read().decode())[1])
        threadpool.map(addToClsfy, threadpool.map(ns_skinprocess, data['skins']))
        return(data['pagination']['next'])

def getNewData():
    global ns_nxpg
    global ns_taglist
    if len(os.listdir('dataset/sfw')) > len(os.listdir('dataset/nsfw')):
        for tg in ns_taglist.copy():
            ns_nxpg=ns_dlskins(f'https://minecraft.novaskin.me/gallery/tag/{tg}?next={ns_nxpg}')
            if ns_nxpg == '':
                ns_taglist.pop(0)
            else: # if the server returned 404, remove old tag and try new tag, else break loop
                break
    else:
        pgdt = json.loads(urlopen(f'https://api.mineskin.org/get/list/{randint(1,256)}?size=64').read().decode())
        threadpool.map(addToClsfy, threadpool.map(ms_skinprocess, pgdt['skins']))

threadpool=Pool(processes=16)
ns_regex = re.compile(r'data = ({.*})',)
ns_taglist = ['nudes', 'sexy']
ns_nxpg = ''

guisize = 256
# how wide (in pixels) should the gui be?

# how many skins to download preemtively, and to keep in history
skinbuffer = 20

clsfy = []
def addToClsfy(imnm):
    global clsfy
    if not (isfile(f'dataset/nsfw/{imnm}') or isfile(f'dataset/sfw/{imnm}')):
        clsfy.append((imnm, 'false', ''))
    if not (isfile(f'dataset/nsfw/ol-{imnm}') or isfile(f'dataset/sfw/ol-{imnm}')):
        clsfy.append((imnm, 'true', 'ol-'))
# threadpool.map(addToClsfy, os.listdir('dataset/skins'))
# for some reason this^ doesn't work >_>
for imnm in os.listdir('dataset/skins'):
    addToClsfy(imnm)
if len(clsfy) < skinbuffer:
    getNewData()

def getimagedata(pos):
    global clsfy
    print(f'get image data for pos {pos} ({clsfy[pos][0]})')
    return(urlopen(f'http://localhost/dataset/render.php?file={clsfy[pos][0]}&facing=front&overlay={clsfy[pos][1]}').read())

def renderskin(pos):
    global canvas
    global listpos
    global pillowimage
    global imagesprite
    print(f'render at pos {pos}')
    # canvas.delete("all")
    canvas.pack()
    pilImage = PIL.Image.open(io.BytesIO(getimagedata(pos))).resize((guisize, guisize*2))
    pillowimage = PIL.ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(guisize/2,guisize,image=pillowimage)
    listpos = pos

# f = nsfw
# j = sfw
listpos = 0
def keyhandler(event):
    global clsfy
    global listpos
    print(event.keysym)
    groupmaps = {'j':'sfw', 'f':'nsfw'}
    if event.keysym in groupmaps:
        for group in groupmaps:
            try:
                os.remove(f'dataset/{groupmaps[group]}/{clsfy[listpos][2]}{clsfy[listpos][0]}')
            except FileNotFoundError:
                pass
        open(f'dataset/{groupmaps[event.keysym]}/{clsfy[listpos][2]}{clsfy[listpos][0]}', 'wb').write(getimagedata(listpos))
        move = 1

    if event.keysym in ('XF86Forward','Right'):
        move = 1
    if event.keysym in ('XF86Back','Left'):
        move = -1

    if 'move' in dir():
        print(f'move {move}')
        if listpos > skinbuffer:
            del clsfy[0]
            listpos = listpos-1
        renderskin(listpos+move)
        if len(clsfy)-listpos < skinbuffer:
            getNewData()


root = Tk()
root.geometry(f'{guisize}x{guisize*2}')
canvas = Canvas(root,width=guisize,height=guisize*2)
renderskin(listpos)
root.bind('<Key>',keyhandler)
root.mainloop()