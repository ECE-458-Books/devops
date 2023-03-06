from imaginary_books_api.apps import Postman
from imaginary_books_api import serializer
import csv
import os
from pprint import pprint

def import_csvfile(csvfile):
    data_directory_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data'))
    filepath = f'{data_directory_path}/{csvfile}'
    l = list() 

    with open(filepath) as data:
        for line in csv.reader(data):
            l.append(line)

    return l

if __name__ == "__main__":
    csvfile = 'Ev2_Prefab_Data_Books.csv'

    datalist = import_csvfile(csvfile)

    postman = Postman()
    data = serializer._format(method='book_add', data=datalist)
    pprint(data)
    for book in data:
        response = postman.post(method='book_add', data=book)
        print(response)
        if 'errors' in response:
            print(book['title'], response)

