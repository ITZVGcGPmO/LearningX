import urllib.request
from multiprocessing import Pool
from os import listdir

def renderhandler(filename):
    urllib.request.urlretrieve(f'http://localhost/dataset/render.php?file={filename}&facing=front&overlay=false', f'dataset/rendered/{filename}')
    urllib.request.urlretrieve(f'http://localhost/dataset/render.php?file={filename}&facing=front&overlay=true', f'dataset/rendered/ol-{filename}')

with Pool(processes=16) as p:
    p.map(renderhandler, listdir('dataset/skins'))