#  OCR Based Search System

#  Design a system that asks to browse the folder
# import libraries
import os
import tkinter as tk
from tkinter import filedialog
import sqlite3
from tkinter import ttk
import pytesseract
from PIL import Image
import requests

# root setup
root = tk.Tk()
root.withdraw()

#  keep the book name in the database

book_name = filedialog.askdirectory()
book_name = book_name.split('/')[-1]
print(book_name)

#  extract text (using OCR) from the images


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    # it will use Pillow's Image class to open the image and pytesseract to detect the string in the image
    text = pytesseract.image_to_string(Image.open(filename))  
    return text

#  save those in the database too


conn = sqlite3.connect('books.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS books
                (book_name text, page_number integer, text text)''')

for i in os.listdir(book_name):
    text = ocr_core(book_name + '/' + i)
    c.execute("INSERT INTO books VALUES (?, ?, ?)", (book_name, i.split('.')[0], text))
    conn.commit()

#  design the search box in such a way that if someone types anything that is searched in the database 
#  with autofill and returns the book title, and page number on which that text has appeared


root = tk.Tk()
root.title('Search Box')

def search(event):
    search = entry.get()
    c.execute("SELECT * FROM books WHERE text LIKE ?", ('%' + search + '%',))
    results = c.fetchall()
    for i in tree.get_children():
        tree.delete(i)
    for i in results:
        tree.insert('', 'end', values=i)

entry = tk.Entry(root)
entry.bind('<Return>', search)
entry.pack()

tree = ttk.Treeview(root, columns=('book_name', 'page_number', 'text'), show='headings')
tree.heading('book_name', text='Book Name')
tree.heading('page_number', text='Page Number')
tree.heading('text', text='Text')
tree.pack()

root.mainloop()

#  On clicking that page should be downloaded   

def download(url, filename):
    with open(filename, 'wb') as f:
        f.write(requests.get(url).content)

for i in tree.selection():
    book_name, page_number, _ = tree.item(i)['values']
    download('search box/' + book_name + '/' + page_number + '.jpg', page_number + '.jpg')
