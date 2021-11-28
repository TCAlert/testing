from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib.request
import imageio

usage = '```$msfc [satellite] [bands 2, 5, 7, 8, 13, or 14] [latitude] [longitude]```'

def build(satt, band, lat, lon):
    if band == '2' or band == '5':
        htmldata = urlopen(f'https://weather.msfc.nasa.gov/cgi-bin/get-abi?satellite=GOES{satt.capitalize()}fullDiskband{band.zfill(2)}&lat={lat}&lon={lon}&zoom=2&type=Animation&numframes=25&width=809&height=500&palette=ir1.pal')
    elif band == '7':
        htmldata = urlopen(f'https://weather.msfc.nasa.gov/cgi-bin/get-abi?satellite=GOES{satt.capitalize()}fullDiskband07&lat={lat}&lon={lon}&zoom=1&type=Animation&numframes=25&width=809&height=500&palette=ir1.pal')
    elif band == '8':
        htmldata = urlopen(f'https://weather.msfc.nasa.gov/cgi-bin/get-abi?satellite=GOES{satt.capitalize()}fullDiskband08&lat={lat}&lon={lon}&zoom=1&type=Animation&numframes=25&width=809&height=500&palette=wv3.pal')
    elif band == '13' or band == '14':
        htmldata = urlopen(f'https://weather.msfc.nasa.gov/cgi-bin/get-abi?satellite=GOES{satt.capitalize()}fullDiskband{band.zfill(2)}&lat={lat}&lon={lon}&zoom=1&type=Animation&numframes=25&width=809&height=500&palette=ir10.pal')
    soup = BeautifulSoup(htmldata, 'html.parser')

    images = str(soup.find('body')).split(');">')[0]
    images = (((images.split('<body onload="setup('))[1]).split(','))
    for x in range(len(images)):
        if ('[') in images[x]:
            images[x] = images[x][1:]
        elif (']') in images[x]:
            images[x] = images[x][:-1]
        images[x] = images[x][1:][:-1]
        images[x] = f'https://weather.msfc.nasa.gov{images[x]}'

    for x in range(len(images) - 1):
        urllib.request.urlretrieve(images[x], r"C:\Users\Jariwala\Downloads\msfcloops\imagenumber" + str(x + 1) + ".png")

    with imageio.get_writer(r"C:\Users\Jariwala\Downloads\msfcloop.gif", mode='I', duration = 0.1) as writer:
        for x in range(len(images) - 1):
            writer.append_data(imageio.imread((r"C:\Users\Jariwala\Downloads\msfcloops\imagenumber" + str(x + 1) + ".png").format(i = x)))
        for y in range(0, 9):
            writer.append_data(imageio.imread((r"C:\Users\Jariwala\Downloads\msfcloops\imagenumber" + str(x + 1) + ".png").format(i = x)))

#build('west', 9, 13.2, -136.5)