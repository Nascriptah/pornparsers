import face_recognition
import requests, re
from PIL import Image
import sqlite3
import pickle
import time
import os

class Vars():
    def __init__(self):
        self.pages_link_list = []
        self.name = ''
        self.photo_link = ''
        self.link = ''
        self.boobs = None
        self.hair = None
        self.tattoo = False
        self.img = None
        self.encoding = None
        self.thumb_iter = 0
        self.page_iter = 1
        self.name_link_format = ''

vars = Vars()

con = sqlite3.connect('baza.db')
cur = con.cursor()
def main():
    getter()
    while True:
        while vars.thumb_iter < len(vars.pages_link_list):
            parser()
            print(f'Page: {vars.page_iter} thumb: {vars.thumb_iter} name: {vars.name}')
            ph_link_checker()
            face_detector()
            dbwriter()
            vars.thumb_iter += 1
        vars.thumb_iter = 0
        vars.page_iter += 1
        getter()

def getter():
    r = requests.get('https://nookthem.com/pornstars/female?page=' + str(vars.page_iter))
    vars.pages_link_list = re.findall(r'<a title=".+" href="(.+)\">', r.text)

def parser():
    r = requests.get(vars.pages_link_list[vars.thumb_iter])
    vars.tags = re.findall(r'name="keywords" content="(.+)', r.text)
    vars.tags = ''.join(vars.tags)
    boobs_list = ['small', 'normal', 'big', 'large']
    for boobs in boobs_list:
        if boobs in vars.tags:
            vars.boobs = boobs
    hair_list = ['blonde', 'brown', 'black', 'pink', 'red']
    for hair in hair_list:
        if hair in vars.tags:
            vars.hair = hair
    if 'tattoo' in vars.tags:
        vars.tattoo = True
    else:
        vars.tattoo = False

    vars.photo_link = re.findall(r'<img src="(.+)" alt=".+"', r.text)[0]
    vars.name = re.findall(r'<img src=".+" alt="(.+)"', r.text)[0]
    vars.link = ('https://www.pornhub.com/pornstar/' + vars.name)
    if ' ' in vars.name:
        vars.name_link_format = vars.name.replace(' ', '-').lower()
        vars.link = ('https://www.pornhub.com/pornstar/' + vars.name_link_format)

def ph_link_checker():
    r = requests.get(vars.link, timeout=10)
    if (vars.name) not in r.text:
        vars.link = None


def face_detector():
    r = requests.get(vars.photo_link)
    temp_file = open('temp.jpg', 'w+b')
    temp_file.write(r.content)
    try:
        image = face_recognition.load_image_file('temp.jpg')
        face = face_recognition.face_locations(image)
    except:
        print('[NO FACE temp.jpg]')
        vars.thumb_iter += 1
        return
    vars.encoding = face_recognition.face_encodings(image)
    vars.encoding = pickle.dumps(vars.encoding)

def dbwriter():
    photo = open('temp.jpg', 'rb').read()
    show = open('temp_size.jpg', 'rb' ).read()
    try:
        cur.execute('INSERT INTO stars  (name, photo, link, boobs, hair, tattoo, encoding)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?);',
                    (vars.name, photo, vars.link, vars.boobs, vars.hair, vars.tattoo, vars.encoding))
    except:
        print('[DB INSERT ERROR]')
    con.commit()
main()