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
    return(f'{x["id"]}.png')

def ns_skinprocess(x):
    if x['model'] == 'Player' and x['id'] != None:
        if not isfile(f'skins/{x["id"]}.png'):
            print(f'processing skin ns {x["id"]}')
            urlretrieve(x['url_direct'], f'skins/{x["id"]}.png')
        return(f'{x["id"]}.png')
def ns_dlskins(url):
    global ns_regex
    print(f'crawl {url}')
    try:
        get = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
    except Exception as e:
        if e.getcode() == 404:
            print(f'404 not found ({url})')
            return()
    data = json.loads(ns_regex.search(get.read().decode())[1])
    return(data['pagination']['next'], procpool.map(ns_skinprocess, data['skins']))

def getNewData():
    global clsfy
    global ns_nxpg
    global ns_taglist
    global skinbuffer
    if len(os.listdir('dataset/sfw')) > len(os.listdir('dataset/nsfw')):
        for tg in ns_taglist.copy():
            try:
                ns_nxpg, flist = ns_dlskins(f'https://minecraft.novaskin.me/gallery/tag/{tg}?next={ns_nxpg}')
            except ValueError: # if the server returned 404, remove old tag and try new tag
                del ns_taglist[0]
                ns_nxpg = ''
            else:
                break
    else:
        pgdt = json.loads(urlopen(f'https://api.mineskin.org/get/list/{randint(1,256)}?size=64').read().decode())
        flist = procpool.map(ms_skinprocess, pgdt['skins'])
    for imnm in flist:
        if not (isfile(f'dataset/nsfw/{imnm}') or isfile(f'dataset/sfw/{imnm}')):
            clsfy.append([imnm, 'false', '', None])
        if not (isfile(f'dataset/nsfw/ol-{imnm}') or isfile(f'dataset/sfw/ol-{imnm}')):
            clsfy.append([imnm, 'true', 'ol-', None])
    if skinbuffer > len(clsfy):
        getNewData()
gnd = Thread(target = getNewData)
procpool=Pool(processes=16)
ns_regex = re.compile(r'data = ({.*})',)
ns_taglist = ['nudes', 'sexy']
ns_nxpg = ''
listpos = 0

guisize = 256
# how wide (in pixels) should the gui be?

# how many skins to download preemtively, and to keep in history
skinbuffer = 25

clsfy = []
def addToClsfy(imnm):
    # this function is also cloned to getNewData, as the function is run under a thread and cannot call this one
    global clsfy
    if not (isfile(f'dataset/nsfw/{imnm}') or isfile(f'dataset/sfw/{imnm}')):
        clsfy.append([imnm, 'false', '', None])
    if not (isfile(f'dataset/nsfw/ol-{imnm}') or isfile(f'dataset/sfw/ol-{imnm}')):
        clsfy.append([imnm, 'true', 'ol-', None])
# procpool.map(addToClsfy, os.listdir('skins'))
# for some reason this^ doesn't work >_>
for imnm in os.listdir('skins'):
    addToClsfy(imnm)
if len(clsfy) < skinbuffer:
    gnd.start()
    gnd.join()

def renderskin(pos):
    global canvas
    global listpos
    global pillowimage
    global imagesprite
    pre_rend(False, pos)
    print(f'render at pos {pos} ({clsfy[pos][0]})')
    try:
        # canvas.delete("all")
        canvas.pack()
        pilImage = PIL.Image.open(io.BytesIO(clsfy[pos][3])).resize((guisize, guisize*2))
        pillowimage = PIL.ImageTk.PhotoImage(pilImage)
        imagesprite = canvas.create_image(guisize/2,guisize,image=pillowimage)
        listpos = pos
    except IndexError:
        print(f'reached end of list')
        pass

def pre_rend(dobuffer=True, ps=False):
    if ps == False:
        global listpos
        ps = listpos
    # print(f'prerendering from {ps}')
    global clsfy
    global skinbuffer
    if clsfy[ps][3] == None:
        print(f'prerendering {ps} ({clsfy[ps][0]})')
        clsfy[ps][3] = check_output(['php', 'render.php', clsfy[ps][0], 'front', clsfy[ps][1]])
    if dobuffer == True:
        for pos in range(ps+1,ps+skinbuffer):
            if clsfy[pos][3] == None:
                try:
                    print(f'prerendering {pos} ({clsfy[pos][0]})')
                    clsfy[pos][3] = check_output(['php', 'render.php', clsfy[pos][0], 'front', clsfy[pos][1]])
                except TypeError:
                    print(f'TypeError with {pos} ({clsfy[pos][0]}), removing')
                    del clsfy[pos]
                    pass
rend = Thread(target = pre_rend)
# f = nsfw
# j = sfw
def keyhandler(event):
    global gnd
    global rend
    global clsfy
    global listpos
    print(f'key:{event.keysym}')
    groupmaps = {'j':'sfw', 'f':'nsfw'}
    if event.keysym in groupmaps:
        for group in groupmaps:
            try:
                os.remove(f'dataset/{groupmaps[group]}/{clsfy[listpos][2]}{clsfy[listpos][0]}')
            except FileNotFoundError:
                pass
        print(f'labelled {clsfy[listpos][2]}{clsfy[listpos][0]} as {groupmaps[event.keysym]}')
        open(f'dataset/{groupmaps[event.keysym]}/{clsfy[listpos][2]}{clsfy[listpos][0]}', 'wb').write(clsfy[listpos][3])
        move = 1

    if event.keysym in ('XF86Forward','Right'):
        move = 1
    if event.keysym in ('XF86Back','Left'):
        if listpos > 0:
            move = -1

    if 'move' in dir():
        print(f'move {move}')
        if listpos > skinbuffer:
            del clsfy[0]
            listpos = listpos-1
        renderskin(listpos+move)
        if rend.isAlive() is False:
            rend = Thread(target = pre_rend)
            rend.start()
        if gnd.isAlive() is False and len(clsfy)-listpos < skinbuffer:
            gnd = Thread(target = getNewData)
            gnd.start()
rend.start()
root = Tk()
root.geometry(f'{guisize}x{guisize*2}')
canvas = Canvas(root,width=guisize,height=guisize*2)
renderskin(listpos)
root.bind('<Key>',keyhandler)
root.mainloop()
exit()