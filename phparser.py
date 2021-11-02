import face_recognition
import requests, re
from PIL import Image
import sqlite3
import pickle
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

con = sqlite3.connect('baza.db')
cur = con.cursor()

class Vars():
    def __init__(self):
        self.name_list = []
        self.phlink_list = []
        self.duck_links = []
        self.sourse_photo = None
        self.img = None
        self.pick_encoding = None
        self.duck_photo_link = ''
        self.thumb_iter = 47
        self.page_iter = 36

vars = Vars()

options = Options()
options.binary_location = (r'C:/Users/Nascriptah/AppData/Local/Mozilla Firefox/firefox.exe')
options.headless = False
driver = webdriver.Firefox(options=options)

def main():
    parser()
    while True:
        while vars.thumb_iter < len(vars.phlink_list):
            selenium_finder()
            photo_downloader()
            vars.thumb_iter += 1
        vars.thumb_iter = 0
        vars.page_iter += 1
        parser()


def parser():
    #pornhub парсер (по фильтрам на сайте), лист имён и ссылок на профиль.
    r = requests.get('https://rt.pornhub.com/pornstars?gender=female&ethnicity=white&page=' + str(vars.page_iter))
    if r.status_code != 200:
        print('[PORNHUB ERROR 404]')
    else:
        vars.name_list = re.findall(r'<a class="js-mxp" data-mxptype=".+" data-mxptext="(.+)" href="/.+">', r.text)
        vars.phlink_list = re.findall(r'<a class="js-mxp" data-mxptype=".+" data-mxptext=".+" href="/(.+)">', r.text)


def selenium_finder():
    #selenium webdriver парсит ссылки по запросу на фотографии
    name = vars.name_list[vars.thumb_iter]
    if ' ' in vars.name_list[vars.thumb_iter]:
        name = name.replace(' ', '+')
    driver.get(f'https://duckduckgo.com/?q={name}+pornstar&t=h_&iar=images&iax=images&ia=images')
    time.sleep(2)
    elem = driver.find_element(By.CLASS_NAME, 'dropdown--safe-search')
    elem.click()
    elem = driver.find_element(By.LINK_TEXT, 'Выкл')
    elem.click()
    time.sleep(2)
    data = driver.page_source
    vars.duck_links = re.findall(r'data-src="(//external\S+=1)"', data)

def photo_downloader():
    if (len(vars.duck_links)) == 0:
        vars.thumb_iter += 1
        print(['NO FIND DUCKDUCK ERROR'])
        return
    #идёт по ссылкам, скачивает фото в файл temp.jpg
    iter = 0
    while (iter < len(vars.duck_links)) and iter <= 30:
        try:
            sourse_photo = requests.get('https:' + vars.duck_links[iter], timeout=10)
        except:
            continue
        temp_file = open('temp.jpg', 'w+b')
        temp_file.write(sourse_photo.content)
        #проверка на лицо. Если лицо есть лицо и оно одно, то сохраняет файл в архив temp + путь
        face = []
        try:
            image = face_recognition.load_image_file('temp.jpg')
            face = face_recognition.face_locations(image)
        except:
            print('[cannot identify image file temp.jpg]')
        if len(face) == 1:
            print(f'Page: {vars.page_iter} thumb: {vars.thumb_iter} {vars.name_list[vars.thumb_iter]} [FACE]')
            if 'pornstar' in vars.phlink_list[vars.thumb_iter]:
                file_path = ('C:/project/temp/pornstar/' + vars.name_list[vars.thumb_iter] + '/')
            elif 'model' in vars.phlink_list[vars.thumb_iter]:
                file_path = 'C:/project/temp/model/' + vars.name_list[vars.thumb_iter] + '/'
            else:
                file_path = 'C:/project/temp/other/' +  vars.name_list[vars.thumb_iter] + '/'
            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)
            image_file = open(file_path  + str(iter) + '.jpg', 'w+b')
            image_file.write(sourse_photo.content)

        else:
            print(f'Page: {vars.page_iter} thumb: {vars.thumb_iter} {vars.name_list[vars.thumb_iter]} [NO FACE]')
            iter += 1
            continue
        iter += 1
        #ссылка на профиль на pornhub
        file_link = open(file_path + '/' + 'link.txt', 'w')
        file_link.write('https://pornhub.com/' + vars.phlink_list[vars.thumb_iter])
        file_link.close()
    print(vars.name_list[vars.thumb_iter]+ ' [Download photos is done]')


def resizer():
    #сохранение с уменьшением размера и сжатием. Размер регулируется переменной width.
    width = 350
    ratio = (width / float(vars.img.size[0]))
    height = int((float(vars.img.size[1]) * float(ratio)))
    vars.img = vars.img.resize((width, height))
    vars.img.save('temp_size.jpg', quality=60, optimize=True)

def dbwriter():
    im = open('temp_size.jpg', 'r+b')
    im.array = im.read()
    try:
        cur.execute('INSERT INTO stars  (name, link, ethnicity, encoding, photo) VALUES (?, ?, ?, ?, ?);',
                    (vars.name_list[vars.thumb_iter], vars.phlink_list[vars.thumb_iter], 'white', vars.pick_encoding, im.array))
    except:
        print('[DB INSERT ERROR]')

    con.commit()
main()