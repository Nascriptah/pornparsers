import pickle
import re
import sqlite3
import face_recognition
con = sqlite3.connect('baza.db')
cur = con.cursor()



def finder():
    list = []
    filter_list = []
    final_list = []
    unknown_image = face_recognition.load_image_file("test.jpg")
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    cur.execute('SELECT name, tags, encoding FROM stars')
    rows = cur.fetchall()
    for row in rows:
        stars_encoding = pickle.loads(row[2])
        results = face_recognition.compare_faces([stars_encoding][0], unknown_encoding, tolerance=0.65)
        if results == [True]:
            list.append(row)
            print(row[0])
    for i in list:
        if 'big boobs' in i[1]:
            filter_list.append(i)
    for i in filter_list:
        if 'brown hair' in i[1]:
            final_list.append(i[0])
    print(final_list)

finder()
